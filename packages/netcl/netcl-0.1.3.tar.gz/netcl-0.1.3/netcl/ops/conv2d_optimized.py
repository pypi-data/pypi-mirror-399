"""
Optimized Conv2D kernels with device-side operations.
Eliminates host copies by keeping all operations on GPU.
"""

from __future__ import annotations

import os
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

_DTYPE_CNAME = {"float": "float", "float32": "float", "half": "half", "float16": "half"}
_KERNEL_CACHE = {}


def _build_bias_grad_kernel(ctx: "cl.Context", dtype_c: str = "float"):
    """
    Reduce grad_out over N, OH, OW to produce bias grad (F,).
    """
    cache_key = (ctx.int_ptr, "conv2d_bias_grad", dtype_c)
    if cache_key in _KERNEL_CACHE:
        return _KERNEL_CACHE[cache_key]
    src = f"""
    __kernel void conv2d_bias_grad(__global const {dtype_c}* grad_out, __global {dtype_c}* grad_b,
                                   const int N, const int F, const int OH, const int OW) {{
        int f = get_global_id(0);
        if (f >= F) return;
        float acc = 0.0f;
        int spatial = OH * OW;
        int batch = N * spatial;
        for (int n = 0; n < N; ++n) {{
            int base = (n * F + f) * spatial;
            for (int s = 0; s < spatial; ++s) {{
                acc += grad_out[base + s];
            }}
        }}
        grad_b[f] = acc;
    }}
    """
    prg = cl.Program(ctx, src).build()
    _KERNEL_CACHE[cache_key] = prg.conv2d_bias_grad
    return prg.conv2d_bias_grad


def _build_reshape_transpose_kernel(ctx: "cl.Context", dtype_c: str = "float"):
    """
    Device-side reshape and transpose from (N*OH*OW, F) to (N, F, OH, OW).
    Eliminates host copy in im2col path.
    """
    cache_key = (ctx.int_ptr, "reshape_transpose", dtype_c)
    if cache_key in _KERNEL_CACHE:
        return _KERNEL_CACHE[cache_key]
    
    src = f"""
    __kernel void reshape_transpose_nohwf_to_nfhw(
        __global const {dtype_c}* in,
        __global {dtype_c}* out,
        const int N, const int F, const int OH, const int OW
    ) {{
        int gid = get_global_id(0);
        int total = N * F * OH * OW;
        if (gid >= total) return;
        
        // Output index: (n, f, oh, ow) in NFHW layout
        int ow = gid % OW;
        int oh = (gid / OW) % OH;
        int f = (gid / (OW * OH)) % F;
        int n = gid / (F * OH * OW);
        
        // Input index: ((n*OH + oh)*OW + ow) * F + f in (N*OH*OW, F) layout
        int in_idx = ((n * OH + oh) * OW + ow) * F + f;
        out[gid] = in[in_idx];
    }}
    """
    prg = cl.Program(ctx, src).build()
    kernel = prg.reshape_transpose_nohwf_to_nfhw
    _KERNEL_CACHE[cache_key] = kernel
    return kernel


def _build_bias_add_4d_kernel(ctx: "cl.Context", dtype_c: str = "float"):
    """
    Add bias to 4D tensor (N, F, OH, OW) where bias is (F,).
    """
    cache_key = (ctx.int_ptr, "bias_add_4d", dtype_c)
    if cache_key in _KERNEL_CACHE:
        return _KERNEL_CACHE[cache_key]
    
    src = f"""
    __kernel void bias_add_4d(
        __global {dtype_c}* out,
        __global const {dtype_c}* bias,
        const int N, const int F, const int OH, const int OW
    ) {{
        int gid = get_global_id(0);
        int total = N * F * OH * OW;
        if (gid >= total) return;
        
        int f = (gid / (OH * OW)) % F;
        out[gid] += bias[f];
    }}
    """
    prg = cl.Program(ctx, src).build()
    kernel = prg.bias_add_4d
    _KERNEL_CACHE[cache_key] = kernel
    return kernel


