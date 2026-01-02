"""
Conv2D forward/backward (NCHW) with stride and padding.
With automatic selection of optimized kernels (Implicit GEMM, Tiled Local Memory).
"""

from __future__ import annotations

import os
import time
from typing import Optional, Tuple

from netcl.core.tensor import Tensor
from netcl.core.memory import BufferPool
from netcl.core.backend import get_backend, ensure_same_backend
from netcl.ops.im2col import im2col, col2im
from netcl.ops.matmul import matmul as mm
from netcl.ops.transpose import transpose2d
from netcl.core.tensor import reshape as treshape
from netcl.core.kernel_selector import get_kernel_selector, KernelVariant
from netcl.ops.conv2d_cpu import conv2d_cpu, conv2d_backward_cpu
from netcl.ops.conv2d_optimized import (
    conv2d_implicit_gemm,
    conv2d_tiled_local,
    conv2d_winograd_f2x2_3x3,
    conv2d_backward_optimized,
)

try:
    import numpy as np  # type: ignore
except ImportError:  # pragma: no cover
    np = None

try:
    import pyopencl as cl  # type: ignore
except ImportError:  # pragma: no cover
    cl = None

_DTYPE_CNAME = {"float": "float", "float32": "float", "half": "half", "float16": "half"}
_ENV_DEFAULT_ALGO = os.environ.get("NETCL_CONV_ALGO", "im2col").lower()
_ENV_ENABLE_AUTO = os.environ.get("NETCL_CONV_AUTO", "1") not in ("0", "", "false", "False")
_ENV_AUTOTUNE = os.environ.get("NETCL_CONV_AUTOTUNE", "0") not in ("0", "", "false", "False")
_ENV_AUTOTUNE_WARMUP = int(os.environ.get("NETCL_CONV_AUTOTUNE_WARMUP", "2"))
_ENV_AUTOTUNE_RUNS = int(os.environ.get("NETCL_CONV_AUTOTUNE_RUNS", "3"))
_ENV_FORCE_AUTOTUNE = os.environ.get("NETCL_CONV_AUTOTUNE_FORCE", "0") not in ("0", "", "false", "False")
# New: Enable optimized kernels by default
_ENV_USE_OPTIMIZED = os.environ.get("NETCL_CONV_OPTIMIZED", "0") not in ("0", "", "false", "False")
_ENV_FORCE_LEGACY = os.environ.get("NETCL_CONV_LEGACY", "0") in ("1", "true", "True")
_ENV_OPTIMIZED_THRESHOLD = int(os.environ.get("NETCL_CONV_OPTIMIZED_THRESHOLD", "1024"))  # output elements threshold
_WARN_ON_FALLBACK = os.environ.get("NETCL_CONV_WARN_FALLBACK", "1") not in ("0", "", "false", "False")
_ENV_CONV_BENCH = os.environ.get("NETCL_CONV_BENCH_PER_SHAPE", "0") not in ("0", "", "false", "False")
_PROFILE_CONV = os.environ.get("NETCL_PROFILE_STATS", "0") not in ("0", "", "false", "False")
_ENV_CONV_TILE_AUTOTUNE = os.environ.get("NETCL_CONV_TILE_AUTOTUNE", "0") not in ("0", "", "false", "False")
_PROFILE_CONV_EVENTS = os.environ.get("NETCL_PROFILE_EVENTS", "0") not in ("0", "", "false", "False")
_ENV_OPT_AUTOTUNE_SHAPE = os.environ.get("NETCL_CONV_OPT_AUTOTUNE_SHAPE", "0") not in ("0", "", "false", "False")
_ENV_CONV_FUSE_RELU = os.environ.get("NETCL_CONV_FUSE_RELU", "0") not in ("0", "", "false", "False")
_ENV_CONV_IM2COL_OPT_MATMUL = os.environ.get("NETCL_CONV_IM2COL_OPT_MATMUL", "1") not in ("0", "", "false", "False")
_ENV_CONV_PERF_GATE = os.environ.get("NETCL_CONV_PERF_GATE", "1") not in ("0", "", "false", "False")

_TUNE_CACHE: dict = {}
_IN_TUNING = False
_HEUR_CACHE: dict = {}
_STRATEGY_CACHE: dict = {}
_IN_BENCH = False
_BENCH_CACHE: dict = {}
_OPT_TUNE_CACHE: dict = {}
_OPT_PERF_CACHE: dict = {}
_IN_OPT_TUNE = False
_IN_OPT_PERF = False
_CONV_STATS = {"fwd_calls": 0, "bwd_calls": 0, "fwd_time": 0.0, "bwd_time": 0.0}
_CONV_TILE_CACHE: dict = {}
_CONV_EVENT_STATS = {"fwd_events": 0, "fwd_event_time": 0.0, "bwd_events": 0, "bwd_event_time": 0.0}
try:
    from netcl.core.capabilities import device_profile, kernel_strategy
except ImportError:  # pragma: no cover
    device_profile = None  # type: ignore
    kernel_strategy = None  # type: ignore

if _PROFILE_CONV:
    import atexit

    def _print_conv_stats():
        if _CONV_STATS["fwd_calls"] + _CONV_STATS["bwd_calls"] == 0:
            return
        print(
            f"[conv stats] fwd_calls={_CONV_STATS['fwd_calls']} total_ms={_CONV_STATS['fwd_time']*1000:.2f} "
            f"bwd_calls={_CONV_STATS['bwd_calls']} total_ms={_CONV_STATS['bwd_time']*1000:.2f}"
        )
        if _PROFILE_CONV_EVENTS:
            print(
                f"[conv events] fwd_events={_CONV_EVENT_STATS['fwd_events']} event_ms={_CONV_EVENT_STATS['fwd_event_time']*1000:.2f} "
                f"bwd_events={_CONV_EVENT_STATS['bwd_events']} event_ms={_CONV_EVENT_STATS['bwd_event_time']*1000:.2f}"
            )

    atexit.register(_print_conv_stats)

# Lazy imports for optimized kernels
_conv2d_implicit_gemm = None
_conv2d_tiled_local = None
_REORDER_KERNEL_CACHE: dict = {}
_NCHW2COL_KERNEL_CACHE: dict = {}

def _preferred_conv_tile(device: Optional["cl.Device"]) -> int:
    """Pick a reasonable conv tile for this device."""
    if device is None:
        return 4
    vendor = getattr(device, "vendor", "").lower()
    if "nvidia" in vendor:
        return 8
    return 4


def _device_hash(device: Optional["cl.Device"]) -> str:
    if device is None:
        return "unknown"
    name = getattr(device, "name", "unknown")
    vendor = getattr(device, "vendor", "unknown")
    lmem = getattr(device, "local_mem_size", 0)
    wg = getattr(device, "max_work_group_size", 0)
    return f"{vendor}|{name}|{lmem}|{wg}"


