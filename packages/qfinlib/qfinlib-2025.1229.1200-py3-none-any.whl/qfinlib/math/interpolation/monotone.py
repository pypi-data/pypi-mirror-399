"""Monotone interpolation helper.

For now we keep the implementation lightweight by delegating to linear
interpolation which preserves monotonicity for monotone data sets.
"""
from __future__ import annotations

from typing import Sequence

from .linear import LinearInterpolator


class MonotoneInterpolator(LinearInterpolator):
    """Alias for linear interpolation that emphasises monotonicity."""

    def interpolate(self, x: Sequence[float], y: Sequence[float], x_new: float) -> float:
        return super().interpolate(x, y, x_new)
