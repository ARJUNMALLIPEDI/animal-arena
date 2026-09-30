from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel

CommentaryStyle = Literal["scientific", "sports", "documentary"]


class CommentaryRequest(BaseModel):
    matchup_id: str
    style: CommentaryStyle = "scientific"
    force_refresh: bool = False


class CommentaryOut(BaseModel):
    matchup_id: str
    style: CommentaryStyle
    text: str
    created_at: datetime
    generated_by_llm: bool = True
