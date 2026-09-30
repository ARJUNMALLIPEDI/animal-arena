from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


def _uuid() -> str:
    return str(uuid.uuid4())


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Matchup(Base):
    """A persisted record of one simulated matchup (single or as part of a
    tournament match). Stores both inputs and the full aggregated result so
    history can be re-displayed without re-running the simulation."""

    __tablename__ = "matchups"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    animal_a_id: Mapped[str] = mapped_column(ForeignKey("animals.id"), nullable=False)
    animal_b_id: Mapped[str] = mapped_column(ForeignKey("animals.id"), nullable=False)
    environment_id: Mapped[str] = mapped_column(ForeignKey("environments.id"), nullable=False)

    num_simulations: Mapped[int] = mapped_column(Integer, nullable=False)
    seed: Mapped[int | None] = mapped_column(Integer, nullable=True)

    animal_a_wins: Mapped[int] = mapped_column(Integer, nullable=False)
    animal_b_wins: Mapped[int] = mapped_column(Integer, nullable=False)
    draws: Mapped[int] = mapped_column(Integer, nullable=False)
    win_pct_a: Mapped[float] = mapped_column(Float, nullable=False)
    win_pct_b: Mapped[float] = mapped_column(Float, nullable=False)
    avg_rounds: Mapped[float] = mapped_column(Float, nullable=False)
    std_rounds: Mapped[float] = mapped_column(Float, nullable=False)
    ces_a: Mapped[float] = mapped_column(Float, nullable=False)
    ces_b: Mapped[float] = mapped_column(Float, nullable=False)

    effective_attributes_a: Mapped[dict] = mapped_column(JSON, default=dict)
    effective_attributes_b: Mapped[dict] = mapped_column(JSON, default=dict)
    key_factors: Mapped[list] = mapped_column(JSON, default=list)
    what_if_overrides: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
