"""
Elementwise operation helper built on PrimitiveBuilder.
With automatic vectorization for large tensors.
"""

from __future__ import annotations

import os
import re
import math
from typing import Optional, Tuple

from netcl.core.kernels import build_elementwise_kernel, KernelSpec
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

# Environment control for vectorized kernels
_USE_VECTORIZED = os.environ.get("NETCL_ELEMENTWISE_VECTORIZED", "1") not in ("0", "false", "False")
_VECTORIZED_THRESHOLD = int(os.environ.get("NETCL_ELEMENTWISE_THRESHOLD", "1000000"))  # 1M elements min

# Lazy import for vectorized kernels
_vectorized_relu = None
_vectorized_add = None

def _get_vectorized_ops():
    """Lazy import of vectorized elementwise ops."""
    global _vectorized_relu, _vectorized_add
    if _vectorized_relu is None:
        try:
            from netcl.ops.elementwise_optimized import vectorized_relu, vectorized_add
            _vectorized_relu = vectorized_relu
            _vectorized_add = vectorized_add
        except ImportError:
            _vectorized_relu = False
            _vectorized_add = False
    return _vectorized_relu, _vectorized_add


_DTYPE_NBYTES = {"float": 4, "float32": 4, "double": 8, "float64": 8}
_DTYPE_CNAME = {"float": "float", "float32": "float", "half": "half", "float16": "half", "double": "double", "float64": "double"}


def _dtype_nbytes(dtype: str) -> int:
    if dtype not in _DTYPE_NBYTES:
        raise ValueError(f"unsupported dtype {dtype}")
    return _DTYPE_NBYTES[dtype]


_KERNEL_CACHE = {}


def _strip_float_suffix(expr: str) -> str:
    return re.sub(r"([0-9])([fF])", r"\1", expr)


def _strip_outer_parens(expr: str) -> str:
    while expr.startswith("(") and expr.endswith(")"):
        depth = 0
        valid = True
        for i, ch in enumerate(expr):
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
                if depth == 0 and i != len(expr) - 1:
                    valid = False
                    break
        if depth != 0 or not valid:
            break
        expr = expr[1:-1]
    return expr


def _split_ternary(expr: str):
    expr = _strip_outer_parens(expr)
    depth = 0
    q_index = -1
    for i, ch in enumerate(expr):
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        elif ch == "?" and depth == 0:
            q_index = i
            break
    if q_index < 0:
        return None
    depth = 0
    nested = 0
    for i in range(q_index + 1, len(expr)):
        ch = expr[i]
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        elif ch == "?" and depth == 0:
            nested += 1
        elif ch == ":" and depth == 0:
            if nested == 0:
                return expr[:q_index], expr[q_index + 1 : i], expr[i + 1 :]
            nested -= 1
    return None


def _convert_ternary(expr: str) -> str:
    split = _split_ternary(expr)
    if split is None:
        return _normalize_logic(expr)
    cond, true_expr, false_expr = split
    cond = _convert_ternary(cond)
    true_expr = _convert_ternary(true_expr)
    false_expr = _convert_ternary(false_expr)
    return f"np.where({cond}, {true_expr}, {false_expr})"


def _normalize_logic(expr: str) -> str:
    if "&&" in expr or "||" in expr:
        expr = expr.replace("&&", ")&(").replace("||", ")|(")
        expr = f"({expr})"
    return expr


def _eval_expression_cpu(expression: str, a_arr, b_arr):
    expr = expression.replace(" ", "").replace("\t", "")
    expr = _strip_float_suffix(expr)
    expr = expr.lower()
    expr = _convert_ternary(expr)
    expr = expr.replace("v0", "a").replace("v1", "b")
    expr = expr.replace("fmax(", "np.maximum(")
    expr = expr.replace("fmin(", "np.minimum(")
    expr = expr.replace("exp(", "np.exp(")
    expr = expr.replace("tanh(", "np.tanh(")
    expr = expr.replace("log(", "np.log(")
    expr = expr.replace("abs(", "np.abs(")

    def add(x, y):
        return x + y

    def mul(x, y):
        return x * y

    def sub(x, y):
        return x - y

    def relu(x):
        return np.maximum(0, x)

    if np is None:
        raise ImportError("numpy required for CPU elementwise ops")
    erf_vec = np.vectorize(math.erf)
    safe = {
        "np": np,
        "a": a_arr,
        "b": b_arr,
        "add": add,
        "mul": mul,
        "sub": sub,
        "relu": relu,
        "erf": erf_vec,
    }
    try:
        res = eval(expr, {"__builtins__": {}}, safe)
    except Exception as exc:
        raise ValueError(f"unsupported CPU expression: {expression}") from exc
    res = np.asarray(res, dtype=a_arr.dtype)
    if res.shape != a_arr.shape:
        res = np.broadcast_to(res, a_arr.shape).copy()
    return res


