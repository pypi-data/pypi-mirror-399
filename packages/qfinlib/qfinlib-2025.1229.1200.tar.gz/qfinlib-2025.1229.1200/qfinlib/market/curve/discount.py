"""Discount curve."""
from __future__ import annotations

import math
from typing import Mapping, Optional, Sequence

from .base import Curve, InterpolatorLike


class DiscountCurve(Curve):
    """Curve representing discount factors or zero rates.

    Values are stored internally as zero rates with continuous compounding to
    keep the representation consistent across different construction inputs.
    """

    def __init__(
        self,
        pillars: Sequence[float] = (),
        zero_rates: Optional[Sequence[float]] = None,
        discount_factors: Optional[Sequence[float]] = None,
        instruments: Optional[Sequence[str]] = None,
        interpolation: InterpolatorLike = "log_linear",
        extrapolation: str = "flat",
        curve_type: str = "discount",
        market_data: Mapping[str, float] = None,
        metadata: Mapping[str, object] = None,
    ):
        rates = list(zero_rates or [])
        if discount_factors is not None:
            if len(discount_factors) != len(pillars):
                raise ValueError("discount_factors must align with pillars")
            rates = [self._df_to_rate(df, t) for df, t in zip(discount_factors, pillars)]
        super().__init__(
            pillars=pillars,
            values=rates,
            instruments=instruments,
            interpolation=interpolation,
            extrapolation=extrapolation,
            curve_type=curve_type,
            market_data=market_data or {},
            metadata=metadata or {},
        )

    @staticmethod
    def _df_to_rate(df: float, t: float) -> float:
        if t == 0:
            return 0.0
        return -math.log(float(df)) / float(t)

    def zero_rate(self, t: float) -> float:
        return self.value(t)

    def discount_factor(self, t: float) -> float:
        rate = self.zero_rate(t)
        return math.exp(-rate * float(t))
