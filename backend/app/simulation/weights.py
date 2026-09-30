"""
Default weighting scheme used to combine an animal's normalized attributes
into a single Combat Effectiveness Score (CES).

CES is NOT what decides a matchup outcome -- it is only used (a) as an
input to the per-round combat simulation and (b) to compute the "key
factors" explanation after the fact. The actual win probability comes from
running thousands of stochastic round-by-round encounters (see engine.py).

Weights sum to 1.0. They are intentionally centralized here, in one
reviewable place, rather than scattered as magic numbers through the
codebase.
"""
from __future__ import annotations

from .attributes import ATTRIBUTE_NAMES

DEFAULT_WEIGHTS: dict[str, float] = {
    "size": 0.14,
    "strength": 0.20,
    "speed": 0.10,
    "agility": 0.11,
    "defense": 0.15,
    "weapon": 0.20,
    "endurance": 0.10,
}

assert set(DEFAULT_WEIGHTS) == set(ATTRIBUTE_NAMES)
assert abs(sum(DEFAULT_WEIGHTS.values()) - 1.0) < 1e-9


def combat_effectiveness_score(attributes, weights: dict[str, float] | None = None) -> float:
    """Weighted sum of an animal's attributes, 0-100 scale."""
    w = weights or DEFAULT_WEIGHTS
    attrs = attributes.as_dict()
    return sum(w[name] * attrs[name] for name in ATTRIBUTE_NAMES)
