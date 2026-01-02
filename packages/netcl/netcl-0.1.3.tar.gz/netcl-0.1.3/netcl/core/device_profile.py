"""
Extended Device Profile and Kernel Selector for GPU-adaptive optimization.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional, Dict, Tuple, Any

try:
    import pyopencl as cl
except ImportError:
    cl = None


class GPUFamily(Enum):
    """GPU Family classification for kernel selection."""
    NVIDIA_AMPERE = auto()      # RTX 30xx, A100, etc.
    NVIDIA_TURING = auto()      # RTX 20xx, GTX 16xx
    NVIDIA_VOLTA = auto()       # V100, Titan V
    NVIDIA_PASCAL = auto()      # GTX 10xx
    NVIDIA_MAXWELL = auto()     # GTX 9xx
    NVIDIA_OTHER = auto()       # Older NVIDIA
    
    AMD_RDNA3 = auto()          # RX 7xxx
    AMD_RDNA2 = auto()          # RX 6xxx
    AMD_RDNA = auto()           # RX 5xxx
    AMD_VEGA = auto()           # Vega 56/64
    AMD_GCN = auto()            # Older GCN
    AMD_OTHER = auto()
    
    INTEL_ARC = auto()          # Arc Alchemist
    INTEL_XE = auto()           # Xe integrated
    INTEL_GEN = auto()          # Older Gen
    INTEL_OTHER = auto()
    
    CPU = auto()
    UNKNOWN = auto()


@dataclass
class ExtendedDeviceProfile:
    """Extended device profile with GPU-specific optimizations."""
    # Basic info
    name: str
    vendor: str
    device_type: str
    driver_version: str
    
    # Compute capabilities
    compute_units: int
    max_work_group_size: int
    max_work_item_sizes: Tuple[int, int, int]
    max_sub_groups: int
    sub_group_sizes: Tuple[int, ...]
    
    # Memory
    global_mem_size: int
    local_mem_size: int
    max_constant_buffer_size: int
    global_mem_cache_size: int
    global_mem_cache_line_size: int
    max_mem_alloc_size: int
    
    # Vector capabilities
    preferred_vector_width_float: int
    preferred_vector_width_half: int
    native_vector_width_float: int
    
    # Extensions
    extensions: Tuple[str, ...]
    has_fp16: bool
    has_fp64: bool
    has_subgroups: bool
    has_local_atomics: bool
    has_global_atomics: bool
    has_images: bool
    
    # Derived properties
    gpu_family: GPUFamily = GPUFamily.UNKNOWN
    estimated_flops: float = 0.0  # TFLOPS estimate
    memory_bandwidth: float = 0.0  # GB/s estimate
    
    # Optimal configurations (determined at runtime)
    optimal_tile_m: int = 32
    optimal_tile_n: int = 32
    optimal_tile_k: int = 8
    optimal_wg_size_1d: int = 256
    optimal_wg_size_2d: Tuple[int, int] = (16, 16)
    use_vectorization: bool = True
    use_local_memory: bool = True


_EXTENDED_PROFILE_CACHE: Dict[str, ExtendedDeviceProfile] = {}


def _detect_gpu_family(name: str, vendor: str, extensions: Tuple[str, ...]) -> GPUFamily:
    """Detect GPU family from device info."""
    name_lower = name.lower()
    vendor_lower = vendor.lower()
    
    # CPU first: catch CPU devices even if vendor string matches GPU vendors
    if "cpu" in name_lower or "cpu" in vendor_lower:
        return GPUFamily.CPU
    
    # NVIDIA detection
    if "nvidia" in vendor_lower or "nvidia" in name_lower:
        if any(x in name_lower for x in ["rtx 30", "rtx 40", "a100", "a10", "a30"]):
            return GPUFamily.NVIDIA_AMPERE
        elif any(x in name_lower for x in ["rtx 20", "gtx 16", "titan rtx"]):
            return GPUFamily.NVIDIA_TURING
        elif any(x in name_lower for x in ["v100", "titan v"]):
            return GPUFamily.NVIDIA_VOLTA
        elif any(x in name_lower for x in ["gtx 10", "p100", "titan x pascal"]):
            return GPUFamily.NVIDIA_PASCAL
        elif any(x in name_lower for x in ["gtx 9", "titan x maxwell"]):
            return GPUFamily.NVIDIA_MAXWELL
        else:
            return GPUFamily.NVIDIA_OTHER
    
    # AMD detection
    if "amd" in vendor_lower or "advanced micro" in vendor_lower:
        if any(x in name_lower for x in ["rx 7", "radeon 7"]):
            return GPUFamily.AMD_RDNA3
        elif any(x in name_lower for x in ["rx 6", "radeon 6"]):
            return GPUFamily.AMD_RDNA2
        elif any(x in name_lower for x in ["rx 5", "radeon 5"]):
            return GPUFamily.AMD_RDNA
        elif "vega" in name_lower:
            return GPUFamily.AMD_VEGA
        elif any(x in name_lower for x in ["rx 4", "rx 5", "r9", "r7"]):
            return GPUFamily.AMD_GCN
        else:
            return GPUFamily.AMD_OTHER
    
    # Intel detection
    if "intel" in vendor_lower:
        if "arc" in name_lower:
            return GPUFamily.INTEL_ARC
        elif "xe" in name_lower or "iris" in name_lower:
            return GPUFamily.INTEL_XE
        elif "hd" in name_lower or "uhd" in name_lower:
            return GPUFamily.INTEL_GEN
        else:
            return GPUFamily.INTEL_OTHER
    
    # CPU fallback
    if "cpu" in name_lower:
        return GPUFamily.CPU
    
    return GPUFamily.UNKNOWN


def _get_optimal_config(family: GPUFamily, local_mem: int, max_wg: int) -> Dict[str, Any]:
    """Get optimal kernel configuration based on GPU family."""
    config = {
        "tile_m": 32,
        "tile_n": 32,
        "tile_k": 8,
        "wg_1d": 256,
        "wg_2d": (16, 16),
        "vectorize": True,
        "use_local": True,
    }
    
    # NVIDIA configs - generally favor larger tiles
    if family in (GPUFamily.NVIDIA_AMPERE, GPUFamily.NVIDIA_TURING):
        config.update({
            "tile_m": 64,
            "tile_n": 64,
            "tile_k": 16,
            "wg_2d": (16, 16),
        })
    elif family in (GPUFamily.NVIDIA_VOLTA, GPUFamily.NVIDIA_PASCAL):
        config.update({
            "tile_m": 64,
            "tile_n": 64,
            "tile_k": 8,
            "wg_2d": (16, 16),
        })
    
    # AMD configs - prefer 64-wide wavefronts
    elif family in (GPUFamily.AMD_RDNA2, GPUFamily.AMD_RDNA3):
        config.update({
            "tile_m": 64,
            "tile_n": 64,
            "tile_k": 16,
            "wg_1d": 64,
            "wg_2d": (16, 4),  # 64 threads
        })
    elif family in (GPUFamily.AMD_RDNA, GPUFamily.AMD_VEGA, GPUFamily.AMD_GCN):
        config.update({
            "tile_m": 32,
            "tile_n": 32,
            "tile_k": 8,
            "wg_1d": 64,
            "wg_2d": (8, 8),
        })
    
    # Intel configs
    elif family in (GPUFamily.INTEL_ARC, GPUFamily.INTEL_XE):
        config.update({
            "tile_m": 32,
            "tile_n": 32,
            "tile_k": 8,
            "wg_1d": 256,
            "wg_2d": (16, 16),
        })
    
    # CPU - simpler configs
    elif family == GPUFamily.CPU:
        config.update({
            "tile_m": 16,
            "tile_n": 16,
            "tile_k": 4,
            "wg_1d": 16,
            "wg_2d": (4, 4),
            "vectorize": True,
            "use_local": False,
        })
    
    # Adjust for limited local memory
    if local_mem < 32 * 1024:
        config["tile_m"] = min(config["tile_m"], 32)
        config["tile_n"] = min(config["tile_n"], 32)
        config["tile_k"] = min(config["tile_k"], 8)
        if local_mem < 16 * 1024:
            config["use_local"] = False
    
    # Clamp to device limits
    wg_limit = max_wg
    wg_1d = min(config["wg_1d"], wg_limit)
    wg_2d_0 = config["wg_2d"][0]
    wg_2d_1 = config["wg_2d"][1]
    while wg_2d_0 * wg_2d_1 > wg_limit:
        if wg_2d_0 >= wg_2d_1:
            wg_2d_0 //= 2
        else:
            wg_2d_1 //= 2
    config["wg_1d"] = wg_1d
    config["wg_2d"] = (max(1, wg_2d_0), max(1, wg_2d_1))
    
    return config


def extended_device_profile(device) -> ExtendedDeviceProfile:
    """Create extended device profile with full GPU detection."""
    if cl is None:
        raise ImportError("pyopencl required")
    
    key = getattr(device, "int_ptr", None) or str(device.name)
    if key in _EXTENDED_PROFILE_CACHE:
        return _EXTENDED_PROFILE_CACHE[key]
    
    # Basic info
    name = device.name
    vendor = device.vendor
    device_type = str(device.type)
    driver_version = getattr(device, "driver_version", "unknown")
    
    # Compute
    compute_units = int(device.max_compute_units)
    max_work_group_size = int(device.max_work_group_size)
    max_work_item_sizes = tuple(int(x) for x in device.max_work_item_sizes)
    
    # Subgroup info
    max_sub_groups = 0
    sub_group_sizes = (32,)  # Default
    try:
        if hasattr(device, "max_num_sub_groups"):
            max_sub_groups = int(device.max_num_sub_groups)
        # Try to get subgroup sizes if available
        if hasattr(cl, "device_info") and hasattr(cl.device_info, "SUB_GROUP_SIZES_INTEL"):
            try:
                sub_group_sizes = tuple(device.get_info(cl.device_info.SUB_GROUP_SIZES_INTEL))
            except:
                pass
    except:
        pass
    
    # Memory
    global_mem_size = int(device.global_mem_size)
    local_mem_size = int(device.local_mem_size)
    max_constant_buffer_size = int(device.max_constant_buffer_size)
    global_mem_cache_size = int(getattr(device, "global_mem_cache_size", 0))
    global_mem_cache_line_size = int(getattr(device, "global_mem_cacheline_size", 64))
    max_mem_alloc_size = int(device.max_mem_alloc_size)
    
    # Vector widths
    preferred_vector_width_float = int(device.preferred_vector_width_float)
    preferred_vector_width_half = int(getattr(device, "preferred_vector_width_half", 0))
    native_vector_width_float = int(getattr(device, "native_vector_width_float", 4))
    
    # Extensions
    extensions = tuple(device.extensions.strip().split())
    has_fp16 = "cl_khr_fp16" in extensions
    has_fp64 = "cl_khr_fp64" in extensions
    has_subgroups = any("subgroup" in ext.lower() for ext in extensions)
    has_local_atomics = "cl_khr_local_int32_base_atomics" in extensions
    has_global_atomics = "cl_khr_global_int32_base_atomics" in extensions
    has_images = device.image_support
    
    # GPU Family detection
    gpu_family = _detect_gpu_family(name, vendor, extensions)
    
    # Optimal config
    optimal = _get_optimal_config(gpu_family, local_mem_size, max_work_group_size)
    
    # Estimate performance (rough)
    # NVIDIA: ~64 FLOPS/cycle/CU at typical clocks
    # AMD: ~64 FLOPS/cycle/CU
    # This is a very rough estimate
    clock_mhz = 1500  # Default assumption
    flops_per_cu = 64 * 2  # FMA counts as 2
    estimated_flops = (compute_units * flops_per_cu * clock_mhz) / 1e6  # TFLOPS
    
    # Memory bandwidth estimate (rough)
    # Assumes typical configs
    memory_bandwidth = 300.0  # GB/s default
    if gpu_family in (GPUFamily.NVIDIA_AMPERE,):
        memory_bandwidth = 600.0
    elif gpu_family in (GPUFamily.AMD_RDNA2, GPUFamily.AMD_RDNA3):
        memory_bandwidth = 500.0
    
    profile = ExtendedDeviceProfile(
        name=name,
        vendor=vendor,
        device_type=device_type,
        driver_version=driver_version,
        compute_units=compute_units,
        max_work_group_size=max_work_group_size,
        max_work_item_sizes=max_work_item_sizes,
        max_sub_groups=max_sub_groups,
        sub_group_sizes=sub_group_sizes,
        global_mem_size=global_mem_size,
        local_mem_size=local_mem_size,
        max_constant_buffer_size=max_constant_buffer_size,
        global_mem_cache_size=global_mem_cache_size,
        global_mem_cache_line_size=global_mem_cache_line_size,
        max_mem_alloc_size=max_mem_alloc_size,
        preferred_vector_width_float=preferred_vector_width_float,
        preferred_vector_width_half=preferred_vector_width_half,
        native_vector_width_float=native_vector_width_float,
        extensions=extensions,
        has_fp16=has_fp16,
        has_fp64=has_fp64,
        has_subgroups=has_subgroups,
        has_local_atomics=has_local_atomics,
        has_global_atomics=has_global_atomics,
        has_images=has_images,
        gpu_family=gpu_family,
        estimated_flops=estimated_flops,
        memory_bandwidth=memory_bandwidth,
        optimal_tile_m=optimal["tile_m"],
        optimal_tile_n=optimal["tile_n"],
        optimal_tile_k=optimal["tile_k"],
        optimal_wg_size_1d=optimal["wg_1d"],
        optimal_wg_size_2d=optimal["wg_2d"],
        use_vectorization=optimal["vectorize"],
        use_local_memory=optimal["use_local"],
    )
    
    _EXTENDED_PROFILE_CACHE[key] = profile
    return profile


def get_device_family(device) -> GPUFamily:
    """Quick helper to get GPU family."""
    profile = extended_device_profile(device)
    return profile.gpu_family


def get_optimal_matmul_config(device) -> Dict[str, int]:
    """Get optimal MatMul configuration for device."""
    # Handle if already a profile
    if isinstance(device, ExtendedDeviceProfile):
        profile = device
    else:
        profile = extended_device_profile(device)
    return {
        "tile_m": profile.optimal_tile_m,
        "tile_n": profile.optimal_tile_n,
        "tile_k": profile.optimal_tile_k,
        "wpt_m": 4 if profile.gpu_family in (GPUFamily.NVIDIA_AMPERE, GPUFamily.NVIDIA_TURING) else 2,
        "wpt_n": 4 if profile.gpu_family in (GPUFamily.NVIDIA_AMPERE, GPUFamily.NVIDIA_TURING) else 2,
    }


def get_optimal_conv_config(device) -> Dict[str, Any]:
    """Get optimal Conv2D configuration for device."""
    # Accept either a raw device or a precomputed profile to keep callers simple.
    if isinstance(device, ExtendedDeviceProfile):
        profile = device
    else:
        profile = extended_device_profile(device)
    
    config = {
        "use_implicit_gemm": True,
        "use_local_memory": profile.use_local_memory,
        "tile_size": profile.optimal_tile_m,
        "use_fp16": profile.has_fp16,
    }
    
    # NVIDIA prefers implicit GEMM
    if profile.gpu_family in (GPUFamily.NVIDIA_AMPERE, GPUFamily.NVIDIA_TURING, 
                               GPUFamily.NVIDIA_VOLTA, GPUFamily.NVIDIA_PASCAL):
        config["use_implicit_gemm"] = True
        config["tile_size"] = 64
    
    # AMD may prefer tiled approach
    elif profile.gpu_family in (GPUFamily.AMD_RDNA2, GPUFamily.AMD_RDNA3):
        config["use_implicit_gemm"] = True
        config["tile_size"] = 32
    
    # CPU prefers simple direct conv
    elif profile.gpu_family == GPUFamily.CPU:
        config["use_implicit_gemm"] = False
        config["use_local_memory"] = False
        config["tile_size"] = 16
    
    return config


__all__ = [
    'GPUFamily',
    'ExtendedDeviceProfile',
    'extended_device_profile',
    'get_device_family',
    'get_optimal_matmul_config',
    'get_optimal_conv_config',
]
