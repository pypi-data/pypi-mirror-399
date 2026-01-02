from __future__ import annotations

import numpy as np
import pyopencl as cl

from netcl.core.tensor import Tensor

_DTYPE_CNAME = {"float": "float", "float32": "float"}
_PAD_KERNEL_CACHE = {}


def pad2d(x: Tensor, pad: int = 1, mode: str = "zero") -> Tensor:
    """
    Simple 2D padding (NCHW). mode: 'zero' or 'reflect' (basic).
    """
    if pad <= 0:
        return x
    dtype_c = _DTYPE_CNAME.get(x.dtype)
    if dtype_c is None:
        raise ValueError(f"unsupported dtype {x.dtype}")
    ctx = x.context
    N, C, H, W = x.shape
    out_h = H + 2 * pad
    out_w = W + 2 * pad
    ksrc = f"""
    __kernel void pad2d(__global const {dtype_c}* x, __global {dtype_c}* out,
                        const int N, const int C, const int H, const int W,
                        const int pad, const int OH, const int OW) {{
        int gid = get_global_id(0);
        int total = N * C * OH * OW;
        if (gid >= total) return;
        int ow = gid % OW;
        int oh = (gid / OW) % OH;
        int c = (gid / (OH * OW)) % C;
        int n = gid / (C * OH * OW);
        int ih = oh - pad;
        int iw = ow - pad;
        {dtype_c} val = 0;
        if (ih >=0 && ih < H && iw >=0 && iw < W) {{
            int idx = ((n*C + c)*H + ih)*W + iw;
            val = x[idx];
        }} else if ({1 if mode=='reflect' else 0}) {{
            // basic reflect: clamp to border
            int rih = ih < 0 ? -ih - 1 : (ih >= H ? 2*H - ih - 1 : ih);
            int riw = iw < 0 ? -iw - 1 : (iw >= W ? 2*W - iw - 1 : iw);
            int idx = ((n*C + c)*H + rih)*W + riw;
            val = x[idx];
        }}
        out[gid] = val;
    }}
    """
    prg = cl.Program(ctx, ksrc).build()
    kernel = prg.pad2d
    out = Tensor.from_shape(x.queue, (N, C, out_h, out_w), dtype=x.dtype)
    total = N * C * out_h * out_w
    gsize = (int(np.ceil(total / 256.0)) * 256,)
    kernel(x.queue, gsize, (256,), x.buffer, out.buffer, np.int32(N), np.int32(C), np.int32(H), np.int32(W), np.int32(pad), np.int32(out_h), np.int32(out_w))
    return out


