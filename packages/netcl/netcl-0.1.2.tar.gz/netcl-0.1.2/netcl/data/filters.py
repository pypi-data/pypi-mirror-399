from __future__ import annotations

from typing import Callable, Iterable, Tuple

import numpy as np


Batch = Tuple[np.ndarray, np.ndarray]
FilterFn = Callable[[np.ndarray, np.ndarray], Batch]


def apply_filters(batch: Batch, filters: FilterFn | Iterable[FilterFn] | None) -> Batch:
    if filters is None:
        return batch
    xb, yb = batch
    if callable(filters):
        return filters(xb, yb)
    for f in filters:
        xb, yb = f(xb, yb)
    return xb, yb


def to_float(scale: float = 255.0, scale_if_int: bool = True) -> FilterFn:
    def _fn(xb: np.ndarray, yb: np.ndarray) -> Batch:
        x = xb.astype(np.float32, copy=False)
        if scale and scale != 1.0:
            if not scale_if_int or xb.dtype.kind in ("u", "i"):
                x = x / float(scale)
        return x, yb

    return _fn


def normalize(mean, std) -> FilterFn:
    mean = np.asarray(mean, dtype=np.float32).reshape(1, -1, 1, 1)
    std = np.asarray(std, dtype=np.float32).reshape(1, -1, 1, 1)

    def _fn(xb: np.ndarray, yb: np.ndarray) -> Batch:
        x = xb.astype(np.float32, copy=False)
        return (x - mean) / std, yb

    return _fn


def horizontal_flip(p: float = 0.5) -> FilterFn:
    def _fn(xb: np.ndarray, yb: np.ndarray) -> Batch:
        if p <= 0.0:
            return xb, yb
        if p >= 1.0:
            return xb[:, :, :, ::-1].copy(), yb
        mask = np.random.rand(xb.shape[0]) < p
        if not mask.any():
            return xb, yb
        x = xb.copy()
        x[mask] = x[mask, :, :, ::-1]
        return x, yb

    return _fn


def random_crop(padding: int = 4, crop_size: int = 32, pad_mode: str = "reflect") -> FilterFn:
    def _fn(xb: np.ndarray, yb: np.ndarray) -> Batch:
        n, c, h, w = xb.shape
        if padding > 0:
            padded = np.pad(xb, ((0, 0), (0, 0), (padding, padding), (padding, padding)), mode=pad_mode)
        else:
            padded = xb
        max_y = padded.shape[2] - crop_size
        max_x = padded.shape[3] - crop_size
        ys = np.random.randint(0, max_y + 1, size=n)
        xs = np.random.randint(0, max_x + 1, size=n)
        out = np.empty((n, c, crop_size, crop_size), dtype=xb.dtype)
        for i in range(n):
            out[i] = padded[i, :, ys[i] : ys[i] + crop_size, xs[i] : xs[i] + crop_size]
        return out, yb

    return _fn


def default_cifar10_filters() -> list[FilterFn]:
    mean = (0.4914, 0.4822, 0.4465)
    std = (0.2023, 0.1994, 0.2010)
    return [
        random_crop(padding=4, crop_size=32),
        horizontal_flip(p=0.5),
        to_float(scale=255.0),
        normalize(mean=mean, std=std),
    ]


def basic_cifar10_filters() -> list[FilterFn]:
    """
    Minimal CIFAR-10 preprocessing without augmentation.
    """
    mean = (0.4914, 0.4822, 0.4465)
    std = (0.2023, 0.1994, 0.2010)
    return [
        to_float(scale=255.0),
        normalize(mean=mean, std=std),
    ]
