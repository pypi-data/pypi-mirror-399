"""Swap pricer."""

from __future__ import annotations

import math
from typing import Optional

from qfinlib.instruments.rates.swap.irs import Swap
from qfinlib.market.container import MarketContainer
from qfinlib.pricing.pricers.base import Pricer


class SwapPricer(Pricer):
    """Discounted cashflow pricer for vanilla and basis swaps."""

    def __init__(self, discount_curve: str = "discount_curve", fallback_rate: float = 0.0):
        self.discount_curve = discount_curve
        self.fallback_rate = fallback_rate

    def _discount_factor(self, market: MarketContainer, t: float) -> float:
        curve = market.get_curve(self.discount_curve)
        if curve is not None and hasattr(curve, "discount_factor"):
            return curve.discount_factor(t)
        rate = market.data.get("discount_rate", self.fallback_rate)
        return math.exp(-rate * t)

    def _forward_rate(self, market: MarketContainer, curve_name: Optional[str]) -> float:
        if curve_name:
            curve = market.get_curve(curve_name)
            if curve is not None:
                getter = getattr(curve, "forward_rate", None) or getattr(curve, "rate", None)
                if getter:
                    return getter()
        return float(market.data.get("forward_rate", 0.0))

    def _leg_pv(self, market: MarketContainer, leg) -> float:
        forward = self._forward_rate(market, leg.forward_curve)
        pv = 0.0
        for t, cf in zip(leg.payment_times_list, leg.cashflows(forward)):
            pv += cf * self._discount_factor(market, t)
        return pv

    def price(self, instrument: Swap, market: MarketContainer, as_of=None):
        pay_pv = self._leg_pv(market, instrument.pay_leg)
        receive_pv = self._leg_pv(market, instrument.receive_leg)
        pv = receive_pv + pay_pv

        annuity = sum(
            leg.day_count * self._discount_factor(market, t)
            for leg in instrument.legs
            for t in leg.payment_times_list
        )
        par_rate = 0.0
        if annuity != 0:
            float_leg = instrument.receive_leg if not instrument.receive_leg.is_fixed() else instrument.pay_leg
            float_forward = self._forward_rate(market, float_leg.forward_curve)
            par_rate = float(float_forward + float_leg.spread)

        fixed_rate = instrument.fixed_rate
        swap_carry = par_rate - fixed_rate if fixed_rate is not None else 0.0
        swap_roll_convexity = market.data.get("swap_roll_convexity_adjustment", 0.0)
        convexity_adjustment_rate = market.data.get("convexity_adjustment_rate", 0.0)

        return {
            "pv": pv,
            "pay_leg_pv": pay_pv,
            "receive_leg_pv": receive_pv,
            "annuity": annuity,
            "par_rate": par_rate,
            "swap_carry": swap_carry,
            "swap_roll_convexity_adjustment": swap_roll_convexity,
            "convexity_adjustment_rate": convexity_adjustment_rate,
        }