def _build_implicit_gemm_conv2d_kernel(ctx: "cl.Context", dtype_c: str = "float", 
                                        tile_m: int = 8, tile_n: int = 8, tile_k: int = 8,
                                        fuse_relu: bool = False):
    """
    Implicit GEMM Conv2D - computes im2col on-the-fly during GEMM.
    No separate im2col buffer needed.
    """
    cache_key = (ctx.int_ptr, "implicit_gemm_conv2d", dtype_c, tile_m, tile_n, tile_k)
    if cache_key in _KERNEL_CACHE:
        return _KERNEL_CACHE[cache_key]
    
    src = f"""
    #define TILE_M {tile_m}
    #define TILE_N {tile_n}
    #define TILE_K {tile_k}
    
    __kernel void implicit_gemm_conv2d(
        __global const {dtype_c}* x,
        __global const {dtype_c}* w,
        __global const {dtype_c}* bias,
        __global {dtype_c}* out,
        const int N, const int C, const int H, const int W,
        const int F, const int KH, const int KW,
        const int OH, const int OW,
        const int stride, const int pad
    ) {{
        // Each work-item computes one output element
        int gid = get_global_id(0);
        int total = N * F * OH * OW;
        if (gid >= total) return;
        
        int ow = gid % OW;
        int oh = (gid / OW) % OH;
        int f = (gid / (OH * OW)) % F;
        int n = gid / (F * OH * OW);
        
        {dtype_c} acc = 0;
        
        // Implicit im2col: compute input indices on-the-fly
        for (int c = 0; c < C; ++c) {{
            for (int kh = 0; kh < KH; ++kh) {{
                int ih = oh * stride + kh - pad;
                if (ih < 0 || ih >= H) continue;
                
                for (int kw = 0; kw < KW; ++kw) {{
                    int iw = ow * stride + kw - pad;
                    if (iw < 0 || iw >= W) continue;
                    
                    // x[n, c, ih, iw]
                    int x_idx = ((n * C + c) * H + ih) * W + iw;
                    // w[f, c, kh, kw]
                    int w_idx = ((f * C + c) * KH + kh) * KW + kw;
                    
                    acc += x[x_idx] * w[w_idx];
                }}
            }}
        }}
        
        // Add bias if present
        if (bias != 0) {{
            acc += bias[f];
        }}
        
        if (bias != 0) {{
            acc += bias[f];
        }}
        {"acc = acc > 0 ? acc : 0;" if fuse_relu else ""}
        out[gid] = acc;
    }}
    """
    prg = cl.Program(ctx, src).build()
    kernel = prg.implicit_gemm_conv2d
    _KERNEL_CACHE[cache_key] = kernel
    return kernel


def _build_tiled_conv2d_local_mem_kernel(ctx: "cl.Context", dtype_c: str = "float",
                                          tile_oh: int = 4, tile_ow: int = 4,
                                          fuse_relu: bool = False):
    """
    Tiled Conv2D with local memory for input caching.
    Better memory access patterns and reduced global memory traffic.
    """
    cache_key = (ctx.int_ptr, "tiled_conv2d_local", dtype_c, tile_oh, tile_ow)
    if cache_key in _KERNEL_CACHE:
        return _KERNEL_CACHE[cache_key]
    
    # Maximum kernel size we'll support with local memory
    max_kh, max_kw = 7, 7
    local_h = tile_oh + max_kh - 1
    local_w = tile_ow + max_kw - 1
    
    src = f"""
    #define TILE_OH {tile_oh}
    #define TILE_OW {tile_ow}
    #define LOCAL_H {local_h}
    #define LOCAL_W {local_w}
    
    __kernel void tiled_conv2d_local(
        __global const {dtype_c}* x,
        __global const {dtype_c}* w,
        __global const {dtype_c}* bias,
        __global {dtype_c}* out,
        const int N, const int C, const int H, const int W,
        const int F, const int KH, const int KW,
        const int OH, const int OW,
        const int stride, const int pad
    ) {{
        __local {dtype_c} x_local[LOCAL_H][LOCAL_W];
        
        int tx = get_local_id(0);  // Within tile: 0..TILE_OW-1
        int ty = get_local_id(1);  // Within tile: 0..TILE_OH-1
        int bx = get_group_id(0);  // Tile x index
        int by = get_group_id(1);  // Tile y index
        int nf = get_group_id(2);  // Batch * Filter index
        
        int n = nf / F;
        int f = nf % F;
        
        int oh_base = by * TILE_OH;
        int ow_base = bx * TILE_OW;
        
        int oh = oh_base + ty;
        int ow = ow_base + tx;
        
        {dtype_c} acc = 0;
        
        // Iterate over input channels
        for (int c = 0; c < C; ++c) {{
            // Cooperative load of x into local memory
            int ih_start = oh_base * stride - pad;
            int iw_start = ow_base * stride - pad;
            
            barrier(CLK_LOCAL_MEM_FENCE);
            
            // Each thread loads multiple elements if needed
            for (int ly = ty; ly < LOCAL_H; ly += TILE_OH) {{
                for (int lx = tx; lx < LOCAL_W; lx += TILE_OW) {{
                    int ih = ih_start + ly;
                    int iw = iw_start + lx;
                    
                    if (ih >= 0 && ih < H && iw >= 0 && iw < W) {{
                        x_local[ly][lx] = x[((n * C + c) * H + ih) * W + iw];
                    }} else {{
                        x_local[ly][lx] = 0;
                    }}
                }}
            }}
            
            barrier(CLK_LOCAL_MEM_FENCE);
            
            // Compute convolution using local memory
            if (oh < OH && ow < OW) {{
                for (int kh = 0; kh < KH; ++kh) {{
                    for (int kw = 0; kw < KW; ++kw) {{
                        int ly = ty * stride + kh;
                        int lx = tx * stride + kw;
                        
                        int w_idx = ((f * C + c) * KH + kh) * KW + kw;
                        acc += x_local[ly][lx] * w[w_idx];
                    }}
                }}
            }}
        }}
        
        // Write output
        if (oh < OH && ow < OW) {{
            int out_idx = ((n * F + f) * OH + oh) * OW + ow;
            if (bias != 0) {{
                acc += bias[f];
            }}
            {"acc = acc > 0 ? acc : 0;" if fuse_relu else ""}
            out[out_idx] = acc;
        }}
    }}
    """
    prg = cl.Program(ctx, src).build()
    kernel = prg.tiled_conv2d_local
    _KERNEL_CACHE[cache_key] = kernel
    return kernel