def _get_binary_kernel(ctx: "cl.Context", dtype: str, expression: str) -> "cl.Kernel":
    cache_key = (ctx.int_ptr, dtype, expression)
    if cache_key in _KERNEL_CACHE:
        return _KERNEL_CACHE[cache_key]
    _, kernel = build_elementwise_kernel(
        context=ctx, name="eltwise_bin", arity=2, expression=expression, dtype=dtype
    )
    if kernel is None:
        raise RuntimeError("failed to build elementwise kernel")
    _KERNEL_CACHE[cache_key] = kernel
    return kernel


def _get_unary_kernel(ctx: "cl.Context", dtype: str, expression: str) -> "cl.Kernel":
    cache_key = (ctx.int_ptr, dtype, expression, "unary")
    if cache_key in _KERNEL_CACHE:
        return _KERNEL_CACHE[cache_key]
    _, kernel = build_elementwise_kernel(
        context=ctx, name="eltwise_un", arity=1, expression=expression, dtype=dtype
    )
    if kernel is None:
        raise RuntimeError("failed to build elementwise kernel")
    _KERNEL_CACHE[cache_key] = kernel
    return kernel


def elementwise_binary(
    a: Tensor, b: Tensor, expression: str, out: Optional[Tensor] = None, pool: Optional[BufferPool] = None
) -> Tensor:
    backend = ensure_same_backend((a, b), op="elementwise_binary")
    if a.shape != b.shape:
        raise ValueError(f"elementwise expects matching shapes, got {a.shape} vs {b.shape}")
    if a.dtype != b.dtype:
        raise ValueError(f"dtype mismatch: {a.dtype} vs {b.dtype}")
    if backend == "cpu":
        if np is None:
            raise ImportError("numpy required for CPU elementwise ops")
        a_arr = a.array
        b_arr = b.array
        if a_arr is None or b_arr is None:
            raise ValueError("CPU tensors require array storage")
        res = _eval_expression_cpu(expression, a_arr, b_arr)
        if out is None:
            return Tensor.from_host(a.queue, res.astype(a_arr.dtype), dtype=a.dtype, backend="cpu")
        if out.shape != a.shape or out.dtype != a.dtype:
            raise ValueError("output tensor shape/dtype mismatch")
        out.array[...] = res
        return out

    if cl is None:
        raise ImportError("pyopencl is required for elementwise ops")
    if a.queue != b.queue:
        raise ValueError("input tensors must share the same command queue")
    ctx = a.context
    kernel = _get_binary_kernel(ctx, a.dtype, expression)

    n = 1
    for d in a.shape:
        n *= d

    if out is None:
        out = Tensor.from_shape(a.queue, a.shape, dtype=a.dtype, pool=pool)
    else:
        if out.shape != a.shape or out.dtype != a.dtype:
            raise ValueError("output tensor shape/dtype mismatch")

    gsize = (int(np.ceil(n / 256.0)) * 256,) if np is not None else (n,)
    lsize = (256,) if np is not None else None
    kernel(a.queue, gsize, lsize, a.buffer, b.buffer, out.buffer, np.int32(n) if np is not None else n)  # type: ignore
    return out


def relu(x: Tensor, out: Optional[Tensor] = None, pool: Optional[BufferPool] = None) -> Tensor:
    backend = getattr(x, "backend", "cl")
    if backend == "cpu":
        if np is None:
            raise ImportError("numpy required for CPU relu")
        arr = x.array
        if arr is None:
            raise ValueError("CPU tensors require array storage")
        res = np.maximum(0, arr)
        if out is None:
            return Tensor.from_host(x.queue, res.astype(arr.dtype), dtype=x.dtype, backend="cpu")
        if out.shape != x.shape or out.dtype != x.dtype:
            raise ValueError("output tensor shape/dtype mismatch")
        out.array[...] = res
        return out
    if cl is None:
        raise ImportError("pyopencl is required for elementwise ops")
    
    # Use vectorized kernel for large tensors
    n = 1
    for d in x.shape:
        n *= d
    
    if _USE_VECTORIZED and n >= _VECTORIZED_THRESHOLD:
        vec_relu, _ = _get_vectorized_ops()
        if vec_relu:
            try:
                return vec_relu(x, out=out, pool=pool)
            except Exception:
                pass  # Fall back to scalar kernel
    
    ctx = x.context
    kernel = _get_unary_kernel(ctx, x.dtype, "RELU(v0)")
    if out is None:
        out = Tensor.from_shape(x.queue, x.shape, dtype=x.dtype, pool=pool)
    else:
        if out.shape != x.shape or out.dtype != x.dtype:
            raise ValueError("output tensor shape/dtype mismatch")
    gsize = (int(np.ceil(n / 256.0)) * 256,) if np is not None else (n,)
    lsize = (256,) if np is not None else None
    kernel(x.queue, gsize, lsize, x.buffer, out.buffer, np.int32(n) if np is not None else n)  # type: ignore
    return out


