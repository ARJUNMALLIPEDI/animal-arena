from __future__ import annotations

from pydantic import BaseModel


class AnimalWinRate(BaseModel):
    animal_id: str
    common_name: str
    total_matchups: int
    wins: int
    win_pct: float


class DashboardOut(BaseModel):
    total_matchups: int
    total_tournaments: int
    total_simulations_run: int
    most_simulated_animals: list[AnimalWinRate]
    recent_matchups: list[str]  # matchup ids, most recent first
