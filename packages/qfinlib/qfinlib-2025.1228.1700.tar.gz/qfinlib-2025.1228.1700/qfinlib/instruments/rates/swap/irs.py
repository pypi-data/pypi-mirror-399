"""Interest rate swap instrument."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Callable, Iterable, Optional, Tuple

from qfinlib.instruments.base import Instrument
from qfinlib.instruments.rates.swap.leg import SwapLeg


SwapLegFactory = Callable[..., Tuple[SwapLeg, SwapLeg]]


def vanilla_fixed_float_generator(
    *,
    notional: float,
    currency: str,
    fixed_rate: float,
    float_forward_curve: Optional[str],
    payment_times_fixed: Iterable[float],
    payment_times_float: Iterable[float],
    pay_fixed: bool = True,
    spread: float = 0.0,
    day_count: float = 1.0,
) -> Tuple[SwapLeg, SwapLeg]:
    """Construct a vanilla fixed-versus-floating swap."""

    fixed_leg = SwapLeg(
        notional=notional,
        currency=currency,
        payment_times=payment_times_fixed,
        fixed_rate=fixed_rate,
        pay=pay_fixed,
        day_count=day_count,
    )
    float_leg = SwapLeg(
        notional=notional,
        currency=currency,
        payment_times=payment_times_float,
        fixed_rate=None,
        forward_curve=float_forward_curve,
        spread=spread,
        pay=not pay_fixed,
        day_count=day_count,
    )
    return fixed_leg, float_leg


def basis_swap_generator(
    *,
    notional: float,
    currency: str,
    payment_times_leg1: Iterable[float],
    payment_times_leg2: Iterable[float],
    leg1_forward_curve: Optional[str],
    leg2_forward_curve: Optional[str],
    leg1_spread: float = 0.0,
    leg2_spread: float = 0.0,
    pay_leg1: bool = True,
    day_count: float = 1.0,
) -> Tuple[SwapLeg, SwapLeg]:
    """Construct a simple basis swap with two floating legs."""

    leg1 = SwapLeg(
        notional=notional,
        currency=currency,
        payment_times=payment_times_leg1,
        fixed_rate=None,
        forward_curve=leg1_forward_curve,
        spread=leg1_spread,
        pay=pay_leg1,
        day_count=day_count,
    )
    leg2 = SwapLeg(
        notional=notional,
        currency=currency,
        payment_times=payment_times_leg2,
        fixed_rate=None,
        forward_curve=leg2_forward_curve,
        spread=leg2_spread,
        pay=not pay_leg1,
        day_count=day_count,
    )
    return leg1, leg2


DEFAULT_GENERATORS = {
    "vanilla": vanilla_fixed_float_generator,
    "basis": basis_swap_generator,
}


@dataclass
class Swap(Instrument):
    """Interest rate swap with two legs."""

    pay_leg: SwapLeg
    receive_leg: SwapLeg
    trade_date: Optional[date] = None
    generator: Optional[str] = None

    def __post_init__(self) -> None:
        if self.pay_leg.currency != self.receive_leg.currency:
            raise ValueError("Both swap legs must share the same currency")

    @property
    def legs(self) -> Tuple[SwapLeg, SwapLeg]:
        """Return swap legs ordered as pay/receive."""

        return self.pay_leg, self.receive_leg

    def notional(self) -> float:
        return max(self.pay_leg.notional, self.receive_leg.notional)

    def currency(self) -> str:
        return self.pay_leg.currency

    @classmethod
    def from_generator(cls, name: str, **kwargs) -> "Swap":
        """Instantiate a swap using a named generator."""

        if name not in DEFAULT_GENERATORS:
            raise KeyError(f"Unknown swap generator '{name}'")
        pay_leg, receive_leg = DEFAULT_GENERATORS[name](**kwargs)
        return cls(pay_leg=pay_leg, receive_leg=receive_leg, generator=name)

    @property
    def fixed_rate(self) -> Optional[float]:
        """Return the fixed rate if the swap contains a fixed leg."""

        for leg in self.legs:
            if leg.is_fixed():
                return leg.fixed_rate
        return None
