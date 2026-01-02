from __future__ import annotations

import numpy as np
from typing import Iterable, Iterator, Tuple, Optional, Callable, Any
import threading
from queue import Queue
from concurrent.futures import ThreadPoolExecutor


class DataLoader:
    """
    DataLoader with multi-threaded prefetching and async GPU transfer support.
    
    Args:
        dataset: Iterable dataset of (x, y) samples
        batch_size: Number of samples per batch
        shuffle: Whether to shuffle data each epoch
        drop_last: Drop last incomplete batch
        seed: Random seed for shuffling
        prefetch: Number of batches to prefetch (0 = disabled)
        device_queue: OpenCL queue for GPU transfers
        augment: Augmentation function
        overlap: Enable overlapped GPU transfers
        autocast: Enable autocasting in augmentation
        transforms: CPU transforms to apply
        num_workers: Number of worker threads for data loading (default 2)
        pin_memory: Pre-allocate pinned memory for faster transfers
        async_transfer: Enable async GPU memory transfers
    """
    def __init__(
        self,
        dataset: Iterable,
        batch_size: int = 32,
        shuffle: bool = True,
        drop_last: bool = False,
        seed: Optional[int] = None,
        prefetch: int = 0,
        device_queue=None,
        augment: Optional[Callable[[Any], Any]] = None,
        overlap: bool = False,
        autocast: bool = False,
        transforms: Optional[Callable[[Any, Any], Any] | Iterable[Callable[[Any, Any], Any]]] = None,
        num_workers: int = 2,
        pin_memory: bool = False,
        async_transfer: bool = True,
    ):
        self.dataset = list(dataset)
        self.batch_size = batch_size
        self.shuffle = shuffle
        self.drop_last = drop_last
        self.rng = np.random.default_rng(seed)
        self.prefetch = prefetch
        self.device_queue = device_queue
        self.augment = augment
        self.overlap = overlap
        self.autocast = autocast
        self.transforms = transforms
        self.num_workers = num_workers
        self.pin_memory = pin_memory
        self.async_transfer = async_transfer
        
        # Thread pool for async operations
        self._executor: Optional[ThreadPoolExecutor] = None
        self._transfer_queue: Optional["Queue"] = None
        self._pending_transfers = []

    def __iter__(self) -> Iterator:
        if self.prefetch and self.prefetch > 0:
            if self.async_transfer and self.device_queue is not None:
                yield from self._iter_async_prefetch()
            else:
                yield from self._iter_prefetch()
            return
        yield from self._iter_batches()
    
    def _iter_async_prefetch(self) -> Iterator:
        """
        Advanced prefetching with async GPU transfers.
        Uses double-buffering to overlap CPU preparation with GPU transfer.
        """
        sentinel = object()
        prep_queue: Queue = Queue(maxsize=self.prefetch + 1)
        transfer_queue: Queue = Queue(maxsize=2)  # Double buffer
        
        def prepare_worker():
            """Prepare batches on CPU."""
            try:
                for batch in self._iter_batches_raw():
                    prep_queue.put(batch)
            finally:
                prep_queue.put(sentinel)
        
        def transfer_worker():
            """Transfer prepared batches to GPU."""
            try:
                while True:
                    item = prep_queue.get()
                    if item is sentinel:
                        break
                    # Transfer to GPU
                    xb, yb = item
                    xb_gpu = self._to_device(xb)
                    yb_gpu = self._maybe_move_labels_gpu(yb)
                    transfer_queue.put((xb_gpu, yb_gpu))
            finally:
                transfer_queue.put(sentinel)
        
        # Start workers
        prep_thread = threading.Thread(target=prepare_worker, daemon=True)
        transfer_thread = threading.Thread(target=transfer_worker, daemon=True)
        prep_thread.start()
        transfer_thread.start()
        
        # Yield GPU batches
        while True:
            item = transfer_queue.get()
            if item is sentinel:
                break
            yield item
    
    def _iter_batches_raw(self) -> Iterator:
        """Generate raw batches without GPU transfer."""
        idx = np.arange(len(self.dataset))
        if self.shuffle:
            self.rng.shuffle(idx)
        batch = []
        for i in idx:
            batch.append(self.dataset[i])
            if len(batch) == self.batch_size:
                yield self._prepare_batch_cpu(batch)
                batch = []
        if batch and not self.drop_last:
            yield self._prepare_batch_cpu(batch)
    
    def _prepare_batch_cpu(self, batch):
        """Prepare batch on CPU (stacking + transforms)."""
        xb, yb = self._stack(batch)
        if self.transforms is not None:
            if callable(self.transforms):
                xb, yb = self.transforms(xb, yb)
            else:
                for t in self.transforms:
                    xb, yb = t(xb, yb)
        return xb, yb
    
    def _to_device(self, xb):
        """Transfer numpy array to GPU tensor."""
        if self.device_queue is None:
            return xb
        try:
            from netcl.core.tensor import Tensor
            if hasattr(self.device_queue, "context"):
                return Tensor.from_host(self.device_queue, xb.astype(np.float32))
        except Exception:
            pass
        return xb
    
    def _maybe_move_labels_gpu(self, yb):
        """Move labels to GPU with one-hot encoding if needed."""
        if self.device_queue is None:
            return yb
        try:
            from netcl.core.tensor import Tensor
            if hasattr(self.device_queue, "context"):
                if yb.ndim == 1:
                    num_classes = int(yb.max()) + 1
                    y_oh = np.eye(num_classes, dtype=np.float32)[yb.astype(np.int64)]
                    return Tensor.from_host(self.device_queue, y_oh)
                else:
                    return Tensor.from_host(self.device_queue, yb.astype(np.float32))
        except Exception:
            pass
        return yb

    def _iter_batches(self) -> Iterator:
        idx = np.arange(len(self.dataset))
        if self.shuffle:
            self.rng.shuffle(idx)
        batch = []
        for i in idx:
            batch.append(self.dataset[i])
            if len(batch) == self.batch_size:
                yield self._process_batch(batch)
                batch = []
        if batch and not self.drop_last:
            yield self._process_batch(batch)

    def _iter_prefetch(self) -> Iterator:
        """
        Prefetch batches on a background thread into a bounded queue.
        """
        sentinel = object()
        q: Queue = Queue(maxsize=self.prefetch)

        def worker():
            try:
                for b in self._iter_batches():
                    q.put(b)
            finally:
                q.put(sentinel)

        t = threading.Thread(target=worker, daemon=True)
        t.start()
        while True:
            item = q.get()
            if item is sentinel:
                break
            yield item

    def _stack(self, batch):
        # assume each item is (x, y) arrays
        xs, ys = zip(*batch)
        return np.stack(xs, axis=0), np.stack(ys, axis=0)

    def _process_batch(self, batch):
        xb, yb = self._stack(batch)
        # apply optional CPU transforms first
        if self.transforms is not None:
            if callable(self.transforms):
                xb, yb = self.transforms(xb, yb)
            else:
                for t in self.transforms:
                    xb, yb = t(xb, yb)
        if self.augment is None:
            return self._maybe_move_labels(xb, yb)
        # Optional overlap: submit augment on separate queue if provided
        if self.overlap and self.device_queue is not None and hasattr(self.device_queue, "context"):
            import pyopencl as cl  # type: ignore

            aug_queue = cl.CommandQueue(self.device_queue.context, properties=self.device_queue.properties)
            # reuse a single augment queue per loader to avoid churn
            if not hasattr(self, "_aug_queue"):
                self._aug_queue = aug_queue
            xb, yb = self._call_augment((xb, yb), device_queue=self._aug_queue)
        else:
            xb, yb = self._call_augment((xb, yb), device_queue=self.device_queue)
        return self._maybe_move_labels(xb, yb)

    def _maybe_move_labels(self, xb, yb):
        """
        If device_queue is provided and labels are integer class ids, move labels to device
        one-hot to reduce host copies downstream (when queue is a CL queue).
        """
        if self.device_queue is None:
            return xb, yb
        try:
            import pyopencl as cl  # type: ignore
            from netcl.core.tensor import Tensor
            if hasattr(self.device_queue, "context"):
                # only convert int labels; leave already-one-hot untouched
                if yb.ndim == 1:
                    num_classes = int(yb.max()) + 1
                    y_oh = np.eye(num_classes, dtype=np.float32)[yb.astype(np.int64)]
                    yb_t = Tensor.from_host(self.device_queue, y_oh)
                    return xb, yb_t
        except Exception:
            pass
        return xb, yb

    def _call_augment(self, batch, **kwargs):
        # prefer passing autocast flag if augment accepts it; otherwise fall back
        try:
            return self.augment(batch, autocast=self.autocast, **kwargs)
        except TypeError:
            return self.augment(batch, **kwargs)

    def __len__(self) -> int:
        n = len(self.dataset)
        if self.drop_last:
            return n // self.batch_size
        return (n + self.batch_size - 1) // self.batch_size
