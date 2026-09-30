"""Unit tests for the pure simulation engine (app.simulation.*).

These tests exercise the engine in complete isolation from the API,
database, and LLM layers -- exactly the guarantee that makes this
"an actual simulation" rather than an LLM guess.
"""
from __future__ import annotations

import numpy as np
import pytest

from app.simulation.attributes import AnimalProfile, CombatAttributes, EnvironmentProfile
from app.simulation.engine import run_simulation
from app.simulation.environment import apply_environment


def make_animal(id_, name, **attrs) -> AnimalProfile:
    defaults = dict(size=50, strength=50, speed=50, agility=50, defense=50, weapon=50, endurance=50)
    defaults.update(attrs)
    return AnimalProfile(id=id_, name=name, attributes=CombatAttributes(**defaults))


NEUTRAL_ENV = EnvironmentProfile(id="open_plains", name="Open Plains", tags=())


class TestDeterminism:
    def test_same_seed_gives_identical_results(self):
        a = make_animal("lion", "Lion", strength=70, weapon=65, agility=75, speed=70, defense=55, endurance=60, size=55)
        b = make_animal("bear", "Grizzly Bear", strength=90, weapon=70, agility=45, speed=55, defense=75, endurance=80, size=85)

        r1 = run_simulation(a, b, NEUTRAL_ENV, num_simulations=2000, seed=42)
        r2 = run_simulation(a, b, NEUTRAL_ENV, num_simulations=2000, seed=42)

        assert r1.animal_a_wins == r2.animal_a_wins
        assert r1.animal_b_wins == r2.animal_b_wins
        assert r1.avg_rounds == r2.avg_rounds

    def test_different_seed_can_give_different_results(self):
        a = make_animal("lion", "Lion", strength=70, weapon=65)
        b = make_animal("bear", "Bear", strength=72, weapon=66)

        r1 = run_simulation(a, b, NEUTRAL_ENV, num_simulations=500, seed=1)
        r2 = run_simulation(a, b, NEUTRAL_ENV, num_simulations=500, seed=2)

        # Extremely unlikely (though not impossible) that two independent
        # random batches produce byte-identical win counts.
        assert (r1.animal_a_wins, r1.animal_b_wins) != (r2.animal_a_wins, r2.animal_b_wins)


class TestSymmetryAndSanity:
    def test_identical_animals_are_roughly_even(self):
        a = make_animal("a", "Twin A")
        b = make_animal("b", "Twin B")
        result = run_simulation(a, b, NEUTRAL_ENV, num_simulations=8000, seed=7)

        assert 42 <= result.win_pct_a <= 58
        assert 42 <= result.win_pct_b <= 58
        assert result.animal_a_wins + result.animal_b_wins + result.draws == 8000

    def test_strictly_dominant_animal_wins_majority(self):
        strong = make_animal("s", "Strong", strength=95, weapon=95, defense=90, speed=90, agility=90, endurance=90, size=90)
        weak = make_animal("w", "Weak", strength=15, weapon=15, defense=15, speed=15, agility=15, endurance=15, size=15)

        result = run_simulation(strong, weak, NEUTRAL_ENV, num_simulations=3000, seed=11)

        assert result.win_pct_a > 90
        assert result.win_pct_a > result.win_pct_b

    def test_win_probability_is_never_absolute_for_a_plausible_gap(self):
        # A strongly favored -- but not physically absurd -- gap should
        # still leave randomness room for the underdog to occasionally
        # win, rather than collapsing to a deterministic 100/0 outcome.
        strong = make_animal("s", "Strong", strength=72, weapon=68, defense=62, speed=58, agility=55, endurance=60, size=60)
        weak = make_animal("w", "Weak", strength=38, weapon=35, defense=32, speed=42, agility=45, endurance=40, size=40)

        result = run_simulation(strong, weak, NEUTRAL_ENV, num_simulations=5000, seed=3)
        assert result.animal_b_wins > 0
        assert result.win_pct_a > result.win_pct_b

    def test_num_simulations_must_be_positive(self):
        a = make_animal("a", "A")
        b = make_animal("b", "B")
        with pytest.raises(ValueError):
            run_simulation(a, b, NEUTRAL_ENV, num_simulations=0)


