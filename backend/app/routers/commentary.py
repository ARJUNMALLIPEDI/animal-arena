from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.commentary import CommentaryOut, CommentaryRequest
from app.services.commentary_service import generate_commentary

router = APIRouter(prefix="/api/commentary", tags=["commentary"])


@router.post("", response_model=CommentaryOut)
def create_commentary(request: CommentaryRequest, db: Session = Depends(get_db)) -> CommentaryOut:
    try:
        return generate_commentary(db, request.matchup_id, request.style, request.force_refresh)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
