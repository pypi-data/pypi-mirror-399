"""Swap leg definitions."""

from dataclasses import dataclass, field
from typing import Iterable, List, Optional


@dataclass
class SwapLeg:
    """Represents one leg of a swap.

    Parameters
    ----------
    notional:
        The notional amount for the leg.
    currency:
        ISO currency code for cashflows.
    payment_times:
        Payment times in years from the valuation date.
    fixed_rate:
        Fixed coupon rate. If ``None`` the leg is treated as floating.
    spread:
        Constant spread added to the reference rate for floating legs.
    pay:
        ``True`` if the leg pays cashflows (i.e. negative from the holder's
        perspective), ``False`` if it receives.
    day_count:
        Accrual factor applied to each coupon.
    forward_curve:
        Optional name of the forward curve used to project floating coupons.
    """

    notional: float
    currency: str
    payment_times: Iterable[float]
    fixed_rate: Optional[float] = None
    spread: float = 0.0
    pay: bool = True
    day_count: float = 1.0
    forward_curve: Optional[str] = None
    payment_times_list: List[float] = field(init=False)

    def __post_init__(self) -> None:
        self.payment_times_list = [float(t) for t in self.payment_times]
        if not self.payment_times_list:
            raise ValueError("SwapLeg requires at least one payment time")
        if self.fixed_rate is not None and self.fixed_rate < 0:
            raise ValueError("Fixed rate must be non-negative")

    @property
    def direction(self) -> int:
        """Return +1 for receive legs and -1 for pay legs."""

        return -1 if self.pay else 1

    def is_fixed(self) -> bool:
        """Return ``True`` when the leg pays fixed coupons."""

        return self.fixed_rate is not None

    def coupon_rate(self, forward_rate: float) -> float:
        """Return the effective coupon rate for the leg.

        For fixed legs, this simply returns ``fixed_rate``. For floating legs
        it uses ``forward_rate`` plus the configured spread.
        """

        if self.is_fixed():
            assert self.fixed_rate is not None
            return self.fixed_rate
        return forward_rate + self.spread

    def cashflows(self, forward_rate: float) -> List[float]:
        """Return the expected coupon cashflows for each payment time."""

        rate = self.coupon_rate(forward_rate)
        coupon = self.notional * self.day_count * rate * self.direction
        return [coupon for _ in self.payment_times_list]
