from __future__ import annotations

from typing import Iterable

from netcl.core.tensor import Tensor


def get_backend(t: Tensor) -> str:
    return getattr(t, "backend", "cl")


def ensure_same_backend(tensors: Iterable[Tensor], op: str = "") -> str:
    bks = {get_backend(t) for t in tensors}
    if len(bks) != 1:
        raise ValueError(f"{op} expects tensors on the same backend, got {bks}")
    return bks.pop()
