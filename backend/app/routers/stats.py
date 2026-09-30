from __future__ import annotations

from collections import defaultdict

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.animal import Animal
from app.models.matchup import Matchup
from app.models.tournament import Tournament
from app.schemas.stats import AnimalWinRate, DashboardOut

router = APIRouter(prefix="/api/stats", tags=["stats"])


@router.get("/dashboard", response_model=DashboardOut)
def dashboard(db: Session = Depends(get_db)) -> DashboardOut:
    matchups = db.query(Matchup).order_by(Matchup.created_at.desc()).limit(500).all()
    total_matchups = db.query(Matchup).count()
    total_tournaments = db.query(Tournament).count()
    total_simulations = sum(m.num_simulations for m in matchups)

    appearances: dict[str, int] = defaultdict(int)
    wins: dict[str, int] = defaultdict(int)
    for m in matchups:
        appearances[m.animal_a_id] += 1
        appearances[m.animal_b_id] += 1
        if m.win_pct_a >= m.win_pct_b:
            wins[m.animal_a_id] += 1
        else:
            wins[m.animal_b_id] += 1

    top_ids = sorted(appearances, key=lambda k: appearances[k], reverse=True)[:10]
    names = {a.id: a.common_name for a in db.query(Animal).filter(Animal.id.in_(top_ids)).all()}

    most_simulated = [
        AnimalWinRate(
            animal_id=animal_id,
            common_name=names.get(animal_id, animal_id),
            total_matchups=appearances[animal_id],
            wins=wins[animal_id],
            win_pct=round(100 * wins[animal_id] / appearances[animal_id], 1) if appearances[animal_id] else 0.0,
        )
        for animal_id in top_ids
    ]

    return DashboardOut(
        total_matchups=total_matchups,
        total_tournaments=total_tournaments,
        total_simulations_run=total_simulations,
        most_simulated_animals=most_simulated,
        recent_matchups=[m.id for m in matchups[:20]],
    )
