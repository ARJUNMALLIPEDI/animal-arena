from __future__ import annotations

import logging

from sqlalchemy.orm import Session

from app.models.animal import Animal
from app.models.environment import Environment
from app.models.matchup import Matchup
from app.schemas.matchup import MatchupResultOut, SimulateRequest
from app.simulation import apply_environment, run_simulation

from .mapper import animal_to_profile, environment_to_profile

logger = logging.getLogger(__name__)


class AnimalNotFoundError(Exception):
    def __init__(self, animal_id: str):
        super().__init__(f"animal '{animal_id}' not found")
        self.animal_id = animal_id


class EnvironmentNotFoundError(Exception):
    def __init__(self, environment_id: str):
        super().__init__(f"environment '{environment_id}' not found")
        self.environment_id = environment_id


def get_animal_or_404(db: Session, animal_id: str) -> Animal:
    animal = db.get(Animal, animal_id)
    if animal is None:
        raise AnimalNotFoundError(animal_id)
    return animal


def get_environment_or_404(db: Session, environment_id: str) -> Environment:
    environment = db.get(Environment, environment_id)
    if environment is None:
        raise EnvironmentNotFoundError(environment_id)
    return environment


def _resolve_equalized_overrides(
    animal_a: Animal, animal_b: Animal, environment, equalize_attributes: list[str]
) -> tuple[dict[str, float], dict[str, float]]:
    """For each attribute in `equalize_attributes`, compute both animals'
    environment-adjusted value and set both to their average -- this is
    what powers a "what if they were equally strong" query."""
    if not equalize_attributes:
        return {}, {}

    profile_a = animal_to_profile(animal_a)
    profile_b = animal_to_profile(animal_b)
    eff_a = apply_environment(profile_a, environment)
    eff_b = apply_environment(profile_b, environment)

    overrides_a: dict[str, float] = {}
    overrides_b: dict[str, float] = {}
    for name in equalize_attributes:
        avg = (getattr(eff_a, name) + getattr(eff_b, name)) / 2.0
        overrides_a[name] = avg
        overrides_b[name] = avg
    return overrides_a, overrides_b


def simulate_matchup(db: Session, request: SimulateRequest) -> MatchupResultOut:
    animal_a = get_animal_or_404(db, request.animal_a_id)
    animal_b = get_animal_or_404(db, request.animal_b_id)
    environment_model = get_environment_or_404(db, request.environment_id)
    environment = environment_to_profile(environment_model)

    eq_overrides_a, eq_overrides_b = _resolve_equalized_overrides(
        animal_a, animal_b, environment, request.equalize_attributes
    )
    overrides_a = {**eq_overrides_a, **request.overrides_a.as_dict()}
    overrides_b = {**eq_overrides_b, **request.overrides_b.as_dict()}

    logger.info(
        "simulating matchup animal_a=%s animal_b=%s environment=%s n=%d seed=%s",
        animal_a.id, animal_b.id, environment.id, request.num_simulations, request.seed,
    )

    result = run_simulation(
        animal_to_profile(animal_a),
        animal_to_profile(animal_b),
        environment,
        num_simulations=request.num_simulations,
        seed=request.seed,
        overrides_a=overrides_a or None,
        overrides_b=overrides_b or None,
    )

    what_if = None
    if request.equalize_attributes or overrides_a or overrides_b:
        what_if = {
            "equalize_attributes": request.equalize_attributes,
            "overrides_a": overrides_a,
            "overrides_b": overrides_b,
        }

    matchup = Matchup(
        animal_a_id=animal_a.id,
        animal_b_id=animal_b.id,
        environment_id=environment.id,
        num_simulations=result.num_simulations,
        seed=result.seed,
        animal_a_wins=result.animal_a_wins,
        animal_b_wins=result.animal_b_wins,
        draws=result.draws,
        win_pct_a=result.win_pct_a,
        win_pct_b=result.win_pct_b,
        avg_rounds=result.avg_rounds,
        std_rounds=result.std_rounds,
        ces_a=result.ces_a,
        ces_b=result.ces_b,
        effective_attributes_a=result.effective_attributes_a,
        effective_attributes_b=result.effective_attributes_b,
        key_factors=[kf.__dict__ for kf in result.key_factors],
        what_if_overrides=what_if,
    )
    db.add(matchup)
    db.commit()
    db.refresh(matchup)

    logger.info(
        "matchup %s result: %s=%.1f%% %s=%.1f%% draws=%d avg_rounds=%.1f",
        matchup.id, animal_a.id, result.win_pct_a, animal_b.id, result.win_pct_b,
        result.draws, result.avg_rounds,
    )

    return _to_schema(matchup)


def _to_schema(matchup: Matchup) -> MatchupResultOut:
    return MatchupResultOut.model_validate(matchup)


def get_matchup(db: Session, matchup_id: str) -> Matchup | None:
    return db.get(Matchup, matchup_id)


def list_matchups(db: Session, limit: int = 50) -> list[Matchup]:
    return (
        db.query(Matchup)
        .order_by(Matchup.created_at.desc())
        .limit(limit)
        .all()
    )
