"""
Tiled matrix multiplication built from basic OpenCL primitives (no special instructions).
With automatic selection of optimized kernels for large matrices.
"""

from __future__ import annotations

import json
import os
import time
from typing import Optional, Tuple

from netcl.core.kernels import KernelSpec
from netcl.core.tensor import Tensor
from netcl.core.backend import ensure_same_backend
from netcl.core.memory import BufferPool

try:
    import numpy as np  # type: ignore
except ImportError:  # pragma: no cover
    np = None

try:
    import pyopencl as cl  # type: ignore
except ImportError:  # pragma: no cover
    cl = None

# Environment control for optimized kernels
_USE_OPTIMIZED = os.environ.get("NETCL_MATMUL_OPTIMIZED", "0") not in ("0", "false", "False")
_OPTIMIZED_THRESHOLD = int(os.environ.get("NETCL_MATMUL_OPTIMIZED_THRESHOLD", "4096"))  # M*N threshold
_PROFILE_MATMUL = os.environ.get("NETCL_PROFILE_STATS", "0") not in ("0", "", "false", "False")
_AUTOTUNE_TILES = os.environ.get("NETCL_MATMUL_AUTOTUNE", "0") not in ("0", "", "false", "False")
_PROFILE_EVENTS = os.environ.get("NETCL_PROFILE_EVENTS", "0") not in ("0", "", "false", "False")
_AUTOTUNE_PER_SHAPE = os.environ.get("NETCL_MATMUL_AUTOTUNE_SHAPE", "0") not in ("0", "", "false", "False")
_MATMUL_STATS: dict = {"calls": 0, "time": 0.0, "flops": 0.0}
_TILE_CACHE: dict = {}
_TILE_CACHE_PATH = os.path.join(os.path.expanduser("~"), ".cache", "netcl", "matmul_tiles.json")
_TUNING_CACHE_PATH = os.path.join(os.path.expanduser("~"), ".cache", "netcl", "tuning.json")

if _PROFILE_MATMUL:
    import atexit
    def _print_matmul_stats():
        if _MATMUL_STATS["calls"] == 0:
            return
        avg = _MATMUL_STATS["time"] / _MATMUL_STATS["calls"]
        gflops = (_MATMUL_STATS["flops"] / (_MATMUL_STATS["time"] + 1e-12)) / 1e9
        print(f"[matmul stats] calls={_MATMUL_STATS['calls']} total_ms={_MATMUL_STATS['time']*1000:.2f} "
              f"avg_ms={avg*1000:.3f} effective_GFLOP/s={gflops:.1f}")
    atexit.register(_print_matmul_stats)

# Lazy import for optimized kernel to avoid circular imports
_matmul_optimized = None

def _get_matmul_optimized():
    """Lazy import of optimized matmul kernel."""
    global _matmul_optimized
    if _matmul_optimized is None:
        try:
            from netcl.ops.matmul_optimized import matmul_optimized
            _matmul_optimized = matmul_optimized
        except ImportError:
            _matmul_optimized = False  # Mark as unavailable
    return _matmul_optimized if _matmul_optimized else None


_DTYPE_INFO = {
    "float": ("float", 4),
    "float32": ("float", 4),
    "half": ("half", 2),
    "float16": ("half", 2),
    "double": ("double", 8),
    "float64": ("double", 8),
}


def _dtype_info(dtype: str) -> Tuple[str, int]:
    if dtype not in _DTYPE_INFO:
        raise ValueError(f"unsupported dtype {dtype}")
    return _DTYPE_INFO[dtype]


def _device_hash(device: Optional["cl.Device"]) -> str:
    if device is None:
        return "unknown"
    name = getattr(device, "name", "unknown")
    vendor = getattr(device, "vendor", "unknown")
    lmem = getattr(device, "local_mem_size", 0)
    wg = getattr(device, "max_work_group_size", 0)
    return f"{vendor}|{name}|{lmem}|{wg}"


