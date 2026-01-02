"""Zero curve built on top of the :class:`DiscountCurve`."""
from __future__ import annotations

from typing import Mapping, Optional, Sequence

from .discount import DiscountCurve
from .base import InterpolatorLike


class ZeroCurve(DiscountCurve):
    """Convenience alias emphasising zero-rate semantics."""

    def __init__(
        self,
        pillars: Sequence[float] = (),
        zero_rates: Optional[Sequence[float]] = None,
        instruments: Optional[Sequence[str]] = None,
        interpolation: InterpolatorLike = "log_linear",
        extrapolation: str = "flat",
        market_data: Mapping[str, float] = None,
        metadata: Mapping[str, object] = None,
    ):
        super().__init__(
            pillars=pillars,
            zero_rates=zero_rates,
            instruments=instruments,
            interpolation=interpolation,
            extrapolation=extrapolation,
            curve_type="zero",
            market_data=market_data or {},
            metadata=metadata or {},
        )
