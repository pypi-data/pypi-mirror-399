"""Swaption instrument definition."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Optional, Union

from qfinlib.instruments.base import Instrument
from qfinlib.instruments.rates.swap.irs import Swap


@dataclass
class Swaption(Instrument):
    """European swaption on an underlying interest rate swap."""

    swap: Swap
    expiry: Union[float, date]
    option_type: str = "payer"  # payer (call) or receiver (put)
    strike: Optional[float] = None
    trade_date: Optional[date] = None

    def notional(self) -> float:
        return self.swap.notional()

    def currency(self) -> str:
        return self.swap.currency()

    @property
    def resolved_strike(self) -> float:
        """Return the strike rate for the swaption.

        If no explicit strike is provided, the fixed rate of the underlying
        swap is used when available.
        """

        if self.strike is not None:
            return self.strike
        if self.swap.fixed_rate is not None:
            return float(self.swap.fixed_rate)
        raise ValueError("Swaption requires an explicit strike when swap has no fixed leg")

    @property
    def is_payer(self) -> bool:
        return self.option_type.lower() == "payer"
