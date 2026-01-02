"""
Memory helpers and buffer pool with persistent caching.

Includes:
- BufferPool: Simple power-of-two bucketed buffer pool
- PersistentBufferPool: Advanced pool with statistics and size limits
- Pinned memory support for faster host-device transfers
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import threading

try:
    import numpy as np
except ImportError:
    np = None

try:
    import pyopencl as cl  # type: ignore
except ImportError:  # pragma: no cover
    cl = None


@dataclass
class BufferHandle:
    buffer: "cl.Buffer"
    nbytes: int
    bucket_size: int = 0
    pool: Optional["BufferPool"] = None
    
    def release(self) -> None:
        """Release buffer back to pool if it came from one."""
        if self.pool is not None:
            self.pool.release(self)


@dataclass
class PoolStats:
    """Statistics for buffer pool usage."""
    hits: int = 0
    misses: int = 0
    bytes_allocated: int = 0
    bytes_cached: int = 0
    
    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0


class BufferPool:
    """
    Simple bucketed buffer pool to reduce allocation overhead.

    Buckets are power-of-two sizes; buffers are reused on release.
    """

    def __init__(self, context: Optional["cl.Context"]) -> None:
        self.context = context
        self._free: Dict[int, list[BufferHandle]] = {}
        self._lock = threading.Lock()
        self.stats = PoolStats()

    @staticmethod
    def _bucket_size(nbytes: int) -> int:
        size = 1
        while size < nbytes:
            size <<= 1
        return size

    def allocate(self, nbytes: int, flags: Optional[int] = None) -> BufferHandle:
        if cl is None:
            raise ImportError("pyopencl required for BufferPool")
        if self.context is None:
            raise ValueError("BufferPool has no context")
        bucket = self._bucket_size(nbytes)
        
        with self._lock:
            free_list = self._free.get(bucket)
            if free_list:
                self.stats.hits += 1
                handle = free_list.pop()
                self.stats.bytes_cached -= bucket
                return handle
        
        self.stats.misses += 1
        self.stats.bytes_allocated += bucket
        mf = cl.mem_flags
        use_flags = flags if flags is not None else (mf.READ_WRITE)
        buf = cl.Buffer(self.context, use_flags, bucket)
        return BufferHandle(buffer=buf, nbytes=bucket, bucket_size=bucket, pool=self)

    def release(self, handle: BufferHandle) -> None:
        bucket = self._bucket_size(handle.nbytes)
        with self._lock:
            self._free.setdefault(bucket, []).append(handle)
            self.stats.bytes_cached += bucket
    
    def clear(self) -> None:
        """Clear all cached buffers."""
        with self._lock:
            self._free.clear()
            self.stats.bytes_cached = 0


class PersistentBufferPool:
    """
    Advanced buffer pool with size limits and better statistics.
    
    Features:
    - Fixed bucket sizes for common allocations
    - Maximum cache size limit
    - Per-bucket limits to prevent memory hoarding
    - Thread-safe operations
    """
    
    # Common bucket sizes (aligned to typical tensor sizes)
    BUCKETS = [
        1024,           # 1KB
        4096,           # 4KB
        16384,          # 16KB
        65536,          # 64KB
        262144,         # 256KB
        1048576,        # 1MB
        4194304,        # 4MB
        16777216,       # 16MB
        67108864,       # 64MB
        268435456,      # 256MB
    ]
    
    def __init__(
        self, 
        context: "cl.Context",
        queue: "cl.CommandQueue",
        max_cached_bytes: int = 512 * 1024 * 1024,  # 512MB default
        max_buffers_per_bucket: int = 16
    ):
        self.context = context
        self.queue = queue
        self.max_cached_bytes = max_cached_bytes
        self.max_buffers_per_bucket = max_buffers_per_bucket
        
        self._free: Dict[int, List[BufferHandle]] = {size: [] for size in self.BUCKETS}
        self._lock = threading.Lock()
        self.stats = PoolStats()
    
    def _find_bucket(self, nbytes: int) -> int:
        """Find smallest bucket that fits the requested size."""
        for bucket in self.BUCKETS:
            if bucket >= nbytes:
                return bucket
        # For very large allocations, round up to power of 2
        size = 1
        while size < nbytes:
            size <<= 1
        return size
    
    def allocate(self, nbytes: int, flags: Optional[int] = None) -> BufferHandle:
        """Allocate a buffer, reusing from cache if possible."""
        if cl is None:
            raise ImportError("pyopencl required for PersistentBufferPool")
        
        bucket = self._find_bucket(nbytes)
        
        with self._lock:
            if bucket in self._free and self._free[bucket]:
                self.stats.hits += 1
                handle = self._free[bucket].pop()
                self.stats.bytes_cached -= bucket
                return handle
        
        # Allocate new buffer
        self.stats.misses += 1
        self.stats.bytes_allocated += bucket
        
        mf = cl.mem_flags
        use_flags = flags if flags is not None else mf.READ_WRITE
        buf = cl.Buffer(self.context, use_flags, bucket)
        
        return BufferHandle(buffer=buf, nbytes=nbytes, bucket_size=bucket, pool=self)
    
    def release(self, handle: BufferHandle) -> None:
        """Return buffer to pool for reuse."""
        bucket = handle.bucket_size or self._find_bucket(handle.nbytes)
        
        with self._lock:
            # Check if we should cache this buffer
            if self.stats.bytes_cached + bucket > self.max_cached_bytes:
                # Pool is full, let buffer be garbage collected
                return
            
            if bucket not in self._free:
                self._free[bucket] = []
            
            if len(self._free[bucket]) >= self.max_buffers_per_bucket:
                # Bucket is full
                return
            
            self._free[bucket].append(handle)
            self.stats.bytes_cached += bucket
    
    def clear(self) -> None:
        """Clear all cached buffers."""
        with self._lock:
            for bucket in self._free:
                self._free[bucket].clear()
            self.stats.bytes_cached = 0
    
    def get_stats(self) -> Dict:
        """Get pool statistics."""
        with self._lock:
            return {
                "hits": self.stats.hits,
                "misses": self.stats.misses,
                "hit_rate": self.stats.hit_rate,
                "bytes_allocated": self.stats.bytes_allocated,
                "bytes_cached": self.stats.bytes_cached,
                "buckets": {k: len(v) for k, v in self._free.items() if v},
            }


def create_pinned_buffer(queue: "cl.CommandQueue", nbytes: int) -> "cl.Buffer":
    """
    Create a pinned (page-locked) host buffer for faster transfers.
    
    Pinned memory enables DMA transfers which are faster than pageable memory.
    """
    if cl is None:
        raise ImportError("pyopencl required")
    
    mf = cl.mem_flags
    return cl.Buffer(
        queue.context,
        mf.READ_WRITE | mf.ALLOC_HOST_PTR,
        nbytes
    )


def create_zero_copy_buffer(queue: "cl.CommandQueue", host_array: "np.ndarray") -> Tuple["cl.Buffer", "np.ndarray"]:
    """
    Create a zero-copy buffer that shares memory between host and device.
    
    Best for integrated GPUs (Intel, AMD APU) where host and device share memory.
    
    Returns:
        Tuple of (cl.Buffer, mapped numpy array)
    """
    if cl is None or np is None:
        raise ImportError("pyopencl and numpy required")
    
    mf = cl.mem_flags
    buf = cl.Buffer(
        queue.context,
        mf.READ_WRITE | mf.USE_HOST_PTR,
        hostbuf=host_array
    )
    return buf, host_array
