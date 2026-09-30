from __future__ import annotations

from sqlalchemy import JSON, Float, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Animal(Base):
    __tablename__ = "animals"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    common_name: Mapped[str] = mapped_column(String(128), nullable=False)
    scientific_name: Mapped[str] = mapped_column(String(128), nullable=False)
    category: Mapped[str] = mapped_column(String(32), nullable=False)
    diet: Mapped[str] = mapped_column(String(32), nullable=False)
    fighting_style: Mapped[str] = mapped_column(String(32), nullable=False)
    description: Mapped[str] = mapped_column(String(512), default="")

    avg_weight_kg: Mapped[float] = mapped_column(Float, nullable=False)
    max_weight_kg: Mapped[float] = mapped_column(Float, nullable=False)
    avg_length_m: Mapped[float] = mapped_column(Float, nullable=False)
    top_speed_kmh: Mapped[float] = mapped_column(Float, nullable=False)
    bite_force_psi: Mapped[float | None] = mapped_column(Float, nullable=True)

    natural_weapons: Mapped[list] = mapped_column(JSON, default=list)
    habitats: Mapped[list] = mapped_column(JSON, default=list)
    adaptations: Mapped[list] = mapped_column(JSON, default=list)

    # 0-100 normalized combat attributes -- see simulation/attributes.py
    combat_size: Mapped[float] = mapped_column(Float, nullable=False)
    combat_strength: Mapped[float] = mapped_column(Float, nullable=False)
    combat_speed: Mapped[float] = mapped_column(Float, nullable=False)
    combat_agility: Mapped[float] = mapped_column(Float, nullable=False)
    combat_defense: Mapped[float] = mapped_column(Float, nullable=False)
    combat_weapon: Mapped[float] = mapped_column(Float, nullable=False)
    combat_endurance: Mapped[float] = mapped_column(Float, nullable=False)

    # Which combat attributes are "derived" from measured data vs. the
    # project's own "estimated" combat-relevance rating. See
    # docs/SIMULATION_METHODOLOGY.md.
    attribute_sources: Mapped[dict] = mapped_column(JSON, default=dict)

    image_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
