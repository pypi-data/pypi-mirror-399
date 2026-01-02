"""Swaption pricer using Black's model."""

from __future__ import annotations

import math
from datetime import date
from typing import Optional

from qfinlib.instruments.rates.option.swaption import Swaption
from qfinlib.market.container import MarketContainer
from qfinlib.pricing.pricers.base import Pricer
from qfinlib.pricing.pricers.rates.swap import SwapPricer


def _norm_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def _norm_pdf(x: float) -> float:
    return math.exp(-0.5 * x * x) / math.sqrt(2.0 * math.pi)


class SwaptionPricer(Pricer):
    """European swaption priced with the Black closed form."""

    def __init__(
        self,
        swap_pricer: Optional[SwapPricer] = None,
        discount_curve: str = "discount_curve",
        vol_surface: str = "swaption_vol",
        fallback_vol: float = 0.01,
    ) -> None:
        self.swap_pricer = swap_pricer or SwapPricer(discount_curve)
        self.discount_curve = discount_curve
        self.vol_surface = vol_surface
        self.fallback_vol = fallback_vol

    def _discount_factor(self, market: MarketContainer, t: float) -> float:
        curve = market.get_curve(self.discount_curve)
        if curve is not None and hasattr(curve, "discount_factor"):
            return curve.discount_factor(t)
        rate = market.data.get("discount_rate", 0.0)
        return math.exp(-rate * t)

    def _volatility(self, market: MarketContainer, expiry: float, strike: float, forward: float) -> float:
        surface = market.get_surface(self.vol_surface)
        if surface is not None:
            getter = getattr(surface, "__call__", None) or getattr(surface, "vol", None)
            if callable(getter):
                return float(getter(expiry, strike, forward))
            if getter is not None:
                return float(getter)
        return float(market.data.get("volatility", self.fallback_vol))

    def _expiry_in_years(self, expiry, as_of=None, market=None) -> float:
        if isinstance(expiry, (int, float)):
            return float(expiry)
        if isinstance(expiry, date):
            as_of_date = as_of or (market.as_of if market is not None else None)
            if as_of_date is None:
                raise ValueError("Expiry provided as date requires an as_of date on market or input")
            delta_days = (expiry - as_of_date).days
            return delta_days / 365.0
        raise ValueError("Expiry must be provided as a year fraction or date for pricing")

    def _black_price(self, forward: float, strike: float, vol: float, expiry: float, call: bool, discount: float):
        if vol <= 0 or expiry <= 0:
            intrinsic = max(0.0, (forward - strike) if call else (strike - forward))
            delta = discount if (call and forward > strike) else -discount if (not call and forward < strike) else 0.0
            return intrinsic * discount, delta, 0.0, 0.0, 0.0

        sigma_sqrt_t = vol * math.sqrt(expiry)
        d1 = math.log(forward / strike) / sigma_sqrt_t + 0.5 * sigma_sqrt_t
        d2 = d1 - sigma_sqrt_t
        if call:
            price = discount * (forward * _norm_cdf(d1) - strike * _norm_cdf(d2))
            delta = discount * _norm_cdf(d1)
        else:
            price = discount * (strike * _norm_cdf(-d2) - forward * _norm_cdf(-d1))
            delta = discount * (_norm_cdf(d1) - 1.0)
        gamma = discount * _norm_pdf(d1) / (forward * sigma_sqrt_t)
        vega = discount * forward * _norm_pdf(d1) * math.sqrt(expiry)
        theta = -discount * forward * _norm_pdf(d1) * vol / (2 * math.sqrt(expiry))
        return price, delta, gamma, vega, theta

    def price(self, instrument: Swaption, market: MarketContainer, as_of=None):
        expiry = self._expiry_in_years(instrument.expiry, as_of=as_of, market=market)
        swap_data = self.swap_pricer.price(instrument.swap, market, as_of)

        annuity = swap_data.get("annuity", 0.0) or 1.0
        forward = swap_data.get("par_rate", 0.0)
        strike = instrument.resolved_strike
        vol = self._volatility(market, expiry, strike, forward)
        discount = self._discount_factor(market, expiry)

        payer = instrument.is_payer
        price, delta, gamma, vega, theta = self._black_price(
            forward=forward,
            strike=strike,
            vol=vol,
            expiry=expiry,
            call=payer,
            discount=discount,
        )

        # Scale results by the swap annuity
        price *= annuity
        delta *= annuity
        gamma *= annuity
        vega *= annuity
        theta *= annuity

        # Additional diagnostics
        atm_vol = self._volatility(market, expiry, forward, forward)
        sabr_parameters = {
            "alpha": market.data.get("sabr_alpha"),
            "beta": market.data.get("sabr_beta"),
            "rho": market.data.get("sabr_rho"),
            "nu": market.data.get("sabr_nu"),
        }

        return {
            "pv": price,
            "delta": delta,
            "gamma": gamma,
            "vega": vega,
            "theta": theta,
            "forward": forward,
            "strike": strike,
            "volatility": vol,
            "annuity": annuity,
            "implied_vol_at_strike": vol,
            "implied_vol_atm": atm_vol,
            "sabr_parameters": sabr_parameters,
            "swap_metrics": swap_data,
        }
