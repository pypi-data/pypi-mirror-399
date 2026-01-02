"""Base curve implementations.

The curve framework is designed to be flexible enough to host swap, bond,
repo, FX and other rate curves. Nodes can be configured with arbitrary
pillars, instrument identifiers and market quotes while supporting
multiple interpolation and extrapolation conventions.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple, Union

from qfinlib.math.interpolation import (
    CubicInterpolator,
    Interpolator,
    LinearInterpolator,
    LogLinearInterpolator,
    MonotoneInterpolator,
)

InterpolatorLike = Union[str, Interpolator]


def _make_interpolator(kind: InterpolatorLike, extrapolation: str) -> Interpolator:
    if isinstance(kind, Interpolator):
        return kind
    kind_normalised = str(kind).lower()
    mapping = {
        "linear": LinearInterpolator,
        "log_linear": LogLinearInterpolator,
        "log-linear": LogLinearInterpolator,
        "monotone": MonotoneInterpolator,
        "cubic": CubicInterpolator,
    }
    if kind_normalised not in mapping:
        raise ValueError(f"Unsupported interpolation type: {kind}")
    return mapping[kind_normalised](extrapolation=extrapolation)


@dataclass
class Curve:
    """Generic curve definition.

    Parameters
    ----------
    pillars:
        Times (in year fractions) where market information is known.
    values:
        Quotes aligned with ``pillars``. Quotes can be discount factors,
        zero rates, forward rates or spreads depending on the specific curve
        type.
    instruments:
        Optional instrument identifiers (e.g. swaps, deposits, bonds) used
        to construct the curve. They are stored to help consumers trace the
        origin of each node.
    interpolation:
        Interpolation scheme name or :class:`~qfinlib.math.interpolation.Interpolator`
        instance. Supported names are ``linear``, ``log_linear``,
        ``monotone`` and ``cubic``.
    extrapolation:
        Extrapolation policy. ``flat`` will hold the nearest node value,
        ``linear`` extends the end slopes and ``nearest`` picks the closest
        node.
    curve_type:
        Free-form tag describing the family (swap, bond, repo, fx, etc.).
    """

    pillars: Sequence[float]
    values: Sequence[float]
    instruments: Optional[Sequence[str]] = None
    interpolation: InterpolatorLike = "linear"
    extrapolation: str = "flat"
    curve_type: str = "generic"
    market_data: Mapping[str, float] = field(default_factory=dict)
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if len(self.pillars) != len(self.values):
            raise ValueError("pillars and values must have the same length")
        combined = sorted(zip(self.pillars, self.values, self._build_instruments()))
        self.pillars = [float(p) for p, _, _ in combined]
        self.values = [float(v) for _, v, _ in combined]
        self.instruments = [ins for _, _, ins in combined]
        self._interpolator: Interpolator = _make_interpolator(self.interpolation, self.extrapolation)

    def _build_instruments(self) -> List[str]:
        if self.instruments is None:
            return [f"node_{i}" for i in range(len(self.pillars))]
        if len(self.instruments) != len(self.pillars):
            raise ValueError("instruments must be None or have the same length as pillars")
        return list(self.instruments)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "curve_type": self.curve_type,
            "pillars": list(self.pillars),
            "values": list(self.values),
            "instruments": list(self.instruments or []),
            "interpolation": self.interpolation if isinstance(self.interpolation, str) else type(self.interpolation).__name__,
            "extrapolation": self.extrapolation,
            "metadata": dict(self.metadata),
        }

    def nodes(self) -> List[Tuple[float, float, str]]:
        return list(zip(self.pillars, self.values, self.instruments))

    def value(self, t: float) -> float:
        """Return the curve value at time ``t`` using the configured interpolation."""

        if not self.pillars:
            raise ValueError("Curve has no pillars defined")
        if len(self.pillars) == 1:
            return self.values[0]
        return float(self._interpolator(self.pillars, self.values, float(t)))

    def update_market_quotes(self, quotes: Mapping[str, float]) -> None:
        """Update node values using a mapping keyed by instrument names."""

        updated = False
        values = list(self.values)
        for idx, instrument in enumerate(self.instruments):
            if instrument in quotes:
                values[idx] = float(quotes[instrument])
                updated = True
        if updated:
            self.values = values
        self.market_data = {**dict(self.market_data), **dict(quotes)}

    def add_node(self, pillar: float, value: float, instrument: Optional[str] = None) -> None:
        """Insert a new curve node and keep internal ordering consistent."""

        instrument = instrument or f"node_{len(self.pillars)}"
        self.pillars = list(self.pillars) + [float(pillar)]
        self.values = list(self.values) + [float(value)]
        self.instruments = list(self.instruments) + [instrument]
        combined = sorted(zip(self.pillars, self.values, self.instruments))
        self.pillars, self.values, self.instruments = map(list, zip(*combined))

    def bump(self, spread: float) -> "Curve":
        """Return a bumped copy of the curve."""

        bumped_values = [val + spread for val in self.values]
        return type(self)(
            pillars=list(self.pillars),
            values=bumped_values,
            instruments=list(self.instruments),
            interpolation=self.interpolation,
            extrapolation=self.extrapolation,
            curve_type=self.curve_type,
            market_data=self.market_data,
            metadata=self.metadata,
        )

    def __repr__(self) -> str:  # pragma: no cover - representation aid
        return f"{self.curve_type.capitalize()}Curve({len(self.pillars)} nodes, interpolation={self.interpolation}, extrapolation={self.extrapolation})"


class InstrumentCurve(Curve):
    """Convenience wrapper tagging the curve with an instrument family."""

    def __init__(
        self,
        pillars: Sequence[float],
        values: Sequence[float],
        instrument_type: str,
        instruments: Optional[Sequence[str]] = None,
        interpolation: InterpolatorLike = "linear",
        extrapolation: str = "flat",
        market_data: Mapping[str, float] = None,
        metadata: Mapping[str, Any] = None,
    ):
        super().__init__(
            pillars=pillars,
            values=values,
            instruments=instruments,
            interpolation=interpolation,
            extrapolation=extrapolation,
            curve_type=instrument_type,
            market_data=market_data or {},
            metadata=metadata or {},
        )
