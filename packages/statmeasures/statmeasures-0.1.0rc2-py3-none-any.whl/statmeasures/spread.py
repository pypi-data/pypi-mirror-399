"""Measures of dispersion."""

__all__ = ("stderr",)

import numpy as np


def stderr(data: np.ndarray) -> float:
    """Return the standard error."""
    return data.std(ddof=1) / np.sqrt(len(data))
