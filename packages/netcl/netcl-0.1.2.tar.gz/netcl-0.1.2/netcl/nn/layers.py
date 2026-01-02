from __future__ import annotations

from typing import List, Sequence

from netcl.core.tensor import Tensor
from netcl.core.parameter import Parameter
from netcl.ops.matmul import matmul
from netcl.ops import bias_add as bias_add  # bias_add exposed via ops
from netcl.ops.elementwise import relu as relu_op, sigmoid as sigmoid_op, tanh as tanh_op, leaky_relu as leaky_relu_op, dropout as dropout_op
from netcl.ops.conv2d import conv2d
from netcl.nn.pooling import max_pool2d as max_pool2d_op
def flatten_op(x: Tensor, shape):
    # use autograd flatten via ops import to avoid circular import at module import time
    from netcl.core.tensor import reshape as tensor_reshape

    return tensor_reshape(x, shape)
from netcl.core.memory import BufferPool
from netcl.nn import init as init_ops
import numpy as np


class Module:
    """
    Lightweight base with recursive parameter collection. Subclasses can override
    if they need custom behaviour, otherwise all Tensors stored on attributes /
    in containers (list/tuple/dict/set) are collected automatically.
    """

    def _collect_params(self, obj, seen: set[int]) -> List[Tensor]:
        if id(obj) in seen:
            return []
        seen.add(id(obj))
        params: List[Tensor] = []
        if isinstance(obj, Parameter):
            params.append(obj)
            return params
        if isinstance(obj, Tensor) and getattr(obj, "requires_grad", False):
            params.append(obj)
            return params
        if isinstance(obj, Module):
            for v in obj.__dict__.values():
                params.extend(self._collect_params(v, seen))
            return params
        if isinstance(obj, (list, tuple, set)):
            for v in obj:
                params.extend(self._collect_params(v, seen))
            return params
        if isinstance(obj, dict):
            for v in obj.values():
                params.extend(self._collect_params(v, seen))
            return params
        return params

    def parameters(self) -> List[Tensor]:
        return self._collect_params(self, set())

    def state_dict(self) -> dict:
        raise NotImplementedError

    def load_state_dict(self, state: dict) -> None:
        raise NotImplementedError

    def train(self, mode: bool = True):
        self.training = mode
        for v in self.__dict__.values():
            if isinstance(v, Module):
                v.train(mode)
            elif isinstance(v, (list, tuple, set)):
                for it in v:
                    if isinstance(it, Module):
                        it.train(mode)
            elif isinstance(v, dict):
                for it in v.values():
                    if isinstance(it, Module):
                        it.train(mode)
        return self

    def eval(self):
        return self.train(False)

    def __call__(self, *args, **kwargs):
        return self.forward(*args, **kwargs)

    def forward(self, *args, **kwargs):
        raise NotImplementedError


from netcl.core.device import manager, CPUQueue
class Linear(Module):
    def __init__(self, queue=None, in_features: int = None, out_features: int = None, bias: bool = True, pool: BufferPool | None = None, device: str | None = None, backend: str | None = None):
        if queue is None:
            backend = backend or ("cpu" if device == "cpu" else "cl")
            if backend == "cpu":
                queue = CPUQueue()
            else:
                dev = manager.default(device=device or "auto")
                if dev is None:
                    raise RuntimeError("No OpenCL device available")
                queue = dev.queue
        self.queue = queue
        self.in_features = in_features
        self.out_features = out_features
        self.pool = pool
        self.weight = Parameter.from_shape(queue, (in_features, out_features), dtype="float32", pool=pool)
        init_ops.xavier_uniform(self.weight)
        self.bias = None
        if bias:
            self.bias = Parameter.from_shape(queue, (out_features,), dtype="float32", pool=pool)
            init_ops.xavier_uniform(self.bias)

    def forward(self, x):
        use_autograd = hasattr(x, "value")
        if use_autograd:
            from netcl import autograd as ag

            x_node = x if hasattr(x, "value") else ag.tensor(x)
            w_node = ag.tensor(self.weight, requires_grad=True)
            out = ag.matmul_op(x_node, w_node)
            if self.bias is not None:
                b_node = ag.tensor(self.bias, requires_grad=True)
                out = ag.bias_add(out, b_node)
            return out
        # no autograd path
        out = matmul(x, self.weight, pool=self.pool)
        if self.bias is not None:
            out = bias_add(out, self.bias, pool=self.pool)
        return out

    def parameters(self) -> List[Tensor]:
        params = [self.weight]
        if self.bias is not None:
            params.append(self.bias)
        return params

    def state_dict(self) -> dict:
        return {
            "weight": self.weight.to_host(),
            "bias": None if self.bias is None else self.bias.to_host(),
            "in_features": self.in_features,
            "out_features": self.out_features,
        }

    def load_state_dict(self, state: dict) -> None:
        if "weight" in state:
            if getattr(self.weight, "backend", "cl") == "cpu":
                self.weight.array[...] = state["weight"]
            else:
                import pyopencl as cl
                cl.enqueue_copy(self.queue, self.weight.buffer, state["weight"]).wait()
        if self.bias is not None and state.get("bias") is not None:
            if getattr(self.bias, "backend", "cl") == "cpu":
                self.bias.array[...] = state["bias"]
            else:
                import pyopencl as cl
                cl.enqueue_copy(self.queue, self.bias.buffer, state["bias"]).wait()