def _load_tile_cache() -> None:
    if _TILE_CACHE:
        return
    try:
        if os.path.exists(_TILE_CACHE_PATH):
            with open(_TILE_CACHE_PATH, "r", encoding="utf-8") as f:
                _TILE_CACHE.update(json.load(f))
    except Exception:
        pass


def _save_tile_cache() -> None:
    try:
        os.makedirs(os.path.dirname(_TILE_CACHE_PATH), exist_ok=True)
        with open(_TILE_CACHE_PATH, "w", encoding="utf-8") as f:
            json.dump(_TILE_CACHE, f)
    except Exception:
        pass


def _load_tuning_cache() -> dict:
    try:
        if os.path.exists(_TUNING_CACHE_PATH):
            with open(_TUNING_CACHE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return {}


def _save_tuning_cache(data: dict) -> None:
    try:
        os.makedirs(os.path.dirname(_TUNING_CACHE_PATH), exist_ok=True)
        with open(_TUNING_CACHE_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f)
    except Exception:
        pass


def _preferred_tile(device: Optional["cl.Device"]) -> int:
    """
    Choose a starting tile size based on the device family.
    Pascal (Quadro P6000) benefits from larger tiles (32) than the old default (16).
    """
    if device is None:
        return 16
    name = getattr(device, "name", "").lower()
    vendor = getattr(device, "vendor", "").lower()
    if "nvidia" in vendor:
        # Pascal/Turing like 32x32 tiles for fp32 when local memory allows it.
        return 32
    return 16


def choose_tile_size(device: Optional["cl.Device"], requested: Optional[int] = None, dtype_bytes: int = 4) -> int:
    """
    Choose a tile size that does not exceed the device's max work-group size.
    Prefers power-of-two sizes up to requested.
    """
    tile = requested if requested is not None else _preferred_tile(device)
    if device is None:
        return tile
    limit = device.max_work_group_size
    dim_limit = min(device.max_work_item_sizes[0], device.max_work_item_sizes[1])
    local_mem_limit = getattr(device, "local_mem_size", 0)
    while (
        (tile * tile > limit)
        or (tile > dim_limit)
        or (local_mem_limit and (tile * tile * dtype_bytes * 2) > local_mem_limit)
    ) and tile > 1:
        tile //= 2
    tile = max(1, tile)
    if tile < 4:
        candidate = 4
        if (
            candidate * candidate <= limit
            and candidate <= dim_limit
            and (local_mem_limit == 0 or (candidate * candidate * dtype_bytes * 2) <= local_mem_limit)
        ):
            tile = candidate
    return tile


def _candidate_tiles(device: Optional["cl.Device"], dtype_bytes: int) -> Tuple[int, ...]:
    # Cap tile size to avoid oversized workgroups on Pascal-class GPUs.
    cap = 64
    vendor = getattr(device, "vendor", "").lower() if device is not None else ""
    if "nvidia" in vendor:
        cap = 32
    base = [_preferred_tile(device), 16, 32, 64]
    uniq = []
    for t in base:
        if t > cap:
            continue
        t_valid = choose_tile_size(device, requested=t, dtype_bytes=dtype_bytes)
        if t_valid not in uniq:
            uniq.append(t_valid)
    return tuple(uniq)


def _benchmark_tile(ctx: "cl.Context", device: Optional["cl.Device"], tile: int, dtype: str = "float") -> float:
    """Return median seconds for a fixed small matmul at given tile."""
    tile = choose_tile_size(device, requested=tile, dtype_bytes=4)
    # Use a moderate size to be representative but quick.
    M = N = K = 512
    spec, kernel = build_matmul_kernel(context=ctx, tile=tile, dtype=dtype)
    # Allocate buffers
    mf = cl.mem_flags
    a_buf = cl.Buffer(ctx, mf.READ_ONLY, size=M * K * 4)
    b_buf = cl.Buffer(ctx, mf.READ_ONLY, size=K * N * 4)
    c_buf = cl.Buffer(ctx, mf.WRITE_ONLY, size=M * N * 4)
    queue = cl.CommandQueue(ctx)
    # Warmup
    for _ in range(2):
        kernel(queue, (((M + tile - 1) // tile) * tile, ((N + tile - 1) // tile) * tile), (tile, tile), a_buf, b_buf, c_buf, np.int32(M), np.int32(N), np.int32(K))
        queue.finish()
    times = []
    for _ in range(4):
        t0 = time.perf_counter()
        kernel(queue, (((M + tile - 1) // tile) * tile, ((N + tile - 1) // tile) * tile), (tile, tile), a_buf, b_buf, c_buf, np.int32(M), np.int32(N), np.int32(K))
        queue.finish()
        times.append(time.perf_counter() - t0)
    return float(np.median(times)) if np is not None else sum(times) / len(times)


def _autotune_tile_shape(ctx: "cl.Context", device: Optional["cl.Device"], dtype_bytes: int, dtype: str, M: int, K: int, N: int) -> int:
    """
    Benchmark candidate tiles for a specific shape and return the fastest.
    Cached persistently per device+shape.
    """
    if not _AUTOTUNE_PER_SHAPE or cl is None or np is None:
        return choose_tile_size(device, None, dtype_bytes)
    tuning = _load_tuning_cache()
    dev_key = _device_hash(device)
    shape_key = f"{dtype_bytes}:{M}:{K}:{N}"
    cache_key = f"{dev_key}|{shape_key}"
    cached = tuning.get("matmul_shape", {}).get(cache_key)
    if cached:
        return choose_tile_size(device, requested=cached, dtype_bytes=dtype_bytes)
    best_tile = choose_tile_size(device, None, dtype_bytes)
    best_t = 1e9
    for t in _candidate_tiles(device, dtype_bytes):
        t_valid = choose_tile_size(device, requested=t, dtype_bytes=dtype_bytes)
        t0 = time.perf_counter()
        spec, kernel = build_matmul_kernel(context=ctx, tile=t_valid, dtype=dtype)
        if kernel is None:
            continue
        mf = cl.mem_flags
        a_buf = cl.Buffer(ctx, mf.READ_ONLY, size=M * K * dtype_bytes)
        b_buf = cl.Buffer(ctx, mf.READ_ONLY, size=K * N * dtype_bytes)
        c_buf = cl.Buffer(ctx, mf.WRITE_ONLY, size=M * N * dtype_bytes)
        q = cl.CommandQueue(ctx, properties=cl.command_queue_properties.PROFILING_ENABLE)
        # warmup
        kernel(q, (((M + t_valid - 1) // t_valid) * t_valid, ((N + t_valid - 1) // t_valid) * t_valid), (t_valid, t_valid), a_buf, b_buf, c_buf, np.int32(M), np.int32(N), np.int32(K))
        q.finish()
        times = []
        for _ in range(2):
            evt = kernel(q, (((M + t_valid - 1) // t_valid) * t_valid, ((N + t_valid - 1) // t_valid) * t_valid), (t_valid, t_valid), a_buf, b_buf, c_buf, np.int32(M), np.int32(N), np.int32(K))
            evt.wait()
            try:
                dt = (evt.profile.end - evt.profile.start) * 1e-9
            except Exception:
                dt = time.perf_counter() - t0
            times.append(dt)
        if times:
            dt_med = float(np.median(times))
            if dt_med < best_t:
                best_t = dt_med
                best_tile = t_valid
    tuning.setdefault("matmul_shape", {})[cache_key] = int(best_tile)
    _save_tuning_cache(tuning)
    return best_tile


def _autotune_tile(ctx: "cl.Context", device: Optional["cl.Device"], dtype_bytes: int, dtype: str) -> int:
    """Benchmark a few candidate tiles and cache the fastest per device."""
    if not _AUTOTUNE_TILES or cl is None or np is None:
        return choose_tile_size(device, None, dtype_bytes)
    _load_tile_cache()
    key = f"{_device_hash(device)}|{dtype_bytes}"
    if key in _TILE_CACHE:
        cached = _TILE_CACHE[key]
        return choose_tile_size(device, cached, dtype_bytes)
    best_tile = None
    best_t = 1e9
    for tile in _candidate_tiles(device, dtype_bytes):
        t = _benchmark_tile(ctx, device, tile, dtype=_dtype_info(dtype)[0])
        if t < best_t:
            best_t = t
            best_tile = tile
    if best_tile is None:
        best_tile = choose_tile_size(device, None, dtype_bytes)
    best_tile = choose_tile_size(device, requested=best_tile, dtype_bytes=dtype_bytes)
    _TILE_CACHE[key] = int(best_tile)
    _save_tile_cache()
    return best_tile


def matmul_kernel_spec(tile: int = 16, dtype: str = "float") -> KernelSpec:
    preamble = ""
    if dtype == "half":
        preamble = "#pragma OPENCL EXTENSION cl_khr_fp16 : enable\n"
    body = f"""
    const int row = get_global_id(0);
    const int col = get_global_id(1);
    const int local_row = get_local_id(0);
    const int local_col = get_local_id(1);
    __local {dtype} As[{tile}][{tile}];
    __local {dtype} Bs[{tile}][{tile}];
    {dtype} acc = 0;
    const int num_tiles = (K + {tile} - 1) / {tile};
    for (int t = 0; t < num_tiles; ++t) {{
        int k_base = t * {tile};
        int a_col = k_base + local_col;
        int b_row = k_base + local_row;
        {dtype} a_val = 0;
        {dtype} b_val = 0;
        if (row < M && a_col < K) {{
            a_val = A[row * K + a_col];
        }}
        if (b_row < K && col < N) {{
            b_val = B[b_row * N + col];
        }}
        As[local_row][local_col] = a_val;
        Bs[local_row][local_col] = b_val;
        barrier(CLK_LOCAL_MEM_FENCE);
        for (int k = 0; k < {tile}; ++k) {{
            acc += As[local_row][k] * Bs[k][local_col];
        }}
        barrier(CLK_LOCAL_MEM_FENCE);
    }}
    if (row < M && col < N) {{
        C[row * N + col] = acc;
    }}
    """
    params = [
        f"__global const {dtype}* A",
        f"__global const {dtype}* B",
        f"__global {dtype}* C",
        "const int M",
        "const int N",
        "const int K",
    ]
    return KernelSpec(name=f"matmul_t{tile}", params=params, body=body, preamble=preamble)


def build_matmul_kernel(
    context: Optional["cl.Context"], tile: int = 16, dtype: str = "float"
) -> Tuple[KernelSpec, Optional["cl.Kernel"]]:
    ocl_dtype, _ = _dtype_info(dtype)
    spec = matmul_kernel_spec(tile=tile, dtype=ocl_dtype)
    if context is None:
        return spec, None
    if cl is None:
        raise ImportError("pyopencl is required to build matmul kernels")
    build_opts = ""
    if ocl_dtype == "half":
        build_opts = "-cl-fast-relaxed-math -cl-std=CL1.2"
    program = cl.Program(context, spec.to_source()).build(options=build_opts)
    return spec, getattr(program, spec.name)


def matmul(a: Tensor, b: Tensor, tile: int = 16, out: Optional[Tensor] = None, pool: Optional[BufferPool] = None, force_naive: bool = False) -> Tensor:
    backend = ensure_same_backend((a, b), op="matmul")
    if len(a.shape) != 2 or len(b.shape) != 2:
        raise ValueError("matmul expects 2D tensors")
    M, K = a.shape
    Kb, N = b.shape
    if K != Kb:
        raise ValueError("inner dimensions must match for matmul")
    dtype = a.dtype
    if dtype != b.dtype:
        raise ValueError("dtype mismatch between inputs")

    t0_prof = time.perf_counter() if _PROFILE_MATMUL else None
    if backend == "cpu":
        if np is None:
            raise ImportError("numpy required for CPU matmul")
        a_arr = a.array
        b_arr = b.array
        if a_arr is None or b_arr is None:
            raise ValueError("CPU tensors require array storage")
        res = a_arr @ b_arr
        if out is None:
            out_tensor = Tensor.from_host(a.queue, res.astype(a_arr.dtype), dtype=dtype, backend="cpu")
        else:
            if out.shape != (M, N) or out.dtype != dtype:
                raise ValueError("output tensor shape/dtype mismatch")
            out.array[...] = res
            out_tensor = out
        if _PROFILE_MATMUL and t0_prof is not None:
            dt = time.perf_counter() - t0_prof
            flops = 2 * M * K * N
            _MATMUL_STATS["calls"] += 1
            _MATMUL_STATS["time"] += dt
            _MATMUL_STATS["flops"] += flops
        return out_tensor

    if cl is None:
        raise ImportError("pyopencl is required for matmul")
    if a.queue != b.queue:
        raise ValueError("input tensors must share the same command queue")
    
    # Use optimized kernel for large matrices
    if _USE_OPTIMIZED and not force_naive and M * N >= _OPTIMIZED_THRESHOLD:
        opt_matmul = _get_matmul_optimized()
        if opt_matmul is not None:
            try:
                result = opt_matmul(a, b, out=out, pool=pool)
                if _PROFILE_MATMUL and t0_prof is not None:
                    dt = time.perf_counter() - t0_prof
                    flops = 2 * M * K * N
                    _MATMUL_STATS["calls"] += 1
                    _MATMUL_STATS["time"] += dt
                    _MATMUL_STATS["flops"] += flops
                return result
            except Exception:
                pass  # Fall back to basic kernel
    
    ocl_dtype, dtype_bytes = _dtype_info(dtype)

    queue = a.queue
    ctx = a.context
    dev = ctx.devices[0] if ctx and ctx.devices else None
    if _AUTOTUNE_PER_SHAPE:
        tile_eff = _autotune_tile_shape(ctx, dev, dtype_bytes, dtype, M, K, N)
    elif _AUTOTUNE_TILES:
        tile_eff = _autotune_tile(ctx, dev, dtype_bytes, dtype)
    else:
        tile_eff = choose_tile_size(dev, requested=tile, dtype_bytes=dtype_bytes)
    tile_eff = choose_tile_size(dev, requested=tile_eff, dtype_bytes=dtype_bytes)

    spec, kernel = build_matmul_kernel(context=ctx, tile=tile_eff, dtype=ocl_dtype)
    if kernel is None:
        raise RuntimeError("failed to build matmul kernel")

    mf = cl.mem_flags
    if out is None:
        if pool is not None:
            handle = pool.allocate(M * N * dtype_bytes)
            buf_out = handle.buffer
            out = Tensor(buffer=buf_out, shape=(M, N), dtype=dtype, context=ctx, queue=queue, pool_handle=handle, backend="cl")
        else:
            buf_out = cl.Buffer(ctx, mf.WRITE_ONLY, size=M * N * dtype_bytes)
            out = Tensor(buffer=buf_out, shape=(M, N), dtype=dtype, context=ctx, queue=queue, backend="cl")
    else:
        if out.shape != (M, N):
            raise ValueError("output tensor has wrong shape")
        if out.dtype != dtype:
            raise ValueError("output tensor dtype mismatch")

    # Global sizes rounded up to tile size.
    g0 = ((M + tile_eff - 1) // tile_eff) * tile_eff
    g1 = ((N + tile_eff - 1) // tile_eff) * tile_eff
    local = (tile_eff, tile_eff)
    m_i = np.int32(M) if np is not None else M
    n_i = np.int32(N) if np is not None else N
    k_i = np.int32(K) if np is not None else K
    evt = kernel(queue, (g0, g1), local, a.buffer, b.buffer, out.buffer, m_i, n_i, k_i)
    if _PROFILE_MATMUL and t0_prof is not None:
        if _PROFILE_EVENTS and evt is not None and hasattr(evt, "profile"):
            try:
                evt.wait()
                dt = (evt.profile.end - evt.profile.start) * 1e-9
            except Exception:
                dt = time.perf_counter() - t0_prof
        else:
            dt = time.perf_counter() - t0_prof
        flops = 2 * M * K * N
        _MATMUL_STATS["calls"] += 1
        _MATMUL_STATS["time"] += dt
        _MATMUL_STATS["flops"] += flops
    return out
