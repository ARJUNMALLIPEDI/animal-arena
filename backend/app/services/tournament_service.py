from __future__ import annotations

import logging
import math

from sqlalchemy.orm import Session

from app.models.tournament import Tournament, TournamentMatch
from app.schemas.matchup import SimulateRequest
from app.schemas.tournament import TournamentCreateRequest

from .matchup_service import get_animal_or_404, get_environment_or_404, simulate_matchup

logger = logging.getLogger(__name__)


class TournamentNotFoundError(Exception):
    def __init__(self, tournament_id: str):
        super().__init__(f"tournament '{tournament_id}' not found")


def create_tournament(db: Session, request: TournamentCreateRequest) -> Tournament:
    for animal_id in request.animal_ids:
        get_animal_or_404(db, animal_id)
    get_environment_or_404(db, request.environment_id)

    tournament = Tournament(
        name=request.name,
        environment_id=request.environment_id,
        status="pending",
        participant_ids=request.animal_ids,
    )
    db.add(tournament)
    db.flush()  # assign tournament.id

    num_participants = len(request.animal_ids)
    num_rounds = int(math.log2(num_participants))

    # Round 1 gets the seeded animals; later rounds start empty (TBD) and
    # are filled in as earlier rounds are decided.
    for round_number in range(1, num_rounds + 1):
        matches_in_round = num_participants // (2 ** round_number)
        for i in range(matches_in_round):
            if round_number == 1:
                animal_a_id = request.animal_ids[2 * i]
                animal_b_id = request.animal_ids[2 * i + 1]
            else:
                animal_a_id = None
                animal_b_id = None
            db.add(
                TournamentMatch(
                    tournament_id=tournament.id,
                    round_number=round_number,
                    match_index=i,
                    animal_a_id=animal_a_id,
                    animal_b_id=animal_b_id,
                )
            )

    db.commit()
    db.refresh(tournament)
    return tournament


def _get_tournament(db: Session, tournament_id: str) -> Tournament:
    tournament = db.get(Tournament, tournament_id)
    if tournament is None:
        raise TournamentNotFoundError(tournament_id)
    return tournament


def get_matches(db: Session, tournament_id: str) -> list[TournamentMatch]:
    return (
        db.query(TournamentMatch)
        .filter(TournamentMatch.tournament_id == tournament_id)
        .order_by(TournamentMatch.round_number, TournamentMatch.match_index)
        .all()
    )


def advance_tournament(
    db: Session, tournament_id: str, num_simulations: int = 5000, seed: int | None = None
) -> Tournament:
    """Simulate every decidable match in the earliest round that still has
    unresolved matches, then propagate winners into the next round. Called
    repeatedly (or in a loop by the caller) to fully resolve a bracket."""
    tournament = _get_tournament(db, tournament_id)
    matches = get_matches(db, tournament_id)
    if not matches:
        return tournament

    rounds = sorted({m.round_number for m in matches})
    for round_number in rounds:
        round_matches = [m for m in matches if m.round_number == round_number]
        unresolved = [m for m in round_matches if m.winner_id is None]
        if not unresolved:
            continue

        ready = [m for m in unresolved if m.animal_a_id and m.animal_b_id]
        if not ready:
            # Nothing in this round can be simulated yet (waiting on an
            # earlier round) -- stop here.
            break

        for match in ready:
            result = simulate_matchup(
                db,
                SimulateRequest(
                    animal_a_id=match.animal_a_id,
                    animal_b_id=match.animal_b_id,
                    environment_id=tournament.environment_id,
                    num_simulations=num_simulations,
                    seed=seed,
                ),
            )
            winner_id = match.animal_a_id if result.win_pct_a >= result.win_pct_b else match.animal_b_id
            match.winner_id = winner_id
            match.matchup_id = result.id

            next_round = [m for m in matches if m.round_number == round_number + 1]
            if next_round:
                next_match = next(
                    (m for m in next_round if m.match_index == match.match_index // 2), None
                )
                if next_match is not None:
                    if match.match_index % 2 == 0:
                        next_match.animal_a_id = winner_id
                    else:
                        next_match.animal_b_id = winner_id

        db.commit()
        logger.info("tournament %s: resolved round %d", tournament_id, round_number)
        break  # only advance one round per call

    final_round = max(rounds)
    db.refresh(tournament)
    all_matches = get_matches(db, tournament_id)
    final_matches = [m for m in all_matches if m.round_number == final_round]
    if final_matches and all(m.winner_id for m in final_matches):
        tournament.status = "completed"
    elif any(m.winner_id for m in all_matches):
        tournament.status = "in_progress"
    db.commit()
    db.refresh(tournament)
    return tournament


def champion_id(db: Session, tournament_id: str) -> str | None:
    matches = get_matches(db, tournament_id)
    if not matches:
        return None
    final_round = max(m.round_number for m in matches)
    final_match = next((m for m in matches if m.round_number == final_round), None)
    return final_match.winner_id if final_match else None
