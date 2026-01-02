"""Log-linear interpolation."""
from __future__ import annotations

import math
from typing import Sequence

from .base import Interpolator


class LogLinearInterpolator(Interpolator):
    """Interpolate on the logarithm of y-values (useful for discount factors)."""

    def interpolate(self, x: Sequence[float], y: Sequence[float], x_new: float) -> float:
        if any(value <= 0 for value in y):
            raise ValueError("Log-linear interpolation requires strictly positive y values")
        log_y = [math.log(val) for val in y]
        linear = LinearLike(self.extrapolation)
        result = linear.interpolate(x, log_y, x_new)
        return math.exp(result)


class LinearLike(Interpolator):
    """Small helper to reuse the linear logic without a circular import."""

    def interpolate(self, x: Sequence[float], y: Sequence[float], x_new: float) -> float:
        if not x or not y:
            raise ValueError("x and y values must be provided for interpolation")
        if len(x) != len(y):
            raise ValueError("x and y must have the same length")
        if len(x) == 1:
            return y[0]

        if x_new < x[0] or x_new > x[-1]:
            return self._extrapolate(x, y, x_new)

        idx = self._find_segment(x, x_new)
        if idx == -1:
            return y[-1]
        x0, x1 = x[idx], x[idx + 1]
        y0, y1 = y[idx], y[idx + 1]
        if x1 == x0:
            return y0
        weight = (x_new - x0) / (x1 - x0)
        return y0 + weight * (y1 - y0)
