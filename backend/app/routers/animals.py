from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.animal import Animal
from app.schemas.animal import AnimalOut

router = APIRouter(prefix="/api/animals", tags=["animals"])


@router.get("", response_model=list[AnimalOut])
def list_animals(
    db: Session = Depends(get_db),
    category: str | None = Query(default=None),
    habitat: str | None = Query(default=None),
    search: str | None = Query(default=None, description="Case-insensitive substring match on common name."),
) -> list[AnimalOut]:
    query = db.query(Animal)
    if category:
        query = query.filter(Animal.category == category)
    if search:
        query = query.filter(Animal.common_name.ilike(f"%{search}%"))
    animals = query.order_by(Animal.common_name).all()
    if habitat:
        animals = [a for a in animals if habitat in (a.habitats or [])]
    return [AnimalOut.from_model(a) for a in animals]


@router.get("/{animal_id}", response_model=AnimalOut)
def get_animal(animal_id: str, db: Session = Depends(get_db)) -> AnimalOut:
    animal = db.get(Animal, animal_id)
    if animal is None:
        raise HTTPException(status_code=404, detail=f"animal '{animal_id}' not found")
    return AnimalOut.from_model(animal)
