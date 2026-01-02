"""Inflation curve."""
from __future__ import annotations

from typing import Mapping, Optional, Sequence

from qfinlib.market.curve.base import Curve, InterpolatorLike


class InflationCurve(Curve):
    """Simple CPI-based inflation curve."""

    def __init__(
        self,
        pillars: Sequence[float] = (),
        inflation_rates: Sequence[float] = (),
        instruments: Optional[Sequence[str]] = None,
        interpolation: InterpolatorLike = "linear",
        extrapolation: str = "flat",
        curve_type: str = "inflation",
        market_data: Mapping[str, float] = None,
        metadata: Mapping[str, object] = None,
    ):
        super().__init__(
            pillars=pillars,
            values=inflation_rates,
            instruments=instruments,
            interpolation=interpolation,
            extrapolation=extrapolation,
            curve_type=curve_type,
            market_data=market_data or {},
            metadata=metadata or {},
        )

    def inflation_rate(self, t: float) -> float:
        return self.value(t)