def _choose_conv_tile(device: Optional["cl.Device"], preferred: Optional[int] = None) -> int:
    """
    Select a tile size that respects device work-group limits.
    Falls back through candidate list until a valid tile is found.
    """
    key = getattr(device, "int_ptr", None) or getattr(device, "name", None)
    if key in _CONV_TILE_CACHE:
        return _CONV_TILE_CACHE[key]
    max_wg = getattr(device, "max_work_group_size", 256) if device is not None else 256
    max_dim = 0
    try:
        if device is not None:
            max_dim = min(device.max_work_item_sizes[0], device.max_work_item_sizes[1])
    except Exception:
        max_dim = 0
    candidates = [preferred] if preferred else []
    candidates.extend([_preferred_conv_tile(device), 8, 4])
    seen = set()
    tile_sel = 4
    for t in candidates:
        if t is None or t in seen:
            continue
        seen.add(t)
        if t * t <= max_wg and (max_dim == 0 or t <= max_dim):
            tile_sel = t
            break
    _CONV_TILE_CACHE[key] = tile_sel
    return tile_sel


def _bench_tiled_tile(x: Tensor, w: Tensor, bias: Optional[Tensor], stride: int, pad: int, tile_oh: int, tile_ow: int) -> float:
    """Benchmark a single tiled_local run and return seconds."""
    if cl is None or np is None:
        return 1e9
    try:
        t0 = time.perf_counter()
        out = conv2d_tiled_local(x, w, bias=bias, stride=stride, pad=pad, tile_oh=tile_oh, tile_ow=tile_ow)
        out.queue.finish()
        return time.perf_counter() - t0
    except Exception:
        return 1e9


def _autotune_conv_tile(x: Tensor, w: Tensor, bias: Optional[Tensor], stride: int, pad: int) -> Tuple[int, int]:
    """
    Autotune tiled_local tile sizes for this device/shape. Returns (tile_oh, tile_ow).
    Cached per device and shape to avoid repeated tuning.
    """
    if not _ENV_CONV_TILE_AUTOTUNE:
        t = _choose_conv_tile(x.queue.device, None)
        return t, t
    dev = getattr(x.queue, "device", None)
    key = (_device_hash(dev), x.shape, w.shape, stride, pad, x.dtype, w.dtype)
    if key in _CONV_TILE_CACHE:
        t_sel = _CONV_TILE_CACHE[key]
        return t_sel, t_sel
    candidates = [4, 8, 16, 32]  # Guardrail: cap tiles for Pascal-class GPUs
    best_t = 1e9
    best_tile = _choose_conv_tile(dev, None)
    for t in candidates:
        t_valid = _choose_conv_tile(dev, t)
        dt = _bench_tiled_tile(x, w, bias, stride, pad, t_valid, t_valid)
        if dt < best_t:
            best_t = dt
            best_tile = t_valid
    _CONV_TILE_CACHE[key] = best_tile
    return best_tile, best_tile


def _autotune_optimized_conv(
    x: Tensor,
    w: Tensor,
    bias: Optional[Tensor],
    stride: int,
    pad: int,
) -> Tuple[str, Optional[Tuple[int, int]]]:
    """
    Autotune between optimized variants (implicit_gemm, tiled_local, im2col) for this shape/device.
    Returns (variant, tile) where tile is only used for tiled_local.
    """
    if not _ENV_OPT_AUTOTUNE_SHAPE:
        return "implicit_gemm", None
    dev = getattr(x.queue, "device", None)
    key = (_device_hash(dev), x.shape, w.shape, stride, pad, x.dtype, w.dtype)
    if key in _OPT_TUNE_CACHE:
        return _OPT_TUNE_CACHE[key]
    candidates = []
    implicit, tiled = _get_optimized_conv_kernels()
    if implicit:
        candidates.append("implicit_gemm")
    if tiled:
        candidates.append("tiled_local")
    # Always include im2col as baseline
    candidates.append("im2col")
    best = "im2col"
    best_t = 1e9
    best_tile: Optional[Tuple[int, int]] = None
    global _IN_OPT_TUNE
    if _IN_OPT_TUNE:
        return "im2col", None
    _IN_OPT_TUNE = True
    try:
        for cand in candidates:
            try:
                # Prepare output buffer reuse
                if cand == "implicit_gemm":
                    t0 = time.perf_counter()
                    out = conv2d_implicit_gemm(x, w, bias=bias, stride=stride, pad=pad)
                    out.queue.finish()
                    dt = time.perf_counter() - t0
                elif cand == "tiled_local":
                    tile_oh, tile_ow = _autotune_conv_tile(x, w, bias, stride, pad)
                    t0 = time.perf_counter()
                    out = conv2d_tiled_local(x, w, bias=bias, stride=stride, pad=pad, tile_oh=tile_oh, tile_ow=tile_ow)
                    out.queue.finish()
                    dt = time.perf_counter() - t0
                else:  # im2col fallback
                    t0 = time.perf_counter()
                    out = conv2d(x, w, bias=bias, stride=stride, pad=pad, algo="im2col")  # type: ignore
                    out.queue.finish()
                    dt = time.perf_counter() - t0
                if dt < best_t:
                    best_t = dt
                    best = cand
                    best_tile = (tile_oh, tile_ow) if cand == "tiled_local" else None
            except Exception:
                continue
    finally:
        _IN_OPT_TUNE = False
    _OPT_TUNE_CACHE[key] = (best, best_tile if best == "tiled_local" else None)  # type: ignore
    return _OPT_TUNE_CACHE[key]

def _get_optimized_conv_kernels():
    """Lazy import of optimized conv2d kernels."""
    global _conv2d_implicit_gemm, _conv2d_tiled_local
    if _conv2d_implicit_gemm is None:
        try:
            from netcl.ops.conv2d_optimized import conv2d_implicit_gemm, conv2d_tiled_local
            _conv2d_implicit_gemm = conv2d_implicit_gemm
            _conv2d_tiled_local = conv2d_tiled_local
        except ImportError:
            _conv2d_implicit_gemm = False
            _conv2d_tiled_local = False
    return _conv2d_implicit_gemm, _conv2d_tiled_local


def conv2d_output_shape(
    x_shape: Tuple[int, int, int, int], w_shape: Tuple[int, int, int, int], stride: int = 1, pad: int = 0
) -> Tuple[int, int, int, int]:
    N, C, H, W = x_shape
    F, Cw, KH, KW = w_shape
    if C != Cw:
        raise ValueError("input and weight channel mismatch")
    OH = (H + 2 * pad - KH) // stride + 1
    OW = (W + 2 * pad - KW) // stride + 1
    return (N, F, OH, OW)


def _build_forward_kernel(ctx: "cl.Context", dtype_c: str):
    src = f"""
    __kernel void conv2d_fwd(__global const {dtype_c}* x, __global const {dtype_c}* w, __global const {dtype_c}* b, __global {dtype_c}* out,
                             const int N, const int C, const int H, const int W,
                             const int KH, const int KW, const int OH, const int OW, const int F,
                             const int stride, const int pad) {{
        int gid = get_global_id(0);
        int total = N * F * OH * OW;
        if (gid >= total) return;
        int ow = gid % OW;
        int oh = (gid / OW) % OH;
        int f = (gid / (OH * OW)) % F;
        int n = gid / (F * OH * OW);
        float acc = 0.0f;
        for (int c = 0; c < C; ++c) {{
            for (int kh = 0; kh < KH; ++kh) {{
                int ih = oh * stride + kh - pad;
                if (ih < 0 || ih >= H) continue;
                for (int kw = 0; kw < KW; ++kw) {{
                    int iw = ow * stride + kw - pad;
                    if (iw < 0 || iw >= W) continue;
                    int x_idx = ((n*C + c)*H + ih)*W + iw;
                    int w_idx = ((f*C + c)*KH + kh)*KW + kw;
                    acc += x[x_idx] * w[w_idx];
                }}
            }}
        }}
        if (b != 0) acc += b[f];
        out[gid] = acc;
    }}
    """
    prg = cl.Program(ctx, src).build()
    return prg.conv2d_fwd