def _build_vectorized_conv2d_kernel(ctx: "cl.Context", dtype_c: str = "float"):
    """
    Vectorized Conv2D using float4 for better memory bandwidth utilization.
    Works best when output width is multiple of 4.
    """
    cache_key = (ctx.int_ptr, "vectorized_conv2d", dtype_c)
    if cache_key in _KERNEL_CACHE:
        return _KERNEL_CACHE[cache_key]
    
    src = f"""
    __kernel void vectorized_conv2d(
        __global const {dtype_c}* x,
        __global const {dtype_c}* w,
        __global const {dtype_c}* bias,
        __global {dtype_c}4* out,
        const int N, const int C, const int H, const int W,
        const int F, const int KH, const int KW,
        const int OH, const int OW,
        const int stride, const int pad
    ) {{
        // Each work-item computes 4 consecutive output elements
        int gid = get_global_id(0);
        int total = N * F * OH * (OW / 4);
        if (gid >= total) return;
        
        int ow4 = gid % (OW / 4);
        int oh = (gid / (OW / 4)) % OH;
        int f = (gid / ((OW / 4) * OH)) % F;
        int n = gid / (F * OH * (OW / 4));
        
        int ow_base = ow4 * 4;
        
        {dtype_c}4 acc = ({dtype_c}4)(0, 0, 0, 0);
        
        for (int c = 0; c < C; ++c) {{
            for (int kh = 0; kh < KH; ++kh) {{
                int ih = oh * stride + kh - pad;
                if (ih < 0 || ih >= H) continue;
                
                for (int kw = 0; kw < KW; ++kw) {{
                    {dtype_c} w_val = w[((f * C + c) * KH + kh) * KW + kw];
                    
                    // Load 4 input values
                    {dtype_c}4 x_vals;
                    for (int i = 0; i < 4; ++i) {{
                        int iw = (ow_base + i) * stride + kw - pad;
                        if (iw >= 0 && iw < W) {{
                            int x_idx = ((n * C + c) * H + ih) * W + iw;
                            if (i == 0) x_vals.x = x[x_idx];
                            else if (i == 1) x_vals.y = x[x_idx];
                            else if (i == 2) x_vals.z = x[x_idx];
                            else x_vals.w = x[x_idx];
                        }} else {{
                            if (i == 0) x_vals.x = 0;
                            else if (i == 1) x_vals.y = 0;
                            else if (i == 2) x_vals.z = 0;
                            else x_vals.w = 0;
                        }}
                    }}
                    
                    acc += x_vals * w_val;
                }}
            }}
        }}
        
        // Add bias
        if (bias != 0) {{
            {dtype_c} b = bias[f];
            acc += ({dtype_c}4)(b, b, b, b);
        }}
        
        out[gid] = acc;
    }}
    """
    prg = cl.Program(ctx, src).build()
    kernel = prg.vectorized_conv2d
    _KERNEL_CACHE[cache_key] = kernel
    return kernel


def reshape_transpose_device(
    input_tensor: Tensor, 
    N: int, F: int, OH: int, OW: int,
    out: Optional[Tensor] = None,
    pool: Optional[BufferPool] = None
) -> Tensor:
    """
    Device-side reshape and transpose from (N*OH*OW, F) to (N, F, OH, OW).
    Replaces host-side .to_host().reshape().transpose().copy()
    """
    if cl is None or np is None:
        raise ImportError("pyopencl and numpy required")
    
    ctx = input_tensor.context
    q = input_tensor.queue
    dtype_c = _DTYPE_CNAME.get(input_tensor.dtype, "float")
    
    kernel = _build_reshape_transpose_kernel(ctx, dtype_c)
    
    out_shape = (N, F, OH, OW)
    if out is None:
        out = Tensor.from_shape(q, out_shape, dtype=input_tensor.dtype, pool=pool)
    
    total = N * F * OH * OW
    gsize = (int(np.ceil(total / 256.0)) * 256,)
    
    kernel(q, gsize, (256,),
           input_tensor.buffer, out.buffer,
           np.int32(N), np.int32(F), np.int32(OH), np.int32(OW))
    
    return out


def bias_add_4d_device(out: Tensor, bias: Tensor) -> Tensor:
    """
    Add bias to 4D tensor in-place on device.
    """
    if cl is None or np is None:
        raise ImportError("pyopencl and numpy required")
    
    ctx = out.context
    q = out.queue
    dtype_c = _DTYPE_CNAME.get(out.dtype, "float")
    
    kernel = _build_bias_add_4d_kernel(ctx, dtype_c)
    
    N, F, OH, OW = out.shape
    total = N * F * OH * OW
    gsize = (int(np.ceil(total / 256.0)) * 256,)
    
    kernel(q, gsize, (256,),
           out.buffer, bias.buffer,
           np.int32(N), np.int32(F), np.int32(OH), np.int32(OW))
    
    return out


