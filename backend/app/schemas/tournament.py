from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from .matchup import MatchupResultOut


class TournamentCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    environment_id: str
    animal_ids: list[str] = Field(min_length=2, max_length=32)
    num_simulations: int = Field(default=5_000, ge=100, le=50_000)
    seed: int | None = None

    @field_validator("animal_ids")
    @classmethod
    def power_of_two(cls, value: list[str]) -> list[str]:
        if len(set(value)) != len(value):
            raise ValueError("animal_ids must be unique")
        n = len(value)
        if n & (n - 1) != 0:
            raise ValueError("number of animals must be a power of two (2, 4, 8, 16, 32)")
        return value


class TournamentMatchOut(BaseModel):
    id: str
    round_number: int
    match_index: int
    animal_a_id: str | None
    animal_b_id: str | None
    winner_id: str | None
    matchup: MatchupResultOut | None = None

    model_config = {"from_attributes": True}


class TournamentOut(BaseModel):
    id: str
    name: str
    environment_id: str
    status: str
    participant_ids: list[str]
    matches: list[TournamentMatchOut]
    champion_id: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
