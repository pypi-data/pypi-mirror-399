"""Spread curve."""
from __future__ import annotations

import math
from typing import Mapping, Optional, Sequence

from .base import Curve, InterpolatorLike


class SpreadCurve(Curve):
    """Curve representing a spread on top of a base curve."""

    def __init__(
        self,
        base_curve: Curve,
        pillars: Sequence[float] = (),
        spreads: Sequence[float] = (),
        instruments: Optional[Sequence[str]] = None,
        interpolation: InterpolatorLike = "linear",
        extrapolation: str = "flat",
        curve_type: str = "spread",
        market_data: Mapping[str, float] = None,
        metadata: Mapping[str, object] = None,
    ):
        self.base_curve = base_curve
        super().__init__(
            pillars=pillars or base_curve.pillars,
            values=spreads or [0.0 for _ in base_curve.pillars],
            instruments=instruments or base_curve.instruments,
            interpolation=interpolation,
            extrapolation=extrapolation,
            curve_type=curve_type,
            market_data=market_data or {},
            metadata=metadata or {},
        )

    def value(self, t: float) -> float:
        base = self.base_curve.value(t)
        spread = super().value(t)
        return base + spread

    def discount_factor(self, t: float) -> float:
        getter = getattr(self.base_curve, "discount_factor", None)
        if getter is None:
            raise AttributeError("Base curve does not support discount factors")
        base_rate = getattr(self.base_curve, "zero_rate", None)
        if base_rate is None:
            return getter(t)
        total_rate = base_rate(t) + super().value(t)
        return math.exp(-total_rate * float(t))