def conv2d_implicit_gemm(
    x: Tensor,
    w: Tensor,
    bias: Optional[Tensor] = None,
    stride: int = 1,
    pad: int = 0,
    out: Optional[Tensor] = None,
    pool: Optional[BufferPool] = None,
    fuse_relu: bool = False,
) -> Tensor:
    """
    Implicit GEMM Conv2D - no separate im2col allocation.
    Better for memory-constrained scenarios.
    """
    if cl is None or np is None:
        raise ImportError("pyopencl and numpy required")
    
    ctx = x.context
    q = x.queue
    dtype_c = _DTYPE_CNAME.get(x.dtype, "float")
    
    N, C, H, W_in = x.shape
    F, _, KH, KW = w.shape
    OH = (H + 2 * pad - KH) // stride + 1
    OW = (W_in + 2 * pad - KW) // stride + 1
    
    kernel = _build_implicit_gemm_conv2d_kernel(ctx, dtype_c, fuse_relu=fuse_relu)
    
    out_shape = (N, F, OH, OW)
    if out is None:
        out = Tensor.from_shape(q, out_shape, dtype=x.dtype, pool=pool)
    
    total = N * F * OH * OW
    gsize = (int(np.ceil(total / 256.0)) * 256,)
    
    kernel(q, gsize, (256,),
           x.buffer, w.buffer,
           bias.buffer if bias is not None else None,
           out.buffer,
           np.int32(N), np.int32(C), np.int32(H), np.int32(W_in),
           np.int32(F), np.int32(KH), np.int32(KW),
           np.int32(OH), np.int32(OW),
           np.int32(stride), np.int32(pad))
    
    return out


def conv2d_tiled_local(
    x: Tensor,
    w: Tensor,
    bias: Optional[Tensor] = None,
    stride: int = 1,
    pad: int = 0,
    tile_oh: int = 4,
    tile_ow: int = 4,
    out: Optional[Tensor] = None,
    pool: Optional[BufferPool] = None,
    fuse_relu: bool = False,
) -> Tensor:
    """
    Tiled Conv2D with local memory caching.
    Better for larger feature maps.
    """
    if cl is None or np is None:
        raise ImportError("pyopencl and numpy required")
    
    ctx = x.context
    q = x.queue
    dtype_c = _DTYPE_CNAME.get(x.dtype, "float")
    
    N, C, H, W_in = x.shape
    F, _, KH, KW = w.shape
    OH = (H + 2 * pad - KH) // stride + 1
    OW = (W_in + 2 * pad - KW) // stride + 1
    
    kernel = _build_tiled_conv2d_local_mem_kernel(ctx, dtype_c, tile_oh, tile_ow, fuse_relu=fuse_relu)
    
    out_shape = (N, F, OH, OW)
    if out is None:
        out = Tensor.from_shape(q, out_shape, dtype=x.dtype, pool=pool)
    
    # Global size based on tiles
    gsize = (
        int(np.ceil(OW / tile_ow)) * tile_ow,
        int(np.ceil(OH / tile_oh)) * tile_oh,
        N * F
    )
    lsize = (tile_ow, tile_oh, 1)
    
    kernel(q, gsize, lsize,
           x.buffer, w.buffer,
           bias.buffer if bias is not None else None,
           out.buffer,
           np.int32(N), np.int32(C), np.int32(H), np.int32(W_in),
           np.int32(F), np.int32(KH), np.int32(KW),
           np.int32(OH), np.int32(OW),
           np.int32(stride), np.int32(pad))
    
    return out


# ============================================================================
# WINOGRAD CONVOLUTION F(2x2, 3x3)
# ============================================================================

def _build_winograd_input_transform_kernel(ctx: "cl.Context", dtype_c: str = "float"):
    """
    Winograd input transform: B^T * d * B
    For F(2x2, 3x3): 4x4 tiles -> 4x4 transformed tiles.
    """
    cache_key = (ctx.int_ptr, "winograd_input_transform", dtype_c)
    if cache_key in _KERNEL_CACHE:
        return _KERNEL_CACHE[cache_key]
    
    # B^T matrix for F(2x2, 3x3)
    src = f"""
    __kernel void winograd_input_transform(
        __global const {dtype_c}* x,
        __global {dtype_c}* V,
        const int N, const int C, const int H, const int W,
        const int num_tiles_h, const int num_tiles_w, const int pad
    ) {{
        int gid = get_global_id(0);
        int total_tiles = N * C * num_tiles_h * num_tiles_w;
        if (gid >= total_tiles) return;
        
        int tw = gid % num_tiles_w;
        int th = (gid / num_tiles_w) % num_tiles_h;
        int c = (gid / (num_tiles_w * num_tiles_h)) % C;
        int n = gid / (C * num_tiles_h * num_tiles_w);
        
        // Load 4x4 input tile
        {dtype_c} d[4][4];
        int h_start = th * 2 - pad;
        int w_start = tw * 2 - pad;
        
        for (int i = 0; i < 4; ++i) {{
            for (int j = 0; j < 4; ++j) {{
                int h_idx = h_start + i;
                int w_idx = w_start + j;
                if (h_idx >= 0 && h_idx < H && w_idx >= 0 && w_idx < W) {{
                    d[i][j] = x[((n * C + c) * H + h_idx) * W + w_idx];
                }} else {{
                    d[i][j] = 0;
                }}
            }}
        }}
        
        // B^T * d * B transformation for F(2x2, 3x3)
        // B^T = [[1, 0, -1, 0], [0, 1, 1, 0], [0, -1, 1, 0], [0, 1, 0, -1]]
        {dtype_c} tmp[4][4];
        
        // First: tmp = B^T * d (row transformation)
        for (int j = 0; j < 4; ++j) {{
            tmp[0][j] = d[0][j] - d[2][j];
            tmp[1][j] = d[1][j] + d[2][j];
            tmp[2][j] = -d[1][j] + d[2][j];
            tmp[3][j] = d[1][j] - d[3][j];
        }}
        
        // Second: V = tmp * B (column transformation)
        {dtype_c} V_tile[4][4];
        for (int i = 0; i < 4; ++i) {{
            V_tile[i][0] = tmp[i][0] - tmp[i][2];
            V_tile[i][1] = tmp[i][1] + tmp[i][2];
            V_tile[i][2] = -tmp[i][1] + tmp[i][2];
            V_tile[i][3] = tmp[i][1] - tmp[i][3];
        }}
        
        // Store to V[alpha][beta][n][c][th][tw]
        int base = (n * C + c) * num_tiles_h * num_tiles_w + th * num_tiles_w + tw;
        int stride_tile = N * C * num_tiles_h * num_tiles_w;
        
        for (int i = 0; i < 4; ++i) {{
            for (int j = 0; j < 4; ++j) {{
                int idx = (i * 4 + j) * stride_tile + base;
                V[idx] = V_tile[i][j];
            }}
        }}
    }}
    """
    prg = cl.Program(ctx, src).build()
    _KERNEL_CACHE[cache_key] = prg.winograd_input_transform
    return prg.winograd_input_transform