def _build_forward_tiled_kernel(ctx: "cl.Context", dtype_c: str, tile_h: int = 8, tile_w: int = 8):
    src = f"""
    #define TILE_H {tile_h}
    #define TILE_W {tile_w}
    __kernel void conv2d_fwd_tiled(__global const {dtype_c}* x, __global const {dtype_c}* w, __global const {dtype_c}* b, __global {dtype_c}* out,
                                   const int N, const int C, const int H, const int W,
                                   const int KH, const int KW, const int OH, const int OW, const int F,
                                   const int stride, const int pad) {{
        int ow = get_global_id(0);
        int oh = get_global_id(1);
        int nf = get_global_id(2);
        if (ow >= OW || oh >= OH) return;
        int n = nf / F;
        int f = nf - n * F;
        if (n >= N) return;
        float acc = 0.0f;
        for (int c = 0; c < C; ++c) {{
            for (int kh = 0; kh < KH; ++kh) {{
                int ih = oh * stride + kh - pad;
                if (ih < 0 || ih >= H) continue;
                for (int kw = 0; kw < KW; ++kw) {{
                    int iw = ow * stride + kw - pad;
                    if (iw < 0 || iw >= W) continue;
                    int x_idx = ((n*C + c)*H + ih)*W + iw;
                    int w_idx = ((f*C + c)*KH + kh)*KW + kw;
                    acc += x[x_idx] * w[w_idx];
                }}
            }}
        }}
        if (b != 0) acc += b[f];
        int out_idx = ((n*F + f)*OH + oh)*OW + ow;
        out[out_idx] = acc;
    }}
    """
    prg = cl.Program(ctx, src).build()
    return prg.conv2d_fwd_tiled


def _build_grad_input_kernel(ctx: "cl.Context", dtype_c: str):
    src = f"""
    __kernel void conv2d_grad_input(__global const {dtype_c}* grad_out, __global const {dtype_c}* w, __global {dtype_c}* grad_in,
                                    const int N, const int C, const int H, const int W,
                                    const int KH, const int KW, const int OH, const int OW, const int F,
                                    const int stride, const int pad) {{
        int gid = get_global_id(0);
        int total = N * C * H * W;
        if (gid >= total) return;
        int wcoord = gid % W;
        int hcoord = (gid / W) % H;
        int c = (gid / (H * W)) % C;
        int n = gid / (C * H * W);
        float acc = 0.0f;
        for (int f = 0; f < F; ++f) {{
            for (int kh = 0; kh < KH; ++kh) {{
                int oh_num = hcoord + pad - kh;
                if (oh_num < 0) continue;
                if (oh_num % stride != 0) continue;
                int oh = oh_num / stride;
                if (oh < 0 || oh >= OH) continue;
                for (int kw = 0; kw < KW; ++kw) {{
                    int ow_num = wcoord + pad - kw;
                    if (ow_num < 0) continue;
                    if (ow_num % stride != 0) continue;
                    int ow = ow_num / stride;
                    if (ow < 0 || ow >= OW) continue;
                    int go_idx = ((n*F + f)*OH + oh)*OW + ow;
                    int w_idx = ((f*C + c)*KH + kh)*KW + kw;
                    acc += grad_out[go_idx] * w[w_idx];
                }}
            }}
        }}
        grad_in[gid] = acc;
    }}
    """
    prg = cl.Program(ctx, src).build()
    return prg.conv2d_grad_input


def _build_grad_input_tiled_kernel(ctx: "cl.Context", dtype_c: str, tile_h: int = 8, tile_w: int = 8):
    src = f"""
    #define TILE_H {tile_h}
    #define TILE_W {tile_w}
    __kernel void conv2d_grad_input_tiled(__global const {dtype_c}* grad_out, __global const {dtype_c}* w, __global {dtype_c}* grad_in,
                                          const int N, const int C, const int H, const int W,
                                          const int KH, const int KW, const int OH, const int OW, const int F,
                                          const int stride, const int pad) {{
        int wcoord = get_global_id(0);
        int hcoord = get_global_id(1);
        int nc = get_global_id(2);
        if (wcoord >= W || hcoord >= H) return;
        int n = nc / C;
        int c = nc - n * C;
        if (n >= N) return;
        float acc = 0.0f;
        for (int f = 0; f < F; ++f) {{
            for (int kh = 0; kh < KH; ++kh) {{
                int oh_num = hcoord + pad - kh;
                if (oh_num < 0) continue;
                if (oh_num % stride != 0) continue;
                int oh = oh_num / stride;
                if (oh < 0 || oh >= OH) continue;
                for (int kw = 0; kw < KW; ++kw) {{
                    int ow_num = wcoord + pad - kw;
                    if (ow_num < 0) continue;
                    if (ow_num % stride != 0) continue;
                    int ow = ow_num / stride;
                    if (ow < 0 || ow >= OW) continue;
                    int go_idx = ((n*F + f)*OH + oh)*OW + ow;
                    int w_idx = ((f*C + c)*KH + kh)*KW + kw;
                    acc += grad_out[go_idx] * w[w_idx];
                }}
            }}
        }}
        int out_idx = ((n*C + c)*H + hcoord)*W + wcoord;
        grad_in[out_idx] = acc;
    }}
    """
    prg = cl.Program(ctx, src).build()
    return prg.conv2d_grad_input_tiled


def _build_grad_weight_kernel(ctx: "cl.Context", dtype_c: str):
    src = f"""
    __kernel void conv2d_grad_weight(__global const {dtype_c}* x, __global const {dtype_c}* grad_out, __global {dtype_c}* grad_w,
                                     const int N, const int C, const int H, const int W,
                                     const int KH, const int KW, const int OH, const int OW, const int F,
                                     const int stride, const int pad) {{
        int gid = get_global_id(0);
        int total = F * C * KH * KW;
        if (gid >= total) return;
        int kw = gid % KW;
        int kh = (gid / KW) % KH;
        int c = (gid / (KH * KW)) % C;
        int f = gid / (C * KH * KW);
        float acc = 0.0f;
        for (int n = 0; n < N; ++n) {{
            for (int oh = 0; oh < OH; ++oh) {{
                int ih = oh * stride + kh - pad;
                if (ih < 0 || ih >= H) continue;
                for (int ow = 0; ow < OW; ++ow) {{
                    int iw = ow * stride + kw - pad;
                    if (iw < 0 || iw >= W) continue;
                    int x_idx = ((n*C + c)*H + ih)*W + iw;
                    int go_idx = ((n*F + f)*OH + oh)*OW + ow;
                    acc += x[x_idx] * grad_out[go_idx];
                }}
            }}
        }}
        grad_w[gid] = acc;
    }}
    """
    prg = cl.Program(ctx, src).build()
    return prg.conv2d_grad_weight


