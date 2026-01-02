from __future__ import annotations

from typing import Callable, Dict, List, Any

from netcl.nn.layers import Conv2d, Linear, ReLU, MaxPool2d, Flatten, Dropout, LeakyReLU, Sigmoid, Tanh, Sequential, Module
from netcl.nn.batchnorm import BatchNorm2dModule
import json
import pathlib

LayerCtor = Callable[..., Module]

_REGISTRY: Dict[str, LayerCtor] = {}
_REQUIRED_ARGS: Dict[str, List[str]] = {
    "Conv2d": ["in_channels", "out_channels", "kernel_size"],
    "Linear": ["in_features", "out_features"],
    "BatchNorm2d": ["num_features"],
}


def register_layer(name: str, ctor: LayerCtor) -> None:
    _REGISTRY[name] = ctor


def get_registry() -> Dict[str, LayerCtor]:
    return dict(_REGISTRY)


def _ensure_defaults():
    if _REGISTRY:
        return
    register_layer("Conv2d", Conv2d)
    register_layer("Linear", Linear)
    register_layer("BatchNorm2d", BatchNorm2dModule)
    register_layer("ReLU", lambda *args, **kwargs: ReLU())
    register_layer("LeakyReLU", lambda negative_slope=0.01, **kwargs: LeakyReLU(negative_slope=negative_slope))
    register_layer("Sigmoid", lambda *args, **kwargs: Sigmoid())
    register_layer("Tanh", lambda *args, **kwargs: Tanh())
    register_layer("Dropout", lambda p=0.5, seed=None, **kwargs: Dropout(p=p, seed=seed))
    register_layer("MaxPool2d", lambda kernel_size=2, stride=2, **kwargs: MaxPool2d(kernel_size=kernel_size, stride=stride))
    register_layer("Flatten", lambda *args, **kwargs: Flatten())


def _validate_config(config: List[Dict[str, Any]]):
    if not isinstance(config, list):
        raise ValueError("Config must be a list of layer definitions")
    for idx, entry in enumerate(config):
        if not isinstance(entry, dict):
            raise ValueError(f"Layer entry at index {idx} must be a dict")
        if "type" not in entry:
            raise ValueError(f"Layer entry at index {idx} missing 'type'")
        ltype = entry["type"]
        if ltype not in _REGISTRY:
            raise ValueError(f"Unknown layer type {ltype}")
        args = entry.get("args", {})
        if args is None:
            args = {}
            entry["args"] = args
        if not isinstance(args, dict):
            raise ValueError(f"Layer '{ltype}' at index {idx} has non-dict args")
        required = _REQUIRED_ARGS.get(ltype, [])
        for req in required:
            if req not in args:
                raise ValueError(f"Layer '{ltype}' at index {idx} missing required arg '{req}'")


def build_sequential(queue, config: List[Dict[str, Any]]) -> Sequential:
    """
    Build a Sequential model from a list of layer configs.
    Each config: {"type": "Conv2d", "args": {...}} where args are passed to the ctor.
    """
    _ensure_defaults()
    _validate_config(config)
    layers = []
    for entry in config:
        ltype = entry.get("type")
        args = entry.get("args", {})
        if ltype not in _REGISTRY:
            raise ValueError(f"Unknown layer type {ltype}")
        ctor = _REGISTRY[ltype]
        # inject queue if ctor expects it
        if ltype in ("Conv2d", "Linear", "BatchNorm2d"):
            layer = ctor(queue=queue, **args)
        else:
            layer = ctor(**args)
        layers.append(layer)
    return Sequential(*layers)


def build_sequential_from_json(queue, path: str | pathlib.Path) -> Sequential:
    """
    Load a JSON config file and build a Sequential model.
    JSON schema: [{"type": "Conv2d", "args": {"in_channels":3,"out_channels":32,"kernel_size":3,"stride":1,"pad":1}}, ...]
    """
    p = pathlib.Path(path)
    data = json.loads(p.read_text())
    if not isinstance(data, list):
        raise ValueError("JSON config must be a list of layer definitions")
    return build_sequential(queue, data)


def example_cnn_config(in_ch: int = 3, num_classes: int = 10) -> List[Dict[str, Any]]:
    """
    Simple CNN config: Conv-ReLU-Pool x2 -> Flatten -> Linear.
    """
    return [
        {"type": "Conv2d", "args": {"in_channels": in_ch, "out_channels": 32, "kernel_size": 3, "stride": 1, "pad": 1}},
        {"type": "ReLU"},
        {"type": "MaxPool2d", "args": {"kernel_size": 2, "stride": 2}},
        {"type": "Conv2d", "args": {"in_channels": 32, "out_channels": 64, "kernel_size": 3, "stride": 1, "pad": 1}},
        {"type": "ReLU"},
        {"type": "MaxPool2d", "args": {"kernel_size": 2, "stride": 2}},
        {"type": "Flatten"},
        {"type": "Linear", "args": {"in_features": 64 * 8 * 8, "out_features": num_classes}},
    ]