class ReLU(Module):
    def forward(self, x):
        if hasattr(x, "value"):
            from netcl import autograd as ag

            x_node = x if hasattr(x, "value") else ag.tensor(x)
            return ag.relu(x_node)
        return relu_op(x)

    def parameters(self) -> List[Tensor]:
        return []

    def state_dict(self) -> dict:
        return {}

    def load_state_dict(self, state: dict) -> None:
        return


class Sigmoid(Module):
    def forward(self, x):
        if hasattr(x, "value"):
            from netcl import autograd as ag

            x_node = x if hasattr(x, "value") else ag.tensor(x)
            return ag.sigmoid(x_node)
        return sigmoid_op(x)

    def parameters(self) -> List[Tensor]:
        return []

    def state_dict(self) -> dict:
        return {}

    def load_state_dict(self, state: dict) -> None:
        return


class Tanh(Module):
    def forward(self, x):
        if hasattr(x, "value"):
            from netcl import autograd as ag

            x_node = x if hasattr(x, "value") else ag.tensor(x)
            return ag.tanh(x_node)
        return tanh_op(x)

    def parameters(self) -> List[Tensor]:
        return []

    def state_dict(self) -> dict:
        return {}

    def load_state_dict(self, state: dict) -> None:
        return


class LeakyReLU(Module):
    def __init__(self, negative_slope: float = 0.01):
        self.negative_slope = negative_slope

    def forward(self, x):
        if hasattr(x, "value"):
            from netcl import autograd as ag

            x_node = x if hasattr(x, "value") else ag.tensor(x)
            return ag.leaky_relu(x_node, negative_slope=self.negative_slope)
        return leaky_relu_op(x, negative_slope=self.negative_slope)

    def parameters(self) -> List[Tensor]:
        return []

    def state_dict(self) -> dict:
        return {"negative_slope": self.negative_slope}

    def load_state_dict(self, state: dict) -> None:
        self.negative_slope = state.get("negative_slope", self.negative_slope)


class Dropout(Module):
    def __init__(self, p: float = 0.5, seed: int | None = None):
        self.p = p
        self.seed = seed
        self.training = True

    def forward(self, x):
        if hasattr(self, "training") and not self.training:
            return x
        if hasattr(x, "value"):
            from netcl import autograd as ag

            x_node = x if hasattr(x, "value") else ag.tensor(x)
            return ag.dropout(x_node, p=self.p, seed=self.seed)
        return dropout_op(x, p=self.p, seed=self.seed)

    def parameters(self) -> List[Tensor]:
        return []

    def state_dict(self) -> dict:
        return {"p": self.p, "seed": self.seed}

    def load_state_dict(self, state: dict) -> None:
        self.p = state.get("p", self.p)
        self.seed = state.get("seed", self.seed)


class MaxPool2d(Module):
    def __init__(self, kernel_size: int = 2, stride: int = 2):
        self.kernel_size = kernel_size
        self.stride = stride

    def forward(self, x):
        if hasattr(x, "value"):
            from netcl import autograd as ag

            x_node = x if hasattr(x, "value") else ag.tensor(x)
            return ag.max_pool2d(x_node, kernel_size=self.kernel_size, stride=self.stride)
        return max_pool2d_op(x, kernel_size=self.kernel_size, stride=self.stride)

    def parameters(self) -> List[Tensor]:
        return []

    def state_dict(self) -> dict:
        return {"kernel_size": self.kernel_size, "stride": self.stride}

    def load_state_dict(self, state: dict) -> None:
        self.kernel_size = state.get("kernel_size", self.kernel_size)
        self.stride = state.get("stride", self.stride)


