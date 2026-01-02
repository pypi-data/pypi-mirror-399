from __future__ import annotations

from netcl.core.tensor import Tensor
from netcl.core.backend import get_backend
import numpy as np
import pyopencl as cl  # type: ignore


_DTYPE_CNAME = {"float32": "float", "float": "float"}
_POOL_PROG_CACHE = {}


def _pool2d_windows_cpu(x_arr: np.ndarray, kernel_size: int, stride: int, out_h: int, out_w: int) -> np.ndarray:
    """
    Create a strided view over the input with shape (N, C, OH, OW, KH, KW) for vectorized pooling.
    """
    sN, sC, sH, sW = x_arr.strides
    return np.lib.stride_tricks.as_strided(
        x_arr,
        shape=(x_arr.shape[0], x_arr.shape[1], out_h, out_w, kernel_size, kernel_size),
        strides=(sN, sC, sH * stride, sW * stride, sH, sW),
        writeable=False,
    )


def max_pool2d(x: Tensor, kernel_size: int = 2, stride: int = 2) -> Tensor:
    """
    Simple NCHW max-pool (no padding). Assumes stride == kernel_size for non-overlap.
    """
    backend = get_backend(x)
    N, C, H, W = x.shape
    out_h = (H - kernel_size) // stride + 1
    out_w = (W - kernel_size) // stride + 1
    if backend == "cpu":
        if np is None:
            raise ImportError("numpy required for CPU max_pool2d")
        x_arr = x.array
        if x_arr is None:
            raise ValueError("CPU tensors require array storage")
        x_arr = np.ascontiguousarray(x_arr)
        windows = _pool2d_windows_cpu(x_arr, kernel_size, stride, out_h, out_w)
        out_arr = windows.max(axis=(4, 5))
        return Tensor.from_host(x.queue, out_arr, dtype=x.dtype, backend="cpu")
    ctx = x.context
    dtype_c = _DTYPE_CNAME.get(x.dtype)
    if dtype_c is None:
        raise ValueError(f"unsupported dtype {x.dtype} for max_pool2d")
    cache_key = (ctx.int_ptr, "max_fwd", dtype_c)
    if cache_key in _POOL_PROG_CACHE:
        program = _POOL_PROG_CACHE[cache_key]
    else:
        ksrc = f"""
    __kernel void max_pool2d(__global const {dtype_c}* x, __global {dtype_c}* out,
                             const int N, const int C, const int H, const int W,
                             const int KH, const int KW, const int stride, const int OH, const int OW) {{
        int gid = get_global_id(0);
        int total = N * C * OH * OW;
        if (gid >= total) return;
        int ow = gid % OW;
        int oh = (gid / OW) % OH;
        int c = (gid / (OH * OW)) % C;
        int n = gid / (C * OH * OW);
        int hstart = oh * stride;
        int wstart = ow * stride;
        {dtype_c} m = x[((n*C + c)*H + hstart)*W + wstart];
        for (int kh = 0; kh < KH; ++kh) {{
            for (int kw = 0; kw < KW; ++kw) {{
                int ih = hstart + kh;
                int iw = wstart + kw;
                int idx = ((n*C + c)*H + ih)*W + iw;
                {dtype_c} v = x[idx];
                if (v > m) m = v;
            }}
        }}
        out[gid] = m;
    }}
    """
        program = cl.Program(ctx, ksrc).build()
        _POOL_PROG_CACHE[cache_key] = program
    kernel = program.max_pool2d
    out = Tensor.from_shape(x.queue, (N, C, out_h, out_w), dtype=x.dtype)
    total = N * C * out_h * out_w
    gsize = (int(np.ceil(total / 256.0)) * 256,)
    kernel(x.queue, gsize, (256,), x.buffer, out.buffer, np.int32(N), np.int32(C), np.int32(H), np.int32(W), np.int32(kernel_size), np.int32(kernel_size), np.int32(stride), np.int32(out_h), np.int32(out_w))
    return out


