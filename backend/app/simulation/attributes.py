"""
Core data structures for the simulation engine.

This module has zero dependencies on FastAPI, SQLAlchemy, or any web
framework -- it is a plain Python/NumPy library that can be imported and
unit tested in complete isolation from the rest of the application.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Tuple

# The seven combat dimensions every animal is scored on, each normalized to
# a 0-100 scale. See docs/SIMULATION_METHODOLOGY.md for how these are
# derived from raw biological data (weight, speed, bite force, etc.) and
# for which fields are directly measured vs. estimated/normalized.
ATTRIBUTE_NAMES: Tuple[str, ...] = (
    "size",
    "strength",
    "speed",
    "agility",
    "defense",
    "weapon",
    "endurance",
)


@dataclass(frozen=True)
class CombatAttributes:
    """Normalized 0-100 combat attributes used directly by the engine."""

    size: float
    strength: float
    speed: float
    agility: float
    defense: float
    weapon: float
    endurance: float

    def __post_init__(self) -> None:
        for name in ATTRIBUTE_NAMES:
            value = getattr(self, name)
            if not (0.0 <= value <= 100.0):
                raise ValueError(f"attribute '{name}' out of range [0,100]: {value}")

    def as_dict(self) -> dict[str, float]:
        return {name: getattr(self, name) for name in ATTRIBUTE_NAMES}

    def scaled(self, name: str, multiplier: float, cap_pct: float = 0.15) -> "CombatAttributes":
        """Return a copy with one attribute scaled by `multiplier`, where the
        deviation from 1.0 is clamped to +/- cap_pct. This is what keeps
        environment modifiers from ever becoming extreme."""
        clamped_multiplier = 1.0 + max(-cap_pct, min(cap_pct, multiplier - 1.0))
        current = getattr(self, name)
        new_value = max(0.0, min(100.0, current * clamped_multiplier))
        return replace(self, **{name: new_value})


@dataclass(frozen=True)
class AnimalProfile:
    """A minimal, engine-facing view of an animal. The API layer maps the
    richer database model down to this shape before handing it to the
    simulation engine, keeping the engine decoupled from persistence."""

    id: str
    name: str
    attributes: CombatAttributes
    habitats: Tuple[str, ...] = ()
    adaptations: Tuple[str, ...] = ()
    fighting_style: str = "generalist"


@dataclass(frozen=True)
class EnvironmentProfile:
    """An environment as the engine understands it: a small bag of tags
    that the modifier system (see environment.py) matches against animal
    adaptations and habitats."""

    id: str
    name: str
    tags: Tuple[str, ...] = ()
