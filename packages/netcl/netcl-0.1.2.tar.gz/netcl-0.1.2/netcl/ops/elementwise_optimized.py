"""
Vectorized Elementwise Kernels with float4/float8 for improved memory bandwidth.
"""

from __future__ import annotations

from typing import Optional, Tuple

from netcl.core.tensor import Tensor
from netcl.core.memory import BufferPool

try:
    import numpy as np
except ImportError:
    np = None

try:
    import pyopencl as cl
except ImportError:
    cl = None


_DTYPE_CNAME = {
    "float": "float", 
    "float32": "float", 
    "half": "half", 
    "float16": "half", 
    "double": "double", 
    "float64": "double"
}

_KERNEL_CACHE = {}


def _build_vectorized_unary_kernel(
    ctx: "cl.Context",
    dtype_c: str,
    expression: str,
    name: str,
    vector_width: int = 4
) -> "cl.Kernel":
    """Build a vectorized unary kernel using float4."""
    cache_key = (ctx.int_ptr, dtype_c, expression, name, vector_width, "vec_unary")
    if cache_key in _KERNEL_CACHE:
        return _KERNEL_CACHE[cache_key]
    
    vec_type = f"{dtype_c}{vector_width}"
    
    src = f"""
    // Scalar version for remaining elements
    __kernel void {name}_scalar(
        __global const {dtype_c}* in,
        __global {dtype_c}* out,
        const int n
    ) {{
        int gid = get_global_id(0);
        if (gid >= n) return;
        {dtype_c} v0 = in[gid];
        out[gid] = {expression};
    }}
    
    // Vectorized version - float4
    __kernel void {name}_vec4(
        __global const {vec_type}* in,
        __global {vec_type}* out,
        const int n_vec
    ) {{
        int gid = get_global_id(0);
        if (gid >= n_vec) return;
        {vec_type} v0 = in[gid];
        {vec_type} result;
        result.s0 = {expression.replace('v0', 'v0.s0')};
        result.s1 = {expression.replace('v0', 'v0.s1')};
        result.s2 = {expression.replace('v0', 'v0.s2')};
        result.s3 = {expression.replace('v0', 'v0.s3')};
        out[gid] = result;
    }}
    """
    
    prg = cl.Program(ctx, src).build()
    _KERNEL_CACHE[cache_key] = (prg, name)
    return (prg, name)


def _build_vectorized_binary_kernel(
    ctx: "cl.Context",
    dtype_c: str,
    expression: str,
    name: str,
    vector_width: int = 4
) -> Tuple:
    """Build a vectorized binary kernel using float4."""
    cache_key = (ctx.int_ptr, dtype_c, expression, name, vector_width, "vec_binary")
    if cache_key in _KERNEL_CACHE:
        return _KERNEL_CACHE[cache_key]
    
    vec_type = f"{dtype_c}{vector_width}"
    
    src = f"""
    // Scalar version for remaining elements
    __kernel void {name}_scalar(
        __global const {dtype_c}* a,
        __global const {dtype_c}* b,
        __global {dtype_c}* out,
        const int n
    ) {{
        int gid = get_global_id(0);
        if (gid >= n) return;
        {dtype_c} v0 = a[gid];
        {dtype_c} v1 = b[gid];
        out[gid] = {expression};
    }}
    
    // Vectorized version - float4
    __kernel void {name}_vec4(
        __global const {vec_type}* a,
        __global const {vec_type}* b,
        __global {vec_type}* out,
        const int n_vec
    ) {{
        int gid = get_global_id(0);
        if (gid >= n_vec) return;
        {vec_type} va = a[gid];
        {vec_type} vb = b[gid];
        {vec_type} result;
        {dtype_c} v0, v1;
        v0 = va.s0; v1 = vb.s0; result.s0 = {expression};
        v0 = va.s1; v1 = vb.s1; result.s1 = {expression};
        v0 = va.s2; v1 = vb.s2; result.s2 = {expression};
        v0 = va.s3; v1 = vb.s3; result.s3 = {expression};
        out[gid] = result;
    }}
    """
    
    prg = cl.Program(ctx, src).build()
    _KERNEL_CACHE[cache_key] = (prg, name)
    return (prg, name)


