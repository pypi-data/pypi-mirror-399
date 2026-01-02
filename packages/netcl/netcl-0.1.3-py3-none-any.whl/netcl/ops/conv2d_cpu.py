from __future__ import annotations

import numpy as np

from netcl.core.tensor import Tensor


def _im2col_cpu(x: np.ndarray, KH: int, KW: int, stride: int, pad: int):
    """
    Vectorized im2col for NCHW input. Returns (col, OH, OW).
    col shape: (N*OH*OW, C*KH*KW)
    """
    N, C, H, W = x.shape
    H_p = H + 2 * pad
    W_p = W + 2 * pad
    x_padded = np.pad(x, ((0, 0), (0, 0), (pad, pad), (pad, pad)), mode="constant")
    OH = (H_p - KH) // stride + 1
    OW = (W_p - KW) // stride + 1
    sN, sC, sH, sW = x_padded.strides
    windows = np.lib.stride_tricks.as_strided(
        x_padded,
        shape=(N, C, OH, OW, KH, KW),
        strides=(sN, sC, sH * stride, sW * stride, sH, sW),
        writeable=False,
    )
    col = windows.transpose(0, 2, 3, 1, 4, 5).reshape(N * OH * OW, C * KH * KW)
    return col, OH, OW, x_padded


def _col2im_cpu(grad_col: np.ndarray, x_padded_shape: tuple[int, int, int, int], KH: int, KW: int, stride: int, OH: int, OW: int):
    """
    Inverse of im2col for gradients. grad_col shape: (N*OH*OW, C*KH*KW).
    """
    N, C, Hp, Wp = x_padded_shape
    grad_padded = np.zeros((N, C, Hp, Wp), dtype=grad_col.dtype)
    grad_col = grad_col.reshape(N, OH, OW, C, KH, KW).transpose(0, 3, 4, 5, 1, 2)  # N,C,KH,KW,OH,OW
    for kh in range(KH):
        h_slice = slice(kh, kh + stride * OH, stride)
        for kw in range(KW):
            w_slice = slice(kw, kw + stride * OW, stride)
            grad_padded[:, :, h_slice, w_slice] += grad_col[:, :, kh, kw, :, :]
    return grad_padded


def conv2d_cpu(x: Tensor, w: Tensor, bias: Tensor | None = None, stride: int = 1, pad: int = 0) -> Tensor:
    """
    Vectorized conv2d (NCHW) on CPU using im2col + GEMM (leverages NumPy/MKL threading).
    """
    if x.array is None or w.array is None:
        raise ValueError("CPU conv2d requires array storage")
    x_arr = np.ascontiguousarray(x.array)
    w_arr = np.ascontiguousarray(w.array)
    N, C, H, W = x_arr.shape
    F, Cw, KH, KW = w_arr.shape
    if C != Cw:
        raise ValueError("channel mismatch")
    # chunked processing to reduce im2col footprint for large batches
    out = np.empty((N, F, (H + 2 * pad - KH) // stride + 1, (W + 2 * pad - KW) // stride + 1), dtype=x_arr.dtype)
    w_flat = w_arr.reshape(F, C * KH * KW)
    per_img_elems = out.shape[2] * out.shape[3] * C * KH * KW
    bytes_per_val = x_arr.dtype.itemsize
    max_bytes = 128 * 1024 * 1024  # 128MB budget for col buffer
    max_imgs = max(1, int(max_bytes // max(1, per_img_elems * bytes_per_val)))
    chunk = min(N, max_imgs)
    for start in range(0, N, chunk):
        end = min(N, start + chunk)
        col, OH, OW, _ = _im2col_cpu(x_arr[start:end], KH, KW, stride, pad)
        out_flat = col @ w_flat.T  # (chunk*OH*OW, F)
        out_chunk = out_flat.reshape(end - start, OH, OW, F).transpose(0, 3, 1, 2)
        out[start:end] = out_chunk
    if bias is not None:
        if bias.array is None:
            raise ValueError("CPU bias requires array storage")
        out += bias.array.reshape(1, F, 1, 1)
    return Tensor.from_host(x.queue, out, dtype=x.dtype, backend="cpu")


def conv2d_backward_cpu(x: Tensor, w: Tensor, grad_out: Tensor, stride: int = 1, pad: int = 0, bias: Tensor | None = None):
    """
    Vectorized conv2d backward (im2col + GEMM for grad_w, col2im for grad_x).
    """
    if x.array is None or w.array is None or grad_out.array is None:
        raise ValueError("CPU conv2d backward requires array storage")
    x_arr = np.ascontiguousarray(x.array)
    w_arr = np.ascontiguousarray(w.array)
    go = np.ascontiguousarray(grad_out.array)
    N, C, H, W = x_arr.shape
    F, _, KH, KW = w_arr.shape
    # chunked processing to reduce memory footprint
    OH = (H + 2 * pad - KH) // stride + 1
    OW = (W + 2 * pad - KW) // stride + 1
    per_img_elems = OH * OW * C * KH * KW
    bytes_per_val = x_arr.dtype.itemsize
    max_bytes = 128 * 1024 * 1024  # 128MB for col buffer
    max_imgs = max(1, int(max_bytes // max(1, per_img_elems * bytes_per_val)))
    chunk = min(N, max_imgs)

    grad_w = np.zeros_like(w_arr)
    grad_x = np.zeros_like(x_arr)
    grad_b_accum = np.zeros((F,), dtype=w_arr.dtype) if bias is not None else None

    for start in range(0, N, chunk):
        end = min(N, start + chunk)
        col, OHc, OWc, x_padded = _im2col_cpu(x_arr[start:end], KH, KW, stride, pad)
        go_chunk = go[start:end]
        go_reshaped = go_chunk.transpose(0, 2, 3, 1).reshape((end - start) * OHc * OWc, F)

        grad_w += (go_reshaped.T @ col).reshape(F, C, KH, KW)
        grad_col = go_reshaped @ w_arr.reshape(F, C * KH * KW)
        grad_padded = _col2im_cpu(grad_col, x_padded.shape, KH, KW, stride, OHc, OWc)
        grad_x[start:end] = grad_padded[:, :, pad : pad + H, pad : pad + W]

        if grad_b_accum is not None:
            grad_b_accum += go_chunk.sum(axis=(0, 2, 3))

    grad_b_t = None
    if bias is not None:
        if bias.array is None:
            raise ValueError("CPU bias requires array storage")
        grad_b_t = Tensor.from_host(w.queue, grad_b_accum.astype(np.float32), dtype="float32", backend="cpu")

    grad_x_t = Tensor.from_host(x.queue, grad_x, dtype=x.dtype, backend="cpu")
    grad_w_t = Tensor.from_host(w.queue, grad_w, dtype=w.dtype, backend="cpu")
    return grad_x_t, grad_w_t, grad_b_t