def max_pool2d_backward(x: Tensor, grad_out: Tensor, kernel_size: int = 2, stride: int = 2) -> Tensor:
    """
    Backward for max-pool. Assumes stride == kernel_size (non-overlapping windows).
    """
    backend = get_backend(x)
    N, C, H, W = x.shape
    _, _, OH, OW = grad_out.shape
    if stride != kernel_size:
        raise ValueError("max_pool2d_backward assumes stride == kernel_size (non-overlap)")
    if backend == "cpu":
        if np is None:
            raise ImportError("numpy required for CPU max_pool2d_backward")
        x_arr = x.array
        go_arr = grad_out.array
        if x_arr is None or go_arr is None:
            raise ValueError("CPU tensors require array storage")
        x_arr = np.ascontiguousarray(x_arr)
        go_arr = np.ascontiguousarray(go_arr)
        windows = _pool2d_windows_cpu(x_arr, kernel_size, stride, OH, OW)
        flat = windows.reshape(N, C, OH, OW, -1)
        idx = flat.argmax(axis=-1)
        h_offsets = idx // kernel_size
        w_offsets = idx % kernel_size
        h_base = (np.arange(OH) * stride).reshape(1, 1, OH, 1)
        w_base = (np.arange(OW) * stride).reshape(1, 1, 1, OW)
        h_pos = h_offsets + h_base
        w_pos = w_offsets + w_base
        grad_in = np.zeros_like(x_arr)
        n_idx = np.arange(N).reshape(N, 1, 1, 1)
        c_idx = np.arange(C).reshape(1, C, 1, 1)
        np.add.at(grad_in, (n_idx, c_idx, h_pos, w_pos), go_arr)
        return Tensor.from_host(x.queue, grad_in, dtype=x.dtype, backend="cpu")
    ctx = x.context
    dtype_c = _DTYPE_CNAME.get(x.dtype)
    if dtype_c is None:
        raise ValueError(f"unsupported dtype {x.dtype}")
    cache_key = (ctx.int_ptr, "max_bwd", dtype_c)
    if cache_key in _POOL_PROG_CACHE:
        prg = _POOL_PROG_CACHE[cache_key]
    else:
        ksrc = f"""
    __kernel void max_pool2d_bwd(__global const {dtype_c}* x, __global const {dtype_c}* grad_out, __global {dtype_c}* grad_in,
                                 const int N, const int C, const int H, const int W,
                                 const int KH, const int KW, const int OH, const int OW, const int stride) {{
        int gid = get_global_id(0);
        int total = N * C * OH * OW;
        if (gid >= total) return;
        int ow = gid % OW;
        int oh = (gid / OW) % OH;
        int c = (gid / (OH * OW)) % C;
        int n = gid / (C * OH * OW);
        int hstart = oh * stride;
        int wstart = ow * stride;
        {dtype_c} maxv = x[((n*C + c)*H + hstart)*W + wstart];
        int max_h = hstart;
        int max_w = wstart;
        for (int kh = 0; kh < KH; ++kh) {{
            for (int kw = 0; kw < KW; ++kw) {{
                int ih = hstart + kh;
                int iw = wstart + kw;
                int idx = ((n*C + c)*H + ih)*W + iw;
                {dtype_c} v = x[idx];
                if (v > maxv) {{
                    maxv = v;
                    max_h = ih;
                    max_w = iw;
                }}
            }}
        }}
        int out_idx = ((n*C + c)*OH + oh)*OW + ow;
        int in_idx = ((n*C + c)*H + max_h)*W + max_w;
        grad_in[in_idx] = grad_out[out_idx];
    }}
    """
        prg = cl.Program(ctx, ksrc).build()
        _POOL_PROG_CACHE[cache_key] = prg
    kernel = prg.max_pool2d_bwd
    grad_in = Tensor.from_shape(x.queue, x.shape, dtype=x.dtype)
    cl.enqueue_fill_buffer(x.queue, grad_in.buffer, np.float32(0), 0, grad_in.buffer.size)  # type: ignore
    total = N * C * OH * OW
    gsize = (int(np.ceil(total / 256.0)) * 256,)
    kernel(
        x.queue,
        gsize,
        (256,),
        x.buffer,
        grad_out.buffer,
        grad_in.buffer,
        np.int32(N),
        np.int32(C),
        np.int32(H),
        np.int32(W),
        np.int32(kernel_size),
        np.int32(kernel_size),
        np.int32(OH),
        np.int32(OW),
        np.int32(stride),
    )
    return grad_in