class TestEnvironmentModifiers:
    def test_cold_resistant_animal_gains_in_arctic(self):
        polar = make_animal("polar", "Polar Bear", endurance=70, defense=70)
        polar = AnimalProfile(**{**polar.__dict__, "adaptations": ("cold_resistant",)})
        arctic = EnvironmentProfile(id="arctic", name="Arctic", tags=("cold",))

        effective = apply_environment(polar, arctic)
        assert effective.endurance > polar.attributes.endurance
        assert effective.defense > polar.attributes.defense

    def test_modifier_never_exceeds_cap(self):
        # Stack every rule that could plausibly apply and confirm no
        # attribute moves more than the documented +/-15% cap.
        animal = make_animal(
            "x", "X", endurance=50, defense=50, speed=50, agility=50,
        )
        animal = AnimalProfile(**{**animal.__dict__, "adaptations": ("cold_resistant", "thick_fur"), "habitats": ("arctic",)})
        arctic = EnvironmentProfile(id="arctic", name="Arctic", tags=("cold",))

        effective = apply_environment(animal, arctic)
        for name in ("endurance", "defense", "speed", "agility"):
            base = getattr(animal.attributes, name)
            eff = getattr(effective, name)
            if base > 0:
                pct_change = (eff - base) / base
                assert pct_change <= 0.15 + 1e-9

    def test_mismatched_animal_is_penalized_not_destroyed(self):
        # A purely aquatic animal fighting on a mountain should be worse
        # off, but never reduced to zero -- the cap keeps penalties sane.
        fish = make_animal("shark", "Shark", speed=80, agility=70, defense=60)
        fish = AnimalProfile(**{**fish.__dict__, "adaptations": ("aquatic",)})
        mountain = EnvironmentProfile(id="mountain", name="Mountain", tags=())

        effective = apply_environment(fish, mountain)
        assert effective.speed < fish.attributes.speed
        assert effective.speed > 0
        pct_change = (effective.speed - fish.attributes.speed) / fish.attributes.speed
        assert pct_change >= -0.15 - 1e-9


class TestKeyFactors:
    def test_key_factors_reflect_actual_attribute_gaps(self):
        a = make_animal("a", "A", strength=90, weapon=85)
        b = make_animal("b", "B", strength=40, weapon=35)
        result = run_simulation(a, b, NEUTRAL_ENV, num_simulations=1000, seed=5)

        assert len(result.key_factors) > 0
        top = result.key_factors[0]
        assert top.attribute in ("strength", "weapon")
        assert top.favored_animal == "a"


class TestOverrides:
    def test_override_equalizes_attribute(self):
        a = make_animal("a", "A", strength=90)
        b = make_animal("b", "B", strength=30)

        baseline = run_simulation(a, b, NEUTRAL_ENV, num_simulations=3000, seed=9)
        equalized = run_simulation(
            a, b, NEUTRAL_ENV, num_simulations=3000, seed=9, overrides_b={"strength": 90}
        )

        # Equalizing B's strength to match A's should narrow A's edge.
        assert equalized.win_pct_a < baseline.win_pct_a

    def test_invalid_override_key_raises(self):
        a = make_animal("a", "A")
        b = make_animal("b", "B")
        with pytest.raises(ValueError):
            run_simulation(a, b, NEUTRAL_ENV, num_simulations=100, overrides_a={"not_a_real_attr": 10})


class TestAttributeValidation:
    def test_out_of_range_attribute_rejected(self):
        with pytest.raises(ValueError):
            CombatAttributes(size=150, strength=50, speed=50, agility=50, defense=50, weapon=50, endurance=50)