def bias_add(x: Tensor, bias: Tensor, out: Optional[Tensor] = None, pool: Optional[BufferPool] = None) -> Tensor:
    """
    Adds bias (shape [N]) to each row of x (shape [M,N]).
    """
    backend = ensure_same_backend((x, bias), op="bias_add")
    if len(x.shape) != 2 or len(bias.shape) != 1:
        raise ValueError("bias_add expects x: [M,N], bias: [N]")
    if x.shape[1] != bias.shape[0]:
        raise ValueError("bias dimension mismatch")
    if x.dtype != bias.dtype:
        raise ValueError("dtype mismatch")
    if backend == "cpu":
        if np is None:
            raise ImportError("numpy required for CPU bias_add")
        x_arr = x.array
        b_arr = bias.array
        if x_arr is None or b_arr is None:
            raise ValueError("CPU tensors require array storage")
        res = x_arr + b_arr.reshape(1, -1)
        if out is None:
            return Tensor.from_host(x.queue, res.astype(x_arr.dtype), dtype=x.dtype, backend="cpu")
        if out.shape != x.shape or out.dtype != x.dtype:
            raise ValueError("output tensor shape/dtype mismatch")
        out.array[...] = res
        return out
    if cl is None:
        raise ImportError("pyopencl is required for bias_add")
    ctx = x.context
    dtype = x.dtype
    dtype_c = _DTYPE_CNAME.get(dtype)
    if dtype_c is None:
        raise ValueError(f"unsupported dtype {dtype}")
    cache_key = (ctx.int_ptr, dtype, "bias_add")
    if cache_key in _KERNEL_CACHE:
        kernel = _KERNEL_CACHE[cache_key]
    else:
        body = """
        int gid = get_global_id(0);
        int col = gid % N;
        int row = gid / N;
        if (row < M) {
            out[gid] = x[gid] + bias[col];
        }
        """
        params = [
            f"__global const {dtype_c}* x",
            f"__global const {dtype_c}* bias",
            f"__global {dtype_c}* out",
            "const int M",
            "const int N",
        ]
        spec = KernelSpec(name="bias_add_kernel", params=params, body=body)
        program = cl.Program(ctx, spec.to_source()).build()
        kernel = getattr(program, spec.name)
        _KERNEL_CACHE[cache_key] = kernel

    M, N = x.shape
    total = M * N
    if out is None:
        out = Tensor.from_shape(x.queue, (M, N), dtype=dtype, pool=pool)
    gsize = (int(np.ceil(total / 256.0)) * 256,) if np is not None else (total,)
    lsize = (256,) if np is not None else None
    kernel(
        x.queue,
        gsize,
        lsize,
        x.buffer,
        bias.buffer,
        out.buffer,
        np.int32(M) if np is not None else M,
        np.int32(N) if np is not None else N,
    )  # type: ignore
    return out


def sigmoid(x: Tensor, out: Optional[Tensor] = None, pool: Optional[BufferPool] = None) -> Tensor:
    if getattr(x, "backend", "cl") == "cpu":
        if np is None:
            raise ImportError("numpy required for CPU sigmoid")
        arr = x.array
        if arr is None:
            raise ValueError("CPU tensors require array storage")
        res = 1.0 / (1.0 + np.exp(-arr))
        if out is None:
            return Tensor.from_host(x.queue, res.astype(arr.dtype), dtype=x.dtype, backend="cpu")
        if out.shape != x.shape or out.dtype != x.dtype:
            raise ValueError("output tensor shape/dtype mismatch")
        out.array[...] = res
        return out
    if cl is None:
        raise ImportError("pyopencl is required for elementwise ops")
    ctx = x.context
    kernel = _get_unary_kernel(ctx, x.dtype, "1.0f / (1.0f + exp(-v0))")
    n = 1
    for d in x.shape:
        n *= d
    if out is None:
        out = Tensor.from_shape(x.queue, x.shape, dtype=x.dtype, pool=pool)
    else:
        if out.shape != x.shape or out.dtype != x.dtype:
            raise ValueError("output tensor shape/dtype mismatch")
    gsize = (int(np.ceil(n / 256.0)) * 256,) if np is not None else (n,)
    lsize = (256,) if np is not None else None
    kernel(x.queue, gsize, lsize, x.buffer, out.buffer, np.int32(n) if np is not None else n)  # type: ignore
    return out


def tanh(x: Tensor, out: Optional[Tensor] = None, pool: Optional[BufferPool] = None) -> Tensor:
    if getattr(x, "backend", "cl") == "cpu":
        if np is None:
            raise ImportError("numpy required for CPU tanh")
        arr = x.array
        if arr is None:
            raise ValueError("CPU tensors require array storage")
        res = np.tanh(arr)
        if out is None:
            return Tensor.from_host(x.queue, res.astype(arr.dtype), dtype=x.dtype, backend="cpu")
        if out.shape != x.shape or out.dtype != x.dtype:
            raise ValueError("output tensor shape/dtype mismatch")
        out.array[...] = res
        return out
    if cl is None:
        raise ImportError("pyopencl is required for elementwise ops")
    ctx = x.context
    kernel = _get_unary_kernel(ctx, x.dtype, "tanh(v0)")
    n = 1
    for d in x.shape:
        n *= d
    if out is None:
        out = Tensor.from_shape(x.queue, x.shape, dtype=x.dtype, pool=pool)
    else:
        if out.shape != x.shape or out.dtype != x.dtype:
            raise ValueError("output tensor shape/dtype mismatch")
    gsize = (int(np.ceil(n / 256.0)) * 256,) if np is not None else (n,)
    lsize = (256,) if np is not None else None
    kernel(x.queue, gsize, lsize, x.buffer, out.buffer, np.int32(n) if np is not None else n)  # type: ignore
    return out