def _build_grad_weight_tiled_kernel(ctx: "cl.Context", dtype_c: str):
    src = f"""
    __kernel void conv2d_grad_weight_tiled(__global const {dtype_c}* x, __global const {dtype_c}* grad_out, __global {dtype_c}* grad_w,
                                           const int N, const int C, const int H, const int W,
                                           const int KH, const int KW, const int OH, const int OW, const int F,
                                           const int stride, const int pad) {{
        int kw = get_global_id(0);
        int kh = get_global_id(1);
        int fc = get_global_id(2);
        if (kw >= KW || kh >= KH) return;
        int f = fc / C;
        int c = fc - f * C;
        if (f >= F || c >= C) return;
        float acc = 0.0f;
        for (int n = 0; n < N; ++n) {{
            for (int oh = 0; oh < OH; ++oh) {{
                int ih = oh * stride + kh - pad;
                if (ih < 0 || ih >= H) continue;
                for (int ow = 0; ow < OW; ++ow) {{
                    int iw = ow * stride + kw - pad;
                    if (iw < 0 || iw >= W) continue;
                    int x_idx = ((n*C + c)*H + ih)*W + iw;
                    int go_idx = ((n*F + f)*OH + oh)*OW + ow;
                    acc += x[x_idx] * grad_out[go_idx];
                }}
            }}
        }}
        int w_idx = ((f*C + c)*KH + kh)*KW + kw;
        grad_w[w_idx] = acc;
    }}
    """
    prg = cl.Program(ctx, src).build()
    return prg.conv2d_grad_weight_tiled


def _build_grad_bias_kernel(ctx: "cl.Context", dtype_c: str):
    src = f"""
    __kernel void conv2d_grad_bias(__global const {dtype_c}* grad_out, __global {dtype_c}* grad_b,
                                   const int N, const int F, const int OH, const int OW) {{
        int f = get_global_id(0);
        if (f >= F) return;
        float acc = 0.0f;
        for (int n = 0; n < N; ++n) {{
            for (int oh = 0; oh < OH; ++oh) {{
                for (int ow = 0; ow < OW; ++ow) {{
                    int idx = ((n*F + f)*OH + oh)*OW + ow;
                    acc += grad_out[idx];
                }}
            }}
        }}
        grad_b[f] = acc;
    }}
    """
    prg = cl.Program(ctx, src).build()
    return prg.conv2d_grad_bias


def _build_out_reorder_kernel(ctx: "cl.Context", dtype_c: str, fuse_relu: bool = False):
    """
    Reorder output from (N*OH*OW, F) to NCHW (N, F, OH, OW) and optionally add bias.
    """
    cache_key = (ctx.int_ptr, "col2nchw", dtype_c, fuse_relu)
    if cache_key in _REORDER_KERNEL_CACHE:
        return _REORDER_KERNEL_CACHE[cache_key]
    fuse_line = f"val = fmax(val, ({dtype_c})0);" if fuse_relu else ""
    src = f"""
    __kernel void col2nchw(__global const {dtype_c}* src, __global const {dtype_c}* bias, __global {dtype_c}* dst,
                           const int N, const int F, const int OH, const int OW) {{
        int gid = get_global_id(0);
        int total = N * F * OH * OW;
        if (gid >= total) return;
        int ow = gid % OW;
        int oh = (gid / OW) % OH;
        int f = (gid / (OW * OH)) % F;
        int n = gid / (OW * OH * F);
        int src_row = n * OH * OW + oh * OW + ow;
        int src_idx = src_row * F + f;
        float val = src[src_idx];
        if (bias != 0) {{
            val += bias[f];
        }}
        {fuse_line}
        dst[gid] = val;
    }}
    """
    prg = cl.Program(ctx, src).build()
    _REORDER_KERNEL_CACHE[cache_key] = prg.col2nchw
    return prg.col2nchw


def _build_nchw_to_col_kernel(ctx: "cl.Context", dtype_c: str):
    """
    Flatten grad_out from NCHW to (N*OH*OW, F) layout expected by GEMM without host roundtrips.
    """
    cache_key = (ctx.int_ptr, "nchw2col", dtype_c)
    if cache_key in _NCHW2COL_KERNEL_CACHE:
        return _NCHW2COL_KERNEL_CACHE[cache_key]
    src = f"""
    __kernel void nchw2col(__global const {dtype_c}* go, __global {dtype_c}* dst,
                           const int N, const int F, const int OH, const int OW) {{
        int gid = get_global_id(0);
        int total = N * F * OH * OW;
        if (gid >= total) return;
        int f = gid % F;
        int ow = (gid / F) % OW;
        int oh = (gid / (F * OW)) % OH;
        int n = gid / (F * OW * OH);
        int src_idx = ((n * F + f) * OH + oh) * OW + ow;
        int row = n * OH * OW + oh * OW + ow;
        dst[row * F + f] = go[src_idx];
    }}
    """
    prg = cl.Program(ctx, src).build()
    _NCHW2COL_KERNEL_CACHE[cache_key] = prg.nchw2col
    return prg.nchw2col


def _auto_select_algo(shape_info: Optional[Tuple[int, int, int, int, int, int, int, int, int]], stride: int, pad: int) -> str:
    """
    Very lightweight heuristic:
    - prefers tile for common 3x3 stride1 (pad 0/1) with moderate featuremaps
    - otherwise falls back to naive
    """
    if shape_info is None:
        return "naive"
    N, C, H, W, F, KH, KW, OH, OW = shape_info
    if KH == 3 and KW == 3 and stride == 1 and pad in (0, 1):
        area = OH * OW
        if F >= 16 and area >= 64:
            return "tile"
    return "naive"


def _autotune_algo(x: Tensor, w: Tensor, bias: Optional[Tensor], stride: int, pad: int, candidates: Tuple[str, ...]) -> str:
    key = (
        x.shape,
        w.shape,
        stride,
        pad,
        x.dtype,
        w.dtype,
    )
    if key in _TUNE_CACHE:
        return _TUNE_CACHE[key]
    global _IN_TUNING
    _IN_TUNING = True
    timings = []
    warmup = max(0, _ENV_AUTOTUNE_WARMUP)
    runs = max(1, _ENV_AUTOTUNE_RUNS)
    for algo in candidates:
        # warmup
        for _ in range(warmup):
            out = conv2d(x, w, bias=bias, stride=stride, pad=pad, algo=algo)  # type: ignore
            out.queue.finish()
        # timed runs
        t_min = 1e9
        for _ in range(runs):
            t0 = time.perf_counter()
            out = conv2d(x, w, bias=bias, stride=stride, pad=pad, algo=algo)  # type: ignore
            out.queue.finish()
            t1 = time.perf_counter()
            t_min = min(t_min, t1 - t0)
        timings.append((t_min, algo))
    _IN_TUNING = False
    best = min(timings, key=lambda p: p[0])[1]
    _TUNE_CACHE[key] = best
    return best


def _heuristic_algo(shape_info: Tuple[int, int, int, int, int, int, int, int, int], stride: int, pad: int, device_name: str) -> str:
    """
    Full heuristic keyed by shape/device. Prefers:
    - tile for typical 3x3 stride1 pad<=1 with moderate spatial size
    - im2col as the safe default for GPU workloads to avoid slow naive paths
    """
    key = (shape_info, stride, pad, device_name)
    if key in _HEUR_CACHE:
        return _HEUR_CACHE[key]
    N, C, H, W, F, KH, KW, OH, OW = shape_info
    area = OH * OW
    algo = "im2col"
    if KH == 3 and KW == 3 and stride == 1 and pad in (0, 1) and F >= 16 and area >= 64:
        algo = "tile"
    elif area <= 16 and F <= 4:
        algo = "naive"
    _HEUR_CACHE[key] = algo
    return algo


