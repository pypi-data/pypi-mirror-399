"""
KernelSelector - Automatic kernel selection based on device and problem size.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional, Dict, Tuple, Any, Callable

from netcl.core.device_profile import (
    ExtendedDeviceProfile, 
    GPUFamily, 
    extended_device_profile,
    get_optimal_matmul_config,
    get_optimal_conv_config,
)

try:
    import pyopencl as cl
except ImportError:
    cl = None


class KernelVariant(Enum):
    """Available kernel implementations."""
    # MatMul variants
    MATMUL_NAIVE = auto()
    MATMUL_TILED = auto()
    MATMUL_REGISTER_TILED = auto()
    MATMUL_VECTORIZED = auto()
    
    # Conv2D variants
    CONV2D_NAIVE = auto()
    CONV2D_IM2COL = auto()
    CONV2D_IMPLICIT_GEMM = auto()
    CONV2D_TILED_LOCAL = auto()
    CONV2D_WINOGRAD = auto()
    
    # Elementwise variants
    ELEMENTWISE_SCALAR = auto()
    ELEMENTWISE_VECTORIZED = auto()
    
    # Reduction variants
    REDUCTION_SEQUENTIAL = auto()
    REDUCTION_PARALLEL = auto()
    REDUCTION_WORKGROUP = auto()
    
    # BatchNorm variants
    BATCHNORM_NAIVE = auto()
    BATCHNORM_FUSED = auto()


@dataclass
class KernelConfig:
    """Configuration for a selected kernel."""
    variant: KernelVariant
    tile_m: int = 32
    tile_n: int = 32
    tile_k: int = 8
    work_per_thread: int = 4
    local_size_1d: int = 256
    local_size_2d: Tuple[int, int] = (16, 16)
    use_local_memory: bool = True
    use_vectorization: bool = True
    vector_width: int = 4
    extra: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.extra is None:
            self.extra = {}


class KernelSelector:
    """
    Automatic kernel selection based on device capabilities and problem size.
    """
    
    def __init__(self, device=None, profile: Optional[ExtendedDeviceProfile] = None):
        """
        Initialize kernel selector with device.
        
        Args:
            device: OpenCL device or None (uses default)
            profile: Pre-computed profile (optional)
        """
        if profile is not None:
            self._profile = profile
        elif device is not None:
            self._profile = extended_device_profile(device)
        else:
            self._profile = None
        
        self._autotune_cache: Dict[Tuple, KernelConfig] = {}
    
    @property
    def profile(self) -> Optional[ExtendedDeviceProfile]:
        return self._profile
    
    def set_device(self, device):
        """Update device profile."""
        self._profile = extended_device_profile(device)
        self._autotune_cache.clear()
    
    def select_matmul_kernel(
        self,
        M: int, N: int, K: int,
        dtype: str = "float32",
        allow_vectorized: bool = True
    ) -> KernelConfig:
        """
        Select optimal MatMul kernel for given dimensions.
        """
        cache_key = ("matmul", M, N, K, dtype, allow_vectorized)
        if cache_key in self._autotune_cache:
            return self._autotune_cache[cache_key]
        
        profile = self._profile
        total_ops = M * N * K * 2  # MAC counts as 2
        
        # Very small matrices - use naive
        if M * N < 256 or total_ops < 100_000:
            config = KernelConfig(
                variant=KernelVariant.MATMUL_NAIVE,
                tile_m=16,
                tile_n=16,
                tile_k=4,
                use_local_memory=False,
            )
        
        # Small to medium - use tiled
        elif total_ops < 10_000_000:
            tile_m = 32
            tile_n = 32
            tile_k = 8
            
            if profile:
                tile_m = min(profile.optimal_tile_m, 32)
                tile_n = min(profile.optimal_tile_n, 32)
            
            config = KernelConfig(
                variant=KernelVariant.MATMUL_TILED,
                tile_m=tile_m,
                tile_n=tile_n,
                tile_k=tile_k,
                local_size_2d=(16, 16) if not profile else profile.optimal_wg_size_2d,
            )
        
        # Large - use register tiled
        else:
            tile_m = 64
            tile_n = 64
            tile_k = 16
            wpt = 4
            
            if profile:
                opt = get_optimal_matmul_config(profile)
                tile_m = opt.get("tile_m", 64)
                tile_n = opt.get("tile_n", 64)
                tile_k = opt.get("tile_k", 16)
                wpt = opt.get("wpt_m", 4)
                
                # GPU family specific tuning
                if profile.gpu_family in (GPUFamily.NVIDIA_AMPERE, GPUFamily.NVIDIA_TURING):
                    tile_m, tile_n = 64, 64
                    wpt = 8
                elif profile.gpu_family in (GPUFamily.AMD_RDNA2, GPUFamily.AMD_RDNA3):
                    tile_m, tile_n = 64, 64
                    wpt = 4
            
            config = KernelConfig(
                variant=KernelVariant.MATMUL_REGISTER_TILED,
                tile_m=tile_m,
                tile_n=tile_n,
                tile_k=tile_k,
                work_per_thread=wpt,
            )
        
        self._autotune_cache[cache_key] = config
        return config
    
    def select_conv2d_kernel(
        self,
        batch: int,
        in_channels: int,
        out_channels: int,
        height: int,
        width: int,
        kernel_h: int,
        kernel_w: int,
        stride: int = 1,
        padding: int = 0,
        dtype: str = "float32"
    ) -> KernelConfig:
        """
        Select optimal Conv2D kernel.
        """
        cache_key = ("conv2d", batch, in_channels, out_channels, height, width, 
                     kernel_h, kernel_w, stride, padding, dtype)
        if cache_key in self._autotune_cache:
            return self._autotune_cache[cache_key]
        
        profile = self._profile
        
        # Calculate output size
        out_h = (height + 2 * padding - kernel_h) // stride + 1
        out_w = (width + 2 * padding - kernel_w) // stride + 1
        
        # Compute intensity approximation
        flops = 2 * batch * out_channels * out_h * out_w * in_channels * kernel_h * kernel_w
        
        # 1x1 convolution - treat as MatMul
        if kernel_h == 1 and kernel_w == 1 and stride == 1 and padding == 0:
            config = KernelConfig(
                variant=KernelVariant.CONV2D_IMPLICIT_GEMM,
                tile_m=32,
                tile_n=32,
                extra={"use_1x1_optimization": True}
            )
        
        # 3x3 with small spatial - try Winograd (if supported)
        elif kernel_h == 3 and kernel_w == 3 and stride == 1:
            # Winograd is complex, fall back to implicit GEMM for now
            config = KernelConfig(
                variant=KernelVariant.CONV2D_IMPLICIT_GEMM,
                tile_m=64 if profile and profile.gpu_family != GPUFamily.CPU else 32,
                tile_n=64 if profile and profile.gpu_family != GPUFamily.CPU else 32,
            )
        
        # Small output - use tiled with local memory
        elif out_h * out_w < 256:
            config = KernelConfig(
                variant=KernelVariant.CONV2D_TILED_LOCAL,
                tile_m=16,
                tile_n=16,
            )
        
        # General case - implicit GEMM
        else:
            tile_size = 32
            if profile:
                conv_opt = get_optimal_conv_config(profile)
                tile_size = conv_opt.get("tile_size", 32)
                
            config = KernelConfig(
                variant=KernelVariant.CONV2D_IMPLICIT_GEMM,
                tile_m=tile_size,
                tile_n=tile_size,
                use_local_memory=profile.use_local_memory if profile else True,
            )
        
        # CPU override
        if profile and profile.gpu_family == GPUFamily.CPU:
            config = KernelConfig(
                variant=KernelVariant.CONV2D_IM2COL,
                use_local_memory=False,
            )
        
        self._autotune_cache[cache_key] = config
        return config
    
    def select_elementwise_kernel(
        self,
        n_elements: int,
        dtype: str = "float32",
        allow_vectorized: bool = True
    ) -> KernelConfig:
        """
        Select optimal elementwise kernel.
        """
        profile = self._profile
        
        # Vectorized for large arrays
        use_vec = allow_vectorized and n_elements >= 1024
        if profile:
            use_vec = use_vec and profile.use_vectorization
        
        if use_vec and n_elements % 4 == 0:
            vec_width = 4
            if profile and profile.preferred_vector_width_float >= 8 and n_elements % 8 == 0:
                vec_width = 8
            
            config = KernelConfig(
                variant=KernelVariant.ELEMENTWISE_VECTORIZED,
                local_size_1d=256,
                vector_width=vec_width,
                use_vectorization=True,
            )
        else:
            config = KernelConfig(
                variant=KernelVariant.ELEMENTWISE_SCALAR,
                local_size_1d=256,
                use_vectorization=False,
            )
        
        return config
    
    def select_reduction_kernel(
        self,
        n_elements: int,
        reduction_type: str = "sum"  # sum, max, min, mean
    ) -> KernelConfig:
        """
        Select optimal reduction kernel.
        """
        profile = self._profile
        
        if n_elements < 256:
            return KernelConfig(variant=KernelVariant.REDUCTION_SEQUENTIAL)
        
        if n_elements < 65536:
            wg_size = 256
            if profile:
                wg_size = profile.optimal_wg_size_1d
            return KernelConfig(
                variant=KernelVariant.REDUCTION_PARALLEL,
                local_size_1d=wg_size,
            )
        
        # Large reductions - multi-stage
        wg_size = 256
        if profile:
            wg_size = profile.optimal_wg_size_1d
        return KernelConfig(
            variant=KernelVariant.REDUCTION_WORKGROUP,
            local_size_1d=wg_size,
            extra={"stages": 2}
        )
    
    def select_batchnorm_kernel(
        self,
        batch: int,
        channels: int,
        spatial: int,
        training: bool = True,
        fuse_relu: bool = False
    ) -> KernelConfig:
        """
        Select optimal BatchNorm kernel.
        """
        profile = self._profile
        
        if fuse_relu and not training:
            return KernelConfig(
                variant=KernelVariant.BATCHNORM_FUSED,
                extra={"fuse_relu": True}
            )
        
        return KernelConfig(variant=KernelVariant.BATCHNORM_NAIVE)
    
    def clear_cache(self):
        """Clear autotune cache."""
        self._autotune_cache.clear()


# Global selector instance
_global_selector: Optional[KernelSelector] = None


def get_kernel_selector(device=None) -> KernelSelector:
    """Get or create global kernel selector."""
    global _global_selector
    
    if _global_selector is None:
        _global_selector = KernelSelector(device=device)
    elif device is not None:
        _global_selector.set_device(device)
    
    return _global_selector


def select_matmul_config(M: int, N: int, K: int, device=None) -> KernelConfig:
    """Convenience function to select matmul kernel."""
    selector = get_kernel_selector(device)
    return selector.select_matmul_kernel(M, N, K)


def select_conv2d_config(
    batch: int, in_c: int, out_c: int, h: int, w: int,
    kh: int, kw: int, stride: int = 1, pad: int = 0,
    device=None
) -> KernelConfig:
    """Convenience function to select conv2d kernel."""
    selector = get_kernel_selector(device)
    return selector.select_conv2d_kernel(batch, in_c, out_c, h, w, kh, kw, stride, pad)


__all__ = [
    'KernelVariant',
    'KernelConfig',
    'KernelSelector',
    'get_kernel_selector',
    'select_matmul_config',
    'select_conv2d_config',
]