def _build_winograd_filter_transform_kernel(ctx: "cl.Context", dtype_c: str = "float"):
    """
    Winograd filter transform: G * g * G^T
    For F(2x2, 3x3): 3x3 filters -> 4x4 transformed filters.
    """
    cache_key = (ctx.int_ptr, "winograd_filter_transform", dtype_c)
    if cache_key in _KERNEL_CACHE:
        return _KERNEL_CACHE[cache_key]
    
    src = f"""
    __kernel void winograd_filter_transform(
        __global const {dtype_c}* g,
        __global {dtype_c}* U,
        const int F_out, const int C
    ) {{
        int gid = get_global_id(0);
        int total = F_out * C;
        if (gid >= total) return;
        
        int c = gid % C;
        int f = gid / C;
        
        // Load 3x3 filter
        {dtype_c} filter[3][3];
        for (int i = 0; i < 3; ++i) {{
            for (int j = 0; j < 3; ++j) {{
                filter[i][j] = g[((f * C + c) * 3 + i) * 3 + j];
            }}
        }}
        
        // G * g * G^T for F(2x2, 3x3)
        // G = [[1, 0, 0], [0.5, 0.5, 0.5], [0.5, -0.5, 0.5], [0, 0, 1]]
        {dtype_c} tmp[4][3];
        
        // First: tmp = G * g
        for (int j = 0; j < 3; ++j) {{
            tmp[0][j] = filter[0][j];
            tmp[1][j] = (filter[0][j] + filter[1][j] + filter[2][j]) * 0.5f;
            tmp[2][j] = (filter[0][j] - filter[1][j] + filter[2][j]) * 0.5f;
            tmp[3][j] = filter[2][j];
        }}
        
        // Second: U = tmp * G^T
        {dtype_c} U_tile[4][4];
        for (int i = 0; i < 4; ++i) {{
            U_tile[i][0] = tmp[i][0];
            U_tile[i][1] = (tmp[i][0] + tmp[i][1] + tmp[i][2]) * 0.5f;
            U_tile[i][2] = (tmp[i][0] - tmp[i][1] + tmp[i][2]) * 0.5f;
            U_tile[i][3] = tmp[i][2];
        }}
        
        // Store to U[alpha][beta][f][c]
        int base = f * C + c;
        int stride_fc = F_out * C;
        
        for (int i = 0; i < 4; ++i) {{
            for (int j = 0; j < 4; ++j) {{
                int idx = (i * 4 + j) * stride_fc + base;
                U[idx] = U_tile[i][j];
            }}
        }}
    }}
    """
    prg = cl.Program(ctx, src).build()
    _KERNEL_CACHE[cache_key] = prg.winograd_filter_transform
    return prg.winograd_filter_transform