def fast_cnn_config(in_ch: int = 3, num_classes: int = 10, c1: int = 16, c2: int = 32) -> List[Dict[str, Any]]:
    """
    Fast CIFAR-10 CNN: small channels, two blocks, minimal compute.
    """
    return [
        {"type": "Conv2d", "args": {"in_channels": in_ch, "out_channels": c1, "kernel_size": 3, "stride": 1, "pad": 1}},
        {"type": "ReLU"},
        {"type": "Conv2d", "args": {"in_channels": c1, "out_channels": c1, "kernel_size": 3, "stride": 1, "pad": 1}},
        {"type": "ReLU"},
        {"type": "MaxPool2d", "args": {"kernel_size": 2, "stride": 2}},
        {"type": "Conv2d", "args": {"in_channels": c1, "out_channels": c2, "kernel_size": 3, "stride": 1, "pad": 1}},
        {"type": "ReLU"},
        {"type": "MaxPool2d", "args": {"kernel_size": 2, "stride": 2}},
        {"type": "Flatten"},
        {"type": "Linear", "args": {"in_features": c2 * 8 * 8, "out_features": num_classes}},
    ]


def fast_bn_cnn_config(in_ch: int = 3, num_classes: int = 10, c1: int = 32, c2: int = 64, p: float = 0.3) -> List[Dict[str, Any]]:
    """
    Fast CNN with BatchNorm for better generalization on small CIFAR-10 subsets.
    """
    return [
        {"type": "Conv2d", "args": {"in_channels": in_ch, "out_channels": c1, "kernel_size": 3, "stride": 1, "pad": 1}},
        {"type": "BatchNorm2d", "args": {"num_features": c1}},
        {"type": "ReLU"},
        {"type": "Conv2d", "args": {"in_channels": c1, "out_channels": c1, "kernel_size": 3, "stride": 1, "pad": 1}},
        {"type": "BatchNorm2d", "args": {"num_features": c1}},
        {"type": "ReLU"},
        {"type": "MaxPool2d", "args": {"kernel_size": 2, "stride": 2}},
        {"type": "Conv2d", "args": {"in_channels": c1, "out_channels": c2, "kernel_size": 3, "stride": 1, "pad": 1}},
        {"type": "BatchNorm2d", "args": {"num_features": c2}},
        {"type": "ReLU"},
        {"type": "MaxPool2d", "args": {"kernel_size": 2, "stride": 2}},
        {"type": "Flatten"},
        {"type": "Dropout", "args": {"p": p}},
        {"type": "Linear", "args": {"in_features": c2 * 8 * 8, "out_features": num_classes}},
    ]


def tiny_cnn_config(in_ch: int = 3, num_classes: int = 10, c1: int = 8, c2: int = 16) -> List[Dict[str, Any]]:
    """
    Tiny CIFAR-10 CNN: fastest sanity-check model.
    """
    return [
        {"type": "Conv2d", "args": {"in_channels": in_ch, "out_channels": c1, "kernel_size": 3, "stride": 1, "pad": 1}},
        {"type": "ReLU"},
        {"type": "MaxPool2d", "args": {"kernel_size": 2, "stride": 2}},
        {"type": "Conv2d", "args": {"in_channels": c1, "out_channels": c2, "kernel_size": 3, "stride": 1, "pad": 1}},
        {"type": "ReLU"},
        {"type": "MaxPool2d", "args": {"kernel_size": 2, "stride": 2}},
        {"type": "Flatten"},
        {"type": "Linear", "args": {"in_features": c2 * 8 * 8, "out_features": num_classes}},
    ]


def big_cnn_config(
    in_ch: int = 3,
    num_classes: int = 10,
    c1: int = 64,
    c2: int = 128,
    c3: int = 256,
    p: float = 0.5,
) -> List[Dict[str, Any]]:
    """
    Larger CNN for stronger learning signal on CIFAR-10.
    """
    return [
        {"type": "Conv2d", "args": {"in_channels": in_ch, "out_channels": c1, "kernel_size": 3, "stride": 1, "pad": 1}},
        {"type": "BatchNorm2d", "args": {"num_features": c1}},
        {"type": "ReLU"},
        {"type": "Conv2d", "args": {"in_channels": c1, "out_channels": c1, "kernel_size": 3, "stride": 1, "pad": 1}},
        {"type": "BatchNorm2d", "args": {"num_features": c1}},
        {"type": "ReLU"},
        {"type": "MaxPool2d", "args": {"kernel_size": 2, "stride": 2}},
        {"type": "Conv2d", "args": {"in_channels": c1, "out_channels": c2, "kernel_size": 3, "stride": 1, "pad": 1}},
        {"type": "BatchNorm2d", "args": {"num_features": c2}},
        {"type": "ReLU"},
        {"type": "Conv2d", "args": {"in_channels": c2, "out_channels": c2, "kernel_size": 3, "stride": 1, "pad": 1}},
        {"type": "BatchNorm2d", "args": {"num_features": c2}},
        {"type": "ReLU"},
        {"type": "MaxPool2d", "args": {"kernel_size": 2, "stride": 2}},
        {"type": "Conv2d", "args": {"in_channels": c2, "out_channels": c3, "kernel_size": 3, "stride": 1, "pad": 1}},
        {"type": "BatchNorm2d", "args": {"num_features": c3}},
        {"type": "ReLU"},
        {"type": "MaxPool2d", "args": {"kernel_size": 2, "stride": 2}},
        {"type": "Flatten"},
        {"type": "Dropout", "args": {"p": p}},
        {"type": "Linear", "args": {"in_features": c3 * 4 * 4, "out_features": num_classes}},
    ]


def example_mlp_config(input_dim: int, hidden: int = 128, num_classes: int = 10) -> List[Dict[str, Any]]:
    """
    Simple MLP config: Linear-ReLU-Linear.
    """
    return [
        {"type": "Linear", "args": {"in_features": input_dim, "out_features": hidden}},
        {"type": "ReLU"},
        {"type": "Linear", "args": {"in_features": hidden, "out_features": num_classes}},
    ]
