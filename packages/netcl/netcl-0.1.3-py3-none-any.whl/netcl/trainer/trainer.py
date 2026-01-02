from __future__ import annotations

import time
from typing import Optional, Sequence, Callable, Any

import numpy as np

from netcl.core.tensor import Tensor
from netcl import autograd as ag
from netcl.optim import AMPGradScaler, clip_grad_norm
from netcl.amp import autocast
from netcl.utils import ProgressBar
from netcl.core.device import manager
from netcl.core.backend import get_backend


class Trainer:
    def __init__(
        self,
        model: Callable,
        optimizer,
        device_queue=None,
        mixed_precision: bool = False,
        grad_clip: Optional[float] = None,
        loss_fn: Callable | None = None,
        metrics_stride: int = 10,
    ):
        self.model = model
        self.optimizer = optimizer
        if device_queue is None:
            dev = manager.default()
            if dev is None:
                raise RuntimeError("No OpenCL device available")
            self.queue = dev.queue
        else:
            self.queue = device_queue
        self.backend = getattr(self.queue, "backend", "cl")
        if self.backend == "cpu" and mixed_precision:
            print("Info: disabling mixed_precision on CPU backend.")
            mixed_precision = False
        self.mixed_precision = mixed_precision
        self.grad_clip = grad_clip
        self.scaler = AMPGradScaler(init_scale=2.0**12) if mixed_precision else None
        self.loss_fn = loss_fn
        self.metrics_stride = max(1, int(metrics_stride))

    def fit(
        self,
        train_loader,
        val_loader=None,
        epochs: int = 1,
        loss_fn: Callable = None,
        log_every: int = 1,
    ):
        if loss_fn is None:
            loss_fn = self.loss_fn
        if loss_fn is None:
            from netcl.nn import functional

            loss_fn = functional.cross_entropy
        for epoch in range(1, epochs + 1):
            t0 = time.perf_counter()
            self._set_training(True)
            pb = ProgressBar(total=len(train_loader), epoch=epoch)
            train_loss = 0.0
            total = 0
            correct = 0
            samples_seen = 0
            metrics_stride = max(1, getattr(self, "metrics_stride", 1))
            last_info = {}
            for i, (xb, yb) in enumerate(train_loader):
                logits, loss, tape = self._forward_backward(xb, yb, loss_fn)
                self._step()
                batch_size = xb.shape[0] if hasattr(xb, "shape") else len(xb)
                samples_seen += int(batch_size)
                if (i % metrics_stride) == 0:
                    loss_host = float(loss.value.to_host()[0])
                    if not np.isfinite(loss_host):
                        raise RuntimeError(f"non-finite loss at step {i}")
                    logits_host = logits.value.to_host()
                    labels = yb
                    if isinstance(labels, Tensor):
                        labels = labels.array if (get_backend(labels) == "cpu" and labels.array is not None) else labels.to_host()
                    labels = labels if labels.ndim == 1 else np.argmax(labels, axis=1)
                    preds = np.argmax(logits_host, axis=1)
                    correct += int((preds == labels).sum())
                    total += labels.size
                    train_loss += loss_host
                    last_info = {"loss": f"{loss_host:.3f}", "acc": f"{(preds==labels).mean()*100:.1f}%"}
                pb.update(i + 1, last_info)
            pb.close()
            elapsed = time.perf_counter() - t0
            acc = correct / max(1, total) if total > 0 else 0.0
            denom = max(1, (len(train_loader) // metrics_stride))
            avg_loss = train_loss / denom
            print(f"Epoch {epoch}: train_loss={avg_loss:.4f} acc={acc*100:.2f}% throughput={samples_seen/elapsed:.1f} img/s")
            if val_loader and epoch % log_every == 0:
                self.evaluate(val_loader, loss_fn=loss_fn)

    def evaluate(self, data_loader, loss_fn: Callable):
        prev = self._get_training_state()
        self._set_training(False)
        if loss_fn is None:
            loss_fn = self.loss_fn
        if loss_fn is None:
            from netcl.nn import functional

            loss_fn = functional.cross_entropy
        total = 0
        correct = 0
        loss_total = 0.0
        for xb, yb in data_loader:
            logits, loss, _ = self._forward(xb, yb, loss_fn)
            loss_val = float(loss.value.to_host()[0])
            if not np.isfinite(loss_val):
                raise RuntimeError("non-finite loss during evaluation")
            loss_total += loss_val
            logits_host = logits.value.to_host()
            labels = yb
            if isinstance(labels, Tensor):
                labels = labels.array if (get_backend(labels) == "cpu" and labels.array is not None) else labels.to_host()
            labels = labels if labels.ndim == 1 else np.argmax(labels, axis=1)
            preds = np.argmax(logits_host, axis=1)
            correct += int((preds == labels).sum())
            total += labels.size
        print(f"Val: loss={loss_total/len(data_loader):.4f} acc={correct/max(1,total)*100:.2f}%")
        if prev is not None:
            self._set_training(prev)

    def _get_training_state(self):
        return getattr(self.model, "training", None)

    def _set_training(self, mode: bool):
        if hasattr(self.model, "train") and callable(getattr(self.model, "train")):
            try:
                self.model.train(mode)
                return
            except TypeError:
                if mode:
                    self.model.train()
                elif hasattr(self.model, "eval") and callable(getattr(self.model, "eval")):
                    self.model.eval()
                else:
                    self.model.train()
                return
        if hasattr(self.model, "training"):
            self.model.training = mode

    def _forward(self, xb, yb, loss_fn: Callable):
        tape = ag.Tape()
        ag.set_current_tape(tape)
        try:
            # Handle both Tensor and numpy array inputs
            if isinstance(xb, Tensor):
                x_tensor = xb
            else:
                x_tensor = Tensor.from_host(self.queue, xb, backend=getattr(self.queue, "backend", "cl"))
            x_node = ag.tensor(x_tensor)
            with autocast(enabled=self.mixed_precision, device_queue=self.queue):
                logits_raw = self.model(x_node)
                # accept Tensor or Node
                if hasattr(logits_raw, "value"):
                    logits_tensor = logits_raw.value
                    logits_node = logits_raw
                    logits_node.requires_grad = True
                else:
                    logits_tensor = logits_raw
                    logits_node = ag.tensor(logits_tensor, requires_grad=True)
                y_onehot = self._prepare_labels(yb, logits_tensor.shape[1])
                loss = loss_fn(logits_node, y_onehot)
            return logits_node, loss, tape
        finally:
            ag.set_current_tape(None)

    def _forward_backward(self, xb, yb, loss_fn: Callable):
        logits, loss, tape = self._forward(xb, yb, loss_fn)
        loss_to_backprop = loss
        if self.mixed_precision and self.scaler:
            loss_to_backprop = self._scale_loss_node(loss, float(self.scaler.scale))
        tape.backward(loss_to_backprop)
        return logits, loss, tape

    def _prepare_labels(self, yb, num_classes: int):
        """
        Accept int labels or one-hot in numpy/Tensor, return autograd tensor on the correct backend.
        """
        backend = getattr(self.queue, "backend", "cl")
        if isinstance(yb, Tensor):
            if len(yb.shape) == 1:
                y_array = yb.array if (get_backend(yb) == "cpu" and yb.array is not None) else yb.to_host()
                self._validate_label_range(y_array, num_classes)
                y_oh = np.eye(num_classes, dtype=np.float32)[y_array.astype(np.int64)]
                return ag.tensor(Tensor.from_host(self.queue, y_oh, backend=backend))
            # handle one-hot tensors that might have fewer columns than num_classes (e.g., limited class subset)
            if len(yb.shape) == 2 and yb.shape[1] != num_classes:
                y_array = yb.array if (get_backend(yb) == "cpu" and yb.array is not None) else yb.to_host()
                labels = np.argmax(y_array, axis=1)
                self._validate_label_range(labels, num_classes)
                y_oh = np.eye(num_classes, dtype=np.float32)[labels.astype(np.int64)]
                return ag.tensor(Tensor.from_host(self.queue, y_oh, backend=backend))
            return ag.tensor(yb)
        y_array = np.asarray(yb)
        if y_array.ndim == 1:
            self._validate_label_range(y_array, num_classes)
            y_oh = np.eye(num_classes, dtype=np.float32)[y_array.astype(np.int64)]
            return ag.tensor(Tensor.from_host(self.queue, y_oh, backend=backend))
        if y_array.ndim == 2 and y_array.shape[1] != num_classes:
            labels = np.argmax(y_array, axis=1)
            self._validate_label_range(labels, num_classes)
            y_array = np.eye(num_classes, dtype=np.float32)[labels.astype(np.int64)]
        return ag.tensor(Tensor.from_host(self.queue, y_array, backend=backend))

    def _validate_label_range(self, labels, num_classes: int) -> None:
        if labels.size == 0:
            raise ValueError("empty labels")
        min_val = int(np.min(labels))
        max_val = int(np.max(labels))
        if min_val < 0 or max_val >= num_classes:
            raise ValueError(f"label out of range: min={min_val} max={max_val} classes={num_classes}")

    def _scale_loss_node(self, loss_node, scale: float):
        from netcl.ops.elementwise import elementwise_binary

        def forward(tensor_val):
            return elementwise_binary(tensor_val, tensor_val, expression=f"MUL(v0, {scale})")

        def grad_fn(grad_out):
            return [elementwise_binary(grad_out, grad_out, expression=f"MUL(v0, {scale})")]

        return ag.apply_op(forward, grad_fn, loss_node)

    def _step(self):
        params = getattr(self.optimizer, "params", None) or []
        if self.mixed_precision and self.scaler:
            found_inf = self.scaler.unscale_grads(params)
            if not found_inf:
                if self.grad_clip is not None:
                    clip_grad_norm(params, self.grad_clip)
                self.optimizer.step()
                self.scaler._growth_tracker += 1
                if self.scaler._growth_tracker % self.scaler.growth_interval == 0:
                    self.scaler._scale *= self.scaler.growth_factor
            else:
                self.scaler._scale *= self.scaler.backoff_factor
                self.scaler._growth_tracker = 0
            self.optimizer.zero_grad()
            return
        if self.grad_clip is not None:
            clip_grad_norm(params, self.grad_clip)
        self.optimizer.step()
        self.optimizer.zero_grad()
