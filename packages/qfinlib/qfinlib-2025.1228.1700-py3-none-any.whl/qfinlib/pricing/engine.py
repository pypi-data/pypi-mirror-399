"""Unified pricing engine."""

from typing import Any, Optional, Type
from datetime import date
from qfinlib.market.container import MarketContainer
from qfinlib.instruments.base import Instrument
from qfinlib.pricing.pricers.base import Pricer


class PricingEngine:
    """Unified pricing engine for all instruments."""

    def __init__(self, market: MarketContainer):
        """Initialize with market data."""
        self.market = market
        self._pricers: dict[str, Pricer] = {}

    def price(self, instrument: Instrument, as_of: Optional[date] = None) -> Any:
        """Price an instrument."""
        pricer = self._get_pricer(instrument)
        return pricer.price(instrument, self.market, as_of)

    def _get_pricer(self, instrument: Instrument) -> Pricer:
        """Get the appropriate pricer for an instrument."""
        instrument_type = type(instrument).__name__
        if instrument_type not in self._pricers:
            # Lazy load pricer based on instrument type
            self._pricers[instrument_type] = self._create_pricer(instrument)
        return self._pricers[instrument_type]

    def _create_pricer(self, instrument: Instrument) -> Pricer:
        """Create a pricer for an instrument type."""
        from qfinlib.instruments.bond.bond import Bond
        from qfinlib.instruments.rates.swap.irs import Swap
        from qfinlib.instruments.rates.option.swaption import Swaption
        from qfinlib.pricing.pricers import BondPricer, SwapPricer, SwaptionPricer

        mapping: dict[Type[Instrument], Type[Pricer]] = {
            Bond: BondPricer,
            Swap: SwapPricer,
            Swaption: SwaptionPricer,
        }

        for cls, pricer_cls in mapping.items():
            if isinstance(instrument, cls):
                return pricer_cls()

        raise ValueError(f"No pricer registered for instrument type {type(instrument).__name__}")
