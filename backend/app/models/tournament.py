from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


def _uuid() -> str:
    return str(uuid.uuid4())


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Tournament(Base):
    __tablename__ = "tournaments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    environment_id: Mapped[str] = mapped_column(ForeignKey("environments.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(16), default="pending")  # pending|in_progress|completed
    participant_ids: Mapped[list] = mapped_column(JSON, default=list)  # seeded order
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class TournamentMatch(Base):
    __tablename__ = "tournament_matches"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    tournament_id: Mapped[str] = mapped_column(ForeignKey("tournaments.id"), nullable=False)
    round_number: Mapped[int] = mapped_column(Integer, nullable=False)
    match_index: Mapped[int] = mapped_column(Integer, nullable=False)  # position within the round
    animal_a_id: Mapped[str | None] = mapped_column(ForeignKey("animals.id"), nullable=True)
    animal_b_id: Mapped[str | None] = mapped_column(ForeignKey("animals.id"), nullable=True)
    winner_id: Mapped[str | None] = mapped_column(ForeignKey("animals.id"), nullable=True)
    matchup_id: Mapped[str | None] = mapped_column(ForeignKey("matchups.id"), nullable=True)
