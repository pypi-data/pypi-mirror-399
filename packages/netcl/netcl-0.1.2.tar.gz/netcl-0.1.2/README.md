# netcl

netcl is an experimental PyOpenCL + NumPy deep learning library. It provides low-level kernels, a minimal autograd engine, and a small high-level API (layers, trainer, optimizers). This README reflects the current API.

## Quickstart (MNIST-style MLP)
```python
import numpy as np
from netcl.core.device import manager
from netcl.nn.layers import Sequential, Flatten, Linear, ReLU
from netcl.nn import functional
from netcl.optim import Adam
from netcl.trainer import Trainer
from netcl.data.dataloader import DataLoader

# Select GPU or CPU backend
queue = manager.default(device="gpu").queue  # or device="cpu"

model = Sequential(
    Flatten(),
    Linear(queue, 28 * 28, 128),
    ReLU(),
    Linear(queue, 128, 10),
)

opt = Adam(model.parameters(), lr=1e-3)
trainer = Trainer(model, opt, device_queue=queue)

# Toy dataset of individual samples
x = np.random.randn(256, 1, 28, 28).astype(np.float32)
y = np.random.randint(0, 10, size=(256,))
loader = DataLoader(list(zip(x, y)), batch_size=32, shuffle=True, device_queue=queue)

trainer.fit(loader, epochs=1, loss_fn=functional.cross_entropy)
```

## Current API Highlights
- **Core**: `manager.default(device="gpu"|"cpu")`, `Tensor.from_host`, `Tensor.from_shape`, `BufferPool`.
- **Ops**: `matmul`, `conv2d`, `depthwise_conv2d`, `conv_transpose2d`, elementwise ops, reduction, softmax, padding.
- **Autograd**: `Tape`/`Node` plus `batch_norm2d`, `layer_norm`, `group_norm`, pooling, dropout, and losses (`mse`, `cross_entropy`, `hinge`, `l1`, `l2`).
- **NN**: `Linear`, `Conv2d`, `BatchNorm2d`, `Sequential`, `build_sequential` configs.
- **Optim**: `SGD`, `Momentum`, `Adam`, `AdamW`, `RMSProp`, `WarmupCosine`, `ReduceLROnPlateau`, `clip_grad_norm`, `AMPGradScaler`.
- **Data**: `DataLoader` with prefetch, optional async device transfer, and CPU transforms.
- **IO**: `save_model`/`load_model` for `Sequential` models with layers: `Conv2d`, `Linear`, `ReLU`, `LeakyReLU`, `Sigmoid`, `Tanh`, `Dropout`, `MaxPool2d`, `Flatten`.

## Notes
- Mixed precision is experimental; disable it on the CPU backend.
- Conv2d has multiple algorithms and optional autotune via env flags (see `netcl/ops/conv2d.py`).
- BatchNorm uses running stats; call `model.eval()` for inference.

## Docs
- `README_PACKAGE.md` for the package summary used on PyPI.
- `wiki/README.md` for a compact API index and examples.
