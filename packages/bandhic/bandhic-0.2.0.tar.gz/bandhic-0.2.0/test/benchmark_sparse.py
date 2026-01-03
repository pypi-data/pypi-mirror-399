# %%
import time
import gc
import sys
from typing import Dict, List

import numpy as np
import pandas as pd
from scipy.sparse import csr_array, coo_array

import bandhic as bh
import hicstraw

data_path = '/Users/wwb/workspace-local/call_loop/data/GSE63525_GM12878_insitu_primary_replicate_combined.hic'

# Resolutions to benchmark
RESOLUTIONS = [1000, 5000, 10000]

MAX_DISTANCE = 8_000_000

# Number of random read/write queries per test (adjust if needed)
N_QUERIES = 100_000_000

RNG = np.random.default_rng(42)


def sizeof_sparse_coo(mat: coo_array) -> int:
    return mat.data.nbytes + mat.row.nbytes + mat.col.nbytes


def sizeof_sparse_csr(mat: csr_array) -> int:
    return mat.data.nbytes + mat.indices.nbytes + mat.indptr.nbytes


def time_random_read(mat, row_idx, col_idx) -> float:
    t0 = time.perf_counter()
    _ = mat[row_idx, col_idx]
    return time.perf_counter() - t0


def time_random_write(mat, row_idx, col_idx, value=1) -> float:
    t0 = time.perf_counter()
    mat[row_idx, col_idx] = value
    return time.perf_counter() - t0


def build_matrices(records, resolution: int):
    row_idx = np.fromiter((rec.binX // resolution for rec in records), dtype=np.int64)
    col_idx = np.fromiter((rec.binY // resolution for rec in records), dtype=np.int64)
    data = np.fromiter((rec.counts for rec in records), dtype=np.float64)

    max_bin = int(max(row_idx.max(initial=0), col_idx.max(initial=0)) + 1)

    mat_coo = coo_array((data, (row_idx, col_idx)), shape=(max_bin, max_bin))
    mat_csr = mat_coo.tocsr()
    mat_csr = mat_csr + mat_csr.T

    mat_bh = bh.band_hic_matrix(
        (data, (row_idx, col_idx)),
        diag_num = MAX_DISTANCE // resolution
    )

    return mat_bh, mat_coo, mat_csr, max_bin


def benchmark_resolution(resolution: int) -> List[Dict]:
    print(f"\n=== Benchmarking resolution {resolution} ===", file=sys.stderr)

    records = hicstraw.straw(
        "observed", "KR", data_path, "1", "1", "BP", resolution
    )

    mat_bh, mat_coo, mat_csr, n = build_matrices(records, resolution)
    
    del records
    gc.collect()

    row_q = RNG.integers(0, n, size=N_QUERIES, dtype=np.int64)
    col_q = RNG.integers(0, n, size=N_QUERIES, dtype=np.int64)

    results = []

    # BandHiC
    mem_bh = mat_bh.memory_usage()
    t_read = time_random_read(mat_bh, row_q, col_q)
    t_write = time_random_write(mat_bh, row_q, col_q, 1)
    results.append(dict(
        resolution=resolution,
        structure="BandHiC",
        memory_MiB=mem_bh / 1024**2,
        read_time_s=t_read,
        write_time_s=t_write
    ))
    
    del mat_bh
    gc.collect()

    # COO
    mem_coo = sizeof_sparse_coo(mat_coo)
    t_read = np.nan
    # COO write is inefficient; convert to CSR-like behavior via assignment
    t_write = np.nan
    results.append(dict(
        resolution=resolution,
        structure="COO",
        memory_MiB=mem_coo / 1024**2,
        read_time_s=t_read,
        write_time_s=t_write
    ))

    # CSR
    mem_csr = sizeof_sparse_csr(mat_csr)
    t_read = time_random_read(mat_csr, row_q, col_q)
    t_write = time_random_write(mat_csr, row_q, col_q, 1)
    results.append(dict(
        resolution=resolution,
        structure="CSR",
        memory_MiB=mem_csr / 1024**2,
        read_time_s=t_read,
        write_time_s=t_write
    ))
    
    del mat_coo
    gc.collect()

    # Dense (NumPy matrix)
    # NOTE: This may fail for large n due to memory constraints
    if resolution <= 1000:
        results.append(dict(
            resolution=resolution,
            structure="Dense",
            memory_MiB=np.nan,
            read_time_s=np.nan,
            write_time_s=np.nan
        ))
        return results
    try:
        dense = mat_csr.todense()
        del mat_csr

        mem_dense = dense.nbytes
        t_read = time_random_read(dense, row_q, col_q)
        t_write = time_random_write(dense, row_q, col_q, 1.0)

        results.append(dict(
            resolution=resolution,
            structure="Dense",
            memory_MiB=mem_dense / 1024**2,
            read_time_s=t_read,
            write_time_s=t_write
        ))

        del dense
    except MemoryError:
        results.append(dict(
            resolution=resolution,
            structure="Dense",
            memory_MiB=np.nan,
            read_time_s=np.nan,
            write_time_s=np.nan
        ))
        
    return results


def main():
    all_results: List[Dict] = []
    for res in RESOLUTIONS:
        all_results.extend(benchmark_resolution(res))

    df = pd.DataFrame(all_results)
    out_path = "benchmark_sparse_results.csv"
    df.to_csv(out_path, index=False)
    print("\nBenchmark results:")
    print(df)
    print(f"\nSaved to {out_path}")


if __name__ == "__main__":
    main()