def avg_pool2d(x: Tensor, kernel_size: int = 2, stride: int = 2) -> Tensor:
    """
    Average pool NCHW. No padding. Assumes stride >= 1.
    """
    backend = get_backend(x)
    N, C, H, W = x.shape
    out_h = (H - kernel_size) // stride + 1
    out_w = (W - kernel_size) // stride + 1
    if backend == "cpu":
        if np is None:
            raise ImportError("numpy required for CPU avg_pool2d")
        x_arr = x.array
        if x_arr is None:
            raise ValueError("CPU tensors require array storage")
        x_arr = np.ascontiguousarray(x_arr)
        windows = _pool2d_windows_cpu(x_arr, kernel_size, stride, out_h, out_w)
        out_arr = windows.mean(axis=(4, 5), dtype=x_arr.dtype)
        return Tensor.from_host(x.queue, out_arr, dtype=x.dtype, backend="cpu")
    ctx = x.context
    dtype_c = _DTYPE_CNAME.get(x.dtype)
    if dtype_c is None:
        raise ValueError(f"unsupported dtype {x.dtype} for avg_pool2d")
    cache_key = (ctx.int_ptr, "avg_fwd", dtype_c)
    if cache_key in _POOL_PROG_CACHE:
        prg = _POOL_PROG_CACHE[cache_key]
    else:
        ksrc = f"""
    __kernel void avg_pool2d(__global const {dtype_c}* x, __global {dtype_c}* out,
                             const int N, const int C, const int H, const int W,
                             const int KH, const int KW, const int stride, const int OH, const int OW) {{
        int gid = get_global_id(0);
        int total = N * C * OH * OW;
        if (gid >= total) return;
        int ow = gid % OW;
        int oh = (gid / OW) % OH;
        int c = (gid / (OH * OW)) % C;
        int n = gid / (C * OH * OW);
        int hstart = oh * stride;
        int wstart = ow * stride;
        float acc = 0.0f;
        for (int kh = 0; kh < KH; ++kh) {{
            for (int kw = 0; kw < KW; ++kw) {{
                int ih = hstart + kh;
                int iw = wstart + kw;
                int idx = ((n*C + c)*H + ih)*W + iw;
                acc += x[idx];
            }}
        }}
        out[gid] = acc / (KH * KW);
    }}
    """
        prg = cl.Program(ctx, ksrc).build()
        _POOL_PROG_CACHE[cache_key] = prg
    kernel = prg.avg_pool2d
    out = Tensor.from_shape(x.queue, (N, C, out_h, out_w), dtype=x.dtype)
    total = N * C * out_h * out_w
    gsize = (int(np.ceil(total / 256.0)) * 256,)
    kernel(x.queue, gsize, (256,), x.buffer, out.buffer, np.int32(N), np.int32(C), np.int32(H), np.int32(W), np.int32(kernel_size), np.int32(kernel_size), np.int32(stride), np.int32(out_h), np.int32(out_w))
    return out