def leaky_relu(x: Tensor, negative_slope: float = 0.01, out: Optional[Tensor] = None, pool: Optional[BufferPool] = None) -> Tensor:
    backend = getattr(x, "backend", "cl")
    if backend == "cpu":
        if np is None:
            raise ImportError("numpy required for CPU leaky_relu")
        arr = x.array
        if arr is None:
            raise ValueError("CPU tensors require array storage")
        res = np.where(arr > 0, arr, negative_slope * arr)
        if out is None:
            return Tensor.from_host(x.queue, res.astype(arr.dtype), dtype=x.dtype, backend="cpu")
        if out.shape != x.shape or out.dtype != x.dtype:
            raise ValueError("output tensor shape/dtype mismatch")
        out.array[...] = res
        return out
    if cl is None:
        raise ImportError("pyopencl is required for elementwise ops")
    ctx = x.context
    expr = f"(v0 > 0 ? v0 : ({negative_slope}f * v0))"
    kernel = _get_unary_kernel(ctx, x.dtype, expr)
    n = 1
    for d in x.shape:
        n *= d
    if out is None:
        out = Tensor.from_shape(x.queue, x.shape, dtype=x.dtype, pool=pool)
    else:
        if out.shape != x.shape or out.dtype != x.dtype:
            raise ValueError("output tensor shape/dtype mismatch")
    gsize = (int(np.ceil(n / 256.0)) * 256,) if np is not None else (n,)
    lsize = (256,) if np is not None else None
    kernel(x.queue, gsize, lsize, x.buffer, out.buffer, np.int32(n) if np is not None else n)  # type: ignore
    return out


def dropout(
    x: Tensor,
    p: float = 0.5,
    seed: Optional[int] = None,
    out: Optional[Tensor] = None,
    pool: Optional[BufferPool] = None,
    return_mask: bool = False,
    mask: Optional[Tensor] = None,
) -> Tensor | Tuple[Tensor, Tensor]:
    """
    Inference-safe dropout: if p==0 or None, returns input. Mask generated on host for simplicity.
    If return_mask=True, also returns the mask Tensor so callers (e.g., autograd) can reuse it in backward.
    """
    if p <= 0:
        if return_mask:
            ones = np.ones(x.shape, dtype=np.float32)
            mask_tensor = Tensor.from_host(x.queue, ones, dtype="float32", backend=getattr(x, "backend", "cl"))
            return x, mask_tensor
        return x
    if getattr(x, "backend", "cl") == "cpu":
        if np is None:
            raise ImportError("numpy required for CPU dropout")
        x_arr = x.array
        if x_arr is None:
            raise ValueError("CPU tensors require array storage")
        rng = np.random.default_rng(seed)
        mask_arr = (rng.random(x_arr.shape, dtype=np.float32) > p).astype(np.float32)
        out_arr = x_arr * mask_arr / (1.0 - p)
        mask_tensor = Tensor.from_host(x.queue, mask_arr, dtype="float32", backend="cpu")
        out_tensor = Tensor.from_host(x.queue, out_arr.astype(x_arr.dtype), dtype=x.dtype, backend="cpu")
        if return_mask:
            return out_tensor, mask_tensor
        return out_tensor
    if cl is None or np is None:
        raise ImportError("pyopencl and numpy required for dropout")
    n = 1
    for d in x.shape:
        n *= d
    ctx = x.context
    mf = cl.mem_flags
    dtype_c = _DTYPE_CNAME.get(x.dtype)
    if dtype_c is None:
        raise ValueError(f"unsupported dtype {x.dtype}")
    if mask is None:
        rng = np.random.default_rng(seed)
        mask_host = (rng.random(n, dtype=np.float32) > p).astype(np.float32).reshape(x.shape)
        mask_buf = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=mask_host)
        mask_tensor = Tensor(buffer=mask_buf, shape=x.shape, dtype="float32", context=ctx, queue=x.queue)
    else:
        mask_tensor = mask
        mask_buf = mask.buffer
    if out is None:
        out = Tensor.from_shape(x.queue, x.shape, dtype=x.dtype, pool=pool)
    gsize = (int(np.ceil(n / 256.0)) * 256,)
    lsize = (256,)
    cache_key = (ctx.int_ptr, x.dtype, "dropout")
    if cache_key in _KERNEL_CACHE:
        kernel = _KERNEL_CACHE[cache_key]
    else:
        expr = f"((float)mask[gid] * in0[gid]) / {(1.0 - p):.6f}"
        params = [
            f"__global const {dtype_c}* in0",
            "__global const float* mask",
            f"__global {dtype_c}* out",
            "const int n",
        ]
        body = """
        int gid = get_global_id(0);
        if (gid >= n) return;
        out[gid] = ((float)mask[gid]) * in0[gid];
        out[gid] = out[gid] / SCALE;
        """.replace("SCALE", f"{1.0 - p:.6f}")
        spec = KernelSpec(name="dropout_kernel", params=params, body=body)
        program = cl.Program(ctx, spec.to_source()).build()
        kernel = getattr(program, spec.name)
        _KERNEL_CACHE[cache_key] = kernel
    kernel(x.queue, gsize, lsize, x.buffer, mask_buf, out.buffer, np.int32(n))
    if return_mask:
        return out, mask_tensor
    return out


