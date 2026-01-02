"""Randomized market data provider for quick testing and examples."""
from __future__ import annotations

import random
from datetime import date
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from qfinlib.market.container import MarketContainer
from qfinlib.market.curve import DiscountCurve, ForwardCurve
from qfinlib.market.data.provider import DataProvider


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

    def _flat_discount_curve(self, rate: float) -> DiscountCurve:
        return DiscountCurve(pillars=[0.0, 30.0], zero_rates=[rate, rate])

    def _flat_forward_curve(self, rate: float) -> ForwardCurve:
        return ForwardCurve(pillars=[0.0, 30.0], forward_rates=[rate, rate], index=self.forward_curve_name)

    @staticmethod
    def _tenor_to_years(tenor: str) -> float:
        units = tenor.strip().upper()
        if units.endswith("Y"):
            return float(units[:-1])
        if units.endswith("M"):
            return float(units[:-1]) / 12.0
        if units.endswith("D"):
            return float(units[:-1]) / 365.0
        raise ValueError(f"Unrecognized tenor format: {tenor}")

    def _swap_curve_profile(self, tenors: Sequence[str], rate_type: str) -> Tuple[List[float], List[str]]:
        pillars: List[float] = []
        names: List[str] = []
        for tenor in tenors:
            t = self._tenor_to_years(tenor)
            pillars.append(round(t, 6))
            names.append(f"USSWAP-{tenor.upper()}-{rate_type.upper()}")
        return pillars, names

    def generate_swap_curve(
        self, tenors: Iterable[str], rate_type: str = "OTC", anchor_rate: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """Generate synthetic swap quotes aligned with supplied tenors and rate type."""

        rate_floor = 0.005 if rate_type.lower() == "otc" else 0.0
        rate_ceiling = 0.055 if rate_type.lower() == "otc" else 0.04
        base_rate = anchor_rate if anchor_rate is not None else self._draw_rate(rate_floor, rate_ceiling)
        slope = 0.003 if rate_type.lower() == "otc" else 0.002
        volatility = 0.0009 if rate_type.lower() == "otc" else 0.0005

        tenors_list = list(tenors)
        pillars, names = self._swap_curve_profile(tenors_list, rate_type)
        instruments: List[Dict[str, Any]] = []
        for idx, (tenor, pillar, name) in enumerate(zip(tenors_list, pillars, names)):
            drift = slope * pillar
            jitter = self.random.uniform(-volatility, volatility)
            quote = base_rate + drift + jitter
            instruments.append(
                {
                    "pillar": pillar,
                    "quote": quote,
                    "instrument": name,
                    "tenor": tenor.upper(),
                    "rate_type": rate_type,
                    "rank": idx,
                }
            )
        return instruments

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
            "discount_curve": self._flat_discount_curve(discount_rate),
            "forward_curve": self._flat_forward_curve(forward_rate),
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