def _bench_algos(
    x: Tensor, w: Tensor, bias: Optional[Tensor], stride: int, pad: int, candidates: Tuple[str, ...]
) -> str:
    """
    Micro-benchmark a set of algos on the current shape/device and return the fastest.
    Intended for debugging on GPUs like P6000 to pick the least-bad path.
    """
    key = (x.shape, w.shape, stride, pad, x.dtype, w.dtype)
    if key in _BENCH_CACHE:
        return _BENCH_CACHE[key]
    q = x.queue
    best = None
    best_t = 1e9
    global _IN_BENCH
    if _IN_BENCH:
        return candidates[0]
    _IN_BENCH = True
    try:
        for algo in candidates:
            try:
                t0 = time.perf_counter()
                out = conv2d(x, w, bias=bias, stride=stride, pad=pad, algo=algo)
                out.queue.finish()
                dt = time.perf_counter() - t0
                if dt < best_t:
                    best_t = dt
                    best = algo
            except Exception:
                continue
    finally:
        _IN_BENCH = False
    if best is None:
        best = candidates[0]
    _BENCH_CACHE[key] = best
    return best


def _resolve_algo(
    algo: Optional[str],
    use_im2col: bool,
    shape_info: Optional[Tuple[int, int, int, int, int, int, int, int, int]],
    stride: int,
    pad: int,
    device_name: str,
    strategy: str,
) -> str:
    """
    Resolve algorithm name to an internal path flag.
    Supports "naive", "im2col", "tile" (forward). Unknown/experimental names fall back to "naive".
    """
    if algo:
        algo = algo.lower()
    if use_im2col and not algo:
        algo = "im2col"
    if not algo or algo == "":
        algo = _ENV_DEFAULT_ALGO or "auto"
    if algo == "auto":
        if _ENV_AUTOTUNE or _ENV_FORCE_AUTOTUNE:
            algo = "auto"  # leave for autotuner
        elif _ENV_ENABLE_AUTO and shape_info is not None:
            algo = _heuristic_algo(shape_info, stride, pad, device_name)
        else:
            algo = "naive"
    allowed = {"naive", "direct", "im2col"} if strategy == "portable" else {"naive", "direct", "im2col", "tile", "winograd", "fft"}
    if algo in allowed:
        return algo
    if algo == "auto":
        return "naive"
    # If user explicitly requested a non-portable algo, honor it (may be slower/unsafe on some devices)
    if algo in ("winograd", "fft", "tile"):
        return algo
    raise ValueError(f"unsupported conv2d algo: {algo}")