class Flatten(Module):
    def forward(self, x):
        if hasattr(x, "value"):
            from netcl import autograd as ag

            x_node = x if hasattr(x, "value") else ag.tensor(x)
            shape = x_node.value.shape
            return ag.flatten(x_node, (shape[0], int(np.prod(shape[1:]))))
        shape = x.shape
        return flatten_op(x, (shape[0], int(np.prod(shape[1:]))))

    def parameters(self) -> List[Tensor]:
        return []

    def state_dict(self) -> dict:
        return {}

    def load_state_dict(self, state: dict) -> None:
        return


class Conv2d(Module):
    def __init__(
        self,
        queue=None,
        in_channels: int = None,
        out_channels: int = None,
        kernel_size: int = None,
        stride: int = 1,
        pad: int = 0,
        bias: bool = True,
        pool: BufferPool | None = None,
        device: str | None = None,
        backend: str | None = None,
    ) -> None:
        if queue is None:
            backend = backend or ("cpu" if device == "cpu" else "cl")
            if backend == "cpu":
                queue = CPUQueue()
            else:
                dev = manager.default(device=device or "auto")
                if dev is None:
                    raise RuntimeError("No OpenCL device available")
                queue = dev.queue
        self.queue = queue
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.kernel_size = kernel_size
        self.stride = stride
        self.pad = pad
        self.pool = pool
        self.weight = Parameter.from_shape(queue, (out_channels, in_channels, kernel_size, kernel_size), pool=pool)
        init_ops.kaiming_uniform(self.weight)
        self.bias = Parameter.from_shape(queue, (out_channels,), pool=pool) if bias else None
        if self.bias is not None:
            init_ops.kaiming_uniform(self.bias)

    def forward(self, x, tape=None):
        use_autograd = hasattr(x, "value")
        if use_autograd:
            from netcl import autograd as ag

            x_node = x if hasattr(x, "value") else ag.tensor(x)
            w_node = ag.tensor(self.weight, requires_grad=True)
            b_node = ag.tensor(self.bias, requires_grad=True) if self.bias is not None else None
            return ag.conv2d(x_node, w_node, bias=b_node, stride=self.stride, pad=self.pad)
        return conv2d(x, self.weight, bias=self.bias, pool=self.pool, stride=self.stride, pad=self.pad)

    def parameters(self) -> List[Tensor]:
        params = [self.weight]
        if self.bias is not None:
            params.append(self.bias)
        return params

    def state_dict(self) -> dict:
        return {
            "weight": self.weight.to_host(),
            "bias": None if self.bias is None else self.bias.to_host(),
            "in_channels": self.in_channels,
            "out_channels": self.out_channels,
            "kernel_size": self.kernel_size,
            "stride": self.stride,
            "pad": self.pad,
        }

    def load_state_dict(self, state: dict) -> None:
        if getattr(self.weight, "backend", "cl") == "cpu":
            self.weight.array[...] = state["weight"]
        else:
            import pyopencl as cl
            cl.enqueue_copy(self.queue, self.weight.buffer, state["weight"]).wait()
        if self.bias is not None and state.get("bias") is not None:
            if getattr(self.bias, "backend", "cl") == "cpu":
                self.bias.array[...] = state["bias"]
            else:
                import pyopencl as cl
                cl.enqueue_copy(self.queue, self.bias.buffer, state["bias"]).wait()