def avg_pool2d_backward(x: Tensor, grad_out: Tensor, kernel_size: int = 2, stride: int = 2) -> Tensor:
    """
    Backward for average pool. Distributes grad_out equally to contributing inputs.
    """
    backend = get_backend(x)
    N, C, H, W = x.shape
    _, _, OH, OW = grad_out.shape
    if backend == "cpu":
        if np is None:
            raise ImportError("numpy required for CPU avg_pool2d_backward")
        x_arr = x.array
        go_arr = grad_out.array
        if x_arr is None or go_arr is None:
            raise ValueError("CPU tensors require array storage")
        x_arr = np.ascontiguousarray(x_arr)
        go_arr = np.ascontiguousarray(go_arr)
        grad_in = np.zeros_like(x_arr)
        scale = np.array(1.0 / (kernel_size * kernel_size), dtype=go_arr.dtype)
        h_coords, w_coords, kh_coords, kw_coords = np.indices((OH, OW, kernel_size, kernel_size))
        h_coords = h_coords * stride + kh_coords
        w_coords = w_coords * stride + kw_coords
        n_idx = np.arange(N).reshape(N, 1, 1, 1, 1, 1)
        c_idx = np.arange(C).reshape(1, C, 1, 1, 1, 1)
        go_expanded = go_arr[:, :, :, :, None, None] * scale
        np.add.at(grad_in, (n_idx, c_idx, h_coords[None, None, ...], w_coords[None, None, ...]), go_expanded)
        return Tensor.from_host(x.queue, grad_in, dtype=x.dtype, backend="cpu")
    ctx = x.context
    dtype_c = _DTYPE_CNAME.get(x.dtype)
    if dtype_c is None:
        raise ValueError(f"unsupported dtype {x.dtype}")
    cache_key = (ctx.int_ptr, "avg_bwd", dtype_c)
    if cache_key in _POOL_PROG_CACHE:
        prg = _POOL_PROG_CACHE[cache_key]
    else:
        ksrc = f"""
    __kernel void avg_pool2d_bwd(__global const {dtype_c}* grad_out, __global {dtype_c}* grad_in,
                                 const int N, const int C, const int H, const int W,
                                 const int KH, const int KW, const int OH, const int OW, const int stride) {{
        int gid = get_global_id(0);
        int total = N * C * H * W;
        if (gid >= total) return;
        int wcoord = gid % W;
        int hcoord = (gid / W) % H;
        int c = (gid / (H * W)) % C;
        int n = gid / (C * H * W);
        float acc = 0.0f;
        for (int oh = 0; oh < OH; ++oh) {{
            int hstart = oh * stride;
            if (hcoord < hstart || hcoord >= hstart + KH) continue;
            for (int ow = 0; ow < OW; ++ow) {{
                int wstart = ow * stride;
                if (wcoord < wstart || wcoord >= wstart + KW) continue;
                int out_idx = ((n*C + c)*OH + oh)*OW + ow;
                acc += grad_out[out_idx] / (KH * KW);
            }}
        }}
        grad_in[gid] = acc;
    }}
    """
        prg = cl.Program(ctx, ksrc).build()
        _POOL_PROG_CACHE[cache_key] = prg
    kernel = prg.avg_pool2d_bwd
    grad_in = Tensor.from_shape(x.queue, x.shape, dtype=x.dtype)
    cl.enqueue_fill_buffer(x.queue, grad_in.buffer, np.float32(0), 0, grad_in.buffer.size)  # type: ignore
    total = N * C * H * W
    gsize = (int(np.ceil(total / 256.0)) * 256,)
    kernel(
        x.queue,
        gsize,
        (256,),
        grad_out.buffer,
        grad_in.buffer,
        np.int32(N),
        np.int32(C),
        np.int32(H),
        np.int32(W),
        np.int32(kernel_size),
        np.int32(kernel_size),
        np.int32(grad_out.shape[2]),
        np.int32(grad_out.shape[3]),
        np.int32(stride),
    )
    return grad_in


