from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


def _uuid() -> str:
    return str(uuid.uuid4())


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Commentary(Base):
    """Cached AI-generated commentary for a matchup, keyed by (matchup, style)
    so repeated views of the same result don't re-call the LLM."""

    __tablename__ = "commentary"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    matchup_id: Mapped[str] = mapped_column(ForeignKey("matchups.id"), nullable=False)
    style: Mapped[str] = mapped_column(String(32), nullable=False)  # scientific|sports|documentary
    text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