def _build_winograd_output_transform_kernel(ctx: "cl.Context", dtype_c: str = "float"):
    """
    Winograd output transform: A^T * M * A
    For F(2x2, 3x3): 4x4 -> 2x2 output tiles.
    """
    cache_key = (ctx.int_ptr, "winograd_output_transform", dtype_c)
    if cache_key in _KERNEL_CACHE:
        return _KERNEL_CACHE[cache_key]
    
    src = f"""
    __kernel void winograd_output_transform(
        __global const {dtype_c}* M,
        __global const {dtype_c}* bias,
        __global {dtype_c}* out,
        const int N, const int F_out, const int OH, const int OW,
        const int num_tiles_h, const int num_tiles_w
    ) {{
        int gid = get_global_id(0);
        int total_tiles = N * F_out * num_tiles_h * num_tiles_w;
        if (gid >= total_tiles) return;
        
        int tw = gid % num_tiles_w;
        int th = (gid / num_tiles_w) % num_tiles_h;
        int f = (gid / (num_tiles_w * num_tiles_h)) % F_out;
        int n = gid / (F_out * num_tiles_h * num_tiles_w);
        
        // Load M[alpha][beta] for this tile
        {dtype_c} m[4][4];
        int base = (n * F_out + f) * num_tiles_h * num_tiles_w + th * num_tiles_w + tw;
        int stride_tile = N * F_out * num_tiles_h * num_tiles_w;
        
        for (int i = 0; i < 4; ++i) {{
            for (int j = 0; j < 4; ++j) {{
                m[i][j] = M[(i * 4 + j) * stride_tile + base];
            }}
        }}
        
        // A^T * M * A for F(2x2, 3x3)
        // A^T = [[1, 1, 1, 0], [0, 1, -1, -1]]
        {dtype_c} tmp[2][4];
        
        // First: tmp = A^T * M
        for (int j = 0; j < 4; ++j) {{
            tmp[0][j] = m[0][j] + m[1][j] + m[2][j];
            tmp[1][j] = m[1][j] - m[2][j] - m[3][j];
        }}
        
        // Second: out = tmp * A
        {dtype_c} out_tile[2][2];
        for (int i = 0; i < 2; ++i) {{
            out_tile[i][0] = tmp[i][0] + tmp[i][1] + tmp[i][2];
            out_tile[i][1] = tmp[i][1] - tmp[i][2] - tmp[i][3];
        }}
        
        // Add bias and store
        {dtype_c} b = (bias != 0) ? bias[f] : 0;
        
        for (int i = 0; i < 2; ++i) {{
            int oh = th * 2 + i;
            if (oh >= OH) continue;
            for (int j = 0; j < 2; ++j) {{
                int ow = tw * 2 + j;
                if (ow >= OW) continue;
                out[((n * F_out + f) * OH + oh) * OW + ow] = out_tile[i][j] + b;
            }}
        }}
    }}
    """
    prg = cl.Program(ctx, src).build()
    _KERNEL_CACHE[cache_key] = prg.winograd_output_transform
    return prg.winograd_output_transform


def _build_winograd_batched_gemm_kernel(ctx: "cl.Context", dtype_c: str = "float"):
    """
    Batched GEMM for Winograd: M[alpha][beta] = U[alpha][beta] * V[alpha][beta]
    16 matrix multiplications, one for each (alpha, beta) pair.
    """
    cache_key = (ctx.int_ptr, "winograd_batched_gemm", dtype_c)
    if cache_key in _KERNEL_CACHE:
        return _KERNEL_CACHE[cache_key]
    
    src = f"""
    __kernel void winograd_batched_gemm(
        __global const {dtype_c}* U,
        __global const {dtype_c}* V,
        __global {dtype_c}* M,
        const int F_out, const int C,
        const int N, const int num_tiles
    ) {{
        // Each work-item computes one element of M
        int gid = get_global_id(0);
        int total = 16 * N * F_out * num_tiles;
        if (gid >= total) return;
        
        int tile_idx = gid % num_tiles;
        int f = (gid / num_tiles) % F_out;
        int n = (gid / (num_tiles * F_out)) % N;
        int ab = gid / (N * F_out * num_tiles);  // alpha * 4 + beta
        
        // M[ab][n][f][tile] = sum_c U[ab][f][c] * V[ab][n][c][tile]
        int stride_U = F_out * C;
        int stride_V = N * C * num_tiles;
        
        {dtype_c} acc = 0;
        for (int c = 0; c < C; ++c) {{
            int u_idx = ab * stride_U + f * C + c;
            int v_idx = ab * stride_V + (n * C + c) * num_tiles + tile_idx;
            acc += U[u_idx] * V[v_idx];
        }}
        
        int m_idx = ab * (N * F_out * num_tiles) + (n * F_out + f) * num_tiles + tile_idx;
        M[m_idx] = acc;
    }}
    """
    prg = cl.Program(ctx, src).build()
    _KERNEL_CACHE[cache_key] = prg.winograd_batched_gemm
    return prg.winograd_batched_gemm


