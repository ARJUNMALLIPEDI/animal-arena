from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.environment import Environment
from app.schemas.environment import EnvironmentOut

router = APIRouter(prefix="/api/environments", tags=["environments"])


@router.get("", response_model=list[EnvironmentOut])
def list_environments(db: Session = Depends(get_db)) -> list[EnvironmentOut]:
    return [EnvironmentOut.model_validate(e) for e in db.query(Environment).order_by(Environment.name).all()]


@router.get("/{environment_id}", response_model=EnvironmentOut)
def get_environment(environment_id: str, db: Session = Depends(get_db)) -> EnvironmentOut:
    env = db.get(Environment, environment_id)
    if env is None:
        raise HTTPException(status_code=404, detail=f"environment '{environment_id}' not found")
    return EnvironmentOut.model_validate(env)
