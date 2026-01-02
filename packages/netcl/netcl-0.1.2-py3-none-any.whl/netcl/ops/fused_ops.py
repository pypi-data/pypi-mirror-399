"""
Fused Operations - Conv+BN+ReLU and other fusion patterns for reduced memory traffic.
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
    "float16": "half"
}

_KERNEL_CACHE = {}


def _build_fused_conv_bn_relu_inference_kernel(
    ctx: "cl.Context",
    dtype_c: str = "float",
    tile_size: int = 16
):
    """
    Fused Conv2D + BatchNorm + ReLU for inference.
    BN is folded into: y = gamma * (x - mean) / sqrt(var + eps) + beta
    Which becomes: y = scale * x + bias  where scale = gamma/sqrt(var+eps), bias = beta - mean*scale
    So at inference: output = ReLU(conv(x) * bn_scale + bn_bias)
    """
    cache_key = (ctx.int_ptr, dtype_c, "fused_conv_bn_relu_inf", tile_size)
    if cache_key in _KERNEL_CACHE:
        return _KERNEL_CACHE[cache_key]
    
    src = f"""
    #define TILE {tile_size}
    
    // Fused Conv2D + BN (pre-folded scale/bias) + ReLU
    // For inference, BN is folded: y = relu(scale * conv_out + bias)
    __kernel void fused_conv_bn_relu(
        __global const {dtype_c}* input,     // [N, C_in, H, W]
        __global const {dtype_c}* weight,    // [C_out, C_in, KH, KW]
        __global const {dtype_c}* bn_scale,  // [C_out] - pre-folded gamma/sqrt(var+eps)
        __global const {dtype_c}* bn_bias,   // [C_out] - pre-folded beta - mean*scale
        __global {dtype_c}* output,          // [N, C_out, H_out, W_out]
        const int N, const int C_in, const int H, const int W,
        const int C_out, const int KH, const int KW,
        const int H_out, const int W_out,
        const int stride, const int pad
    ) {{
        // Global position
        int out_w = get_global_id(0);
        int out_h = get_global_id(1);
        int nc = get_global_id(2);  // combined N*C_out
        
        int n = nc / C_out;
        int c_out = nc % C_out;
        
        if (out_w >= W_out || out_h >= H_out || n >= N) return;
        
        {dtype_c} sum = 0;
        
        // Convolution
        for (int c_in = 0; c_in < C_in; ++c_in) {{
            for (int kh = 0; kh < KH; ++kh) {{
                for (int kw = 0; kw < KW; ++kw) {{
                    int in_h = out_h * stride + kh - pad;
                    int in_w = out_w * stride + kw - pad;
                    
                    if (in_h >= 0 && in_h < H && in_w >= 0 && in_w < W) {{
                        int in_idx = ((n * C_in + c_in) * H + in_h) * W + in_w;
                        int w_idx = ((c_out * C_in + c_in) * KH + kh) * KW + kw;
                        sum += input[in_idx] * weight[w_idx];
                    }}
                }}
            }}
        }}
        
        // Fused BN (pre-folded) + ReLU
        {dtype_c} scaled = sum * bn_scale[c_out] + bn_bias[c_out];
        {dtype_c} result = scaled > 0 ? scaled : 0;
        
        int out_idx = ((n * C_out + c_out) * H_out + out_h) * W_out + out_w;
        output[out_idx] = result;
    }}
    
    // Fused Conv2D + Bias + ReLU (no BN, just bias)
    __kernel void fused_conv_bias_relu(
        __global const {dtype_c}* input,
        __global const {dtype_c}* weight,
        __global const {dtype_c}* bias,
        __global {dtype_c}* output,
        const int N, const int C_in, const int H, const int W,
        const int C_out, const int KH, const int KW,
        const int H_out, const int W_out,
        const int stride, const int pad
    ) {{
        int out_w = get_global_id(0);
        int out_h = get_global_id(1);
        int nc = get_global_id(2);
        
        int n = nc / C_out;
        int c_out = nc % C_out;
        
        if (out_w >= W_out || out_h >= H_out || n >= N) return;
        
        {dtype_c} sum = bias[c_out];
        
        for (int c_in = 0; c_in < C_in; ++c_in) {{
            for (int kh = 0; kh < KH; ++kh) {{
                for (int kw = 0; kw < KW; ++kw) {{
                    int in_h = out_h * stride + kh - pad;
                    int in_w = out_w * stride + kw - pad;
                    
                    if (in_h >= 0 && in_h < H && in_w >= 0 && in_w < W) {{
                        int in_idx = ((n * C_in + c_in) * H + in_h) * W + in_w;
                        int w_idx = ((c_out * C_in + c_in) * KH + kh) * KW + kw;
                        sum += input[in_idx] * weight[w_idx];
                    }}
                }}
            }}
        }}
        
        output[((n * C_out + c_out) * H_out + out_h) * W_out + out_w] = sum > 0 ? sum : 0;
    }}
    """
    
    prg = cl.Program(ctx, src).build()
    _KERNEL_CACHE[cache_key] = prg
    return prg


def _build_fused_linear_bn_relu_kernel(ctx: "cl.Context", dtype_c: str = "float"):
    """Fused Linear + BN + ReLU for FC layers."""
    cache_key = (ctx.int_ptr, dtype_c, "fused_linear_bn_relu")
    if cache_key in _KERNEL_CACHE:
        return _KERNEL_CACHE[cache_key]
    
    src = f"""
    __kernel void fused_linear_bn_relu(
        __global const {dtype_c}* input,     // [N, in_features]
        __global const {dtype_c}* weight,    // [out_features, in_features]
        __global const {dtype_c}* bn_scale,  // [out_features]
        __global const {dtype_c}* bn_bias,   // [out_features]
        __global {dtype_c}* output,          // [N, out_features]
        const int N, const int in_features, const int out_features
    ) {{
        int n = get_global_id(0);
        int out_f = get_global_id(1);
        
        if (n >= N || out_f >= out_features) return;
        
        {dtype_c} sum = 0;
        for (int i = 0; i < in_features; ++i) {{
            sum += input[n * in_features + i] * weight[out_f * in_features + i];
        }}
        
        {dtype_c} scaled = sum * bn_scale[out_f] + bn_bias[out_f];
        output[n * out_features + out_f] = scaled > 0 ? scaled : 0;
    }}
    
    __kernel void fused_linear_bias_relu(
        __global const {dtype_c}* input,
        __global const {dtype_c}* weight,
        __global const {dtype_c}* bias,
        __global {dtype_c}* output,
        const int N, const int in_features, const int out_features
    ) {{
        int n = get_global_id(0);
        int out_f = get_global_id(1);
        
        if (n >= N || out_f >= out_features) return;
        
        {dtype_c} sum = bias[out_f];
        for (int i = 0; i < in_features; ++i) {{
            sum += input[n * in_features + i] * weight[out_f * in_features + i];
        }}
        
        output[n * out_features + out_f] = sum > 0 ? sum : 0;
    }}
    """
    
    prg = cl.Program(ctx, src).build()
    _KERNEL_CACHE[cache_key] = prg
    return prg


def fold_bn_params(
    gamma: Tensor,
    beta: Tensor,
    running_mean: Tensor,
    running_var: Tensor,
    eps: float = 1e-5
) -> Tuple[Tensor, Tensor]:
    """
    Fold BatchNorm parameters for inference fusion.
    Returns (scale, bias) where: y = scale * x + bias
    
    scale = gamma / sqrt(var + eps)
    bias = beta - mean * scale
    """
    if np is None:
        raise ImportError("numpy required")
    
    # Get arrays
    gamma_arr = gamma.to_host() if hasattr(gamma, 'to_host') else gamma.array
    beta_arr = beta.to_host() if hasattr(beta, 'to_host') else beta.array
    mean_arr = running_mean.to_host() if hasattr(running_mean, 'to_host') else running_mean.array
    var_arr = running_var.to_host() if hasattr(running_var, 'to_host') else running_var.array
    
    # Compute folded params
    std = np.sqrt(var_arr + eps)
    scale_arr = gamma_arr / std
    bias_arr = beta_arr - mean_arr * scale_arr
    
    # Create tensors
    q = gamma.queue
    scale = Tensor.from_host(q, scale_arr.astype(np.float32), dtype=gamma.dtype)
    bias = Tensor.from_host(q, bias_arr.astype(np.float32), dtype=beta.dtype)
    
    return scale, bias


def fused_conv_bn_relu_inference(
    input: Tensor,
    weight: Tensor,
    bn_scale: Tensor,
    bn_bias: Tensor,
    stride: int = 1,
    padding: int = 0,
    out: Optional[Tensor] = None,
    pool: Optional[BufferPool] = None
) -> Tensor:
    """
    Fused Conv2D + BatchNorm + ReLU for inference.
    BN params should be pre-folded using fold_bn_params().
    """
    if cl is None or np is None:
        raise ImportError("pyopencl and numpy required")
    
    if len(input.shape) != 4 or len(weight.shape) != 4:
        raise ValueError("Expected 4D input and weight tensors")
    
    N, C_in, H, W = input.shape
    C_out, C_in_w, KH, KW = weight.shape
    
    if C_in != C_in_w:
        raise ValueError("Channel mismatch")
    
    H_out = (H + 2 * padding - KH) // stride + 1
    W_out = (W + 2 * padding - KW) // stride + 1
    
    ctx = input.context
    q = input.queue
    dtype_c = _DTYPE_CNAME.get(input.dtype, "float")
    
    if out is None:
        out = Tensor.from_shape(q, (N, C_out, H_out, W_out), dtype=input.dtype, pool=pool)
    
    prg = _build_fused_conv_bn_relu_inference_kernel(ctx, dtype_c)
    
    global_size = (
        int(np.ceil(W_out / 16) * 16),
        int(np.ceil(H_out / 16) * 16),
        N * C_out
    )
    local_size = (16, 16, 1)
    
    prg.fused_conv_bn_relu(
        q, global_size, local_size,
        input.buffer, weight.buffer, bn_scale.buffer, bn_bias.buffer, out.buffer,
        np.int32(N), np.int32(C_in), np.int32(H), np.int32(W),
        np.int32(C_out), np.int32(KH), np.int32(KW),
        np.int32(H_out), np.int32(W_out),
        np.int32(stride), np.int32(padding)
    )
    
    return out


def fused_conv_bias_relu(
    input: Tensor,
    weight: Tensor,
    bias: Tensor,
    stride: int = 1,
    padding: int = 0,
    out: Optional[Tensor] = None,
    pool: Optional[BufferPool] = None
) -> Tensor:
    """
    Fused Conv2D + Bias + ReLU.
    """
    if cl is None or np is None:
        raise ImportError("pyopencl and numpy required")
    
    if len(input.shape) != 4 or len(weight.shape) != 4:
        raise ValueError("Expected 4D input and weight tensors")
    
    N, C_in, H, W = input.shape
    C_out, C_in_w, KH, KW = weight.shape
    
    if C_in != C_in_w:
        raise ValueError("Channel mismatch")
    if bias.shape[0] != C_out:
        raise ValueError("Bias shape mismatch")
    
    H_out = (H + 2 * padding - KH) // stride + 1
    W_out = (W + 2 * padding - KW) // stride + 1
    
    ctx = input.context
    q = input.queue
    dtype_c = _DTYPE_CNAME.get(input.dtype, "float")
    
    if out is None:
        out = Tensor.from_shape(q, (N, C_out, H_out, W_out), dtype=input.dtype, pool=pool)
    
    prg = _build_fused_conv_bn_relu_inference_kernel(ctx, dtype_c)
    
    global_size = (
        int(np.ceil(W_out / 16) * 16),
        int(np.ceil(H_out / 16) * 16),
        N * C_out
    )
    local_size = (16, 16, 1)
    
    prg.fused_conv_bias_relu(
        q, global_size, local_size,
        input.buffer, weight.buffer, bias.buffer, out.buffer,
        np.int32(N), np.int32(C_in), np.int32(H), np.int32(W),
        np.int32(C_out), np.int32(KH), np.int32(KW),
        np.int32(H_out), np.int32(W_out),
        np.int32(stride), np.int32(padding)
    )
    
    return out


def fused_linear_bias_relu(
    input: Tensor,
    weight: Tensor,
    bias: Tensor,
    out: Optional[Tensor] = None,
    pool: Optional[BufferPool] = None
) -> Tensor:
    """
    Fused Linear + Bias + ReLU.
    """
    if cl is None or np is None:
        raise ImportError("pyopencl and numpy required")
    
    if len(input.shape) != 2 or len(weight.shape) != 2:
        raise ValueError("Expected 2D input and weight tensors")
    
    N, in_features = input.shape
    out_features, in_f_w = weight.shape
    
    if in_features != in_f_w:
        raise ValueError("Feature dimension mismatch")
    if bias.shape[0] != out_features:
        raise ValueError("Bias shape mismatch")
    
    ctx = input.context
    q = input.queue
    dtype_c = _DTYPE_CNAME.get(input.dtype, "float")
    
    if out is None:
        out = Tensor.from_shape(q, (N, out_features), dtype=input.dtype, pool=pool)
    
    prg = _build_fused_linear_bn_relu_kernel(ctx, dtype_c)
    
    global_size = (
        int(np.ceil(N / 16) * 16),
        int(np.ceil(out_features / 16) * 16)
    )
    local_size = (16, 16)
    
    prg.fused_linear_bias_relu(
        q, global_size, local_size,
        input.buffer, weight.buffer, bias.buffer, out.buffer,
        np.int32(N), np.int32(in_features), np.int32(out_features)
    )
    
    return out


__all__ = [
    'fold_bn_params',
    'fused_conv_bn_relu_inference',
    'fused_conv_bias_relu',
    'fused_linear_bias_relu',
]