def gelu(x: Tensor, approximate: bool = True, out: Optional[Tensor] = None) -> Tensor:
    """
    GELU activation. approximate=True uses tanh approximation for speed.
    """
    if getattr(x, "backend", "cl") == "cpu":
        if np is None:
            raise ImportError("numpy required for CPU gelu")
        arr = x.array
        if arr is None:
            raise ValueError("CPU tensors require array storage")
        if approximate:
            t = 0.79788456 * (arr + 0.044715 * np.power(arr, 3))
            res = 0.5 * arr * (1.0 + np.tanh(t))
        else:
            from math import erf
            v_erf = np.vectorize(erf)
            res = 0.5 * arr * (1.0 + v_erf(arr / 1.41421356))
        if out is None:
            return Tensor.from_host(x.queue, res.astype(arr.dtype), dtype=x.dtype, backend="cpu")
        if out.shape != x.shape or out.dtype != x.dtype:
            raise ValueError("output tensor shape/dtype mismatch")
        out.array[...] = res
        return out
    if cl is None:
        raise ImportError("pyopencl is required for elementwise ops")
    ctx = x.context
    if approximate:
        expr = "0.5f * v0 * (1.0f + tanh(0.79788456f * (v0 + 0.044715f * v0 * v0 * v0)))"
    else:
        expr = "0.5f * v0 * (1.0f + erf(v0 / 1.41421356f))"
    kernel = _get_unary_kernel(ctx, x.dtype, expr)
    n = 1
    for d in x.shape:
        n *= d
    if out is None:
        out = Tensor.from_shape(x.queue, x.shape, dtype=x.dtype)
    gsize = (int(np.ceil(n / 256.0)) * 256,)
    lsize = (256,)
    kernel(x.queue, gsize, lsize, x.buffer, out.buffer, np.int32(n))
    return out


def swish(x: Tensor, out: Optional[Tensor] = None) -> Tensor:
    if getattr(x, "backend", "cl") == "cpu":
        if np is None:
            raise ImportError("numpy required for CPU swish")
        arr = x.array
        if arr is None:
            raise ValueError("CPU tensors require array storage")
        res = arr / (1.0 + np.exp(-arr))
        if out is None:
            return Tensor.from_host(x.queue, res.astype(arr.dtype), dtype=x.dtype, backend="cpu")
        if out.shape != x.shape or out.dtype != x.dtype:
            raise ValueError("output tensor shape/dtype mismatch")
        out.array[...] = res
        return out
    if cl is None:
        raise ImportError("pyopencl is required for elementwise ops")
    ctx = x.context
    expr = "v0 / (1.0f + exp(-v0))"
    kernel = _get_unary_kernel(ctx, x.dtype, expr)
    n = 1
    for d in x.shape:
        n *= d
    if out is None:
        out = Tensor.from_shape(x.queue, x.shape, dtype=x.dtype)
    gsize = (int(np.ceil(n / 256.0)) * 256,)
    lsize = (256,)
    kernel(x.queue, gsize, lsize, x.buffer, out.buffer, np.int32(n))
    return out


def elu(x: Tensor, alpha: float = 1.0, out: Optional[Tensor] = None) -> Tensor:
    if getattr(x, "backend", "cl") == "cpu":
        if np is None:
            raise ImportError("numpy required for CPU elu")
        arr = x.array
        if arr is None:
            raise ValueError("CPU tensors require array storage")
        res = np.where(arr > 0, arr, alpha * (np.exp(arr) - 1.0))
        if out is None:
            return Tensor.from_host(x.queue, res.astype(arr.dtype), dtype=x.dtype, backend="cpu")
        if out.shape != x.shape or out.dtype != x.dtype:
            raise ValueError("output tensor shape/dtype mismatch")
        out.array[...] = res
        return out
    if cl is None:
        raise ImportError("pyopencl is required for elementwise ops")
    ctx = x.context
    expr = f"(v0 > 0 ? v0 : ({alpha}f * (exp(v0) - 1.0f)))"
    kernel = _get_unary_kernel(ctx, x.dtype, expr)
    n = 1
    for d in x.shape:
        n *= d
    if out is None:
        out = Tensor.from_shape(x.queue, x.shape, dtype=x.dtype)
    gsize = (int(np.ceil(n / 256.0)) * 256,)
    lsize = (256,)
    kernel(x.queue, gsize, lsize, x.buffer, out.buffer, np.int32(n))
    return out


