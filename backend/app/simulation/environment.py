"""
Environment modifier system.

Design goal (per project spec): modifiers must be *sensible*, never
extreme, and their logic must be auditable in one place rather than
scattered through the codebase. Every modifier here is expressed as a
percentage adjustment to specific attributes, and `CombatAttributes.scaled`
hard-clamps every adjustment to +/- MAX_MODIFIER_PCT regardless of how many
rules stack, so no combination of environment + adaptations can blow an
attribute out to an unrealistic swing.

See docs/SIMULATION_METHODOLOGY.md for the full rule table and rationale.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

from .attributes import AnimalProfile, CombatAttributes, EnvironmentProfile

MAX_MODIFIER_PCT = 0.15  # no single attribute ever moves more than +/-15%


@dataclass(frozen=True)
class EnvironmentRule:
    """One row of the modifier table.

    If the animal's `adaptations` (or `habitats`) intersect `match_tags`,
    `bonus_pct` is applied to each attribute in `bonus_attributes`.

    Otherwise a penalty (`penalty_pct`, applied to `penalty_attributes`)
    kicks in under either of two conditions:
      - the animal carries one of `mismatch_tags` (a specific bad fit --
        e.g. an `aquatic` animal on a Mountain), or
      - `penalize_absence` is True, meaning *any* animal that isn't a
        match is penalized (e.g. non-aquatic animals in the Ocean),
        unless it carries one of `absence_exempt_tags` (a partial fit,
        e.g. `semi_aquatic`, that avoids this blanket penalty without
        earning the full bonus).
    """

    environment_id: str
    match_tags: Tuple[str, ...]
    bonus_attributes: Tuple[str, ...]
    bonus_pct: float
    penalty_attributes: Tuple[str, ...] = ()
    penalty_pct: float = 0.0
    mismatch_tags: Tuple[str, ...] = ()
    penalize_absence: bool = False
    absence_exempt_tags: Tuple[str, ...] = ()


# The rule table. Kept intentionally small and readable -- each row is a
# plain, defensible biological claim, not a tuned "balance" number.
ENVIRONMENT_RULES: Tuple[EnvironmentRule, ...] = (
    # --- Arctic ---
    EnvironmentRule("arctic", ("cold_resistant", "thick_fur"), ("endurance", "defense"), 0.12,
                     penalty_attributes=("speed", "agility"), penalty_pct=-0.10,
                     mismatch_tags=("desert_adapted", "aquatic")),
    EnvironmentRule("arctic", ("arctic",), ("speed", "agility"), 0.05),  # home-turf footing/camouflage

    # --- Desert ---
    EnvironmentRule("desert", ("desert_adapted", "heat_tolerant"), ("endurance", "speed"), 0.12,
                     penalty_attributes=("endurance", "speed"), penalty_pct=-0.10,
                     mismatch_tags=("aquatic", "cold_resistant")),
    EnvironmentRule("desert", ("desert",), ("agility",), 0.05),

    # --- Ocean ---
    EnvironmentRule("ocean", ("aquatic",), ("speed", "agility", "endurance"), 0.15,
                     penalty_attributes=("speed", "agility"), penalty_pct=-0.15,
                     penalize_absence=True, absence_exempt_tags=("semi_aquatic",)),
    EnvironmentRule("ocean", ("semi_aquatic",), ("speed", "agility"), 0.08),

    # --- Forest ---
    EnvironmentRule("forest", ("camouflage", "arboreal", "ambush_adapted"), ("agility", "weapon"), 0.10),
    EnvironmentRule("forest", ("forest",), ("agility",), 0.05),

    # --- Mountain ---
    EnvironmentRule("mountain", ("mountain_adapted", "sure_footed"), ("agility", "defense"), 0.12,
                     penalty_attributes=("speed", "agility"), penalty_pct=-0.12,
                     mismatch_tags=("aquatic",)),
    EnvironmentRule("mountain", ("mountain",), ("endurance",), 0.05),

    # --- Savanna ---
    EnvironmentRule("savanna", ("savanna", "plains_adapted", "pursuit_predator"), ("speed", "endurance"), 0.08),

    # --- Open Plains ---
    EnvironmentRule("open_plains", ("plains_adapted", "pursuit_predator", "herd_animal"), ("speed", "endurance"), 0.10,
                     penalty_attributes=("speed", "endurance"), penalty_pct=-0.08,
                     mismatch_tags=("aquatic", "arboreal")),
)


def apply_environment(profile: AnimalProfile, environment: EnvironmentProfile) -> CombatAttributes:
    """Return a new CombatAttributes for `profile` with every applicable
    environment rule applied. Each attribute accumulates the product of its
    modifiers, but `CombatAttributes.scaled` still clamps the *net* change
    to MAX_MODIFIER_PCT, so stacking rules cannot exceed the cap."""
    attrs = profile.attributes
    tags = set(profile.adaptations) | set(profile.habitats)

    # Accumulate a single net multiplier per attribute, then apply once per
    # attribute so the final clamp is meaningful (clamping after every rule
    # individually would let multiple small bonuses add up unbounded).
    net_multiplier: dict[str, float] = {name: 1.0 for name in attrs.as_dict()}

    for rule in ENVIRONMENT_RULES:
        if rule.environment_id != environment.id:
            continue
        if tags & set(rule.match_tags):
            for attr_name in rule.bonus_attributes:
                net_multiplier[attr_name] *= 1.0 + rule.bonus_pct
            continue

        mismatch_hit = bool(rule.mismatch_tags) and bool(tags & set(rule.mismatch_tags))
        absence_hit = rule.penalize_absence and not (tags & set(rule.absence_exempt_tags))
        if mismatch_hit or absence_hit:
            for attr_name in rule.penalty_attributes:
                net_multiplier[attr_name] *= 1.0 + rule.penalty_pct

    result = attrs
    for attr_name, multiplier in net_multiplier.items():
        if multiplier != 1.0:
            result = result.scaled(attr_name, multiplier, cap_pct=MAX_MODIFIER_PCT)
    return result
