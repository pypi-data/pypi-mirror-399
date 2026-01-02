"""Bond instrument definition."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Any, Dict, Optional

from qfinlib.instruments.base import Instrument


@dataclass
class Bond(Instrument):
    """Plain-vanilla fixed coupon bond.

    The :class:`Bond` stores the economic terms required for pricing while also
    providing a flexible ``metadata`` dictionary to accommodate the extensive
    descriptive fields shown in the product specification (issuer details,
    ratings, identifiers, call features, taxonomy tags, etc.). Only a subset of
    those fields are required for pricing; the rest can be captured inside the
    ``metadata`` mapping without changing the pricing APIs.
    """

    face_value: float
    currency_code: str
    coupon_rate: float
    coupon_frequency: int
    trade_date: Optional[date] = None
    maturity_date: Optional[date] = None
    maturity_in_years: Optional[float] = None
    issue_date: Optional[date] = None
    settlement_date: Optional[date] = None
    yield_rate: Optional[float] = None
    clean_price: Optional[float] = None
    quote_convention: str = "price"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        super().__init__(trade_date=self.trade_date)

    def notional(self) -> float:
        return float(self.face_value)

    def currency(self) -> str:
        return self.currency_code

    def coupon_amount(self) -> float:
        return self.face_value * self.coupon_rate / max(1, self.coupon_frequency)

    def maturity_time(self, as_of: date) -> float:
        """Return time to maturity in years relative to ``as_of``.

        If an explicit ``maturity_in_years`` is provided it takes precedence;
        otherwise the difference between ``maturity_date`` and ``as_of`` is
        converted to a year fraction using a 365-day basis.
        """

        if self.maturity_in_years is not None:
            return max(0.0, float(self.maturity_in_years))
        if self.maturity_date is None:
            return 0.0
        return max(0.0, (self.maturity_date - as_of).days / 365.0)
