from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.matchup import Matchup
from app.schemas.matchup import MatchupResultOut
from app.schemas.tournament import TournamentCreateRequest, TournamentMatchOut, TournamentOut
from app.services.matchup_service import AnimalNotFoundError, EnvironmentNotFoundError
from app.services.tournament_service import (
    TournamentNotFoundError,
    advance_tournament,
    champion_id,
    create_tournament,
    get_matches,
)

router = APIRouter(prefix="/api/tournaments", tags=["tournaments"])


def _to_schema(db: Session, tournament) -> TournamentOut:
    matches = get_matches(db, tournament.id)
    match_outs = []
    for m in matches:
        matchup_out = None
        if m.matchup_id:
            matchup = db.get(Matchup, m.matchup_id)
            if matchup:
                matchup_out = MatchupResultOut.model_validate(matchup)
        match_outs.append(
            TournamentMatchOut(
                id=m.id,
                round_number=m.round_number,
                match_index=m.match_index,
                animal_a_id=m.animal_a_id,
                animal_b_id=m.animal_b_id,
                winner_id=m.winner_id,
                matchup=matchup_out,
            )
        )
    return TournamentOut(
        id=tournament.id,
        name=tournament.name,
        environment_id=tournament.environment_id,
        status=tournament.status,
        participant_ids=tournament.participant_ids,
        matches=match_outs,
        champion_id=champion_id(db, tournament.id),
        created_at=tournament.created_at,
    )


@router.post("", response_model=TournamentOut)
def create(request: TournamentCreateRequest, db: Session = Depends(get_db)) -> TournamentOut:
    try:
        tournament = create_tournament(db, request)
    except (AnimalNotFoundError, EnvironmentNotFoundError) as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return _to_schema(db, tournament)


@router.get("/{tournament_id}", response_model=TournamentOut)
def get_one(tournament_id: str, db: Session = Depends(get_db)) -> TournamentOut:
    from app.models.tournament import Tournament

    tournament = db.get(Tournament, tournament_id)
    if tournament is None:
        raise HTTPException(status_code=404, detail=f"tournament '{tournament_id}' not found")
    return _to_schema(db, tournament)


@router.post("/{tournament_id}/advance", response_model=TournamentOut)
def advance(
    tournament_id: str,
    num_simulations: int = 5000,
    seed: int | None = None,
    resolve_all: bool = True,
    db: Session = Depends(get_db),
) -> TournamentOut:
    """Simulate the next unresolved round. If `resolve_all` is true (default),
    keep advancing until the whole bracket is decided or nothing more can be
    resolved in one call."""
    try:
        tournament = advance_tournament(db, tournament_id, num_simulations=num_simulations, seed=seed)
        if resolve_all:
            # advance_tournament only progresses one round per call; loop
            # until no additional match gets a winner (bracket fully
            # resolved), capped so a malformed bracket can't loop forever.
            resolved_count = sum(1 for m in get_matches(db, tournament_id) if m.winner_id)
            for _ in range(10):
                if tournament.status == "completed":
                    break
                tournament = advance_tournament(db, tournament_id, num_simulations=num_simulations, seed=seed)
                new_resolved_count = sum(1 for m in get_matches(db, tournament_id) if m.winner_id)
                if new_resolved_count == resolved_count:
                    break
                resolved_count = new_resolved_count
    except TournamentNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return _to_schema(db, tournament)