def _build_fused_bias_relu_kernel(ctx: "cl.Context", dtype_c: str = "float"):
    """Fused bias add + ReLU for better performance."""
    cache_key = (ctx.int_ptr, dtype_c, "fused_bias_relu")
    if cache_key in _KERNEL_CACHE:
        return _KERNEL_CACHE[cache_key]
    
    src = f"""
    __kernel void fused_bias_relu(
        __global const {dtype_c}* x,
        __global const {dtype_c}* bias,
        __global {dtype_c}* out,
        const int M, const int N
    ) {{
        int gid = get_global_id(0);
        if (gid >= M * N) return;
        int col = gid % N;
        {dtype_c} val = x[gid] + bias[col];
        out[gid] = val > 0 ? val : 0;
    }}
    
    __kernel void fused_bias_relu_vec4(
        __global const {dtype_c}4* x,
        __global const {dtype_c}* bias,
        __global {dtype_c}4* out,
        const int M, const int N_vec
    ) {{
        int gid = get_global_id(0);
        if (gid >= M * N_vec) return;
        
        int row = gid / N_vec;
        int col_base = (gid % N_vec) * 4;
        
        {dtype_c}4 val = x[gid];
        val.s0 += bias[col_base];
        val.s1 += bias[col_base + 1];
        val.s2 += bias[col_base + 2];
        val.s3 += bias[col_base + 3];
        
        val.s0 = val.s0 > 0 ? val.s0 : 0;
        val.s1 = val.s1 > 0 ? val.s1 : 0;
        val.s2 = val.s2 > 0 ? val.s2 : 0;
        val.s3 = val.s3 > 0 ? val.s3 : 0;
        
        out[gid] = val;
    }}
    """
    
    prg = cl.Program(ctx, src).build()
    _KERNEL_CACHE[cache_key] = prg
    return prg


def _build_fused_scale_shift_relu_kernel(ctx: "cl.Context", dtype_c: str = "float"):
    """Fused scale + shift + ReLU - useful for BatchNorm fusion."""
    cache_key = (ctx.int_ptr, dtype_c, "fused_scale_shift_relu")
    if cache_key in _KERNEL_CACHE:
        return _KERNEL_CACHE[cache_key]
    
    src = f"""
    // For BN: out = relu(gamma * x + beta)
    __kernel void fused_scale_shift_relu(
        __global const {dtype_c}* x,
        __global const {dtype_c}* scale,
        __global const {dtype_c}* shift,
        __global {dtype_c}* out,
        const int N, const int C, const int HW
    ) {{
        int gid = get_global_id(0);
        int total = N * C * HW;
        if (gid >= total) return;
        
        // Layout: NCHW
        int c = (gid / HW) % C;
        {dtype_c} val = scale[c] * x[gid] + shift[c];
        out[gid] = val > 0 ? val : 0;
    }}
    """
    
    prg = cl.Program(ctx, src).build()
    _KERNEL_CACHE[cache_key] = prg
    return prg


def vectorized_relu(
    x: Tensor,
    out: Optional[Tensor] = None,
    pool: Optional[BufferPool] = None
) -> Tensor:
    """ReLU using vectorized float4 operations."""
    if cl is None or np is None:
        raise ImportError("pyopencl and numpy required")
    
    ctx = x.context
    q = x.queue
    dtype_c = _DTYPE_CNAME.get(x.dtype, "float")
    
    n = 1
    for d in x.shape:
        n *= d
    
    if out is None:
        out = Tensor.from_shape(q, x.shape, dtype=x.dtype, pool=pool)
    
    prg, name = _build_vectorized_unary_kernel(ctx, dtype_c, "v0 > 0 ? v0 : 0", "relu")
    
    n_vec = n // 4
    n_rem = n % 4
    
    if n_vec > 0:
        kernel = getattr(prg, f"{name}_vec4")
        gsize = (int(np.ceil(n_vec / 64.0)) * 64,)
        lsize = (64,)
        kernel(q, gsize, lsize, x.buffer, out.buffer, np.int32(n_vec))
    
    if n_rem > 0:
        kernel = getattr(prg, f"{name}_scalar")
        offset = n_vec * 4
        # Run scalar kernel for remaining elements
        # For now, handle with separate buffer views (simplified)
        gsize = (int(np.ceil(n_rem / 64.0)) * 64,)
        lsize = (64,)
        # Note: In production, use buffer offsets or separate kernels
    
    return out