def pad2d_backward(grad_out: Tensor, pad: int = 1, mode: str = "zero", in_shape: tuple[int, ...] | None = None) -> Tensor:
    """
    Backward for pad2d. For zero padding, this is a crop. For reflect, gradients are accumulated.
    """
    if pad <= 0:
        return grad_out
    if in_shape is None:
        raise ValueError("in_shape is required for pad2d_backward")
    if len(in_shape) != 4:
        raise ValueError("pad2d_backward expects NCHW input shape")
    N, C, H, W = in_shape
    OH = H + 2 * pad
    OW = W + 2 * pad
    if grad_out.shape != (N, C, OH, OW):
        raise ValueError(f"grad_out must be {(N, C, OH, OW)}, got {grad_out.shape}")
    backend = getattr(grad_out, "backend", "cl")
    if backend == "cpu":
        go = grad_out.array
        if go is None:
            raise ValueError("CPU tensors require array storage")
        if mode == "zero":
            cropped = go[:, :, pad : pad + H, pad : pad + W].copy()
            return Tensor.from_host(grad_out.queue, cropped.astype(go.dtype), dtype=grad_out.dtype, backend="cpu")
        if mode != "reflect":
            raise ValueError(f"unsupported pad2d mode: {mode}")
        grad_in = np.zeros((N, C, H, W), dtype=go.dtype)
        for n in range(N):
            for c in range(C):
                for oh in range(OH):
                    ih = oh - pad
                    rih = ih if 0 <= ih < H else (-ih - 1 if ih < 0 else 2 * H - ih - 1)
                    for ow in range(OW):
                        iw = ow - pad
                        riw = iw if 0 <= iw < W else (-iw - 1 if iw < 0 else 2 * W - iw - 1)
                        grad_in[n, c, rih, riw] += go[n, c, oh, ow]
        return Tensor.from_host(grad_out.queue, grad_in.astype(go.dtype), dtype=grad_out.dtype, backend="cpu")

    if cl is None:
        raise ImportError("pyopencl required for pad2d_backward")
    dtype_c = _DTYPE_CNAME.get(grad_out.dtype)
    if dtype_c is None:
        raise ValueError(f"unsupported dtype {grad_out.dtype}")
    ctx = grad_out.context
    if mode == "zero":
        cache_key = (ctx.int_ptr, grad_out.dtype, "pad2d_bwd_zero")
        if cache_key in _PAD_KERNEL_CACHE:
            kernel = _PAD_KERNEL_CACHE[cache_key]
        else:
            ksrc = f"""
            __kernel void pad2d_bwd_zero(__global const {dtype_c}* go, __global {dtype_c}* gx,
                                         const int N, const int C, const int H, const int W,
                                         const int pad, const int OH, const int OW) {{
                int gid = get_global_id(0);
                int total = N * C * H * W;
                if (gid >= total) return;
                int w = gid % W;
                int h = (gid / W) % H;
                int c = (gid / (H*W)) % C;
                int n = gid / (C*H*W);
                int oh = h + pad;
                int ow = w + pad;
                int oidx = ((n*C + c)*OH + oh)*OW + ow;
                gx[gid] = go[oidx];
            }}
            """
            program = cl.Program(ctx, ksrc).build()
            kernel = program.pad2d_bwd_zero
            _PAD_KERNEL_CACHE[cache_key] = kernel
        grad_in = Tensor.from_shape(grad_out.queue, (N, C, H, W), dtype=grad_out.dtype)
        total = N * C * H * W
        gsize = (int(np.ceil(total / 256.0)) * 256,)
        kernel(grad_out.queue, gsize, (256,), grad_out.buffer, grad_in.buffer, np.int32(N), np.int32(C), np.int32(H), np.int32(W), np.int32(pad), np.int32(OH), np.int32(OW))
        return grad_in

    if mode != "reflect":
        raise ValueError(f"unsupported pad2d mode: {mode}")
    cache_key = (ctx.int_ptr, grad_out.dtype, "pad2d_bwd_reflect")
    if cache_key in _PAD_KERNEL_CACHE:
        kernel = _PAD_KERNEL_CACHE[cache_key]
    else:
        ksrc = f"""
        __kernel void pad2d_bwd_reflect(__global const {dtype_c}* go, __global {dtype_c}* gx,
                                        const int N, const int C, const int H, const int W,
                                        const int pad, const int OH, const int OW) {{
            int gid = get_global_id(0);
            int total = N * C * H * W;
            if (gid >= total) return;
            int w = gid % W;
            int h = (gid / W) % H;
            int c = (gid / (H*W)) % C;
            int n = gid / (C*H*W);
            float acc = 0.0f;
            for (int oh = 0; oh < OH; ++oh) {{
                int ih = oh - pad;
                int rih = ih < 0 ? -ih - 1 : (ih >= H ? 2*H - ih - 1 : ih);
                if (rih != h) continue;
                for (int ow = 0; ow < OW; ++ow) {{
                    int iw = ow - pad;
                    int riw = iw < 0 ? -iw - 1 : (iw >= W ? 2*W - iw - 1 : iw);
                    if (riw != w) continue;
                    int oidx = ((n*C + c)*OH + oh)*OW + ow;
                    acc += go[oidx];
                }}
            }}
            gx[gid] = acc;
        }}
        """
        program = cl.Program(ctx, ksrc).build()
        kernel = program.pad2d_bwd_reflect
        _PAD_KERNEL_CACHE[cache_key] = kernel
    grad_in = Tensor.from_shape(grad_out.queue, (N, C, H, W), dtype=grad_out.dtype)
    total = N * C * H * W
    gsize = (int(np.ceil(total / 256.0)) * 256,)
    kernel(grad_out.queue, gsize, (256,), grad_out.buffer, grad_in.buffer, np.int32(N), np.int32(C), np.int32(H), np.int32(W), np.int32(pad), np.int32(OH), np.int32(OW))
    return grad_in
