"""Randomized market data provider for quick testing and examples."""

from __future__ import annotations

import math
import random
from datetime import date
from typing import Any, Dict, Optional

from qfinlib.market.container import MarketContainer
from qfinlib.market.data.provider import DataProvider


class _FlatDiscountCurve:
    def __init__(self, rate: float):
        self.rate = float(rate)

    def discount_factor(self, t: float) -> float:
        return math.exp(-self.rate * float(t))


class _FlatForwardCurve:
    def __init__(self, forward: float):
        self.forward = float(forward)

    def forward_rate(self) -> float:
        return self.forward


class _ConstantVolSurface:
    def __init__(self, vol: float):
        self.vol = float(vol)

    def __call__(self, expiry: float, strike: float, forward: float) -> float:
        return self.vol


class RandomMarketDataProvider(DataProvider):
    """Utility provider that fabricates self-consistent market data."""

    def __init__(
        self,
        seed: Optional[int] = None,
        currency: str = "USD",
        discount_curve_name: str = "discount_curve",
        forward_curve_name: str = "libor3m",
        vol_surface_name: str = "swaption_vol",
    ):
        self.random = random.Random(seed)
        self.currency = currency
        self.discount_curve_name = discount_curve_name
        self.forward_curve_name = forward_curve_name
        self.vol_surface_name = vol_surface_name

    def _as_of(self, as_of: Optional[date]) -> date:
        return as_of or date.today()

    def _draw_rate(self, low: float = 0.0, high: float = 0.05) -> float:
        return self.random.uniform(low, high)

    def _draw_vol(self, low: float = 0.05, high: float = 0.50) -> float:
        return self.random.uniform(low, high)

    def get_rates(self, currency: str, as_of: Optional[date] = None) -> Dict[str, Any]:
        as_of_date = self._as_of(as_of)
        discount_rate = self._draw_rate()
        forward_rate = self._draw_rate(discount_rate + 0.0005, discount_rate + 0.03)
        return {
            "currency": currency or self.currency,
            "as_of": as_of_date,
            "discount_curve_name": self.discount_curve_name,
            "forward_curve_name": self.forward_curve_name,
            "discount_rate": discount_rate,
            "forward_rate": forward_rate,
            "discount_curve": _FlatDiscountCurve(discount_rate),
            "forward_curve": _FlatForwardCurve(forward_rate),
        }

    def get_bond_prices(self, bond_id: str, as_of: Optional[date] = None) -> Dict[str, Any]:
        as_of_date = self._as_of(as_of)
        clean_price = self.random.uniform(90.0, 110.0)
        yield_rate = self._draw_rate(0.01, 0.06)
        return {
            "bond_id": bond_id,
            "as_of": as_of_date,
            "clean_price": clean_price,
            "yield": yield_rate,
        }

    def get_volatility(self, asset_class: str, as_of: Optional[date] = None) -> Dict[str, Any]:
        as_of_date = self._as_of(as_of)
        vol = self._draw_vol()
        return {
            "asset_class": asset_class,
            "as_of": as_of_date,
            "volatility": vol,
            "surface_name": self.vol_surface_name,
            "vol_surface": _ConstantVolSurface(vol),
        }

    def get_fx_rates(self, currency_pair: str, as_of: Optional[date] = None) -> Dict[str, Any]:
        as_of_date = self._as_of(as_of)
        spot = self.random.uniform(0.7, 1.4)
        return {
            "currency_pair": currency_pair,
            "as_of": as_of_date,
            "spot": spot,
        }

    def build_market(self, currency: Optional[str] = None, as_of: Optional[date] = None) -> MarketContainer:
        """Create a MarketContainer populated with random curves and surfaces."""

        as_of_date = self._as_of(as_of)
        market = MarketContainer(as_of=as_of_date)

        rates = self.get_rates(currency or self.currency, as_of_date)
        market.add_curve(self.discount_curve_name, rates["discount_curve"])
        market.add_curve(self.forward_curve_name, rates["forward_curve"])
        market.data.update(
            {
                "currency": rates["currency"],
                "discount_rate": rates["discount_rate"],
                "forward_rate": rates["forward_rate"],
            }
        )

        vol_data = self.get_volatility("swaption", as_of_date)
        market.add_surface(self.vol_surface_name, vol_data["vol_surface"])
        market.data["volatility"] = vol_data["volatility"]

        fx_pair = f"{rates['currency']}/USD" if rates["currency"] != "USD" else "USD/USD"
        market.data["fx_rates"] = self.get_fx_rates(fx_pair, as_of_date)

        return market