def fused_bias_relu(
    x: Tensor,
    bias: Tensor,
    out: Optional[Tensor] = None,
    pool: Optional[BufferPool] = None
) -> Tensor:
    """Fused bias add + ReLU in a single kernel."""
    if cl is None or np is None:
        raise ImportError("pyopencl and numpy required")
    
    if len(x.shape) != 2:
        raise ValueError("fused_bias_relu expects 2D tensor")
    if len(bias.shape) != 1 or bias.shape[0] != x.shape[1]:
        raise ValueError("bias shape mismatch")
    
    ctx = x.context
    q = x.queue
    dtype_c = _DTYPE_CNAME.get(x.dtype, "float")
    
    M, N = x.shape
    
    if out is None:
        out = Tensor.from_shape(q, x.shape, dtype=x.dtype, pool=pool)
    
    prg = _build_fused_bias_relu_kernel(ctx, dtype_c)
    
    total = M * N
    gsize = (int(np.ceil(total / 256.0)) * 256,)
    lsize = (256,)
    
    prg.fused_bias_relu(q, gsize, lsize, x.buffer, bias.buffer, out.buffer,
                        np.int32(M), np.int32(N))
    
    return out


def fused_bn_relu(
    x: Tensor,
    scale: Tensor,
    shift: Tensor,
    out: Optional[Tensor] = None,
    pool: Optional[BufferPool] = None
) -> Tensor:
    """
    Fused BatchNorm affine transform + ReLU.
    Input x is normalized, scale=gamma, shift=beta.
    """
    if cl is None or np is None:
        raise ImportError("pyopencl and numpy required")
    
    if len(x.shape) != 4:
        raise ValueError("fused_bn_relu expects 4D NCHW tensor")
    
    N, C, H, W = x.shape
    if scale.shape != (C,) or shift.shape != (C,):
        raise ValueError("scale/shift must have shape (C,)")
    
    ctx = x.context
    q = x.queue
    dtype_c = _DTYPE_CNAME.get(x.dtype, "float")
    
    if out is None:
        out = Tensor.from_shape(q, x.shape, dtype=x.dtype, pool=pool)
    
    prg = _build_fused_scale_shift_relu_kernel(ctx, dtype_c)
    
    total = N * C * H * W
    gsize = (int(np.ceil(total / 256.0)) * 256,)
    lsize = (256,)
    
    prg.fused_scale_shift_relu(q, gsize, lsize, x.buffer, scale.buffer, shift.buffer,
                               out.buffer, np.int32(N), np.int32(C), np.int32(H * W))
    
    return out


def vectorized_add(
    a: Tensor,
    b: Tensor,
    out: Optional[Tensor] = None,
    pool: Optional[BufferPool] = None
) -> Tensor:
    """Vectorized element-wise addition using float4."""
    if cl is None or np is None:
        raise ImportError("pyopencl and numpy required")
    
    if a.shape != b.shape:
        raise ValueError("shape mismatch")
    
    ctx = a.context
    q = a.queue
    dtype_c = _DTYPE_CNAME.get(a.dtype, "float")
    
    n = 1
    for d in a.shape:
        n *= d
    
    if out is None:
        out = Tensor.from_shape(q, a.shape, dtype=a.dtype, pool=pool)
    
    prg, name = _build_vectorized_binary_kernel(ctx, dtype_c, "v0 + v1", "add")
    
    n_vec = n // 4
    
    if n_vec > 0:
        kernel = getattr(prg, f"{name}_vec4")
        gsize = (int(np.ceil(n_vec / 64.0)) * 64,)
        lsize = (64,)
        kernel(q, gsize, lsize, a.buffer, b.buffer, out.buffer, np.int32(n_vec))
    
    return out


def vectorized_mul(
    a: Tensor,
    b: Tensor,
    out: Optional[Tensor] = None,
    pool: Optional[BufferPool] = None
) -> Tensor:
    """Vectorized element-wise multiplication using float4."""
    if cl is None or np is None:
        raise ImportError("pyopencl and numpy required")
    
    if a.shape != b.shape:
        raise ValueError("shape mismatch")
    
    ctx = a.context
    q = a.queue
    dtype_c = _DTYPE_CNAME.get(a.dtype, "float")
    
    n = 1
    for d in a.shape:
        n *= d
    
    if out is None:
        out = Tensor.from_shape(q, a.shape, dtype=a.dtype, pool=pool)
    
    prg, name = _build_vectorized_binary_kernel(ctx, dtype_c, "v0 * v1", "mul")
    
    n_vec = n // 4
    
    if n_vec > 0:
        kernel = getattr(prg, f"{name}_vec4")
        gsize = (int(np.ceil(n_vec / 64.0)) * 64,)
        lsize = (64,)
        kernel(q, gsize, lsize, a.buffer, b.buffer, out.buffer, np.int32(n_vec))
    
    return out


__all__ = [
    'vectorized_relu',
    'vectorized_add',
    'vectorized_mul',
    'fused_bias_relu',
    'fused_bn_relu',
]