def softplus(x: Tensor, out: Optional[Tensor] = None) -> Tensor:
    if getattr(x, "backend", "cl") == "cpu":
        if np is None:
            raise ImportError("numpy required for CPU softplus")
        arr = x.array
        if arr is None:
            raise ValueError("CPU tensors require array storage")
        res = np.log1p(np.exp(arr))
        if out is None:
            return Tensor.from_host(x.queue, res.astype(arr.dtype), dtype=x.dtype, backend="cpu")
        if out.shape != x.shape or out.dtype != x.dtype:
            raise ValueError("output tensor shape/dtype mismatch")
        out.array[...] = res
        return out
    if cl is None:
        raise ImportError("pyopencl is required for elementwise ops")
    ctx = x.context
    expr = "log(1.0f + exp(v0))"
    kernel = _get_unary_kernel(ctx, x.dtype, expr)
    n = 1
    for d in x.shape:
        n *= d
    if out is None:
        out = Tensor.from_shape(x.queue, x.shape, dtype=x.dtype)
    gsize = (int(np.ceil(n / 256.0)) * 256,)
    lsize = (256,)
    kernel(x.queue, gsize, lsize, x.buffer, out.buffer, np.int32(n))
    return out


def hard_sigmoid(x: Tensor, out: Optional[Tensor] = None) -> Tensor:
    if getattr(x, "backend", "cl") == "cpu":
        if np is None:
            raise ImportError("numpy required for CPU hard_sigmoid")
        arr = x.array
        if arr is None:
            raise ValueError("CPU tensors require array storage")
        res = np.minimum(1.0, np.maximum(0.0, 0.2 * arr + 0.5))
        if out is None:
            return Tensor.from_host(x.queue, res.astype(arr.dtype), dtype=x.dtype, backend="cpu")
        if out.shape != x.shape or out.dtype != x.dtype:
            raise ValueError("output tensor shape/dtype mismatch")
        out.array[...] = res
        return out
    if cl is None:
        raise ImportError("pyopencl is required for elementwise ops")
    ctx = x.context
    expr = "fmax(0.0f, fmin(1.0f, 0.2f * v0 + 0.5f))"
    kernel = _get_unary_kernel(ctx, x.dtype, expr)
    n = 1
    for d in x.shape:
        n *= d
    if out is None:
        out = Tensor.from_shape(x.queue, x.shape, dtype=x.dtype)
    gsize = (int(np.ceil(n / 256.0)) * 256,)
    lsize = (256,)
    kernel(x.queue, gsize, lsize, x.buffer, out.buffer, np.int32(n))
    return out


def hard_swish(x: Tensor, out: Optional[Tensor] = None) -> Tensor:
    if getattr(x, "backend", "cl") == "cpu":
        if np is None:
            raise ImportError("numpy required for CPU hard_swish")
        arr = x.array
        if arr is None:
            raise ValueError("CPU tensors require array storage")
        gate = np.minimum(1.0, np.maximum(0.0, 0.2 * arr + 0.5))
        res = arr * gate
        if out is None:
            return Tensor.from_host(x.queue, res.astype(arr.dtype), dtype=x.dtype, backend="cpu")
        if out.shape != x.shape or out.dtype != x.dtype:
            raise ValueError("output tensor shape/dtype mismatch")
        out.array[...] = res
        return out
    if cl is None:
        raise ImportError("pyopencl is required for elementwise ops")
    ctx = x.context
    expr = "(v0 * fmax(0.0f, fmin(1.0f, 0.2f * v0 + 0.5f)))"
    kernel = _get_unary_kernel(ctx, x.dtype, expr)
    n = 1
    for d in x.shape:
        n *= d
    if out is None:
        out = Tensor.from_shape(x.queue, x.shape, dtype=x.dtype)
    gsize = (int(np.ceil(n / 256.0)) * 256,)
    lsize = (256,)
    kernel(x.queue, gsize, lsize, x.buffer, out.buffer, np.int32(n))
    return out