def conv2d_winograd_f2x2_3x3(
    x: Tensor,
    w: Tensor,
    bias: Optional[Tensor] = None,
    pad: int = 1,
    out: Optional[Tensor] = None,
    pool: Optional[BufferPool] = None,
    fuse_relu: bool = False,
) -> Tensor:
    """
    Winograd F(2x2, 3x3) convolution.
    
    Only works for:
    - 3x3 kernels
    - stride = 1
    
    Reduces arithmetic complexity from 9 to 2.25 multiplications per output.
    """
    if cl is None or np is None:
        raise ImportError("pyopencl and numpy required")
    
    N, C, H, W_in = x.shape
    F_out, C_w, KH, KW = w.shape
    
    if KH != 3 or KW != 3:
        raise ValueError("Winograd F(2x2, 3x3) requires 3x3 kernels")
    if C != C_w:
        raise ValueError("Channel mismatch")
    
    ctx = x.context
    q = x.queue
    dtype_c = _DTYPE_CNAME.get(x.dtype, "float")
    
    # Output dimensions (stride=1)
    OH = H + 2 * pad - 2
    OW = W_in + 2 * pad - 2
    
    # Number of 2x2 output tiles
    num_tiles_h = (OH + 1) // 2
    num_tiles_w = (OW + 1) // 2
    num_tiles = num_tiles_h * num_tiles_w
    
    # Allocate intermediate buffers
    # V: transformed input [16, N, C, num_tiles]
    # U: transformed filter [16, F_out, C]
    # M: element-wise product [16, N, F_out, num_tiles]
    V_size = 16 * N * C * num_tiles
    U_size = 16 * F_out * C
    M_size = 16 * N * F_out * num_tiles
    
    V = cl.Buffer(ctx, cl.mem_flags.READ_WRITE, size=V_size * 4)
    U = cl.Buffer(ctx, cl.mem_flags.READ_WRITE, size=U_size * 4)
    M = cl.Buffer(ctx, cl.mem_flags.READ_WRITE, size=M_size * 4)
    
    # 1. Transform input
    input_kernel = _build_winograd_input_transform_kernel(ctx, dtype_c)
    total_tiles = N * C * num_tiles_h * num_tiles_w
    gsize = (int(np.ceil(total_tiles / 64)) * 64,)
    input_kernel(q, gsize, (64,),
                 x.buffer, V,
                 np.int32(N), np.int32(C), np.int32(H), np.int32(W_in),
                 np.int32(num_tiles_h), np.int32(num_tiles_w), np.int32(pad))
    
    # 2. Transform filter
    filter_kernel = _build_winograd_filter_transform_kernel(ctx, dtype_c)
    gsize = (int(np.ceil(F_out * C / 64)) * 64,)
    filter_kernel(q, gsize, (64,),
                  w.buffer, U,
                  np.int32(F_out), np.int32(C))
    
    # 3. Batched GEMM
    gemm_kernel = _build_winograd_batched_gemm_kernel(ctx, dtype_c)
    total_gemm = 16 * N * F_out * num_tiles
    gsize = (int(np.ceil(total_gemm / 64)) * 64,)
    gemm_kernel(q, gsize, (64,),
                U, V, M,
                np.int32(F_out), np.int32(C),
                np.int32(N), np.int32(num_tiles))
    
    # 4. Transform output
    out_shape = (N, F_out, OH, OW)
    if out is None:
        out = Tensor.from_shape(q, out_shape, dtype=x.dtype, pool=pool)
    
    output_kernel = _build_winograd_output_transform_kernel(ctx, dtype_c)
    total_out_tiles = N * F_out * num_tiles_h * num_tiles_w
    gsize = (int(np.ceil(total_out_tiles / 64)) * 64,)
    output_kernel(q, gsize, (64,),
                  M, bias.buffer if bias is not None else None,
                  out.buffer,
                  np.int32(N), np.int32(F_out), np.int32(OH), np.int32(OW),
                  np.int32(num_tiles_h), np.int32(num_tiles_w))
    
    # Optional ReLU fuse post-transform
    if fuse_relu:
        from netcl.ops.elementwise import relu

        out = relu(out)
    return out


# ============================================================================
# BACKWARD PASS FOR OPTIMIZED CONV2D
# ============================================================================

def _build_conv2d_backward_data_kernel(ctx: "cl.Context", dtype_c: str = "float"):
    """
    Backward pass for conv2d: compute gradient w.r.t. input.
    grad_x = conv2d_transpose(grad_out, w)
    """
    cache_key = (ctx.int_ptr, "conv2d_backward_data_opt", dtype_c)
    if cache_key in _KERNEL_CACHE:
        return _KERNEL_CACHE[cache_key]
    
    src = f"""
    __kernel void conv2d_backward_data(
        __global const {dtype_c}* grad_out,
        __global const {dtype_c}* w,
        __global {dtype_c}* grad_x,
        const int N, const int C, const int H, const int W,
        const int F, const int KH, const int KW,
        const int OH, const int OW,
        const int stride, const int pad
    ) {{
        int gid = get_global_id(0);
        int total = N * C * H * W;
        if (gid >= total) return;
        
        int iw = gid % W;
        int ih = (gid / W) % H;
        int c = (gid / (H * W)) % C;
        int n = gid / (C * H * W);
        
        {dtype_c} acc = 0;
        
        for (int f = 0; f < F; ++f) {{
            for (int kh = 0; kh < KH; ++kh) {{
                int oh_num = ih + pad - kh;
                if (oh_num < 0 || oh_num % stride != 0) continue;
                int oh = oh_num / stride;
                if (oh < 0 || oh >= OH) continue;
                
                for (int kw = 0; kw < KW; ++kw) {{
                    int ow_num = iw + pad - kw;
                    if (ow_num < 0 || ow_num % stride != 0) continue;
                    int ow = ow_num / stride;
                    if (ow < 0 || ow >= OW) continue;
                    
                    int go_idx = ((n * F + f) * OH + oh) * OW + ow;
                    int w_idx = ((f * C + c) * KH + kh) * KW + kw;
                    acc += grad_out[go_idx] * w[w_idx];
                }}
            }}
        }}
        
        grad_x[gid] = acc;
    }}
    """
    prg = cl.Program(ctx, src).build()
    _KERNEL_CACHE[cache_key] = prg.conv2d_backward_data
    return prg.conv2d_backward_data


