"""
Autotuner for kernel selection.

Provides runtime profiling and automatic kernel selection based on measured performance.
Caches optimal configurations per problem size and device.
"""

from __future__ import annotations

import os
import json
import time
import hashlib
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Tuple, Any
from pathlib import Path

try:
    import numpy as np
except ImportError:
    np = None

try:
    import pyopencl as cl
except ImportError:
    cl = None

from netcl.core.tensor import Tensor


@dataclass
class TuningResult:
    """Result of a kernel tuning run."""
    kernel_name: str
    time_ms: float
    gflops: Optional[float] = None
    params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TuningConfig:
    """Configuration for autotuning."""
    warmup_runs: int = 3
    benchmark_runs: int = 5
    min_time_ms: float = 0.01
    cache_dir: Optional[str] = None
    enable_cache: bool = True


class KernelProfiler:
    """
    Profiles kernel execution times using OpenCL events.
    """
    
    def __init__(self, queue: "cl.CommandQueue"):
        self.queue = queue
        self._event_stack: List["cl.Event"] = []
    
    def time_kernel(
        self,
        kernel_fn: Callable,
        *args,
        warmup: int = 3,
        runs: int = 5,
        **kwargs
    ) -> float:
        """
        Time a kernel function with warmup and multiple runs.
        Returns median time in milliseconds.
        """
        if cl is None:
            return 0.0
        
        times = []
        
        # Warmup
        for _ in range(warmup):
            result = kernel_fn(*args, **kwargs)
            self.queue.finish()
        
        # Timed runs
        for _ in range(runs):
            start = time.perf_counter()
            result = kernel_fn(*args, **kwargs)
            self.queue.finish()
            end = time.perf_counter()
            times.append((end - start) * 1000)  # Convert to ms
        
        # Return median
        times.sort()
        return times[len(times) // 2]
    
    def time_kernel_with_events(
        self,
        kernel: "cl.Kernel",
        queue: "cl.CommandQueue",
        global_size: Tuple[int, ...],
        local_size: Optional[Tuple[int, ...]],
        *kernel_args,
        warmup: int = 3,
        runs: int = 5
    ) -> float:
        """
        Time a kernel using OpenCL event profiling.
        More accurate than wall-clock timing.
        """
        if cl is None:
            return 0.0
        
        times = []
        
        # Warmup
        for _ in range(warmup):
            kernel(queue, global_size, local_size, *kernel_args)
            queue.finish()
        
        # Timed runs
        for _ in range(runs):
            evt = kernel(queue, global_size, local_size, *kernel_args)
            evt.wait()
            start = evt.profile.start
            end = evt.profile.end
            times.append((end - start) * 1e-6)  # nanoseconds to ms
        
        times.sort()
        return times[len(times) // 2]


class AutoTuner:
    """
    Automatic kernel selection based on runtime profiling.
    Caches optimal configurations per problem size and device.
    """
    
    def __init__(self, config: Optional[TuningConfig] = None):
        self.config = config or TuningConfig()
        self._cache: Dict[str, TuningResult] = {}
        self._profiler: Optional[KernelProfiler] = None
        
        # Load cache from disk if enabled
        if self.config.enable_cache and self.config.cache_dir:
            self._load_cache()
    
    def _get_cache_key(
        self,
        op_type: str,
        shape: Tuple[int, ...],
        dtype: str,
        device_name: str,
        extra: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate a unique cache key for a configuration."""
        key_data = {
            "op": op_type,
            "shape": shape,
            "dtype": dtype,
            "device": device_name,
        }
        if extra:
            key_data.update(extra)
        
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def _load_cache(self):
        """Load tuning cache from disk."""
        if not self.config.cache_dir:
            return
        
        cache_path = Path(self.config.cache_dir) / "autotune_cache.json"
        if cache_path.exists():
            try:
                with open(cache_path, "r") as f:
                    data = json.load(f)
                    for key, result in data.items():
                        self._cache[key] = TuningResult(**result)
            except (json.JSONDecodeError, IOError):
                pass
    
    def _save_cache(self):
        """Save tuning cache to disk."""
        if not self.config.cache_dir:
            return
        
        cache_path = Path(self.config.cache_dir) / "autotune_cache.json"
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        
        data = {}
        for key, result in self._cache.items():
            data[key] = {
                "kernel_name": result.kernel_name,
                "time_ms": result.time_ms,
                "gflops": result.gflops,
                "params": result.params,
            }
        
        with open(cache_path, "w") as f:
            json.dump(data, f, indent=2)
    
    def tune_matmul(
        self,
        M: int,
        N: int,
        K: int,
        dtype: str,
        queue: "cl.CommandQueue",
    ) -> TuningResult:
        """
        Tune MatMul kernel for given dimensions.
        Tests multiple tile sizes and selects the fastest.
        """
        device_name = queue.device.name
        cache_key = self._get_cache_key("matmul", (M, N, K), dtype, device_name)
        
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Import kernels
        try:
            from netcl.ops.matmul import matmul as naive_mm
            from netcl.ops.matmul_optimized import tiled_matmul, get_optimal_tile_size
        except ImportError:
            return TuningResult("naive", 0.0)
        
        if np is None:
            return TuningResult("naive", 0.0)
        
        # Create test tensors
        a = Tensor.from_host(queue, np.random.randn(M, K).astype(np.float32))
        b = Tensor.from_host(queue, np.random.randn(K, N).astype(np.float32))
        
        profiler = KernelProfiler(queue)
        best_result = TuningResult("naive", float("inf"))
        
        # Test naive
        try:
            time_naive = profiler.time_kernel(
                naive_mm, a, b,
                warmup=self.config.warmup_runs,
                runs=self.config.benchmark_runs
            )
            if time_naive < best_result.time_ms:
                best_result = TuningResult("naive", time_naive)
        except Exception:
            pass
        
        # Test tiled with different tile sizes
        for tile_size in [8, 16, 32]:
            try:
                time_tiled = profiler.time_kernel(
                    lambda a, b, ts=tile_size: tiled_matmul(a, b, tile_size=ts),
                    a, b,
                    warmup=self.config.warmup_runs,
                    runs=self.config.benchmark_runs
                )
                if time_tiled < best_result.time_ms:
                    best_result = TuningResult(
                        f"tiled_{tile_size}",
                        time_tiled,
                        params={"tile_size": tile_size}
                    )
            except Exception:
                pass
        
        # Compute GFLOPS
        flops = 2 * M * N * K
        if best_result.time_ms > 0:
            best_result.gflops = flops / (best_result.time_ms * 1e9)
        
        # Cache result
        self._cache[cache_key] = best_result
        if self.config.enable_cache and self.config.cache_dir:
            self._save_cache()
        
        return best_result
    
    def tune_conv2d(
        self,
        N: int,
        C: int,
        H: int,
        W: int,
        F: int,
        KH: int,
        KW: int,
        stride: int,
        pad: int,
        dtype: str,
        queue: "cl.CommandQueue",
    ) -> TuningResult:
        """
        Tune Conv2D kernel for given dimensions.
        Tests naive, implicit GEMM, tiled, and Winograd (for 3x3).
        """
        device_name = queue.device.name
        cache_key = self._get_cache_key(
            "conv2d",
            (N, C, H, W, F, KH, KW, stride, pad),
            dtype,
            device_name
        )
        
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Import kernels
        try:
            from netcl.ops.conv2d import conv2d as naive_conv
            from netcl.ops.conv2d_optimized import (
                conv2d_implicit_gemm,
                conv2d_tiled_local,
                conv2d_winograd_f2x2_3x3,
            )
        except ImportError:
            return TuningResult("naive", 0.0)
        
        if np is None:
            return TuningResult("naive", 0.0)
        
        # Create test tensors
        x = Tensor.from_host(queue, np.random.randn(N, C, H, W).astype(np.float32))
        w = Tensor.from_host(queue, np.random.randn(F, C, KH, KW).astype(np.float32))
        
        profiler = KernelProfiler(queue)
        best_result = TuningResult("naive", float("inf"))
        
        # Test naive
        try:
            time_naive = profiler.time_kernel(
                lambda: naive_conv(x, w, stride=stride, pad=pad),
                warmup=self.config.warmup_runs,
                runs=self.config.benchmark_runs
            )
            if time_naive < best_result.time_ms:
                best_result = TuningResult("naive", time_naive)
        except Exception:
            pass
        
        # Test implicit GEMM (best for 3x3 stride=1)
        if KH == 3 and KW == 3 and stride == 1:
            try:
                time_gemm = profiler.time_kernel(
                    lambda: conv2d_implicit_gemm(x, w, pad=pad),
                    warmup=self.config.warmup_runs,
                    runs=self.config.benchmark_runs
                )
                if time_gemm < best_result.time_ms:
                    best_result = TuningResult("implicit_gemm", time_gemm)
            except Exception:
                pass
        
        # Test tiled local
        for tile_size in [4, 8]:
            try:
                time_tiled = profiler.time_kernel(
                    lambda ts=tile_size: conv2d_tiled_local(
                        x, w, stride=stride, pad=pad, tile_oh=ts, tile_ow=ts
                    ),
                    warmup=self.config.warmup_runs,
                    runs=self.config.benchmark_runs
                )
                if time_tiled < best_result.time_ms:
                    best_result = TuningResult(
                        f"tiled_{tile_size}",
                        time_tiled,
                        params={"tile_size": tile_size}
                    )
            except Exception:
                pass
        
        # Test Winograd (only for 3x3 stride=1)
        if KH == 3 and KW == 3 and stride == 1:
            try:
                time_wino = profiler.time_kernel(
                    lambda: conv2d_winograd_f2x2_3x3(x, w, pad=pad),
                    warmup=self.config.warmup_runs,
                    runs=self.config.benchmark_runs
                )
                if time_wino < best_result.time_ms:
                    best_result = TuningResult("winograd", time_wino)
            except Exception:
                pass
        
        # Compute GFLOPS
        OH = (H + 2 * pad - KH) // stride + 1
        OW = (W + 2 * pad - KW) // stride + 1
        flops = 2 * N * F * OH * OW * C * KH * KW
        if best_result.time_ms > 0:
            best_result.gflops = flops / (best_result.time_ms * 1e9)
        
        # Cache result
        self._cache[cache_key] = best_result
        if self.config.enable_cache and self.config.cache_dir:
            self._save_cache()
        
        return best_result
    
    def get_best_kernel(self, cache_key: str) -> Optional[TuningResult]:
        """Get cached tuning result for a given key."""
        return self._cache.get(cache_key)
    
    def clear_cache(self):
        """Clear in-memory cache."""
        self._cache.clear()


# Global autotuner instance
_GLOBAL_AUTOTUNER: Optional[AutoTuner] = None


def get_autotuner() -> AutoTuner:
    """Get or create the global autotuner instance."""
    global _GLOBAL_AUTOTUNER
    if _GLOBAL_AUTOTUNER is None:
        cache_dir = os.environ.get("NETCL_AUTOTUNE_CACHE", None)
        config = TuningConfig(
            warmup_runs=int(os.environ.get("NETCL_AUTOTUNE_WARMUP", "3")),
            benchmark_runs=int(os.environ.get("NETCL_AUTOTUNE_RUNS", "5")),
            cache_dir=cache_dir,
            enable_cache=cache_dir is not None,
        )
        _GLOBAL_AUTOTUNER = AutoTuner(config)
    return _GLOBAL_AUTOTUNER


def autotune_matmul(M: int, N: int, K: int, dtype: str, queue: "cl.CommandQueue") -> str:
    """
    Auto-select best MatMul kernel for given dimensions.
    Returns kernel name.
    """
    tuner = get_autotuner()
    result = tuner.tune_matmul(M, N, K, dtype, queue)
    return result.kernel_name


def autotune_conv2d(
    N: int, C: int, H: int, W: int,
    F: int, KH: int, KW: int,
    stride: int, pad: int,
    dtype: str,
    queue: "cl.CommandQueue"
) -> str:
    """
    Auto-select best Conv2D kernel for given dimensions.
    Returns kernel name.
    """
    tuner = get_autotuner()
    result = tuner.tune_conv2d(N, C, H, W, F, KH, KW, stride, pad, dtype, queue)
    return result.kernel_name


# Timing utilities for manual profiling

class Timer:
    """Simple timer for profiling code sections."""
    
    def __init__(self, name: str = ""):
        self.name = name
        self._start: float = 0
        self._end: float = 0
        self._elapsed: float = 0
    
    def __enter__(self):
        self._start = time.perf_counter()
        return self
    
    def __exit__(self, *args):
        self._end = time.perf_counter()
        self._elapsed = (self._end - self._start) * 1000
    
    @property
    def elapsed_ms(self) -> float:
        return self._elapsed
    
    def __str__(self):
        if self.name:
            return f"{self.name}: {self._elapsed:.3f} ms"
        return f"{self._elapsed:.3f} ms"


class ProfileContext:
    """
    Context manager for profiling a section of code.
    Collects timing data across multiple runs.
    """
    
    def __init__(self, name: str = "Profile"):
        self.name = name
        self.times: List[float] = []
    
    def __enter__(self):
        self._start = time.perf_counter()
        return self
    
    def __exit__(self, *args):
        elapsed = (time.perf_counter() - self._start) * 1000
        self.times.append(elapsed)
    
    @property
    def mean_ms(self) -> float:
        if not self.times:
            return 0.0
        return sum(self.times) / len(self.times)
    
    @property
    def median_ms(self) -> float:
        if not self.times:
            return 0.0
        sorted_times = sorted(self.times)
        return sorted_times[len(sorted_times) // 2]
    
    @property
    def min_ms(self) -> float:
        return min(self.times) if self.times else 0.0
    
    @property
    def max_ms(self) -> float:
        return max(self.times) if self.times else 0.0
    
    def summary(self) -> str:
        if not self.times:
            return f"{self.name}: No data"
        return (
            f"{self.name}: "
            f"mean={self.mean_ms:.3f}ms, "
            f"median={self.median_ms:.3f}ms, "
            f"min={self.min_ms:.3f}ms, "
            f"max={self.max_ms:.3f}ms, "
            f"runs={len(self.times)}"
        )


__all__ = [
    'TuningResult',
    'TuningConfig',
    'KernelProfiler',
    'AutoTuner',
    'get_autotuner',
    'autotune_matmul',
    'autotune_conv2d',
    'Timer',
    'ProfileContext',
]
