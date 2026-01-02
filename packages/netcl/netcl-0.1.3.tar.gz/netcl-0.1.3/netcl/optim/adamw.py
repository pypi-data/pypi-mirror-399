from __future__ import annotations

from typing import Iterable

import numpy as np
import pyopencl as cl

from netcl.core.tensor import Tensor
from netcl.amp import master_param


class AdamW:
    def __init__(
        self,
        params: Iterable[Tensor],
        lr: float = 1e-3,
        betas=(0.9, 0.999),
        eps: float = 1e-8,
        weight_decay: float = 0.01,
    ):
        self.params = [master_param(p) for p in params]
        self.lr = lr
        if len(betas) != 2:
            raise ValueError("betas must be a tuple of (beta1, beta2)")
        self.beta1, self.beta2 = betas
        if eps <= 0:
            raise ValueError("eps must be positive")
        self.eps = eps
        self.weight_decay = weight_decay
        self.m = {id(p): np.zeros(p.shape, dtype=np.float32) for p in self.params}
        self.v = {id(p): np.zeros(p.shape, dtype=np.float32) for p in self.params}
        self._m_buf = {}
        self._v_buf = {}
        self._adam_kernel = {}
        self._cast16_kernel = {}
        self.t = 0

    def zero_grad(self):
        for p in self.params:
            p.grad = None

    def step(self):
        self.t += 1
        for p in self.params:
            if p.grad is None:
                continue
            backend = getattr(p, "backend", "cl")
            if backend == "cpu":
                if p.array is None or p.grad.array is None:
                    raise ValueError("CPU parameters require array storage")
                g = p.grad.array
                if self.weight_decay != 0.0:
                    p.array[...] = p.array - self.lr * self.weight_decay * p.array
                pid = id(p)
                m = self.m[pid] = self.beta1 * self.m[pid] + (1 - self.beta1) * g
                v = self.v[pid] = self.beta2 * self.v[pid] + (1 - self.beta2) * (g * g)
                m_hat = m / (1 - self.beta1**self.t)
                v_hat = v / (1 - self.beta2**self.t)
                p.array[...] = p.array - self.lr * m_hat / (np.sqrt(v_hat) + self.eps)
                model_p = getattr(p, "_model_param", p)
                if model_p is not p and getattr(model_p, "array", None) is not None:
                    model_p.array[...] = model_p.array - self.lr * m_hat.astype(model_p.array.dtype) / (np.sqrt(v_hat) + self.eps)
                continue
            ctx = p.context
            if ctx is None:
                raise ValueError("CL backend requires a context")
            pid = id(p)
            n = p.size
            # lazily allocate device m/v buffers
            if pid not in self._m_buf:
                mf = cl.mem_flags
                self._m_buf[pid] = cl.Buffer(ctx, mf.READ_WRITE, n * 4)
                self._v_buf[pid] = cl.Buffer(ctx, mf.READ_WRITE, n * 4)
                cl.enqueue_fill_buffer(p.queue, self._m_buf[pid], np.float32(0), 0, n * 4)  # type: ignore
                cl.enqueue_fill_buffer(p.queue, self._v_buf[pid], np.float32(0), 0, n * 4)  # type: ignore
            # build/update kernels per context
            kkey = ctx.int_ptr
            if kkey not in self._adam_kernel:
                ksrc = """
                __kernel void adamw(
                    __global float* p,
                    __global const float* g,
                    __global float* m,
                    __global float* v,
                    const float lr,
                    const float beta1,
                    const float beta2,
                    const float eps,
                    const float weight_decay,
                    const float bc1,
                    const float bc2,
                    const int n) {
                    int gid = get_global_id(0);
                    if (gid >= n) return;
                    float grad = g[gid];
                    float m_new = mad(beta1, m[gid], (1.0f - beta1) * grad);
                    float v_new = mad(beta2, v[gid], (1.0f - beta2) * grad * grad);
                    m[gid] = m_new;
                    v[gid] = v_new;
                    float m_hat = m_new / bc1;
                    float v_hat = v_new / bc2;
                    float upd = m_hat / (sqrt(v_hat) + eps);
                    float val = p[gid];
                    if (weight_decay != 0.0f) {
                        val -= lr * weight_decay * val;
                    }
                    val -= lr * upd;
                    p[gid] = val;
                }
                """
                self._adam_kernel[kkey] = cl.Program(ctx, ksrc).build().adamw
            # optional fp32->fp16 cast kernel
            cast_kernel = None
            model_p = getattr(p, "_model_param", p)
            if model_p is not p and model_p.dtype in ("half", "float16"):
                if kkey not in self._cast16_kernel:
                    ksrc_cast = """
                    #pragma OPENCL EXTENSION cl_khr_fp16 : enable
                    __kernel void cast_fp32_to_fp16(__global const float* src, __global half* dst, const int n) {
                        int gid = get_global_id(0);
                        if (gid >= n) return;
                        dst[gid] = (half)(src[gid]);
                    }
                    """
                    try:
                        self._cast16_kernel[kkey] = cl.Program(ctx, ksrc_cast).build().cast_fp32_to_fp16
                    except Exception:
                        self._cast16_kernel[kkey] = None
                cast_kernel = self._cast16_kernel.get(kkey)

            beta1 = np.float32(self.beta1)
            beta2 = np.float32(self.beta2)
            lr = np.float32(self.lr)
            eps = np.float32(self.eps)
            wd = np.float32(self.weight_decay)
            bc1 = np.float32(1.0 - self.beta1 ** self.t)
            bc2 = np.float32(1.0 - self.beta2 ** self.t)
            g_buf = getattr(p.grad, "buffer", None)
            if g_buf is None:
                raise ValueError("Gradient missing device buffer for CL backend")
            kernel = self._adam_kernel[kkey]
            gsize = (int(np.ceil(n / 256.0)) * 256,)
            kernel(
                p.queue,
                gsize,
                (256,),
                p.buffer,
                g_buf,
                self._m_buf[pid],
                self._v_buf[pid],
                lr,
                beta1,
                beta2,
                eps,
                wd,
                bc1,
                bc2,
                np.int32(n),
            )
            # sync master to model param if distinct
            if model_p is not p:
                if model_p.dtype == "float32":
                    cl.enqueue_copy(p.queue, model_p.buffer, p.buffer)
                elif cast_kernel is not None:
                    gsize_cast = (int(np.ceil(n / 256.0)) * 256,)
                    cast_kernel(p.queue, gsize_cast, (256,), p.buffer, model_p.buffer, np.int32(n))
                else:
                    # fallback: host copy with cast
                    cl.enqueue_copy(p.queue, model_p.buffer, p.to_host().astype(np.float16))
