from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator

from app.simulation.attributes import ATTRIBUTE_NAMES


class AttributeOverrides(BaseModel):
    """Optional what-if overrides for one animal's attributes, applied
    after environment modifiers. Only listed attributes are overridden."""

    size: float | None = Field(default=None, ge=0, le=100)
    strength: float | None = Field(default=None, ge=0, le=100)
    speed: float | None = Field(default=None, ge=0, le=100)
    agility: float | None = Field(default=None, ge=0, le=100)
    defense: float | None = Field(default=None, ge=0, le=100)
    weapon: float | None = Field(default=None, ge=0, le=100)
    endurance: float | None = Field(default=None, ge=0, le=100)

    def as_dict(self) -> dict[str, float]:
        return {k: v for k, v in self.model_dump().items() if v is not None}


class SimulateRequest(BaseModel):
    animal_a_id: str
    animal_b_id: str
    environment_id: str
    num_simulations: int = Field(default=10_000, ge=100, le=50_000)
    seed: int | None = Field(default=None, description="Optional seed for reproducible results.")
    equalize_attributes: list[str] = Field(
        default_factory=list,
        description="What-if: attribute names to force equal between both animals "
        "(each set to the average of the two before simulating).",
    )
    overrides_a: AttributeOverrides = Field(default_factory=AttributeOverrides)
    overrides_b: AttributeOverrides = Field(default_factory=AttributeOverrides)

    @field_validator("equalize_attributes")
    @classmethod
    def validate_equalize(cls, value: list[str]) -> list[str]:
        for name in value:
            if name not in ATTRIBUTE_NAMES:
                raise ValueError(f"unknown attribute '{name}' in equalize_attributes")
        return value

    @field_validator("animal_b_id")
    @classmethod
    def validate_distinct(cls, value: str, info) -> str:
        animal_a_id = info.data.get("animal_a_id")
        if animal_a_id is not None and value == animal_a_id:
            raise ValueError("animal_a_id and animal_b_id must be different")
        return value


class KeyFactorOut(BaseModel):
    attribute: str
    favored_animal: Literal["a", "b"]
    magnitude: float
    description: str


class MatchupResultOut(BaseModel):
    id: str
    animal_a_id: str
    animal_b_id: str
    environment_id: str
    num_simulations: int
    seed: int | None

    animal_a_wins: int
    animal_b_wins: int
    draws: int
    win_pct_a: float
    win_pct_b: float
    avg_rounds: float
    std_rounds: float
    ces_a: float
    ces_b: float

    effective_attributes_a: dict[str, float]
    effective_attributes_b: dict[str, float]
    key_factors: list[KeyFactorOut]
    what_if_overrides: dict | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
