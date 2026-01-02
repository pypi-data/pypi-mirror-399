"""
Optimized MatMul kernels with register tiling and vectorization, plus cached per-shape configs.
"""

from __future__ import annotations

import json
import os
import time
from typing import Optional, Tuple, Dict

from netcl.core.tensor import Tensor
from netcl.core.memory import BufferPool
from netcl.ops.matmul import _device_hash

try:
    import numpy as np
except ImportError:
    np = None

try:
    import pyopencl as cl
except ImportError:
    cl = None


_DTYPE_INFO = {
    "float": ("float", 4),
    "float32": ("float", 4),
    "half": ("half", 2),
    "float16": ("half", 2),
    "double": ("double", 8),
    "float64": ("double", 8),
}

_KERNEL_CACHE = {}
_TUNING_CACHE: Dict[str, Dict[str, int]] = {}
_ENV_GATE_PERF = os.environ.get("NETCL_MATMUL_GATE_PERF", "1") not in ("0", "", "false", "False")


def _dtype_info(dtype: str) -> Tuple[str, int]:
    if dtype not in _DTYPE_INFO:
        raise ValueError(f"unsupported dtype {dtype}")
    return _DTYPE_INFO[dtype]


def _shape_key(M: int, K: int, N: int, dtype: str) -> str:
    return f"{dtype}:{M}:{K}:{N}"


def _candidate_configs(device: Optional["cl.Device"], dtype: str) -> Tuple[dict, ...]:
    """
    Return candidate kernel configs; capped for Pascal-class GPUs (tile<=32).
    """
    cap_tile = 64
    vendor = getattr(device, "vendor", "").lower() if device is not None else ""
    if "nvidia" in vendor:
        cap_tile = 32
    configs = []
    # Register-tiled variants
    for tile_m, tile_n, tile_k, wpt_m, wpt_n in [
        (16, 16, 8, 2, 2),
        (32, 32, 8, 4, 4),
        (32, 16, 8, 4, 2),
        (32, 32, 16, 4, 4),
    ]:
        if tile_m > cap_tile or tile_n > cap_tile:
            continue
        configs.append(
            {
                "kernel": "register_tiled",
                "tile_m": tile_m,
                "tile_n": tile_n,
                "tile_k": tile_k,
                "wpt_m": wpt_m,
                "wpt_n": wpt_n,
            }
        )
    # Vectorized variant (float only)
    if cap_tile >= 16 and dtype in ("float", "float32"):
        configs.append({"kernel": "vectorized", "tile": min(16, cap_tile)})
    # float4 register-tiled variants (float32 only)
    if dtype in ("float", "float32"):
        configs.append(
            {
                "kernel": "register_tiled_vec4",
                "tile_m": min(32, cap_tile),
                "tile_n": min(32, cap_tile),
                "tile_k": 8,
                "wpt_m": 2,
                "wpt_n": 2,
            }
        )
        configs.append(
            {
                "kernel": "register_tiled_vec4_db",
                "tile_m": min(32, cap_tile),
                "tile_n": min(32, cap_tile),
                "tile_k": 8,
                "wpt_m": 2,
                "wpt_n": 2,
            }
        )
    return tuple(configs)

def _shape_key(M: int, K: int, N: int, dtype: str) -> str:
    return f"{dtype}:{M}:{K}:{N}"