def conv2d(
    x: Tensor,
    w: Tensor,
    bias: Optional[Tensor] = None,
    out: Optional[Tensor] = None,
    pool: Optional[BufferPool] = None,
    stride: int = 1,
    pad: int = 0,
    use_im2col: bool = False,
    algo: Optional[str] = None,
    strategy: Optional[str] = None,
) -> Tensor:
    global _IN_OPT_PERF
    t0_prof = time.perf_counter() if _PROFILE_CONV else None
    backend = ensure_same_backend((x, w) + ((bias,) if bias is not None else ()), op="conv2d")
    if x.dtype != w.dtype:
        raise ValueError(f"dtype mismatch: x {x.dtype} vs w {w.dtype}")
    if backend == "cpu":
        return conv2d_cpu(x, w, bias=bias, stride=stride, pad=pad)
    if cl is None or np is None:
        raise ImportError("pyopencl and numpy required for conv2d")
    N, C, H, W = x.shape
    F, Cw, KH, KW = w.shape
    if C != Cw:
        raise ValueError("channel mismatch")
    OH = (H + 2 * pad - KH) // stride + 1
    OW = (W + 2 * pad - KW) // stride + 1
    # Decide optimized usage & perf cache
    use_opt = _ENV_USE_OPTIMIZED and not _ENV_FORCE_LEGACY and not _ENV_FORCE_AUTOTUNE and not _IN_OPT_PERF
    perf_key = None
    if _ENV_CONV_PERF_GATE and not _IN_OPT_PERF:
        dev = getattr(x.queue, "device", None)
        perf_key = (_device_hash(dev), x.shape, w.shape, stride, pad, x.dtype, w.dtype)
        cached_perf = _OPT_PERF_CACHE.get(perf_key)
        if cached_perf and cached_perf[0] == "im2col":
            use_im2col = True
            use_opt = False
    # Optimized path via KernelSelector
    opt_variant = None
    opt_tile = None
    if use_opt:
        try:
            selector = get_kernel_selector(x.queue.device)
            cfg = selector.select_conv2d_kernel(
                batch=N,
                in_channels=C,
                out_channels=F,
                height=H,
                width=W,
                kernel_h=KH,
                kernel_w=KW,
                stride=stride,
                padding=pad,
                dtype=x.dtype,
            )
            if _ENV_OPT_AUTOTUNE_SHAPE:
                opt_variant, opt_tile = _autotune_optimized_conv(x, w, bias, stride, pad)
            else:
                if cfg.variant == KernelVariant.CONV2D_IMPLICIT_GEMM:
                    opt_variant = "implicit_gemm"
                elif cfg.variant == KernelVariant.CONV2D_TILED_LOCAL:
                    opt_variant = "tiled_local"
                    opt_tile = (
                        _autotune_conv_tile(x, w, bias, stride, pad)
                        if _ENV_CONV_TILE_AUTOTUNE
                        else (
                            _choose_conv_tile(x.queue.device, cfg.tile_m),
                            _choose_conv_tile(x.queue.device, cfg.tile_n),
                        )
                    )
                elif cfg.variant == KernelVariant.CONV2D_WINOGRAD:
                    opt_variant = "winograd"
                elif cfg.variant == KernelVariant.CONV2D_IM2COL:
                    algo = "im2col"
                else:
                    algo = None
        except Exception as e:
            algo = None
            if _WARN_ON_FALLBACK and not _ENV_FORCE_LEGACY:
                print(f"[conv2d] warning: optimized forward fallback to legacy path ({e})")
    else:
        algo = None
    dtype_c = _DTYPE_CNAME.get(x.dtype)
    if dtype_c is None:
        raise ValueError(f"unsupported dtype for conv2d: {x.dtype}")
    # fp16 fallback to fp32 if device lacks fp16
    if x.dtype in ("half", "float16"):
        if "cl_khr_fp16" not in x.queue.device.extensions:
            # upcast to fp32 for compute
            x = Tensor.from_host(x.queue, x.to_host().astype(np.float32), dtype="float32")
            w = Tensor.from_host(w.queue, w.to_host().astype(np.float32), dtype="float32")
            if bias is not None:
                bias = Tensor.from_host(bias.queue, bias.to_host().astype(np.float32), dtype="float32")
            dtype_c = "float"
    out_shape = conv2d_output_shape(x.shape, w.shape, stride=stride, pad=pad)
    OH, OW = out_shape[2], out_shape[3]
    ctx = x.context
    q = x.queue
    shape_info = (N, C, H, W, F, KH, KW, OH, OW)
    # Optional perf gate: compare cached/selected variant vs im2col baseline, cache faster one
    if _ENV_OPT_AUTOTUNE_SHAPE and _ENV_CONV_PERF_GATE and not _IN_OPT_PERF:
        if perf_key and perf_key not in _OPT_PERF_CACHE:
            def _bench_variant(variant, tile):
                if variant == "implicit_gemm":
                    t0 = time.perf_counter()
                    out_v = conv2d_implicit_gemm(x, w, bias=bias, stride=stride, pad=pad, out=None, pool=pool, fuse_relu=_ENV_CONV_FUSE_RELU)
                    out_v.queue.finish()
                    return time.perf_counter() - t0
                if variant == "tiled_local":
                    t0 = time.perf_counter()
                    out_v = conv2d_tiled_local(
                        x, w, bias=bias, stride=stride, pad=pad, tile_oh=tile[0] if tile else 4, tile_ow=tile[1] if tile else 4,
                        out=None, pool=pool, fuse_relu=_ENV_CONV_FUSE_RELU
                    )
                    out_v.queue.finish()
                    return time.perf_counter() - t0
                if variant == "winograd":
                    t0 = time.perf_counter()
                    out_v = conv2d_winograd_f2x2_3x3(x, w, bias=bias, stride=stride, pad=pad, out=None, pool=pool, fuse_relu=_ENV_CONV_FUSE_RELU)
                    out_v.queue.finish()
                    return time.perf_counter() - t0
                return 1e9

            # Bench im2col baseline without optimized path to avoid recursion
            try:
                _IN_OPT_PERF = True
                t0 = time.perf_counter()
                out_im2col = conv2d(x, w, bias=bias, stride=stride, pad=pad, algo="im2col", pool=pool)  # type: ignore
                out_im2col.queue.finish()
                t_im2col = time.perf_counter() - t0
            finally:
                _IN_OPT_PERF = False

            t_opt = 1e9
            if opt_variant:
                t_opt = _bench_variant(opt_variant, opt_tile)
            # If im2col baseline is faster, force im2col for this shape
            if t_im2col < t_opt:
                opt_variant = None
                algo = "im2col"
            _OPT_PERF_CACHE[perf_key] = ("im2col" if algo == "im2col" or opt_variant is None else opt_variant, opt_tile)

    if opt_variant == "implicit_gemm":
        out_res = conv2d_implicit_gemm(x, w, bias=bias, stride=stride, pad=pad, out=out, pool=pool, fuse_relu=_ENV_CONV_FUSE_RELU)
        if _ENV_CONV_FUSE_RELU:
            try:
                from netcl.ops.elementwise import relu as _relu

                out_res = _relu(out_res)
            except Exception:
                pass
        return out_res
    if opt_variant == "tiled_local":
        tile_oh, tile_ow = opt_tile if opt_tile is not None else _autotune_conv_tile(x, w, bias, stride, pad)
        out_res = conv2d_tiled_local(
            x, w, bias=bias, stride=stride, pad=pad, tile_oh=tile_oh, tile_ow=tile_ow, out=out, pool=pool, fuse_relu=_ENV_CONV_FUSE_RELU
        )
        if _ENV_CONV_FUSE_RELU:
            try:
                from netcl.ops.elementwise import relu as _relu

                out_res = _relu(out_res)
            except Exception:
                pass
        return out_res
    if opt_variant == "winograd":
        out_res = conv2d_winograd_f2x2_3x3(x, w, bias=bias, stride=stride, pad=pad, out=out, pool=pool, fuse_relu=_ENV_CONV_FUSE_RELU)
        if _ENV_CONV_FUSE_RELU:
            try:
                from netcl.ops.elementwise import relu as _relu

                out_res = _relu(out_res)
            except Exception:
                pass
        return out_res
    
    # Try optimized kernels first for large convolutions
    if _ENV_USE_OPTIMIZED and (algo is None or algo == "auto" or algo == "optimized"):
        output_elements = N * F * OH * OW
        if output_elements >= _ENV_OPTIMIZED_THRESHOLD:
            impl_gemm, tiled_local = _get_optimized_conv_kernels()
            # For 3x3 stride 1 convolutions, use implicit gemm (best for typical CNN workloads)
            if impl_gemm and KH == 3 and KW == 3 and stride == 1:
                try:
                    result = impl_gemm(
                        x, w, bias=bias, out=out, pool=pool, stride=stride, pad=pad, fuse_relu=_ENV_CONV_FUSE_RELU
                    )
                    if _ENV_CONV_FUSE_RELU:
                        try:
                            from netcl.ops.elementwise import relu as _relu

                            result = _relu(result)
                        except Exception:
                            pass
                    return result
                except Exception:
                    pass  # Fall back to standard kernels
            # For other convolutions, try tiled local memory kernel
            elif tiled_local and KH <= 7 and KW <= 7:
                try:
                    result = tiled_local(
                        x, w, bias=bias, out=out, pool=pool, stride=stride, pad=pad, fuse_relu=_ENV_CONV_FUSE_RELU
                    )
                    if _ENV_CONV_FUSE_RELU:
                        try:
                            from netcl.ops.elementwise import relu as _relu

                            result = _relu(result)
                        except Exception:
                            pass
                    return result
                except Exception:
                    pass  # Fall back to standard kernels
    
    strategy = "optimized"
    if device_profile and kernel_strategy:
        dev = getattr(q, "device", None)
        if dev is not None:
            skey = getattr(dev, "hash", getattr(dev, "name", "unknown"))
            if skey in _STRATEGY_CACHE:
                strategy = _STRATEGY_CACHE[skey]
            else:
                prof = device_profile(dev)
                strategy = kernel_strategy(prof)
                _STRATEGY_CACHE[skey] = strategy
    if algo is None or algo == "":
        algo = "auto"
    if (_ENV_AUTOTUNE or _ENV_FORCE_AUTOTUNE) and not _IN_TUNING and (algo == "auto"):
        algo_name = _autotune_algo(x, w, bias, stride, pad, candidates=("naive", "tile", "im2col"))
    else:
        device_name = getattr(q.device, "name", "unknown")
        algo_name = _resolve_algo(algo, use_im2col, shape_info, stride=stride, pad=pad, device_name=device_name, strategy=strategy)
    if _ENV_CONV_BENCH and not _IN_TUNING and not _ENV_FORCE_AUTOTUNE and cl is not None:
        algo_name = _bench_algos(x, w, bias, stride, pad, candidates=("im2col", "tile", "naive"))
    if _ENV_AUTOTUNE or _ENV_FORCE_AUTOTUNE:
        key = (x.shape, w.shape, stride, pad, x.dtype, w.dtype)
        _TUNE_CACHE[key] = algo_name
    # log selection when env requests
    if _ENV_FORCE_AUTOTUNE:
        dn = getattr(q.device, "name", "unknown")
        print(f"[conv2d] strategy={strategy} algo={algo_name} device={dn}")
    if algo_name == "im2col":
        col, _ = im2col(x, KH, KW, stride=stride, pad=pad, pool=pool)
        col_flat = treshape(col, (N * OH * OW, C * KH * KW))
        w_flat = treshape(w, (F, C * KH * KW))
        w_flat_T = transpose2d(w_flat)
        if _ENV_CONV_IM2COL_OPT_MATMUL:
            try:
                from netcl.ops.matmul_optimized import matmul_optimized as mm_opt

                out_col = mm_opt(col_flat, w_flat_T)
            except Exception:
                out_col = mm(col_flat, w_flat_T)
        else:
            out_col = mm(col_flat, w_flat_T)
        if out is None:
            out = Tensor.from_shape(q, out_shape, dtype=x.dtype, pool=pool)
        reorder = _build_out_reorder_kernel(ctx, dtype_c, fuse_relu=_ENV_CONV_FUSE_RELU)
        total = N * F * OH * OW
        gsize = (int(np.ceil(total / 256.0)) * 256,)
        evt = reorder(
            q,
            gsize,
            (256,),
            out_col.buffer,
            bias.buffer if bias is not None else None,
            out.buffer,
            np.int32(N),
            np.int32(F),
            np.int32(OH),
            np.int32(OW),
        )
        if _PROFILE_CONV and t0_prof is not None:
            dt = time.perf_counter() - t0_prof
            _CONV_STATS["fwd_calls"] += 1
            _CONV_STATS["fwd_time"] += dt
            if _PROFILE_CONV_EVENTS and evt is not None and hasattr(evt, "profile"):
                try:
                    evt.wait()
                    dt_evt = (evt.profile.end - evt.profile.start) * 1e-9
                    _CONV_EVENT_STATS["fwd_events"] += 1
                    _CONV_EVENT_STATS["fwd_event_time"] += dt_evt
                except Exception:
                    pass
        if _ENV_CONV_FUSE_RELU:
            try:
                from netcl.ops.elementwise import relu as _relu

                out = _relu(out)
            except Exception:
                pass
        return out
    elif algo_name == "tile":
        kernel = _build_forward_tiled_kernel(ctx, dtype_c)
        if out is None:
            out = Tensor.from_shape(q, out_shape, dtype=x.dtype, pool=pool)
        gsize = (
            int(np.ceil(OW / 8.0)) * 8,
            int(np.ceil(OH / 8.0)) * 8,
            N * F,
        )
        lsize = (8, 8, 1)
        evt = kernel(
            q,
            gsize,
            lsize,
            x.buffer,
            w.buffer,
            bias.buffer if bias is not None else None,
            out.buffer,
            np.int32(N),
            np.int32(C),
            np.int32(H),
            np.int32(W),
            np.int32(KH),
            np.int32(KW),
            np.int32(OH),
            np.int32(OW),
            np.int32(F),
            np.int32(stride),
            np.int32(pad),
        )
        if _PROFILE_CONV and t0_prof is not None:
            dt = time.perf_counter() - t0_prof
            _CONV_STATS["fwd_calls"] += 1
            _CONV_STATS["fwd_time"] += dt
            if _PROFILE_CONV_EVENTS and evt is not None and hasattr(evt, "profile"):
                try:
                    evt.wait()
                    dt_evt = (evt.profile.end - evt.profile.start) * 1e-9
                    _CONV_EVENT_STATS["fwd_events"] += 1
                    _CONV_EVENT_STATS["fwd_event_time"] += dt_evt
                except Exception:
                    pass
        if _ENV_CONV_FUSE_RELU:
            try:
                from netcl.ops.elementwise import relu as _relu

                out = _relu(out)
            except Exception:
                pass
        return out
    elif algo_name == "winograd":
        # Fallback until stable Winograd is in place
        return conv2d(x, w, bias=bias, out=out, pool=pool, stride=stride, pad=pad, algo="naive")
    elif algo_name == "fft":
        if np is None:
            raise ImportError("numpy required for fft path")
        if stride != 1:
            return conv2d(x, w, bias=bias, out=out, pool=pool, stride=stride, pad=pad, algo="naive")
        xh = x.to_host()
        wh = w.to_host()
        pad_effective = pad
        x_pad = np.pad(xh, ((0, 0), (0, 0), (pad_effective, pad_effective), (pad_effective, pad_effective)), mode="constant")
        H_pad, W_pad = x_pad.shape[2], x_pad.shape[3]
        fft_shape = (H_pad, W_pad)
        fft_x = np.fft.rfftn(x_pad, s=fft_shape, axes=(2, 3))
        # pad weights to fft_shape
        w_pad = np.zeros((F, C, H_pad, W_pad), dtype=np.float32)
        w_pad[:, :, :KH, :KW] = wh
        fft_w = np.fft.rfftn(w_pad, s=fft_shape, axes=(2, 3))
        out_freq = (fft_x[:, None, :, :, :] * np.conj(fft_w[None, :, :, :, :])).sum(axis=2)
        out_spatial = np.fft.irfftn(out_freq, s=fft_shape, axes=(2, 3)).real
        out_host = out_spatial[:, :, :OH, :OW].astype(np.float32)
        if bias is not None:
            out_host += bias.to_host().reshape(1, F, 1, 1)
        if out is None:
            out = Tensor.from_host(q, out_host)
        else:
            cl.enqueue_copy(q, out.buffer, out_host).wait()
        return out
    else:
        kernel = _build_forward_kernel(ctx, dtype_c)
        if out is None:
            out = Tensor.from_shape(q, out_shape, dtype=x.dtype, pool=pool)
        total = int(np.prod(out_shape))
        gsize = (int(np.ceil(total / 256.0)) * 256,)
        evt = kernel(
            q,
            gsize,
            (256,),
            x.buffer,
            w.buffer,
            bias.buffer if bias is not None else None,
            out.buffer,
            np.int32(N),
            np.int32(C),
            np.int32(H),
            np.int32(W),
            np.int32(KH),
            np.int32(KW),
            np.int32(OH),
            np.int32(OW),
            np.int32(F),
            np.int32(stride),
            np.int32(pad),
        )
        if _PROFILE_CONV and t0_prof is not None:
            dt = time.perf_counter() - t0_prof
            _CONV_STATS["fwd_calls"] += 1
            _CONV_STATS["fwd_time"] += dt
            if _PROFILE_CONV_EVENTS and evt is not None and hasattr(evt, "profile"):
                try:
                    evt.wait()
                    dt_evt = (evt.profile.end - evt.profile.start) * 1e-9
                    _CONV_EVENT_STATS["fwd_events"] += 1
                    _CONV_EVENT_STATS["fwd_event_time"] += dt_evt
                except Exception:
                    pass
        if _ENV_CONV_FUSE_RELU:
            try:
                from netcl.ops.elementwise import relu as _relu

                out = _relu(out)
            except Exception:
                pass
        return out