def global_avg_pool2d(x: Tensor) -> Tensor:
    """
    Global average over H,W -> output N x C x 1 x 1
    """
    backend = get_backend(x)
    N, C, H, W = x.shape
    if backend == "cpu":
        if np is None:
            raise ImportError("numpy required for CPU global_avg_pool2d")
        arr = x.array
        if arr is None:
            raise ValueError("CPU tensors require array storage")
        out_arr = arr.mean(axis=(2, 3), keepdims=True)
        return Tensor.from_host(x.queue, out_arr.astype(arr.dtype), dtype=x.dtype, backend="cpu")
    ctx = x.context
    dtype_c = _DTYPE_CNAME.get(x.dtype)
    if dtype_c is None:
        raise ValueError(f"unsupported dtype {x.dtype}")
    ksrc = f"""
    __kernel void gap2d(__global const {dtype_c}* x, __global {dtype_c}* out,
                        const int N, const int C, const int H, const int W) {{
        int gid = get_global_id(0);
        int c = gid % C;
        int n = gid / C;
        if (n >= N) return;
        float acc = 0.0f;
        for (int h = 0; h < H; ++h) {{
            for (int w = 0; w < W; ++w) {{
                int idx = ((n*C + c)*H + h)*W + w;
                acc += x[idx];
            }}
        }}
        out[gid] = acc / (H * W);
    }}
    """
    prg = cl.Program(ctx, ksrc).build()
    kernel = prg.gap2d
    out = Tensor.from_shape(x.queue, (N, C, 1, 1), dtype=x.dtype)
    total = N * C
    gsize = (int(np.ceil(total / 256.0)) * 256,)
    kernel(x.queue, gsize, (256,), x.buffer, out.buffer, np.int32(N), np.int32(C), np.int32(H), np.int32(W))
    return out


def global_avg_pool2d_backward(x: Tensor, grad_out: Tensor) -> Tensor:
    """
    Backward for global average pooling (N,C,1,1) -> (N,C,H,W).
    """
    backend = get_backend(x)
    N, C, H, W = x.shape
    if grad_out.shape != (N, C, 1, 1):
        raise ValueError(f"grad_out must be {(N, C, 1, 1)}, got {grad_out.shape}")
    if backend == "cpu":
        if np is None:
            raise ImportError("numpy required for CPU global_avg_pool2d_backward")
        go = grad_out.array
        if go is None:
            raise ValueError("CPU tensors require array storage")
        grad_in = np.broadcast_to(go, (N, C, H, W)).astype(go.dtype) / float(H * W)
        return Tensor.from_host(x.queue, grad_in, dtype=x.dtype, backend="cpu")
    if cl is None:
        raise ImportError("pyopencl required for global_avg_pool2d_backward")
    dtype_c = _DTYPE_CNAME.get(x.dtype)
    if dtype_c is None:
        raise ValueError(f"unsupported dtype {x.dtype}")
    ctx = x.context
    ksrc = f"""
    __kernel void gap2d_bwd(__global const {dtype_c}* go, __global {dtype_c}* gx,
                            const int N, const int C, const int H, const int W) {{
        int gid = get_global_id(0);
        int total = N * C * H * W;
        if (gid >= total) return;
        int w = gid % W;
        int h = (gid / W) % H;
        int c = (gid / (H*W)) % C;
        int n = gid / (C*H*W);
        int go_idx = n * C + c;
        gx[gid] = go[go_idx] / (H * W);
    }}
    """
    program = cl.Program(ctx, ksrc).build()
    kernel = program.gap2d_bwd
    grad_in = Tensor.from_shape(x.queue, x.shape, dtype=x.dtype)
    total = N * C * H * W
    gsize = (int(np.ceil(total / 256.0)) * 256,)
    kernel(x.queue, gsize, (256,), grad_out.buffer, grad_in.buffer, np.int32(N), np.int32(C), np.int32(H), np.int32(W))
    return grad_in
