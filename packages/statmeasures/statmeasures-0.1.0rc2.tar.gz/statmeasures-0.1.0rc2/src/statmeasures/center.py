"""Measures of central tendency."""

__all__ = (
    "harmonic_mean",
    "geometric_mean",
    "trimmed_mean",
    "winsorized_mean",
    "dwe",
    "spwe",
)

import numpy as np
from scipy.stats import mstats


def harmonic_mean(data: np.ndarray) -> float:
    """Return the harmonic mean."""
    return mstats.hmean(data)


def geometric_mean(data: np.ndarray) -> float:
    """Return the geometric mean."""
    return mstats.gmean(data)


def trimmed_mean(data: np.ndarray, alpha: float) -> float:
    """Return the trimmed mean."""
    return mstats.trimmed_mean(data, limits=(alpha, alpha))


def winsorized_mean(data: np.ndarray, alpha: float) -> float:
    """Return the winsorized mean."""
    winsorized_data = mstats.winsorize(data, limits=(alpha, alpha))
    return winsorized_data.mean()


def dwe(data: np.ndarray) -> float:
    """Return the distance-weighted estimator."""
    distances = np.abs(np.subtract.outer(data, data, dtype=np.float64))
    weights = (len(data) - 1) / distances.sum(axis=1)
    return (weights * data).sum() / weights.sum()


def spwe(data: np.ndarray) -> float:
    """Return the scalar-product weighted estimator."""
    a = np.pi / 2 * (data - data.min()) / (data.max() - data.min())
    w = np.abs(np.cos(np.subtract.outer(a, a)))
    x = np.add.outer(data, data) / 2.0

    np.fill_diagonal(w, 0.0)
    np.fill_diagonal(x, 0.0)

    return (w * x).sum() / w.sum()