def _build_conv2d_backward_filter_kernel(ctx: "cl.Context", dtype_c: str = "float"):
    """
    Backward pass for conv2d: compute gradient w.r.t. weights.
    Implicit GEMM style - no explicit im2col.
    """
    cache_key = (ctx.int_ptr, "conv2d_backward_filter_opt", dtype_c)
    if cache_key in _KERNEL_CACHE:
        return _KERNEL_CACHE[cache_key]
    
    src = f"""
    __kernel void conv2d_backward_filter(
        __global const {dtype_c}* x,
        __global const {dtype_c}* grad_out,
        __global {dtype_c}* grad_w,
        const int N, const int C, const int H, const int W,
        const int F, const int KH, const int KW,
        const int OH, const int OW,
        const int stride, const int pad
    ) {{
        int gid = get_global_id(0);
        int total = F * C * KH * KW;
        if (gid >= total) return;
        
        int kw = gid % KW;
        int kh = (gid / KW) % KH;
        int c = (gid / (KH * KW)) % C;
        int f = gid / (C * KH * KW);
        
        {dtype_c} acc = 0;
        
        for (int n = 0; n < N; ++n) {{
            for (int oh = 0; oh < OH; ++oh) {{
                int ih = oh * stride + kh - pad;
                if (ih < 0 || ih >= H) continue;
                
                for (int ow = 0; ow < OW; ++ow) {{
                    int iw = ow * stride + kw - pad;
                    if (iw < 0 || iw >= W) continue;
                    
                    int x_idx = ((n * C + c) * H + ih) * W + iw;
                    int go_idx = ((n * F + f) * OH + oh) * OW + ow;
                    acc += x[x_idx] * grad_out[go_idx];
                }}
            }}
        }}
        
        grad_w[gid] = acc;
    }}
    """
    prg = cl.Program(ctx, src).build()
    _KERNEL_CACHE[cache_key] = prg.conv2d_backward_filter
    return prg.conv2d_backward_filter


def conv2d_backward_optimized(
    x: Tensor,
    w: Tensor,
    grad_out: Tensor,
    bias: Optional[Tensor] = None,
    stride: int = 1,
    pad: int = 0,
    pool: Optional[BufferPool] = None
) -> Tuple[Tensor, Tensor, Optional[Tensor]]:
    """
    Optimized backward pass for conv2d using implicit GEMM style kernels.
    No host copies - all operations stay on GPU.
    """
    if cl is None or np is None:
        raise ImportError("pyopencl and numpy required")
    
    ctx = x.context
    q = x.queue
    dtype_c = _DTYPE_CNAME.get(x.dtype, "float")
    
    N, C, H, W_in = x.shape
    F, _, KH, KW = w.shape
    _, _, OH, OW = grad_out.shape
    
    # Gradient w.r.t. input
    grad_x = Tensor.from_shape(q, x.shape, dtype=x.dtype, pool=pool)
    data_kernel = _build_conv2d_backward_data_kernel(ctx, dtype_c)
    total_x = N * C * H * W_in
    gsize = (int(np.ceil(total_x / 256)) * 256,)
    data_kernel(q, gsize, (256,),
                grad_out.buffer, w.buffer, grad_x.buffer,
                np.int32(N), np.int32(C), np.int32(H), np.int32(W_in),
                np.int32(F), np.int32(KH), np.int32(KW),
                np.int32(OH), np.int32(OW),
                np.int32(stride), np.int32(pad))
    
    # Gradient w.r.t. weights
    grad_w = Tensor.from_shape(q, w.shape, dtype=w.dtype, pool=pool)
    filter_kernel = _build_conv2d_backward_filter_kernel(ctx, dtype_c)
    total_w = F * C * KH * KW
    gsize = (int(np.ceil(total_w / 256)) * 256,)
    filter_kernel(q, gsize, (256,),
                  x.buffer, grad_out.buffer, grad_w.buffer,
                  np.int32(N), np.int32(C), np.int32(H), np.int32(W_in),
                  np.int32(F), np.int32(KH), np.int32(KW),
                  np.int32(OH), np.int32(OW),
                  np.int32(stride), np.int32(pad))
    
    # Gradient w.r.t. bias (device-side reduce)
    grad_b = None
    if bias is not None:
        grad_b = Tensor.from_shape(q, (F,), dtype="float32", pool=pool)
        bias_kernel = _build_bias_grad_kernel(ctx, dtype_c)
        gsize_b = (int(np.ceil(F / 256)) * 256,)
        bias_kernel(
            q,
            gsize_b,
            (256,),
            grad_out.buffer,
            grad_b.buffer,
            np.int32(N),
            np.int32(F),
            np.int32(OH),
            np.int32(OW),
        )

    return grad_x, grad_w, grad_b


# Export optimized functions
__all__ = [
    'reshape_transpose_device',
    'bias_add_4d_device',
    'conv2d_implicit_gemm',
    'conv2d_tiled_local',
    'conv2d_winograd_f2x2_3x3',
    'conv2d_backward_optimized',
]
