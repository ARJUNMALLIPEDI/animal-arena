from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class EnvironmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    description: str
    tags: list[str]
