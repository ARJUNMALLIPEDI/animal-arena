from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.matchup import MatchupResultOut, SimulateRequest
from app.services.matchup_service import (
    AnimalNotFoundError,
    EnvironmentNotFoundError,
    get_matchup,
    list_matchups,
    simulate_matchup,
)

router = APIRouter(prefix="/api/matchups", tags=["matchups"])


@router.post("/simulate", response_model=MatchupResultOut)
def simulate(request: SimulateRequest, db: Session = Depends(get_db)) -> MatchupResultOut:
    try:
        return simulate_matchup(db, request)
    except (AnimalNotFoundError, EnvironmentNotFoundError) as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("", response_model=list[MatchupResultOut])
def get_history(limit: int = 50, db: Session = Depends(get_db)) -> list[MatchupResultOut]:
    return [MatchupResultOut.model_validate(m) for m in list_matchups(db, limit=limit)]


@router.get("/{matchup_id}", response_model=MatchupResultOut)
def get_one(matchup_id: str, db: Session = Depends(get_db)) -> MatchupResultOut:
    matchup = get_matchup(db, matchup_id)
    if matchup is None:
        raise HTTPException(status_code=404, detail=f"matchup '{matchup_id}' not found")
    return MatchupResultOut.model_validate(matchup)
