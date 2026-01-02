"""Unified curve builder interface."""

from typing import Optional, List, Any, Mapping, Tuple
from datetime import date

from qfinlib.market.curve import DiscountCurve, ForwardCurve
from qfinlib.market.container import MarketContainer

# Try to import engine, but make it optional
try:
    from qfinlib.calibration.curve.engine import CurveCalibrationEngine
except ImportError:

    class CurveCalibrationEngine:
        """Placeholder calibration engine."""

        pass


class CurveBuilder:
    """Unified interface for building curves."""

    def __init__(self, market: MarketContainer):
        """Initialize with market data."""
        self.market = market
        self.engine = CurveCalibrationEngine()

    def _nodes_from_instruments(
        self, instruments: Optional[List[Any]], fallback_rate: float, prefix: str
    ) -> Tuple[List[float], List[float], List[str]]:
        if not instruments:
            return [0.0, 30.0], [fallback_rate, fallback_rate], [f"{prefix}_0", f"{prefix}_1"]

        pillars: List[float] = []
        quotes: List[float] = []
        names: List[str] = []
        for idx, instrument in enumerate(instruments):
            name = f"{prefix}_{idx}"
            pillar: Optional[float] = None
            quote: Optional[float] = None
            if isinstance(instrument, Mapping):
                pillar = instrument.get("pillar") or instrument.get("tenor") or instrument.get("time")
                quote = instrument.get("quote")
                name = instrument.get("name") or instrument.get("instrument") or name
            elif isinstance(instrument, tuple) or isinstance(instrument, list):
                if len(instrument) >= 2:
                    pillar, quote = instrument[0], instrument[1]
                if len(instrument) >= 3:
                    name = instrument[2]
            if pillar is None or quote is None:
                raise ValueError("Each instrument must provide a pillar/time and a quote")
            pillars.append(float(pillar))
            quotes.append(float(quote))
            names.append(str(name))
        return pillars, quotes, names

    def build_discount_curve(
        self,
        currency: str,
        instruments: Optional[List[Any]] = None,
        as_of: Optional[date] = None,
        interpolation: str = "log_linear",
        extrapolation: str = "flat",
    ) -> DiscountCurve:
        """Build a discount curve for a currency."""

        rate_guess = float(self.market.data.get("discount_rate", 0.0))
        pillars, quotes, names = self._nodes_from_instruments(instruments, rate_guess, "discount")
        metadata = {"currency": currency, "as_of": as_of or self.market.as_of}
        return DiscountCurve(
            pillars=pillars,
            zero_rates=quotes,
            instruments=names,
            interpolation=interpolation,
            extrapolation=extrapolation,
            market_data=self.market.data,
            metadata=metadata,
        )

    def build_forward_curve(
        self,
        currency: str,
        index: str,
        instruments: Optional[List[Any]] = None,
        as_of: Optional[date] = None,
        interpolation: str = "linear",
        extrapolation: str = "flat",
    ) -> ForwardCurve:
        """Build a forward curve for a currency and index."""

        rate_guess = float(self.market.data.get("forward_rate", 0.0))
        pillars, quotes, names = self._nodes_from_instruments(instruments, rate_guess, index)
        metadata = {"currency": currency, "index": index, "as_of": as_of or self.market.as_of}
        return ForwardCurve(
            pillars=pillars,
            forward_rates=quotes,
            instruments=names,
            interpolation=interpolation,
            extrapolation=extrapolation,
            index=index,
            market_data=self.market.data,
            metadata=metadata,
        )
