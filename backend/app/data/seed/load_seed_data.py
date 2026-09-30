"""Loads animals.json / environments.json into the database. Idempotent --
safe to run multiple times (upserts by primary key)."""
from __future__ import annotations

import json
import logging
from pathlib import Path

from sqlalchemy.orm import Session

from app.models.animal import Animal
from app.models.environment import Environment

logger = logging.getLogger(__name__)
SEED_DIR = Path(__file__).parent


def load_animals(db: Session) -> int:
    data = json.loads((SEED_DIR / "animals.json").read_text())
    count = 0
    for row in data:
        existing = db.get(Animal, row["id"])
        combat = row["combat_attributes"]
        fields = dict(
            common_name=row["common_name"],
            scientific_name=row["scientific_name"],
            category=row["category"],
            diet=row["diet"],
            fighting_style=row["fighting_style"],
            description=row["description"],
            avg_weight_kg=row["avg_weight_kg"],
            max_weight_kg=row["max_weight_kg"],
            avg_length_m=row["avg_length_m"],
            top_speed_kmh=row["top_speed_kmh"],
            bite_force_psi=row["bite_force_psi"],
            natural_weapons=row["natural_weapons"],
            habitats=row["habitats"],
            adaptations=row["adaptations"],
            combat_size=combat["size"],
            combat_strength=combat["strength"],
            combat_speed=combat["speed"],
            combat_agility=combat["agility"],
            combat_defense=combat["defense"],
            combat_weapon=combat["weapon"],
            combat_endurance=combat["endurance"],
            attribute_sources=row["attribute_sources"],
        )
        if existing is None:
            db.add(Animal(id=row["id"], **fields))
        else:
            for key, value in fields.items():
                setattr(existing, key, value)
        count += 1
    db.commit()
    return count


def load_environments(db: Session) -> int:
    data = json.loads((SEED_DIR / "environments.json").read_text())
    count = 0
    for row in data:
        existing = db.get(Environment, row["id"])
        fields = dict(name=row["name"], description=row["description"], tags=row["tags"])
        if existing is None:
            db.add(Environment(id=row["id"], **fields))
        else:
            for key, value in fields.items():
                setattr(existing, key, value)
        count += 1
    db.commit()
    return count


def seed_if_empty(db: Session) -> None:
    if db.query(Animal).count() == 0:
        n = load_animals(db)
        logger.info("seeded %d animals", n)
    if db.query(Environment).count() == 0:
        n = load_environments(db)
        logger.info("seeded %d environments", n)
