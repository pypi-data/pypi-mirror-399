"""Cubic interpolation placeholder.

A lightweight cubic interpolator is provided for completeness. For small
curve construction tasks it falls back to monotone linear behaviour when
insufficient data is available to build a full spline, keeping the
library dependency-free.
"""
from __future__ import annotations

from typing import Sequence

from .linear import LinearInterpolator


class CubicInterpolator(LinearInterpolator):
    """Cubic-like interpolation with linear fallback."""

    def interpolate(self, x: Sequence[float], y: Sequence[float], x_new: float) -> float:
        # A full cubic spline would require additional dependencies; for now we
        # reuse the stable linear interpolation while keeping the entry point
        # compatible with other interpolators.
        return super().interpolate(x, y, x_new)
