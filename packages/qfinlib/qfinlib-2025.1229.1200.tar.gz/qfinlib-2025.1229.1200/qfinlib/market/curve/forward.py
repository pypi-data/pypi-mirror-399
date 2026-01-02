"""Forward curve."""
from __future__ import annotations

from typing import Mapping, Optional, Sequence

from .base import Curve, InterpolatorLike


class ForwardCurve(Curve):
    """Simple forward rate curve.

    The forward rate can be queried at any time. If no time is provided the
    first node is returned, making the class compatible with legacy pricers
    that expect a ``forward_rate()`` callable with no parameters.
    """

    def __init__(
        self,
        pillars: Sequence[float] = (),
        forward_rates: Sequence[float] = (),
        instruments: Optional[Sequence[str]] = None,
        interpolation: InterpolatorLike = "linear",
        extrapolation: str = "flat",
        index: Optional[str] = None,
        curve_type: str = "forward",
        market_data: Mapping[str, float] = None,
        metadata: Mapping[str, object] = None,
    ):
        meta = dict(metadata or {})
        if index:
            meta["index"] = index
        super().__init__(
            pillars=pillars,
            values=forward_rates,
            instruments=instruments,
            interpolation=interpolation,
            extrapolation=extrapolation,
            curve_type=curve_type,
            market_data=market_data or {},
            metadata=meta,
        )

    def forward_rate(self, t: Optional[float] = None) -> float:
        if t is None:
            return float(self.values[0]) if self.values else 0.0
        return self.value(t)

    # Some consumers call ``rate`` instead of ``forward_rate``.
    rate = forward_rate