def _load_tuning_cache() -> Dict[str, Dict[str, int]]:
    global _TUNING_CACHE
    if _TUNING_CACHE:
        return _TUNING_CACHE
    try:
        from netcl.ops.matmul import _TUNING_CACHE_PATH  # reuse common path
        if os.path.exists(_TUNING_CACHE_PATH):
            with open(_TUNING_CACHE_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                _TUNING_CACHE = data.get("matmul_opt", {})
    except Exception:
        _TUNING_CACHE = {}
    return _TUNING_CACHE


def _save_tuning_cache() -> None:
    try:
        from netcl.ops.matmul import _TUNING_CACHE_PATH
        os.makedirs(os.path.dirname(_TUNING_CACHE_PATH), exist_ok=True)
        data = {}
        if os.path.exists(_TUNING_CACHE_PATH):
            try:
                with open(_TUNING_CACHE_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception:
                data = {}
        data.setdefault("matmul_opt", {}).update(_TUNING_CACHE)
        with open(_TUNING_CACHE_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f)
    except Exception:
        pass


def _build_matmul_register_tiled_kernel(
    ctx: "cl.Context", 
    dtype_c: str = "float",
    tile_m: int = 32,
    tile_n: int = 32,
    tile_k: int = 8,
    work_per_thread_m: int = 4,
    work_per_thread_n: int = 4
):
    """
    Register-tiled GEMM kernel.
    Each work-item computes a WPT_M x WPT_N block of output.
    """
    cache_key = (ctx.int_ptr, "matmul_reg_tiled", dtype_c, tile_m, tile_n, tile_k, 
                 work_per_thread_m, work_per_thread_n)
    if cache_key in _KERNEL_CACHE:
        return _KERNEL_CACHE[cache_key]
    
    # Work-group dimensions
    wg_m = tile_m // work_per_thread_m
    wg_n = tile_n // work_per_thread_n
    
    src = f"""
    #define TILE_M {tile_m}
    #define TILE_N {tile_n}
    #define TILE_K {tile_k}
    #define WPT_M {work_per_thread_m}
    #define WPT_N {work_per_thread_n}
    #define WG_M {wg_m}
    #define WG_N {wg_n}
    
    __kernel void matmul_register_tiled(
        __global const {dtype_c}* A,
        __global const {dtype_c}* B,
        __global {dtype_c}* C,
        const int M, const int N, const int K
    ) {{
        // Local memory for tiles
        __local {dtype_c} As[TILE_K][TILE_M];
        __local {dtype_c} Bs[TILE_K][TILE_N];
        
        // Work-item and group indices
        int tx = get_local_id(0);  // 0..WG_N-1
        int ty = get_local_id(1);  // 0..WG_M-1
        int bx = get_group_id(0) * TILE_N;
        int by = get_group_id(1) * TILE_M;
        
        // Register storage for output block
        {dtype_c} acc[WPT_M][WPT_N];
        #pragma unroll
        for (int wm = 0; wm < WPT_M; ++wm) {{
            #pragma unroll
            for (int wn = 0; wn < WPT_N; ++wn) {{
                acc[wm][wn] = 0;
            }}
        }}
        
        // Iterate over K dimension in tiles
        for (int k_base = 0; k_base < K; k_base += TILE_K) {{
            // Cooperative load of A tile into local memory
            // Each thread loads multiple elements
            #pragma unroll
            for (int lm = ty; lm < TILE_M; lm += WG_M) {{
                #pragma unroll
                for (int lk = tx; lk < TILE_K; lk += WG_N) {{
                    int row = by + lm;
                    int col = k_base + lk;
                    if (row < M && col < K) {{
                        As[lk][lm] = A[row * K + col];
                    }} else {{
                        As[lk][lm] = 0;
                    }}
                }}
            }}
            
            // Cooperative load of B tile into local memory
            #pragma unroll
            for (int lk = ty; lk < TILE_K; lk += WG_M) {{
                #pragma unroll
                for (int ln = tx; ln < TILE_N; ln += WG_N) {{
                    int row = k_base + lk;
                    int col = bx + ln;
                    if (row < K && col < N) {{
                        Bs[lk][ln] = B[row * N + col];
                    }} else {{
                        Bs[lk][ln] = 0;
                    }}
                }}
            }}
            
            barrier(CLK_LOCAL_MEM_FENCE);
            
            // Compute partial results
            #pragma unroll
            for (int kk = 0; kk < TILE_K; ++kk) {{
                // Load A values for this row into registers
                {dtype_c} a_reg[WPT_M];
                #pragma unroll
                for (int wm = 0; wm < WPT_M; ++wm) {{
                    a_reg[wm] = As[kk][ty * WPT_M + wm];
                }}
                
                // Load B values for this col into registers
                {dtype_c} b_reg[WPT_N];
                #pragma unroll
                for (int wn = 0; wn < WPT_N; ++wn) {{
                    b_reg[wn] = Bs[kk][tx * WPT_N + wn];
                }}
                
                // Compute outer product
                #pragma unroll
                for (int wm = 0; wm < WPT_M; ++wm) {{
                    #pragma unroll
                    for (int wn = 0; wn < WPT_N; ++wn) {{
                        acc[wm][wn] += a_reg[wm] * b_reg[wn];
                    }}
                }}
            }}
            
            barrier(CLK_LOCAL_MEM_FENCE);
        }}
        
        // Write output block
        #pragma unroll
        for (int wm = 0; wm < WPT_M; ++wm) {{
            int row = by + ty * WPT_M + wm;
            if (row >= M) continue;
            
            #pragma unroll
            for (int wn = 0; wn < WPT_N; ++wn) {{
                int col = bx + tx * WPT_N + wn;
                if (col < N) {{
                    C[row * N + col] = acc[wm][wn];
                }}
            }}
        }}
    }}
    """
    
    prg = cl.Program(ctx, src).build()
    kernel = prg.matmul_register_tiled
    _KERNEL_CACHE[cache_key] = kernel
    return kernel


def _build_matmul_register_tiled_float4_kernel(
    ctx: "cl.Context",
    dtype_c: str = "float",
    tile_m: int = 32,
    tile_n: int = 32,
    tile_k: int = 8,
    work_per_thread_m: int = 2,
    work_per_thread_n: int = 2,
):
    """
    Register-tiled GEMM kernel using float4 vectorized loads.
    """
    cache_key = (ctx.int_ptr, "matmul_reg_tiled_vec4", dtype_c, tile_m, tile_n, tile_k, work_per_thread_m, work_per_thread_n)
    if cache_key in _KERNEL_CACHE:
        return _KERNEL_CACHE[cache_key]

    wg_m = tile_m // work_per_thread_m
    wg_n = tile_n // work_per_thread_n

    src = f"""
    #pragma OPENCL EXTENSION cl_khr_fp16 : enable
    #define TILE_M {tile_m}
    #define TILE_N {tile_n}
    #define TILE_K {tile_k}
    #define WPT_M {work_per_thread_m}
    #define WPT_N {work_per_thread_n}
    #define WG_M {wg_m}
    #define WG_N {wg_n}

    __kernel void matmul_reg_tiled_vec4(
        __global const {dtype_c}* A,
        __global const {dtype_c}* B,
        __global {dtype_c}* C,
        const int M, const int N, const int K
    ) {{
        __local {dtype_c} As[TILE_K][TILE_M];
        __local {dtype_c} Bs[TILE_K][TILE_N];

        int tx = get_local_id(0);
        int ty = get_local_id(1);
        int bx = get_group_id(0) * TILE_N;
        int by = get_group_id(1) * TILE_M;

        {dtype_c} acc[WPT_M][WPT_N];
        for (int wm = 0; wm < WPT_M; ++wm) {{
            for (int wn = 0; wn < WPT_N; ++wn) {{
                acc[wm][wn] = 0;
            }}
        }}

        for (int k_base = 0; k_base < K; k_base += TILE_K) {{
            for (int lm = ty; lm < TILE_M; lm += WG_M) {{
                for (int lk = tx * 4; lk < TILE_K; lk += WG_N * 4) {{
                    int row = by + lm;
                    int col = k_base + lk;
                    if (row < M && (col + 3) < K) {{
                        {dtype_c}4 a_vec = vload4(0, A + row * K + col);
                        As[lk + 0][lm] = a_vec.s0;
                        As[lk + 1][lm] = a_vec.s1;
                        As[lk + 2][lm] = a_vec.s2;
                        As[lk + 3][lm] = a_vec.s3;
                    }} else {{
                        for (int i = 0; i < 4 && (lk + i) < TILE_K; ++i) {{
                            int cc = col + i;
                            As[lk + i][lm] = (row < M && cc < K) ? A[row * K + cc] : 0;
                        }}
                    }}
                }}
            }}
            for (int lk = ty; lk < TILE_K; lk += WG_M) {{
                for (int ln = tx * 4; ln < TILE_N; ln += WG_N * 4) {{
                    int rowb = k_base + lk;
                    int colb = bx + ln;
                    if (rowb < K && (colb + 3) < N) {{
                        {dtype_c}4 b_vec = vload4(0, B + rowb * N + colb);
                        Bs[lk][ln + 0] = b_vec.s0;
                        Bs[lk][ln + 1] = b_vec.s1;
                        Bs[lk][ln + 2] = b_vec.s2;
                        Bs[lk][ln + 3] = b_vec.s3;
                    }} else {{
                        for (int i = 0; i < 4 && (ln + i) < TILE_N; ++i) {{
                            int cc = colb + i;
                            Bs[lk][ln + i] = (rowb < K && cc < N) ? B[rowb * N + cc] : 0;
                        }}
                    }}
                }}
            }}

            barrier(CLK_LOCAL_MEM_FENCE);

            for (int k = 0; k < TILE_K; ++k) {{
                for (int wm = 0; wm < WPT_M; ++wm) {{
                    int row = ty * WPT_M + wm;
                    float a_val = As[k][row];
                    #pragma unroll
                    for (int wn = 0; wn < WPT_N; ++wn) {{
                        int col = tx * WPT_N + wn;
                        acc[wm][wn] += a_val * Bs[k][col];
                    }}
                }}
            }}

            barrier(CLK_LOCAL_MEM_FENCE);
        }}

        for (int wm = 0; wm < WPT_M; ++wm) {{
            int row = by + ty * WPT_M + wm;
            if (row < M) {{
                for (int wn = 0; wn < WPT_N; ++wn) {{
                    int col = bx + tx * WPT_N + wn;
                    if (col < N) {{
                        C[row * N + col] = acc[wm][wn];
                    }}
                }}
            }}
        }}
    }}
    """
    prg = cl.Program(ctx, src).build()
    kernel = prg.matmul_reg_tiled_vec4
    _KERNEL_CACHE[cache_key] = kernel
    return kernel


def _build_matmul_vectorized_kernel(
    ctx: "cl.Context",
    dtype_c: str = "float",
    tile_size: int = 16
):
    """
    Vectorized GEMM using float4 for memory access.
    """
    cache_key = (ctx.int_ptr, "matmul_vec4", dtype_c, tile_size)
    if cache_key in _KERNEL_CACHE:
        return _KERNEL_CACHE[cache_key]
    
    src = f"""
    #define TILE {tile_size}
    
    __kernel void matmul_vec4(
        __global const {dtype_c}* A,
        __global const {dtype_c}* B,
        __global {dtype_c}* C,
        const int M, const int N, const int K
    ) {{
        __local {dtype_c} As[TILE][TILE];
        __local {dtype_c} Bs[TILE][TILE];
        
        int row = get_global_id(0);
        int col = get_global_id(1);
        int lr = get_local_id(0);
        int lc = get_local_id(1);
        
        {dtype_c} acc = 0;
        
        int num_tiles = (K + TILE - 1) / TILE;
        
        for (int t = 0; t < num_tiles; ++t) {{
            int k_base = t * TILE;
            
            // Load tiles
            int a_col = k_base + lc;
            int b_row = k_base + lr;
            
            As[lr][lc] = (row < M && a_col < K) ? A[row * K + a_col] : 0;
            Bs[lr][lc] = (b_row < K && col < N) ? B[b_row * N + col] : 0;
            
            barrier(CLK_LOCAL_MEM_FENCE);
            
            // Compute with manual unrolling for better performance
            #pragma unroll
            for (int k = 0; k < TILE; ++k) {{
                acc += As[lr][k] * Bs[k][lc];
            }}
            
            barrier(CLK_LOCAL_MEM_FENCE);
        }}
        
        if (row < M && col < N) {{
            C[row * N + col] = acc;
        }}
    }}
    """
    
    prg = cl.Program(ctx, src).build()
    kernel = prg.matmul_vec4
    _KERNEL_CACHE[cache_key] = kernel
    return kernel


def _build_matmul_register_tiled_float4_db_kernel(
    ctx: "cl.Context",
    dtype_c: str = "float",
    tile_m: int = 32,
    tile_n: int = 32,
    tile_k: int = 8,
    work_per_thread_m: int = 2,
    work_per_thread_n: int = 2,
):
    """
    Register-tiled GEMM kernel using float4 vectorized loads with double buffering for global->local.
    """
    cache_key = (ctx.int_ptr, "matmul_reg_tiled_vec4_db", dtype_c, tile_m, tile_n, tile_k, work_per_thread_m, work_per_thread_n)
    if cache_key in _KERNEL_CACHE:
        return _KERNEL_CACHE[cache_key]

    wg_m = tile_m // work_per_thread_m
    wg_n = tile_n // work_per_thread_n

    src = f"""
    #pragma OPENCL EXTENSION cl_khr_fp16 : enable
    #define TILE_M {tile_m}
    #define TILE_N {tile_n}
    #define TILE_K {tile_k}
    #define WPT_M {work_per_thread_m}
    #define WPT_N {work_per_thread_n}
    #define WG_M {wg_m}
    #define WG_N {wg_n}

    __kernel void matmul_reg_tiled_vec4_db(
        __global const {dtype_c}* A,
        __global const {dtype_c}* B,
        __global {dtype_c}* C,
        const int M, const int N, const int K
    ) {{
        __local {dtype_c} As0[TILE_K][TILE_M];
        __local {dtype_c} As1[TILE_K][TILE_M];
        __local {dtype_c} Bs0[TILE_K][TILE_N];
        __local {dtype_c} Bs1[TILE_K][TILE_N];

        int tx = get_local_id(0);
        int ty = get_local_id(1);
        int bx = get_group_id(0) * TILE_N;
        int by = get_group_id(1) * TILE_M;

        {dtype_c} acc[WPT_M][WPT_N];
        for (int wm = 0; wm < WPT_M; ++wm) {{
            for (int wn = 0; wn < WPT_N; ++wn) {{
                acc[wm][wn] = 0;
            }}
        }}

        int num_tiles = (K + TILE_K - 1) / TILE_K;

        // Preload first tile into buffer 0
        int k_base = 0;
        for (int lm = ty; lm < TILE_M; lm += WG_M) {{
            for (int lk = tx * 4; lk < TILE_K; lk += WG_N * 4) {{
                int row = by + lm;
                int col = k_base + lk;
                if (row < M && (col + 3) < K) {{
                    {dtype_c}4 a_vec = vload4(0, A + row * K + col);
                    As0[lk + 0][lm] = a_vec.s0;
                    As0[lk + 1][lm] = a_vec.s1;
                    As0[lk + 2][lm] = a_vec.s2;
                    As0[lk + 3][lm] = a_vec.s3;
                }} else {{
                    for (int i = 0; i < 4 && (lk + i) < TILE_K; ++i) {{
                        int cc = col + i;
                        As0[lk + i][lm] = (row < M && cc < K) ? A[row * K + cc] : 0;
                    }}
                }}
            }}
        }}
        for (int lk = ty; lk < TILE_K; lk += WG_M) {{
            for (int ln = tx * 4; ln < TILE_N; ln += WG_N * 4) {{
                int rowb = k_base + lk;
                int colb = bx + ln;
                if (rowb < K && (colb + 3) < N) {{
                    {dtype_c}4 b_vec = vload4(0, B + rowb * N + colb);
                    Bs0[lk][ln + 0] = b_vec.s0;
                    Bs0[lk][ln + 1] = b_vec.s1;
                    Bs0[lk][ln + 2] = b_vec.s2;
                    Bs0[lk][ln + 3] = b_vec.s3;
                }} else {{
                    for (int i = 0; i < 4 && (ln + i) < TILE_N; ++i) {{
                        int cc = colb + i;
                        Bs0[lk][ln + i] = (rowb < K && cc < N) ? B[rowb * N + cc] : 0;
                    }}
                }}
            }}
        }}
        barrier(CLK_LOCAL_MEM_FENCE);

        for (int t = 0; t < num_tiles; ++t) {{
            // Prefetch next tile into buffer 1 while computing on buffer 0, and vice versa
            int next_k_base = (t + 1) * TILE_K;
            int use_buf0 = (t % 2 == 0);
            __local {dtype_c} (*As)[TILE_M] = use_buf0 ? As0 : As1;
            __local {dtype_c} (*Bs)[TILE_N] = use_buf0 ? Bs0 : Bs1;
            __local {dtype_c} (*As_next)[TILE_M] = use_buf0 ? As1 : As0;
            __local {dtype_c} (*Bs_next)[TILE_N] = use_buf0 ? Bs1 : Bs0;

            // Preload next tile if it exists
            if (t + 1 < num_tiles) {{
                for (int lm = ty; lm < TILE_M; lm += WG_M) {{
                    for (int lk = tx * 4; lk < TILE_K; lk += WG_N * 4) {{
                        int row = by + lm;
                        int col = next_k_base + lk;
                        if (row < M && (col + 3) < K) {{
                            {dtype_c}4 a_vec = vload4(0, A + row * K + col);
                            As_next[lk + 0][lm] = a_vec.s0;
                            As_next[lk + 1][lm] = a_vec.s1;
                            As_next[lk + 2][lm] = a_vec.s2;
                            As_next[lk + 3][lm] = a_vec.s3;
                        }} else {{
                            for (int i = 0; i < 4 && (lk + i) < TILE_K; ++i) {{
                                int cc = col + i;
                                As_next[lk + i][lm] = (row < M && cc < K) ? A[row * K + cc] : 0;
                            }}
                        }}
                    }}
                }}
                for (int lk = ty; lk < TILE_K; lk += WG_M) {{
                    for (int ln = tx * 4; ln < TILE_N; ln += WG_N * 4) {{
                        int rowb = next_k_base + lk;
                        int colb = bx + ln;
                        if (rowb < K && (colb + 3) < N) {{
                            {dtype_c}4 b_vec = vload4(0, B + rowb * N + colb);
                            Bs_next[lk][ln + 0] = b_vec.s0;
                            Bs_next[lk][ln + 1] = b_vec.s1;
                            Bs_next[lk][ln + 2] = b_vec.s2;
                            Bs_next[lk][ln + 3] = b_vec.s3;
                        }} else {{
                            for (int i = 0; i < 4 && (ln + i) < TILE_N; ++i) {{
                                int cc = colb + i;
                                Bs_next[lk][ln + i] = (rowb < K && cc < N) ? B[rowb * N + cc] : 0;
                            }}
                        }}
                    }}
                }}
            }}

            barrier(CLK_LOCAL_MEM_FENCE);

            for (int k = 0; k < TILE_K; ++k) {{
                for (int wm = 0; wm < WPT_M; ++wm) {{
                    int row = ty * WPT_M + wm;
                    float a_val = As[k][row];
                    for (int wn = 0; wn < WPT_N; ++wn) {{
                        int col = tx * WPT_N + wn;
                        acc[wm][wn] += a_val * Bs[k][col];
                    }}
                }}
            }}

            barrier(CLK_LOCAL_MEM_FENCE);
        }}

        for (int wm = 0; wm < WPT_M; ++wm) {{
            int row = by + ty * WPT_M + wm;
            if (row < M) {{
                for (int wn = 0; wn < WPT_N; ++wn) {{
                    int col = bx + tx * WPT_N + wn;
                    if (col < N) {{
                        C[row * N + col] = acc[wm][wn];
                    }}
                }}
            }}
        }}
    }}
    """
    prg = cl.Program(ctx, src).build()
    kernel = prg.matmul_reg_tiled_vec4_db
    _KERNEL_CACHE[cache_key] = kernel
    return kernel
def select_matmul_config(M: int, N: int, K: int, device_profile=None) -> dict:
    """
    Select optimal matmul configuration based on problem size and device.
    """
    total_elements = M * N
    # Default configs, will be overridden by tuning if available
    if total_elements < 4096:
        cfg = {
            "kernel": "register_tiled",
            "tile_m": 16,
            "tile_n": 16,
            "tile_k": 8,
            "wpt_m": 2,
            "wpt_n": 2,
        }
    elif total_elements < 65536:
        cfg = {
            "kernel": "register_tiled",
            "tile_m": 32,
            "tile_n": 32,
            "tile_k": 8,
            "wpt_m": 4,
            "wpt_n": 4,
        }
    else:
        cfg = {
            "kernel": "register_tiled",
            "tile_m": 32,  # cap for Pascal-class GPUs
            "tile_n": 32,
            "tile_k": 8,
            "wpt_m": 4,
            "wpt_n": 4,
        }
    # Check tuning cache
    _load_tuning_cache()
    key = (_device_hash(getattr(device_profile, "device", None)) if device_profile else "unknown") + "|" + _shape_key(M, K, N, "float")
    if "matmul_opt" in _TUNING_CACHE and key in _TUNING_CACHE["matmul_opt"]:
        cached = _TUNING_CACHE["matmul_opt"][key]
        cfg.update(cached)
    return cfg


def matmul_optimized(
    a: Tensor,
    b: Tensor,
    out: Optional[Tensor] = None,
    pool: Optional[BufferPool] = None,
    config: Optional[dict] = None
) -> Tensor:
    """
    Optimized matrix multiplication with auto-tuned configuration.
    """
    if cl is None or np is None:
        raise ImportError("pyopencl and numpy required")
    
    if len(a.shape) != 2 or len(b.shape) != 2:
        raise ValueError("matmul expects 2D tensors")
    
    M, K = a.shape
    Kb, N = b.shape
    if K != Kb:
        raise ValueError("inner dimensions must match")
    
    if a.dtype != b.dtype:
        raise ValueError("dtype mismatch")
    
    ctx = a.context
    q = a.queue
    dtype_c, _ = _dtype_info(a.dtype)
    
    # Get configuration
    if config is None:
        config = select_matmul_config(M, N, K, device_profile=getattr(ctx, "device_profile", None))

    # Optional autotune per shape
    autotune = os.environ.get("NETCL_MATMUL_AUTOTUNE_SHAPE", "0") not in ("0", "", "false", "False")
    if autotune and cl is not None and np is not None:
        key = _device_hash(getattr(ctx, "devices", [None])[0] if ctx and getattr(ctx, "devices", None) else None) + "|" + _shape_key(M, K, N, a.dtype)
        _load_tuning_cache()
        if "matmul_opt" not in _TUNING_CACHE or key not in _TUNING_CACHE.get("matmul_opt", {}):
            best_cfg = None
            best_time = 1e9
            for cfg in _candidate_configs(
                getattr(ctx, "devices", [None])[0] if ctx and getattr(ctx, "devices", None) else None,
                a.dtype,
            ):
                # build kernel and time once
                if cfg.get("kernel") == "vectorized":
                    tile = cfg.get("tile", 16)
                    kernel = _build_matmul_vectorized_kernel(ctx, dtype_c, tile)
                    lsize = (tile, tile)
                    gsize = (int(np.ceil(M / tile)) * tile, int(np.ceil(N / tile)) * tile)
                    evt = kernel(
                        q, gsize, lsize,
                        a.buffer, b.buffer,
                        Tensor.from_shape(q, (M, N), dtype=a.dtype, pool=pool).buffer,
                        np.int32(M), np.int32(N), np.int32(K)
                    )
                elif cfg.get("kernel") == "register_tiled_vec4":
                    tile_m = cfg.get("tile_m", 32)
                    tile_n = cfg.get("tile_n", 32)
                    tile_k = cfg.get("tile_k", 8)
                    wpt_m = cfg.get("wpt_m", 2)
                    wpt_n = cfg.get("wpt_n", 2)
                    kernel = _build_matmul_register_tiled_float4_kernel(ctx, dtype_c, tile_m, tile_n, tile_k, wpt_m, wpt_n)
                    wg_m = tile_m // wpt_m
                    wg_n = tile_n // wpt_n
                    gsize = (int(np.ceil(N / tile_n)) * wg_n, int(np.ceil(M / tile_m)) * wg_m)
                    lsize = (wg_n, wg_m)
                    evt = kernel(
                        q, gsize, lsize,
                        a.buffer, b.buffer,
                        Tensor.from_shape(q, (M, N), dtype=a.dtype, pool=pool).buffer,
                        np.int32(M), np.int32(N), np.int32(K)
                    )
                elif cfg.get("kernel") == "register_tiled_vec4_db":
                    tile_m = cfg.get("tile_m", 32)
                    tile_n = cfg.get("tile_n", 32)
                    tile_k = cfg.get("tile_k", 8)
                    wpt_m = cfg.get("wpt_m", 2)
                    wpt_n = cfg.get("wpt_n", 2)
                    kernel = _build_matmul_register_tiled_float4_db_kernel(ctx, dtype_c, tile_m, tile_n, tile_k, wpt_m, wpt_n)
                    wg_m = tile_m // wpt_m
                    wg_n = tile_n // wpt_n
                    gsize = (int(np.ceil(N / tile_n)) * wg_n, int(np.ceil(M / tile_m)) * wg_m)
                    lsize = (wg_n, wg_m)
                    evt = kernel(
                        q, gsize, lsize,
                        a.buffer, b.buffer,
                        Tensor.from_shape(q, (M, N), dtype=a.dtype, pool=pool).buffer,
                        np.int32(M), np.int32(N), np.int32(K)
                    )
                else:
                    tile_m = cfg.get("tile_m", 32)
                    tile_n = cfg.get("tile_n", 32)
                    tile_k = cfg.get("tile_k", 8)
                    wpt_m = cfg.get("wpt_m", 4)
                    wpt_n = cfg.get("wpt_n", 4)
                    kernel = _build_matmul_register_tiled_kernel(ctx, dtype_c, tile_m, tile_n, tile_k, wpt_m, wpt_n)
                    wg_m = tile_m // wpt_m
                    wg_n = tile_n // wpt_n
                    gsize = (int(np.ceil(N / tile_n)) * wg_n, int(np.ceil(M / tile_m)) * wg_m)
                    lsize = (wg_n, wg_m)
                    evt = kernel(
                        q, gsize, lsize,
                        a.buffer, b.buffer,
                        Tensor.from_shape(q, (M, N), dtype=a.dtype, pool=pool).buffer,
                        np.int32(M), np.int32(N), np.int32(K)
                    )
                try:
                    evt.wait()
                    dt = (evt.profile.end - evt.profile.start) * 1e-9
                except Exception:
                    dt = 1e9
                if dt < best_time:
                    best_time = dt
                    best_cfg = cfg
            if best_cfg:
                # Optional performance gate: compare best optimized vs stable matmul and fall back if slower
                if _ENV_GATE_PERF:
                    try:
                        import netcl.ops.matmul as matmul_base

                        prev_opt = matmul_base._USE_OPTIMIZED
                        matmul_base._USE_OPTIMIZED = False
                        t0 = time.perf_counter()
                        out_base = matmul_base.matmul(a, b, pool=pool)
                        out_base.queue.finish()
                        base_time = time.perf_counter() - t0
                        matmul_base._USE_OPTIMIZED = prev_opt
                        if best_time > base_time * 0.95:
                            # Cache sentinel to use stable path
                            _TUNING_CACHE.setdefault("matmul_opt", {})[key] = {"kernel": "stable"}
                            _save_tuning_cache()
                            return out_base
                    except Exception:
                        pass
                _TUNING_CACHE.setdefault("matmul_opt", {})[key] = best_cfg
                _save_tuning_cache()
                config = best_cfg

    kernel_name = config.get("kernel", "register_tiled")

    if kernel_name == "stable":
        import netcl.ops.matmul as matmul_base

        prev_opt = matmul_base._USE_OPTIMIZED
        matmul_base._USE_OPTIMIZED = False
        try:
            return matmul_base.matmul(a, b, out=out, pool=pool)
        finally:
            matmul_base._USE_OPTIMIZED = prev_opt
    if kernel_name == "vectorized":
        tile = config.get("tile", 16)
        kernel = _build_matmul_vectorized_kernel(ctx, dtype_c, tile)
        if out is None:
            out = Tensor.from_shape(q, (M, N), dtype=a.dtype, pool=pool)
        global_size = (
            int(np.ceil(M / tile)) * tile,
            int(np.ceil(N / tile)) * tile,
        )
        kernel(
            q,
            global_size,
            (tile, tile),
            a.buffer,
            b.buffer,
            out.buffer,
            np.int32(M),
            np.int32(N),
            np.int32(K),
        )
        return out
    elif kernel_name == "register_tiled_vec4_db":
        tile_m = config.get("tile_m", 32)
        tile_n = config.get("tile_n", 32)
        tile_k = config.get("tile_k", 8)
        wpt_m = config.get("wpt_m", 2)
        wpt_n = config.get("wpt_n", 2)
        kernel = _build_matmul_register_tiled_float4_db_kernel(ctx, dtype_c, tile_m, tile_n, tile_k, wpt_m, wpt_n)
        if out is None:
            out = Tensor.from_shape(q, (M, N), dtype=a.dtype, pool=pool)
        wg_m = tile_m // wpt_m
        wg_n = tile_n // wpt_n
        global_size = (
            int(np.ceil(N / tile_n)) * wg_n,
            int(np.ceil(M / tile_m)) * wg_m,
        )
        kernel(
            q,
            global_size,
            (wg_n, wg_m),
            a.buffer,
            b.buffer,
            out.buffer,
            np.int32(M),
            np.int32(N),
            np.int32(K),
        )
        return out
    elif kernel_name == "register_tiled_vec4":
        tile_m = config.get("tile_m", 32)
        tile_n = config.get("tile_n", 32)
        tile_k = config.get("tile_k", 8)
        wpt_m = config.get("wpt_m", 2)
        wpt_n = config.get("wpt_n", 2)
        kernel = _build_matmul_register_tiled_float4_kernel(ctx, dtype_c, tile_m, tile_n, tile_k, wpt_m, wpt_n)
        if out is None:
            out = Tensor.from_shape(q, (M, N), dtype=a.dtype, pool=pool)
        wg_m = tile_m // wpt_m
        wg_n = tile_n // wpt_n
        global_size = (
            int(np.ceil(N / tile_n)) * wg_n,
            int(np.ceil(M / tile_m)) * wg_m,
        )
        kernel(
            q,
            global_size,
            (wg_n, wg_m),
            a.buffer,
            b.buffer,
            out.buffer,
            np.int32(M),
            np.int32(N),
            np.int32(K),
        )
        return out

    # Default register-tiled
    kernel = _build_matmul_register_tiled_kernel(
        ctx, dtype_c,
        tile_m=config.get("tile_m", 32),
        tile_n=config.get("tile_n", 32),
        tile_k=config.get("tile_k", 8),
        work_per_thread_m=config.get("wpt_m", 4),
        work_per_thread_n=config.get("wpt_n", 4)
    )

    if out is None:
        out = Tensor.from_shape(q, (M, N), dtype=a.dtype, pool=pool)

    tile_m = config.get("tile_m", 32)
    tile_n = config.get("tile_n", 32)
    wpt_m = config.get("wpt_m", 4)
    wpt_n = config.get("wpt_n", 4)

    wg_m = tile_m // wpt_m
    wg_n = tile_n // wpt_n

    global_m = int(np.ceil(M / tile_m)) * wg_m
    global_n = int(np.ceil(N / tile_n)) * wg_n

    kernel(
        q, (global_n, global_m), (wg_n, wg_m),
        a.buffer, b.buffer, out.buffer,
        np.int32(M), np.int32(N), np.int32(K)
    )

    return out


__all__ = [
    'matmul_optimized',
    'select_matmul_config',
]
