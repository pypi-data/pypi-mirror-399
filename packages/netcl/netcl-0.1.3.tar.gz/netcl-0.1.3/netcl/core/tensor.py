"""
Minimal tensor wrapper around PyOpenCL buffers with optional NumPy (CPU) backend.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Sequence, Tuple, Any

from netcl.core.memory import BufferHandle
from netcl.core.device import CPUQueue

try:
    import numpy as np  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    np = None

try:
    import pyopencl as cl  # type: ignore
except ImportError:  # pragma: no cover
    cl = None


def _np_dtype(dtype: str):
    if np is None:
        raise ImportError("numpy required for host-backed tensors")
    mapping = {
        "float": np.float32,
        "float32": np.float32,
        "half": np.float16,
        "float16": np.float16,
        "float64": np.float64,
        "double": np.float64,
    }
    if dtype not in mapping:
        raise ValueError(f"unsupported dtype {dtype}")
    return mapping[dtype]


def _dtype_nbytes(dtype: str) -> int:
    if dtype in ("float", "float32"):
        return 4
    if dtype in ("half", "float16"):
        return 2
    if dtype in ("double", "float64"):
        return 8
    raise ValueError(f"unsupported dtype {dtype}")


@dataclass
class Tensor:
    buffer: Optional["cl.Buffer"]
    shape: Tuple[int, ...]
    dtype: str
    context: Optional["cl.Context"]
    queue: Any  # cl.CommandQueue or CPUQueue
    pool_handle: Optional[BufferHandle] = None
    persistent: bool = False
    requires_grad: bool = False
    grad: Optional["Tensor"] = None
    grad_fn: Optional[Any] = None  # typically a callable producing grads
    backend: str = "cl"  # "cl" or "cpu"
    array: Optional["np.ndarray"] = None  # used when backend == "cpu"

    @property
    def size(self) -> int:
        total = 1
        for d in self.shape:
            total *= d
        return total

    @classmethod
    def from_host(cls, queue: Any, data, dtype: Optional[str] = None, backend: Optional[str] = None) -> "Tensor":
        dtype_str = dtype or "float32"
        # determine backend: explicit arg overrides queue attribute
        backend = backend or getattr(queue, "backend", "cl")
        if backend == "cpu":
            if np is None:
                raise ImportError("numpy required to create CPU tensors from host")
            arr = np.asarray(data, dtype=_np_dtype(dtype_str))
            return cls(buffer=None, shape=arr.shape, dtype=dtype_str, context=None, queue=queue, backend="cpu", array=arr)
        # CL backend
        if cl is None or np is None:
            raise ImportError("pyopencl and numpy required to create tensors from host")
        arr = np.asarray(data, dtype=_np_dtype(dtype_str))
        ctx = queue.context
        mf = cl.mem_flags
        buf = cl.Buffer(ctx, mf.READ_WRITE | mf.COPY_HOST_PTR, hostbuf=arr)
        return cls(buffer=buf, shape=arr.shape, dtype=dtype_str, context=ctx, queue=queue, backend="cl")

    @classmethod
    def from_shape(
        cls, queue: Any, shape: Sequence[int], dtype: str = "float32", pool: Optional["BufferPool"] = None, backend: Optional[str] = None
    ) -> "Tensor":
        backend = backend or getattr(queue, "backend", "cl")
        if backend == "cpu":
            if np is None:
                raise ImportError("numpy required to create CPU tensors")
            nshape = tuple(int(d) for d in shape)
            arr = np.zeros(nshape, dtype=_np_dtype(dtype))
            return cls(
                buffer=None,
                shape=nshape,
                dtype=dtype,
                context=None,
                queue=queue,
                pool_handle=None,
                backend="cpu",
                array=arr,
            )
        if cl is None:
            raise ImportError("pyopencl required to create tensors")
        ctx = queue.context
        n_elems = 1
        for d in shape:
            n_elems *= int(d)
        nbytes = n_elems * _dtype_nbytes(dtype)
        if pool is not None:
            handle = pool.allocate(nbytes)
            buf = handle.buffer
        else:
            mf = cl.mem_flags
            buf = cl.Buffer(ctx, mf.READ_WRITE, nbytes)
            handle = None
        return cls(
            buffer=buf,
            shape=tuple(int(d) for d in shape),
            dtype=dtype,
            context=ctx,
            queue=queue,
            pool_handle=handle,
            backend="cl",
        )

    def to_host(self):
        if self.backend == "cpu":
            if np is None:
                raise ImportError("numpy required for host transfer")
            # return a copy to match CL semantics
            return np.array(self.array, copy=True)  # type: ignore[arg-type]
        if np is None or cl is None:
            raise ImportError("pyopencl and numpy required for host transfer")
        out = np.empty(self.shape, dtype=_np_dtype(self.dtype))
        cl.enqueue_copy(self.queue, out, self.buffer).wait()  # type: ignore
        return out


def reshape(t: Tensor, shape: Tuple[int, ...]) -> Tensor:
    """
    Return a view Tensor sharing the same buffer with a new shape.
    """
    if t.backend == "cpu":
        arr = t.array
        if arr is None:
            raise ValueError("CPU tensor missing array storage")
        return Tensor(
            buffer=None,
            shape=shape,
            dtype=t.dtype,
            context=None,
            queue=t.queue,
            pool_handle=t.pool_handle,
            persistent=t.persistent,
            requires_grad=t.requires_grad,
            grad=t.grad,
            grad_fn=t.grad_fn,
            backend="cpu",
            array=arr.reshape(shape),
        )
    return Tensor(
        buffer=t.buffer,
        shape=shape,
        dtype=t.dtype,
        context=t.context,
        queue=t.queue,
        pool_handle=t.pool_handle,
        persistent=t.persistent,
        requires_grad=t.requires_grad,
        grad=t.grad,
        grad_fn=t.grad_fn,
        backend="cl",
        array=None,
    )