def clamp(x: Tensor, min_val: float, max_val: float, out: Optional[Tensor] = None) -> Tensor:
    if getattr(x, "backend", "cl") == "cpu":
        if np is None:
            raise ImportError("numpy required for CPU clamp")
        arr = x.array
        if arr is None:
            raise ValueError("CPU tensors require array storage")
        res = np.minimum(np.maximum(arr, min_val), max_val)
        if out is None:
            return Tensor.from_host(x.queue, res.astype(arr.dtype), dtype=x.dtype, backend="cpu")
        if out.shape != x.shape or out.dtype != x.dtype:
            raise ValueError("output tensor shape/dtype mismatch")
        out.array[...] = res
        return out
    if cl is None:
        raise ImportError("pyopencl is required for elementwise ops")
    ctx = x.context
    expr = f"fmin(fmax(v0, {min_val}f), {max_val}f)"
    kernel = _get_unary_kernel(ctx, x.dtype, expr)
    n = 1
    for d in x.shape:
        n *= d
    if out is None:
        out = Tensor.from_shape(x.queue, x.shape, dtype=x.dtype)
    gsize = (int(np.ceil(n / 256.0)) * 256,)
    lsize = (256,)
    kernel(x.queue, gsize, lsize, x.buffer, out.buffer, np.int32(n))
    return out


def hard_tanh(x: Tensor, min_val: float = -1.0, max_val: float = 1.0, out: Optional[Tensor] = None) -> Tensor:
    if getattr(x, "backend", "cl") == "cpu":
        if np is None:
            raise ImportError("numpy required for CPU hard_tanh")
        arr = x.array
        if arr is None:
            raise ValueError("CPU tensors require array storage")
        res = np.minimum(np.maximum(arr, min_val), max_val)
        if out is None:
            return Tensor.from_host(x.queue, res.astype(arr.dtype), dtype=x.dtype, backend="cpu")
        if out.shape != x.shape or out.dtype != x.dtype:
            raise ValueError("output tensor shape/dtype mismatch")
        out.array[...] = res
        return out
    if cl is None:
        raise ImportError("pyopencl is required for elementwise ops")
    ctx = x.context
    expr = f"(v0 < {min_val}f ? {min_val}f : (v0 > {max_val}f ? {max_val}f : v0))"
    kernel = _get_unary_kernel(ctx, x.dtype, expr)
    n = 1
    for d in x.shape:
        n *= d
    if out is None:
        out = Tensor.from_shape(x.queue, x.shape, dtype=x.dtype)
    gsize = (int(np.ceil(n / 256.0)) * 256,)
    lsize = (256,)
    kernel(x.queue, gsize, lsize, x.buffer, out.buffer, np.int32(n))
    return out


def prelu(x: Tensor, alpha: Tensor, out: Optional[Tensor] = None) -> Tensor:
    """
    PReLU with channel-wise alpha (shape matches channel dimension for NCHW).
    """
    if getattr(x, "backend", "cl") == "cpu":
        if np is None:
            raise ImportError("numpy required for CPU prelu")
        x_arr = x.array
        a_arr = alpha.array
        if x_arr is None or a_arr is None:
            raise ValueError("CPU tensors require array storage")
        if x_arr.ndim == 2:
            if a_arr.shape[0] != x_arr.shape[1]:
                raise ValueError("alpha shape must match channels")
            a_b = a_arr.reshape(1, -1)
        elif x_arr.ndim == 4:
            if a_arr.shape[0] != x_arr.shape[1]:
                raise ValueError("alpha shape must match channels")
            a_b = a_arr.reshape(1, -1, 1, 1)
        else:
            raise ValueError("prelu expects 2D or 4D input on CPU")
        res = np.where(x_arr > 0, x_arr, a_b * x_arr)
        if out is None:
            return Tensor.from_host(x.queue, res.astype(x_arr.dtype), dtype=x.dtype, backend="cpu")
        if out.shape != x.shape or out.dtype != x.dtype:
            raise ValueError("output tensor shape/dtype mismatch")
        out.array[...] = res
        return out
    if cl is None:
        raise ImportError("pyopencl is required for elementwise ops")
    ctx = x.context
    dtype_c = _DTYPE_CNAME.get(x.dtype)
    if dtype_c is None:
        raise ValueError(f"unsupported dtype {x.dtype}")
    N, C, H, W = x.shape
    if alpha.shape[0] != C:
        raise ValueError("alpha shape must match channels")
    ksrc = f"""
    __kernel void prelu(__global const {dtype_c}* x, __global const {dtype_c}* a, __global {dtype_c}* out,
                        const int N, const int C, const int H, const int W) {{
        int gid = get_global_id(0);
        int total = N * C * H * W;
        if (gid >= total) return;
        int w = gid % W;
        int h = (gid / W) % H;
        int c = (gid / (H*W)) % C;
        int n = gid / (C*H*W);
        int idx = ((n*C + c)*H + h)*W + w;
        float v = x[idx];
        float s = v > 0 ? v : a[c] * v;
        out[idx] = s;
    }}
    """
    prg = cl.Program(ctx, ksrc).build()
    kernel = prg.prelu
    if out is None:
        out = Tensor.from_shape(x.queue, x.shape, dtype=x.dtype)
    total = N * C * H * W
    gsize = (int(np.ceil(total / 256.0)) * 256,)
    kernel(x.queue, gsize, (256,), x.buffer, alpha.buffer, out.buffer, np.int32(N), np.int32(C), np.int32(H), np.int32(W))
    return out