class Sequential(Module):
    """
    Sequential container with optional layer fusion for inference.
    Automatically fuses Conv2d+BatchNorm+ReLU patterns when training=False.
    """
    def __init__(self, *layers: Module):
        self.layers = list(layers)
        self._fused_layers = None
        self._training = True
    
    def train(self, mode: bool = True):
        """Set training mode. Clears fusion cache when switching modes."""
        if self._training != mode:
            self._fused_layers = None
        self._training = mode
        for layer in self.layers:
            if hasattr(layer, "train") and callable(getattr(layer, "train")):
                try:
                    layer.train(mode)
                except TypeError:
                    layer.train()
            elif hasattr(layer, "training"):
                layer.training = mode
        return self
    
    def eval(self):
        """Set evaluation mode and enable layer fusion."""
        return self.train(False)

    @property
    def training(self) -> bool:
        return self._training

    @training.setter
    def training(self, mode: bool) -> None:
        self.train(mode)
    
    def _try_fuse_layers(self):
        """Attempt to fuse Conv+BN+ReLU patterns for inference."""
        if self._fused_layers is not None:
            return self._fused_layers
        
        try:
            from netcl.ops.fused_ops import fuse_conv_bn_relu, fold_bn_into_conv
        except ImportError:
            self._fused_layers = self.layers
            return self._fused_layers
        
        fused = []
        i = 0
        while i < len(self.layers):
            layer = self.layers[i]
            # Try Conv2d + BatchNorm2d + ReLU fusion
            if (isinstance(layer, Conv2d) and 
                i + 2 < len(self.layers)):
                next1 = self.layers[i + 1]
                next2 = self.layers[i + 2]
                # Check for BatchNorm2d (simplified check)
                if (hasattr(next1, 'running_mean') and hasattr(next1, 'running_var') and
                    isinstance(next2, ReLU)):
                    # Create fused layer wrapper
                    fused.append(_FusedConvBNReLU(layer, next1))
                    i += 3
                    continue
            # Try Conv2d + ReLU fusion (simpler case)
            if isinstance(layer, Conv2d) and i + 1 < len(self.layers):
                next1 = self.layers[i + 1]
                if isinstance(next1, ReLU):
                    fused.append(_FusedConvReLU(layer))
                    i += 2
                    continue
            fused.append(layer)
            i += 1
        
        self._fused_layers = fused
        return fused

    def forward(self, x):
        out = x
        # Use fused layers in eval mode
        layers = self._try_fuse_layers() if not self._training else self.layers
        for layer in layers:
            try:
                out = layer(out)
            except TypeError:
                out = layer(out)
        return out

    def parameters(self) -> List[Tensor]:
        params: List[Tensor] = []
        for layer in self.layers:
            params.extend(layer.parameters())
        return params

    def state_dict(self) -> dict:
        return {"layers": [layer.state_dict() for layer in self.layers], "types": [layer.__class__.__name__ for layer in self.layers]}

    def load_state_dict(self, state: dict) -> None:
        for layer, sd in zip(self.layers, state["layers"]):
            layer.load_state_dict(sd)

class _FusedConvReLU(Module):
    """Internal fused Conv2d + ReLU layer for inference."""
    def __init__(self, conv_layer: Conv2d):
        self.conv = conv_layer
    
    def forward(self, x):
        try:
            from netcl.ops.fused_ops import conv_relu_fused
            return conv_relu_fused(
                x, self.conv.weight, 
                bias=self.conv.bias,
                stride=self.conv.stride, 
                pad=self.conv.pad
            )
        except (ImportError, Exception):
            # Fallback to sequential execution
            out = conv2d(x, self.conv.weight, bias=self.conv.bias, 
                        stride=self.conv.stride, pad=self.conv.pad)
            return relu_op(out)
    
    def parameters(self):
        return self.conv.parameters()


class _FusedConvBNReLU(Module):
    """Internal fused Conv2d + BatchNorm2d + ReLU layer for inference."""
    def __init__(self, conv_layer: Conv2d, bn_layer):
        self.conv = conv_layer
        self.bn = bn_layer
        self._folded_weight = None
        self._folded_bias = None
    
    def _fold_bn(self):
        """Fold BatchNorm parameters into Conv weights (inference only)."""
        if self._folded_weight is not None:
            return
        try:
            from netcl.ops.fused_ops import fold_bn_into_conv
            self._folded_weight, self._folded_bias = fold_bn_into_conv(
                self.conv.weight, self.conv.bias,
                self.bn.running_mean, self.bn.running_var,
                self.bn.gamma if hasattr(self.bn, 'gamma') else None,
                self.bn.beta if hasattr(self.bn, 'beta') else None,
                self.bn.eps if hasattr(self.bn, 'eps') else 1e-5
            )
        except Exception:
            self._folded_weight = self.conv.weight
            self._folded_bias = self.conv.bias
    
    def forward(self, x):
        self._fold_bn()
        try:
            from netcl.ops.fused_ops import conv_relu_fused
            return conv_relu_fused(
                x, self._folded_weight,
                bias=self._folded_bias,
                stride=self.conv.stride,
                pad=self.conv.pad
            )
        except (ImportError, Exception):
            out = conv2d(x, self._folded_weight, bias=self._folded_bias,
                        stride=self.conv.stride, pad=self.conv.pad)
            return relu_op(out)
    
    def parameters(self):
        return self.conv.parameters() + self.bn.parameters() if hasattr(self.bn, 'parameters') else self.conv.parameters()