def conv2d_backward(
    x: Tensor,
    w: Tensor,
    grad_out: Tensor,
    bias: Optional[Tensor] = None,
    pool: Optional[BufferPool] = None,
    stride: int = 1,
    pad: int = 0,
    use_im2col: bool = False,
    algo: Optional[str] = None,
) -> tuple[Tensor, Tensor, Optional[Tensor]]:
    backend = ensure_same_backend((x, w, grad_out) + ((bias,) if bias is not None else ()), op="conv2d_backward")
    if backend == "cpu":
        return conv2d_backward_cpu(x, w, grad_out, stride=stride, pad=pad, bias=bias)
    if cl is None or np is None:
        raise ImportError("pyopencl and numpy required for conv2d backward")
    t0_prof = time.perf_counter() if _PROFILE_CONV else None
    use_opt = _ENV_USE_OPTIMIZED and not _ENV_FORCE_LEGACY and not _ENV_FORCE_AUTOTUNE
    if use_opt:
        try:
            return conv2d_backward_optimized(x, w, grad_out, bias, stride=stride, pad=pad, pool=pool)
        except Exception:
            if _WARN_ON_FALLBACK and not _ENV_FORCE_LEGACY:
                print("[conv2d_backward] warning: optimized backward fallback to legacy path")
            pass
    dtype_c = _DTYPE_CNAME.get(x.dtype)
    if dtype_c is None:
        raise ValueError("unsupported dtype")
    N, C, H, W = x.shape
    F, _, KH, KW = w.shape
    _, _, OH, OW = grad_out.shape
    ctx = x.context
    q = x.queue
    shape_info = (N, C, H, W, F, KH, KW, OH, OW)
    device_name = getattr(q.device, "name", "unknown")
    strategy = "optimized"
    if device_profile and kernel_strategy:
        dev = getattr(q, "device", None)
        if dev is not None:
            skey = getattr(dev, "hash", getattr(dev, "name", "unknown"))
            if skey in _STRATEGY_CACHE:
                strategy = _STRATEGY_CACHE[skey]
            else:
                prof = device_profile(dev)
                strategy = kernel_strategy(prof)
                _STRATEGY_CACHE[skey] = strategy
    if _ENV_AUTOTUNE and not _IN_TUNING and (algo is None or algo == "" or algo == "auto"):
        key = (x.shape, w.shape, stride, pad, x.dtype, w.dtype)
        algo_name = _TUNE_CACHE.get(
            key, _resolve_algo(algo, use_im2col, shape_info, stride=stride, pad=pad, device_name=device_name, strategy=strategy)
        )
    else:
        algo_name = _resolve_algo(algo, use_im2col, shape_info, stride=stride, pad=pad, device_name=device_name, strategy=strategy)
    if algo_name == "im2col":
        col, _ = im2col(x, KH, KW, stride=stride, pad=pad, pool=pool)
        col_flat = treshape(col, (N * OH * OW, C * KH * KW))
        w_flat = treshape(w, (F, C * KH * KW))
        # grad_out to (N*OH*OW, F) on device
        go_flat = Tensor.from_shape(q, (N * OH * OW, F), dtype=grad_out.dtype, pool=pool)
        nchw2col = _build_nchw_to_col_kernel(ctx, dtype_c)
        total_go = N * F * OH * OW
        gsize_go = (int(np.ceil(total_go / 256.0)) * 256,)
        evt_go = nchw2col(
            q,
            gsize_go,
            (256,),
            grad_out.buffer,
            go_flat.buffer,
            np.int32(N),
            np.int32(F),
            np.int32(OH),
            np.int32(OW),
        )
        # grad_w = col^T @ grad_out => shape (C*KH*KW, F)
        col_T = transpose2d(col_flat)
        grad_w_flat = mm(col_T, go_flat)
        grad_w_t = transpose2d(grad_w_flat)
        grad_w = treshape(grad_w_t, w.shape)
        # grad_in: grad_out @ w_flat -> col2im
        go_w = mm(go_flat, w_flat)  # (N*OH*OW, C*KH*KW)
        grad_col = treshape(go_w, (N, OH, OW, C * KH * KW))
        grad_in = col2im(grad_col, (N, C, H, W), KH, KW, stride=stride, pad=pad, pool=pool)
    elif algo_name == "tile":
        grad_in = Tensor.from_shape(q, x.shape, dtype=x.dtype, pool=pool)
        kernel_in = _build_grad_input_tiled_kernel(ctx, dtype_c)
        gsize_in = (
            int(np.ceil(W / 8.0)) * 8,
            int(np.ceil(H / 8.0)) * 8,
            N * C,
        )
        lsize_in = (8, 8, 1)
        evt_in = kernel_in(
            q,
            gsize_in,
            lsize_in,
            grad_out.buffer,
            w.buffer,
            grad_in.buffer,
            np.int32(N),
            np.int32(C),
            np.int32(H),
            np.int32(W),
            np.int32(KH),
            np.int32(KW),
            np.int32(OH),
            np.int32(OW),
            np.int32(F),
            np.int32(stride),
            np.int32(pad),
        )
        grad_w = Tensor.from_shape(q, w.shape, dtype=w.dtype, pool=pool)
        kernel_w = _build_grad_weight_tiled_kernel(ctx, dtype_c)
        gsize_w = (
            int(np.ceil(KW / 4.0)) * 4,
            int(np.ceil(KH / 4.0)) * 4,
            F * C,
        )
        lsize_w = (4, 4, 1)
        evt_w = kernel_w(
            q,
            gsize_w,
            lsize_w,
            x.buffer,
            grad_out.buffer,
            grad_w.buffer,
            np.int32(N),
            np.int32(C),
            np.int32(H),
            np.int32(W),
            np.int32(KH),
            np.int32(KW),
            np.int32(OH),
            np.int32(OW),
            np.int32(F),
            np.int32(stride),
            np.int32(pad),
        )
    else:
        # grad_input
        grad_in = Tensor.from_shape(q, x.shape, dtype=x.dtype, pool=pool)
        kernel_in = _build_grad_input_kernel(ctx, dtype_c)
        total_in = N * C * H * W
        gsize_in = (int(np.ceil(total_in / 256.0)) * 256,)
        kernel_in(
            q,
            gsize_in,
            (256,),
            grad_out.buffer,
            w.buffer,
            grad_in.buffer,
            np.int32(N),
            np.int32(C),
            np.int32(H),
            np.int32(W),
            np.int32(KH),
            np.int32(KW),
            np.int32(OH),
            np.int32(OW),
            np.int32(F),
            np.int32(stride),
            np.int32(pad),
        )
        # grad_weight
        grad_w = Tensor.from_shape(q, w.shape, dtype=w.dtype, pool=pool)
        kernel_w = _build_grad_weight_kernel(ctx, dtype_c)
        total_w = F * C * KH * KW
        gsize_w = (int(np.ceil(total_w / 256.0)) * 256,)
        kernel_w(
            q,
            gsize_w,
            (256,),
            x.buffer,
            grad_out.buffer,
            grad_w.buffer,
            np.int32(N),
            np.int32(C),
            np.int32(H),
            np.int32(W),
            np.int32(KH),
            np.int32(KW),
            np.int32(OH),
            np.int32(OW),
            np.int32(F),
            np.int32(stride),
            np.int32(pad),
        )
    grad_b_out = None
    if bias is not None:
        grad_b_out = Tensor.from_shape(q, bias.shape, dtype=bias.dtype, pool=pool)
        kernel_b = _build_grad_bias_kernel(ctx, dtype_c)
        gsize_b = (int(np.ceil(F / 256.0)) * 256,)
        evt_b = kernel_b(q, gsize_b, (256,), grad_out.buffer, grad_b_out.buffer, np.int32(N), np.int32(F), np.int32(OH), np.int32(OW))
    if _PROFILE_CONV and t0_prof is not None:
        dt = time.perf_counter() - t0_prof
        _CONV_STATS["bwd_calls"] += 1
        _CONV_STATS["bwd_time"] += dt
        if _PROFILE_CONV_EVENTS:
            for ev in ("evt_go", "evt_in", "evt_w", "evt_b"):
                evt_obj = locals().get(ev, None)
                if evt_obj is not None and hasattr(evt_obj, "profile"):
                    try:
                        evt_obj.wait()
                        dt_evt = (evt_obj.profile.end - evt_obj.profile.start) * 1e-9
                        _CONV_EVENT_STATS["bwd_events"] += 1
                        _CONV_EVENT_STATS["bwd_event_time"] += dt_evt
                    except Exception:
                        pass
    return grad_in, grad_w, grad_b_out