def prelu_backward(x: Tensor, alpha: Tensor, grad_out: Tensor) -> Tuple[Tensor, Tensor]:
    """
    PReLU backward: returns (grad_x, grad_alpha).
    """
    backend = getattr(x, "backend", "cl")
    if backend == "cpu":
        if np is None:
            raise ImportError("numpy required for CPU prelu_backward")
        x_arr = x.array
        a_arr = alpha.array
        g_arr = grad_out.array
        if x_arr is None or a_arr is None or g_arr is None:
            raise ValueError("CPU tensors require array storage")
        if x_arr.ndim == 2:
            if a_arr.shape[0] != x_arr.shape[1]:
                raise ValueError("alpha shape must match channels")
            a_b = a_arr.reshape(1, -1)
            mask = x_arr <= 0
            grad_x = g_arr * np.where(mask, a_b, 1.0)
            grad_alpha = np.sum(g_arr * x_arr * mask, axis=0).astype(np.float32)
        elif x_arr.ndim == 4:
            if a_arr.shape[0] != x_arr.shape[1]:
                raise ValueError("alpha shape must match channels")
            a_b = a_arr.reshape(1, -1, 1, 1)
            mask = x_arr <= 0
            grad_x = g_arr * np.where(mask, a_b, 1.0)
            grad_alpha = np.sum(g_arr * x_arr * mask, axis=(0, 2, 3)).astype(np.float32)
        else:
            raise ValueError("prelu_backward expects 2D or 4D input")
        gx = Tensor.from_host(x.queue, grad_x.astype(x_arr.dtype), dtype=x.dtype, backend="cpu")
        ga = Tensor.from_host(x.queue, grad_alpha.astype(a_arr.dtype), dtype=alpha.dtype, backend="cpu")
        return gx, ga

    if cl is None or np is None:
        raise ImportError("pyopencl and numpy required for prelu_backward")
    dtype_c = _DTYPE_CNAME.get(x.dtype)
    if dtype_c is None:
        raise ValueError(f"unsupported dtype {x.dtype}")
    if len(x.shape) == 2:
        N, C = x.shape
        H = 1
        W = 1
    elif len(x.shape) == 4:
        N, C, H, W = x.shape
    else:
        raise ValueError("prelu_backward expects 2D or 4D input")
    if alpha.shape[0] != C:
        raise ValueError("alpha shape must match channels")
    ctx = x.context
    cache_key = (ctx.int_ptr, x.dtype, "prelu_backward")
    if cache_key in _KERNEL_CACHE:
        k_grad_x, k_grad_a = _KERNEL_CACHE[cache_key]
    else:
        ksrc = f"""
        __kernel void prelu_grad_x(__global const {dtype_c}* x, __global const {dtype_c}* a, __global const {dtype_c}* go,
                                   __global {dtype_c}* gx, const int N, const int C, const int H, const int W) {{
            int gid = get_global_id(0);
            int total = N * C * H * W;
            if (gid >= total) return;
            int w = gid % W;
            int h = (gid / W) % H;
            int c = (gid / (H*W)) % C;
            int n = gid / (C*H*W);
            int idx = ((n*C + c)*H + h)*W + w;
            float v = x[idx];
            float slope = v > 0 ? 1.0f : a[c];
            gx[idx] = go[idx] * slope;
        }}
        __kernel void prelu_grad_alpha(__global const {dtype_c}* x, __global const {dtype_c}* go,
                                       __global {dtype_c}* ga, const int N, const int C, const int H, const int W) {{
            int c = get_global_id(0);
            if (c >= C) return;
            float acc = 0.0f;
            for (int n = 0; n < N; ++n) {{
                for (int h = 0; h < H; ++h) {{
                    for (int w = 0; w < W; ++w) {{
                        int idx = ((n*C + c)*H + h)*W + w;
                        float v = x[idx];
                        if (v <= 0) {{
                            acc += go[idx] * v;
                        }}
                    }}
                }}
            }}
            ga[c] = acc;
        }}
        """
        program = cl.Program(ctx, ksrc).build()
        k_grad_x = program.prelu_grad_x
        k_grad_a = program.prelu_grad_alpha
        _KERNEL_CACHE[cache_key] = (k_grad_x, k_grad_a)
    grad_x = Tensor.from_shape(x.queue, x.shape, dtype=x.dtype)
    grad_a = Tensor.from_shape(x.queue, (C,), dtype=x.dtype)
    total = N * C * H * W
    gsize = (int(np.ceil(total / 256.0)) * 256,)
    k_grad_x(x.queue, gsize, (256,), x.buffer, alpha.buffer, grad_out.buffer, grad_x.buffer, np.int32(N), np.int32(C), np.int32(H), np.int32(W))
    gsize_c = (int(np.ceil(C / 64.0)) * 64,)
    k_grad_a(x.queue, gsize_c, (64,), x.buffer, grad_out.buffer, grad_a.buffer, np.int32(N), np.int32(C), np.int32(H), np.int32(W))
    return grad_x, grad_a
