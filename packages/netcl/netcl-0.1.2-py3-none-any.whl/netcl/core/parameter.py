from __future__ import annotations

from typing import Optional, Sequence

from netcl.core.tensor import Tensor, _np_dtype, _dtype_nbytes

try:
    import numpy as np  # type: ignore
except ImportError:  # pragma: no cover
    np = None

try:
    import pyopencl as cl  # type: ignore
except ImportError:  # pragma: no cover
    cl = None


class Parameter(Tensor):
    """
    Thin subclass of Tensor that defaults to requires_grad=True and is used for Module params.
    """

    @classmethod
    def from_host(cls, queue, data, dtype: Optional[str] = None, backend: Optional[str] = None) -> "Parameter":
        dtype_str = dtype or "float32"
        backend = backend or getattr(queue, "backend", "cl")
        if backend == "cpu":
            if np is None:
                raise ImportError("numpy required to create CPU parameters from host")
            arr = np.asarray(data, dtype=_np_dtype(dtype_str))
            return cls(
                buffer=None,
                shape=arr.shape,
                dtype=dtype_str,
                context=None,
                queue=queue,
                requires_grad=True,
                backend="cpu",
                array=arr,
            )
        if cl is None or np is None:
            raise ImportError("pyopencl and numpy required to create parameters from host")
        arr = np.asarray(data, dtype=_np_dtype(dtype_str))
        ctx = queue.context
        mf = cl.mem_flags
        buf = cl.Buffer(ctx, mf.READ_WRITE | mf.COPY_HOST_PTR, hostbuf=arr)
        return cls(buffer=buf, shape=arr.shape, dtype=dtype_str, context=ctx, queue=queue, requires_grad=True, backend="cl")

    @classmethod
    def from_shape(
        cls, queue, shape: Sequence[int], dtype: str = "float32", pool=None, backend: Optional[str] = None
    ) -> "Parameter":
        backend = backend or getattr(queue, "backend", "cl")
        if backend == "cpu":
            if np is None:
                raise ImportError("numpy required to create CPU parameters")
            nshape = tuple(int(d) for d in shape)
            arr = np.zeros(nshape, dtype=_np_dtype(dtype))
            return cls(
                buffer=None,
                shape=nshape,
                dtype=dtype,
                context=None,
                queue=queue,
                pool_handle=None,
                requires_grad=True,
                backend="cpu",
                array=arr,
            )
        if cl is None:
            raise ImportError("pyopencl required to create parameters")
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
            requires_grad=True,
            backend="cl",
        )
