"""
Softmax along the last dimension (axis=1 for 2D) using simple kernels.
"""

from __future__ import annotations

from typing import Optional

from netcl.core.tensor import Tensor
from netcl.core.backend import get_backend
from netcl.core.memory import BufferPool

try:
    import numpy as np  # type: ignore
except ImportError:  # pragma: no cover
    np = None

try:
    import pyopencl as cl  # type: ignore
except ImportError:  # pragma: no cover
    cl = None

_DTYPE_CNAME = {"float": "float", "float32": "float", "half": "half", "float16": "half"}
_KERNEL_CACHE = {}


def _get_softmax_kernels(ctx: "cl.Context", dtype_c: str):
    cache_key = (ctx.int_ptr, dtype_c)
    if cache_key in _KERNEL_CACHE:
        return _KERNEL_CACHE[cache_key]
    ksrc = f"""
    __kernel void row_max(__global const {dtype_c}* x, __global {dtype_c}* rowmax, const int M, const int N) {{
        int row = get_global_id(0);
        if (row >= M) return;
        {dtype_c} m = x[row * N];
        for (int c = 1; c < N; ++c) {{
            {dtype_c} v = x[row * N + c];
            if (v > m) m = v;
        }}
        rowmax[row] = m;
    }}
    __kernel void row_sumexp(__global const {dtype_c}* x, __global const {dtype_c}* rowmax, __global {dtype_c}* rowsum, const int M, const int N) {{
        int row = get_global_id(0);
        if (row >= M) return;
        {dtype_c} m = rowmax[row];
        {dtype_c} s = 0;
        for (int c = 0; c < N; ++c) {{
            s += exp(x[row * N + c] - m);
        }}
        rowsum[row] = s;
    }}
    __kernel void softmax_apply(__global const {dtype_c}* x, __global const {dtype_c}* rowmax, __global const {dtype_c}* rowsum, __global {dtype_c}* out, const int M, const int N) {{
        int gid = get_global_id(0);
        int row = gid / N;
        int col = gid % N;
        if (row >= M) return;
        {dtype_c} m = rowmax[row];
        {dtype_c} s = rowsum[row];
        out[gid] = exp(x[gid] - m) / s;
    }}
    """
    program = cl.Program(ctx, ksrc).build()
    kernels = (program.row_max, program.row_sumexp, program.softmax_apply)
    _KERNEL_CACHE[cache_key] = kernels
    return kernels


def softmax(x: Tensor, out: Optional[Tensor] = None, pool: Optional[BufferPool] = None) -> Tensor:
    backend = get_backend(x)
    if len(x.shape) != 2:
        raise ValueError("softmax currently supports 2D tensors along axis=1")
    if backend == "cpu":
        if np is None:
            raise ImportError("numpy required for CPU softmax")
        x_arr = x.array
        if x_arr is None:
            raise ValueError("CPU tensors require array storage")
        shifted = x_arr - x_arr.max(axis=1, keepdims=True)
        exp = np.exp(shifted)
        probs = exp / exp.sum(axis=1, keepdims=True)
        if out is None:
            return Tensor.from_host(x.queue, probs.astype(x_arr.dtype), dtype=x.dtype, backend="cpu")
        if out.shape != x.shape or out.dtype != x.dtype:
            raise ValueError("output tensor shape/dtype mismatch")
        out.array[...] = probs
        return out
    if cl is None or np is None:
        raise ImportError("pyopencl and numpy required for softmax")
    if x.dtype not in _DTYPE_CNAME:
        raise ValueError("softmax supports float32/float16")
    # fp16: use safe path -> compute in fp32 then cast back
    if x.dtype in ("half", "float16"):
        from netcl.ops.softmax_fp16 import softmax_fp16_safe

        return softmax_fp16_safe(x)
    dtype_c = _DTYPE_CNAME[x.dtype]
    ctx = x.context
    q = x.queue
    M, N = x.shape

    # Buffers
    max_buf = Tensor.from_shape(q, (M,), dtype=x.dtype, pool=pool)
    sum_buf = Tensor.from_shape(q, (M,), dtype=x.dtype, pool=pool)
    if out is None:
        out = Tensor.from_shape(q, x.shape, dtype=x.dtype, pool=pool)

    k_max, k_sum, k_soft = _get_softmax_kernels(ctx, dtype_c)
    g_rows = (int(np.ceil(M / 64.0)) * 64,)
    l_rows = (64,)
    k_max(q, g_rows, l_rows, x.buffer, max_buf.buffer, np.int32(M), np.int32(N))
    k_sum(q, g_rows, l_rows, x.buffer, max_buf.buffer, sum_buf.buffer, np.int32(M), np.int32(N))
    total = M * N
    g_total = (int(np.ceil(total / 256.0)) * 256,)
    k_soft(q, g_total, (256,), x.buffer, max_buf.buffer, sum_buf.buffer, out.buffer, np.int32(M), np.int32(N))
    return out
