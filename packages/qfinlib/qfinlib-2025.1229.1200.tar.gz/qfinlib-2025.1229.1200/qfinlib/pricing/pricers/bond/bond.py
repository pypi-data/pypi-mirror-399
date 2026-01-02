"""Bond pricer."""

from __future__ import annotations

import math
from datetime import date
from typing import Dict, Iterable, Optional, Tuple

from qfinlib.instruments.bond.bond import Bond
from qfinlib.market.container import MarketContainer
from qfinlib.pricing.pricers.base import Pricer


class BondPricer(Pricer):
    """Simple fixed-coupon bond pricer supporting duration and carry metrics."""

    def __init__(self, discount_curve: str = "discount_curve", fallback_yield: float = 0.02):
        self.discount_curve = discount_curve
        self.fallback_yield = fallback_yield

    def _settlement_date(self, instrument: Bond, market: MarketContainer, as_of: Optional[date]) -> date:
        return instrument.settlement_date or as_of or market.as_of or date.today()

    def _period(self, instrument: Bond) -> float:
        return 1.0 / max(1, instrument.coupon_frequency)

    def _yield(self, instrument: Bond, market: MarketContainer) -> float:
        if instrument.yield_rate is not None:
            return float(instrument.yield_rate)

        bond_blob = market.data.get("bond")
        if isinstance(bond_blob, dict) and "yield" in bond_blob:
            return float(bond_blob["yield"])

        return float(market.data.get("yield", self.fallback_yield))

    def _discount_factor(self, market: MarketContainer, t: float, yield_rate: float) -> float:
        curve = market.get_curve(self.discount_curve)
        if curve is not None and hasattr(curve, "discount_factor"):
            return float(curve.discount_factor(t))
        # Fallback to flat continuously-compounded yield
        return math.exp(-yield_rate * t)

    def _cashflows(
        self, instrument: Bond, settlement: date
    ) -> Tuple[Iterable[Tuple[float, float]], float, float, float]:
        period = self._period(instrument)
        time_to_maturity = instrument.maturity_time(settlement)
        if time_to_maturity <= 0:
            return [], 0.0, 0.0, 0.0

        num_periods = max(1, math.ceil(time_to_maturity / period))
        next_coupon_time = max(0.0, time_to_maturity - (num_periods - 1) * period)
        accrued_fraction = max(0.0, min(1.0, (period - next_coupon_time) / period))
        coupon_amount = instrument.coupon_amount()

        cashflows = []
        for idx in range(num_periods):
            t = next_coupon_time + idx * period
            amount = coupon_amount
            if idx == num_periods - 1:
                amount += instrument.face_value
            cashflows.append((t, amount))

        accrued_interest = coupon_amount * accrued_fraction
        return cashflows, accrued_fraction, accrued_interest, period

    @staticmethod
    def _price_from_yield(cashflows: Iterable[Tuple[float, float]], ytm: float, freq: int) -> float:
        freq = max(1, freq)
        return sum(cf * (1.0 + ytm / freq) ** (-freq * t) for t, cf in cashflows)

    def _price_from_curve(
        self, cashflows: Iterable[Tuple[float, float]], market: MarketContainer, ytm: float
    ) -> float:
        return sum(cf * self._discount_factor(market, t, ytm) for t, cf in cashflows)

    def _solve_yield(
        self, cashflows: Iterable[Tuple[float, float]], target_price: float, freq: int, guess: float
    ) -> float:
        low, high = -0.05, 1.0
        for _ in range(64):
            mid = 0.5 * (low + high)
            price = self._price_from_yield(cashflows, mid, freq)
            if price > target_price:
                low = mid
            else:
                high = mid
        return 0.5 * (low + high)

    def price(self, instrument: Bond, market: MarketContainer, as_of: Optional[date] = None) -> Dict[str, object]:
        settlement = self._settlement_date(instrument, market, as_of)
        cashflows, accrued_fraction, accrued_interest, period = self._cashflows(instrument, settlement)

        if not cashflows:
            return {
                "AccruedFraction": 0.0,
                "AccruedInterest": 0.0,
                "DirtyPrice": 0.0,
                "CleanPrice": 0.0,
                "Yield": 0.0,
                "BondDV01": 0.0,
                "MacaulayDuration": 0.0,
                "ModifiedDuration": 0.0,
                "Convexity": 0.0,
                "ParAmount": instrument.face_value,
                "SettlementDate": settlement,
                "MaturityDate": instrument.maturity_date,
                "QuoteConvention": instrument.quote_convention,
            }

        market_yield = self._yield(instrument, market)
        freq = max(1, instrument.coupon_frequency)

        curve_price = self._price_from_curve(cashflows, market, market_yield)
        yield_price = self._price_from_yield(cashflows, market_yield, freq)

        dirty_price = curve_price if market.get_curve(self.discount_curve) else yield_price
        if instrument.clean_price is not None:
            dirty_price = instrument.clean_price + accrued_interest
            if instrument.yield_rate is None:
                market_yield = self._solve_yield(cashflows, dirty_price, freq, market_yield)

        clean_price = dirty_price - accrued_interest

        # DV01 and risk measures using yield-based discounting for stability
        bump = 0.0001
        price_up = self._price_from_yield(cashflows, market_yield + bump, freq)
        price_down = self._price_from_yield(cashflows, max(-0.99, market_yield - bump), freq)
        dv01 = (price_down - price_up) / 2.0

        discounted_cashflows = [
            (t, cf, self._price_from_yield([(t, cf)], market_yield, freq)) for t, cf in cashflows
        ]
        macaulay_numerator = sum(t * pv for t, _, pv in discounted_cashflows)
        convexity_numerator = sum(t * (t + period) * pv for t, _, pv in discounted_cashflows)
        macaulay_duration = macaulay_numerator / dirty_price if dirty_price else 0.0
        modified_duration = macaulay_duration / (1.0 + market_yield / freq) if dirty_price else 0.0
        convexity = convexity_numerator / dirty_price if dirty_price else 0.0

        metrics: Dict[str, object] = {
            "AccruedFraction": accrued_fraction,
            "AccruedInterest": accrued_interest,
            "BondCurvePrice": curve_price,
            "BondDV01": dv01,
            "CleanPrice": clean_price,
            "Convexity": convexity,
            "DirtyPrice": dirty_price,
            "DPdZ": dv01,
            "MacaulayDuration": macaulay_duration,
            "ModifiedDuration": modified_duration,
            "ParAmount": instrument.face_value,
            "MaturityDate": instrument.maturity_date,
            "SettlementDate": settlement,
            "Yield": market_yield,
            "GCRepoCarry_bps_TN_3M_TN_2W_1M_2M_3M_6M_12M": 0.0,
            "CMTRollReturn_bps_1W_2W_1M_2M_3M_6M_12M": 0.0,
            "GCRepoSpread_TN_SN_1W_2W_1M_2M_3M_6M_12M": 0.0,
            "GCRepoReturn_TN_SN_1W_2W_1M_2M_3M_6M_12M": 0.0,
            "ConvexityReturn_bps_3M_6M_12M": 0.0,
            "QuoteConvention": instrument.quote_convention,
        }

        return metrics
