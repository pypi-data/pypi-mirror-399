import numpy as np
import scipy as sp
import bandhic as bh

__all__ = [
    "convolve2d",
    "dense_kernel_to_band_kernel"]

def dense_kernel_to_band_kernel(kernel_dense: np.ndarray) -> np.ndarray:
    """
    Convert a dense convolution kernel K_dense into a band kernel K_band so
    correlate2d on the band matches a dense 2D convolution followed by taking
    the banded region.

    Args:
        kernel_dense: shape (H,W)

    Returns:
        K_band: shape (H, 2*bw-1)
    """
    K = np.asarray(kernel_dense, float)
    H, W = K.shape
    Rh = H // 2
    Rw = W // 2

    # Δshift = dy - dx, roughly in [-(bw-1), +(bw-1)]
    K_band = np.zeros((H, W+H-1), dtype=float)

    # kernel_dense index (kx, ky) corresponds to dx = kx-Rh, dy = ky-Rw
    for kx in range(H):
        for ky in range(W):
            dx = kx - Rh
            dy = ky - Rw
            val = K[kx, ky]
            dshift = dy - dx
            col = dshift + (W - 1)
            if 0 <= col < W+H - 1:
                K_band[kx, col] = val

    return K_band

# --------------------------------------------------------
# 1.2 Do 2D “convolution” on the band (actually correlate2d)
# --------------------------------------------------------
def convolve2d(band_matrix, kernel_dense: np.ndarray) -> "bh.band_hic_matrix":
    """
    Perform 2D “convolution” on a band matrix using scipy.signal.correlate2d:
    - first convert the dense kernel to a band kernel
    - then run correlate2d(mode='same') on self.band

    Returns: a new BandHiCMatrix (shape matches the original band)
    """
    K_band = dense_kernel_to_band_kernel(kernel_dense)
    # Use correlate2d to avoid kernel flipping issues
    out = sp.signal.correlate2d(band_matrix.data, K_band, mode="same", boundary="symm")
    # out.shape == (N, bw); Δ dimension already aligned
    return bh.band_hic_matrix(out,band_data_input=True)
