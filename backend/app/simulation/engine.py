"""
The Monte Carlo combat engine.

Methodology summary (full detail in docs/SIMULATION_METHODOLOGY.md):

1. Environment modifiers are applied once to each animal's attributes
   (environment.py) to get "effective" combat attributes for this matchup.
2. `num_simulations` independent encounters are simulated *simultaneously*
   as vectorized NumPy arrays -- not a single formula, and not a Python
   loop per encounter. Each encounter proceeds round by round:
     - both animals attack each other every round (a mutual exchange)
     - each attack roll and defense roll includes Gaussian noise, so
       identical inputs still produce a distribution of outcomes
     - damage accumulates against a health pool derived from size+endurance
     - the round loop ends per-encounter when a health pool reaches 0, or
       at a hard round cap (decided by remaining health% at that point)
3. Win counts, average/std encounter length, and attribute-level "key
   factors" are aggregated from the batch and returned as a MatchupResult.

Given a fixed `seed`, results are exactly reproducible -- this is what
makes the engine unit-testable.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Sequence

import numpy as np

from .attributes import ATTRIBUTE_NAMES, AnimalProfile, CombatAttributes, EnvironmentProfile
from .environment import apply_environment
from .weights import DEFAULT_WEIGHTS, combat_effectiveness_score

MAX_ROUNDS = 40
BASE_HEALTH = 55.0
HEALTH_FROM_SIZE_ENDURANCE = 0.65  # scales size/endurance contribution to health pool
NOISE_SIGMA = 9.0                  # stddev of per-round performance noise
FORM_SIGMA = 0.16                  # stddev of per-encounter "form" multiplier (day-to-day variability)
DAMAGE_SCALE = 0.55                # converts raw offense-defense gap into damage/round


@dataclass(frozen=True)
class KeyFactor:
    attribute: str
    favored_animal: str  # "a" or "b"
    magnitude: float      # weighted contribution to the CES gap, 0-100 scale
    description: str


@dataclass(frozen=True)
class MatchupResult:
    animal_a_id: str
    animal_b_id: str
    environment_id: str
    num_simulations: int
    seed: Optional[int]
    animal_a_wins: int
    animal_b_wins: int
    draws: int
    win_pct_a: float
    win_pct_b: float
    avg_rounds: float
    std_rounds: float
    ces_a: float
    ces_b: float
    effective_attributes_a: dict[str, float]
    effective_attributes_b: dict[str, float]
    key_factors: list[KeyFactor]


def _health_pool(attrs: CombatAttributes) -> float:
    return BASE_HEALTH + HEALTH_FROM_SIZE_ENDURANCE * (0.45 * attrs.size + 0.55 * attrs.endurance)


def _apply_overrides(attrs: CombatAttributes, overrides: Optional[dict[str, float]]) -> CombatAttributes:
    if not overrides:
        return attrs
    values = attrs.as_dict()
    for key, value in overrides.items():
        if key not in ATTRIBUTE_NAMES:
            raise ValueError(f"unknown attribute override '{key}'")
        values[key] = max(0.0, min(100.0, float(value)))
    return CombatAttributes(**values)


def _effective_attributes(
    profile: AnimalProfile,
    environment: EnvironmentProfile,
    overrides: Optional[dict[str, float]],
) -> CombatAttributes:
    attrs = apply_environment(profile, environment)
    return _apply_overrides(attrs, overrides)


def run_simulation(
    animal_a: AnimalProfile,
    animal_b: AnimalProfile,
    environment: EnvironmentProfile,
    num_simulations: int = 10_000,
    seed: Optional[int] = None,
    overrides_a: Optional[dict[str, float]] = None,
    overrides_b: Optional[dict[str, float]] = None,
    weights: Optional[dict[str, float]] = None,
) -> MatchupResult:
    if num_simulations < 1:
        raise ValueError("num_simulations must be >= 1")

    rng = np.random.default_rng(seed)

    eff_a = _effective_attributes(animal_a, environment, overrides_a)
    eff_b = _effective_attributes(animal_b, environment, overrides_b)

    ces_a = combat_effectiveness_score(eff_a, weights)
    ces_b = combat_effectiveness_score(eff_b, weights)

    n = num_simulations
    health_a = np.full(n, _health_pool(eff_a), dtype=np.float64)
    health_b = np.full(n, _health_pool(eff_b), dtype=np.float64)
    alive = np.ones(n, dtype=bool)
    rounds_taken = np.zeros(n, dtype=np.int32)

    # Static offense/defense baselines, common to every encounter in the batch.
    base_offense_a = 0.5 * eff_a.strength + 0.5 * eff_a.weapon
    base_offense_b = 0.5 * eff_b.strength + 0.5 * eff_b.weapon
    base_guard_a = 0.5 * eff_a.defense + 0.3 * eff_a.agility + 0.2 * eff_a.speed
    base_guard_b = 0.5 * eff_b.defense + 0.3 * eff_b.agility + 0.2 * eff_b.speed
    # Higher endurance -> modest resistance to incoming damage (grit/toughness).
    resist_a = 1.0 - 0.0018 * eff_a.endurance
    resist_b = 1.0 - 0.0018 * eff_b.endurance

    # Per-encounter "form" factor, drawn once per simulated encounter (not
    # per round). This represents the day-to-day variability real animals
    # would show -- injury, hunger, terrain luck, a bad matchup angle --
    # and is what keeps a consistent statistical edge from flattening into
    # a near-certain outcome once compounded over several rounds. Without
    # it, per-round noise alone tends to average out across a multi-round
    # encounter (basic random-walk behavior), which produced unrealistic
    # 100%-0% results for any animal with a clear edge.
    form_a = rng.normal(1.0, FORM_SIGMA, n)
    form_b = rng.normal(1.0, FORM_SIGMA, n)
    offense_a = base_offense_a * form_a
    offense_b = base_offense_b * form_b
    guard_a = base_guard_a * form_a
    guard_b = base_guard_b * form_b

    for round_idx in range(1, MAX_ROUNDS + 1):
        active = alive
        if not active.any():
            break

        noise_atk_a = rng.normal(0, NOISE_SIGMA, n)
        noise_atk_b = rng.normal(0, NOISE_SIGMA, n)
        noise_def_a = rng.normal(0, NOISE_SIGMA * 0.6, n)
        noise_def_b = rng.normal(0, NOISE_SIGMA * 0.6, n)

        dmg_to_b = np.clip(offense_a + noise_atk_a - (guard_b + noise_def_b), 0, None) * DAMAGE_SCALE * resist_b
        dmg_to_a = np.clip(offense_b + noise_atk_b - (guard_a + noise_def_a), 0, None) * DAMAGE_SCALE * resist_a

        health_b = np.where(active, np.clip(health_b - dmg_to_b, 0, None), health_b)
        health_a = np.where(active, np.clip(health_a - dmg_to_a, 0, None), health_a)

        just_finished = active & ((health_a <= 0) | (health_b <= 0))
        rounds_taken = np.where(just_finished, round_idx, rounds_taken)
        alive = active & (health_a > 0) & (health_b > 0)

    # Any encounter that hit the round cap still "alive" is decided by
    # remaining health percentage rather than left unresolved.
    still_alive = alive
    rounds_taken = np.where(still_alive, MAX_ROUNDS, rounds_taken)

    # Explicit outcome resolution:
    a_dead = health_a <= 0
    b_dead = health_b <= 0
    win_a = b_dead & ~a_dead
    win_b = a_dead & ~b_dead
    both_dead_or_cap_tie = (a_dead & b_dead) | (still_alive & (health_a == health_b))
    decided_by_health = still_alive & (health_a != health_b)
    win_a = win_a | (decided_by_health & (health_a > health_b))
    win_b = win_b | (decided_by_health & (health_b > health_a))
    draw = both_dead_or_cap_tie

    animal_a_wins = int(win_a.sum())
    animal_b_wins = int(win_b.sum())
    draws = int(draw.sum())

    win_pct_a = 100.0 * animal_a_wins / n
    win_pct_b = 100.0 * animal_b_wins / n

    avg_rounds = float(rounds_taken.mean())
    std_rounds = float(rounds_taken.std())

    key_factors = _compute_key_factors(eff_a, eff_b, weights)

    return MatchupResult(
        animal_a_id=animal_a.id,
        animal_b_id=animal_b.id,
        environment_id=environment.id,
        num_simulations=n,
        seed=seed,
        animal_a_wins=animal_a_wins,
        animal_b_wins=animal_b_wins,
        draws=draws,
        win_pct_a=win_pct_a,
        win_pct_b=win_pct_b,
        avg_rounds=avg_rounds,
        std_rounds=std_rounds,
        ces_a=ces_a,
        ces_b=ces_b,
        effective_attributes_a=eff_a.as_dict(),
        effective_attributes_b=eff_b.as_dict(),
        key_factors=key_factors,
    )


def _compute_key_factors(
    eff_a: CombatAttributes,
    eff_b: CombatAttributes,
    weights: Optional[dict[str, float]],
    top_n: int = 3,
) -> list[KeyFactor]:
    w = weights or DEFAULT_WEIGHTS
    a = eff_a.as_dict()
    b = eff_b.as_dict()
    contributions = []
    for name in ATTRIBUTE_NAMES:
        diff = a[name] - b[name]
        weighted = w[name] * diff
        contributions.append((name, weighted, diff))

    contributions.sort(key=lambda item: abs(item[1]), reverse=True)
    factors = []
    for name, weighted, diff in contributions[:top_n]:
        favored = "a" if diff > 0 else "b"
        factors.append(
            KeyFactor(
                attribute=name,
                favored_animal=favored,
                magnitude=abs(weighted),
                description=f"{name} differential of {abs(diff):.1f} points ({'A' if favored=='a' else 'B'} favored)",
            )
        )
    return factors
