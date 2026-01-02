"""Market data loader."""

from datetime import date
from typing import Optional

from qfinlib.market.container import MarketContainer
from qfinlib.market.data.provider import DataProvider


class DataLoader:
    """Loads market data from providers into MarketContainer."""

    def __init__(self, provider: DataProvider):
        """Initialize with a data provider."""
        self.provider = provider

    def load(
        self,
        as_of: Optional[date] = None,
        currency: str = "USD",
        asset_class: str = "swaption",
        fx_pair: Optional[str] = None,
        bond_id: Optional[str] = None,
    ) -> MarketContainer:
        """Load market data from the provider into a MarketContainer."""

        market = MarketContainer(as_of=as_of or date.today())

        rate_data = self.provider.get_rates(currency, market.as_of)
        discount_curve_name = getattr(self.provider, "discount_curve_name", "discount_curve")
        forward_curve_name = getattr(self.provider, "forward_curve_name", "forward_curve")
        if "discount_curve" in rate_data:
            market.add_curve(discount_curve_name, rate_data["discount_curve"])
        if "forward_curve" in rate_data:
            market.add_curve(forward_curve_name, rate_data["forward_curve"])
        for key in ("discount_rate", "forward_rate", "currency"):
            if key in rate_data:
                market.data[key] = rate_data[key]

        vol_data = self.provider.get_volatility(asset_class, market.as_of)
        surface_name = vol_data.get("surface_name") or getattr(self.provider, "vol_surface_name", "vol_surface")
        if "vol_surface" in vol_data:
            market.add_surface(surface_name, vol_data["vol_surface"])
        if "volatility" in vol_data:
            market.data["volatility"] = vol_data["volatility"]

        fx_label = fx_pair or rate_data.get("fx_pair")
        if fx_label:
            market.data["fx_rates"] = self.provider.get_fx_rates(fx_label, market.as_of)

        if bond_id:
            market.data["bond"] = self.provider.get_bond_prices(bond_id, market.as_of)

        return market
