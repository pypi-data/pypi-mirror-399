"""
Device discovery and context/queue helpers for PyOpenCL plus a lightweight CPU fallback.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple

try:
    import pyopencl as cl  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    cl = None


@dataclass
class DeviceHandle:
    platform_name: str
    device_name: str
    backend: str  # "cl" or "cpu"
    device_type: str
    context: "cl.Context"
    queue: "cl.CommandQueue"


class CPUQueue:
    """
    Minimal placeholder queue for CPU/NumPy backend.
    """

    def __init__(self, name: str = "cpu"):
        self.backend = "cpu"
        self.name = name
        self.context = None  # parity with CL queues


class DeviceManager:
    """
    Lightweight device manager to obtain a default context/queue.
    """

    def __init__(self) -> None:
        self._cache: dict[str, Optional[DeviceHandle]] = {}

    def _device_type(self, dev: "cl.Device") -> str:
        if cl is None:
            return "unknown"
        dty = getattr(dev, "type", 0)
        if dty & cl.device_type.GPU:
            return "gpu"
        if dty & cl.device_type.CPU:
            return "cpu"
        if dty & cl.device_type.ACCELERATOR:
            return "accel"
        return "other"

    def discover(self) -> List[Tuple["cl.Platform", "cl.Device"]]:
        if cl is None:
            return []
        try:
            platforms = cl.get_platforms()
        except Exception:
            return []
        pairs: List[Tuple["cl.Platform", "cl.Device"]] = []
        for plat in platforms:
            try:
                devices = plat.get_devices()
            except Exception:
                continue
            for dev in devices:
                pairs.append((plat, dev))
        return pairs

    def default(self, device: str = "auto") -> Optional[DeviceHandle]:
        cache_key = device or "auto"
        if cache_key in self._cache:
            return self._cache[cache_key]
        # Explicit CPU-backend request: return NumPy/CPU handle without requiring PyOpenCL.
        if device == "cpu":
            cpu_queue = CPUQueue()
            handle = DeviceHandle(
                platform_name="CPU",
                device_name="NumPy",
                backend="cpu",
                device_type="cpu",
                context=None,
                queue=cpu_queue,  # type: ignore[arg-type]
            )
            self._cache[cache_key] = handle
            return handle
        if cl is None:
            self._cache[cache_key] = None
            return None
        pairs = self.discover()
        if not pairs:
            self._cache[cache_key] = None
            return None
        selected = None
        if device and device != "auto":
            for plat, dev in pairs:
                if self._device_type(dev) == device:
                    selected = (plat, dev)
                    break
        if selected is None:
            # fall back to first device
            selected = pairs[0]
        plat, dev = selected
        ctx = cl.Context(devices=[dev])
        queue = cl.CommandQueue(ctx, dev)
        handle = DeviceHandle(
            platform_name=plat.name,
            device_name=dev.name,
            backend="cl",
            device_type=self._device_type(dev),
            context=ctx,
            queue=queue,
        )
        self._cache[cache_key] = handle
        return handle


manager = DeviceManager()
