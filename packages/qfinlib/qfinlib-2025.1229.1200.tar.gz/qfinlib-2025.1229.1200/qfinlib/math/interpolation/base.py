"""Interpolator base class and helpers for simple curve construction.

The implementations in this module intentionally avoid third-party
numerical dependencies; they are lightweight utilities used by the curve
objects defined in :mod:`qfinlib.market.curve`.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Sequence


class Interpolator(ABC):
    """Abstract interpolator.

    Concrete implementations must provide :meth:`interpolate` which will be
    called by :py:meth:`__call__`.
    """

    def __init__(self, extrapolation: str = "flat"):
        self.extrapolation = extrapolation

    def __call__(self, x: Sequence[float], y: Sequence[float], x_new: float) -> float:
        return self.interpolate(x, y, x_new)

    @abstractmethod
    def interpolate(self, x: Sequence[float], y: Sequence[float], x_new: float) -> float:
        """Interpolate the value for ``x_new`` using known points ``x`` and ``y``."""

    def _extrapolate(self, x: Sequence[float], y: Sequence[float], x_new: float) -> float:
        if len(x) < 2:
            return y[0]
        if self.extrapolation == "flat":
            return y[0] if x_new < x[0] else y[-1]
        if self.extrapolation == "nearest":
            return y[0] if abs(x_new - x[0]) < abs(x_new - x[-1]) else y[-1]
        if self.extrapolation == "linear":
            if x_new < x[0]:
                slope = (y[1] - y[0]) / (x[1] - x[0])
                return y[0] + slope * (x_new - x[0])
            slope = (y[-1] - y[-2]) / (x[-1] - x[-2])
            return y[-1] + slope * (x_new - x[-1])
        raise ValueError(f"Unsupported extrapolation mode: {self.extrapolation}")

    @staticmethod
    def _find_segment(x: Sequence[float], x_new: float) -> int:
        for i in range(len(x) - 1):
            if x[i] <= x_new <= x[i + 1]:
                return i
        return -1
