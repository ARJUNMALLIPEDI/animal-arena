"""Maps SQLAlchemy DB models to the simulation engine's plain dataclasses.
This is the seam that keeps app.simulation free of any ORM/DB dependency."""
from __future__ import annotations

from app.models.animal import Animal
from app.models.environment import Environment
from app.simulation.attributes import AnimalProfile, CombatAttributes, EnvironmentProfile


def animal_to_profile(animal: Animal) -> AnimalProfile:
    return AnimalProfile(
        id=animal.id,
        name=animal.common_name,
        attributes=CombatAttributes(
            size=animal.combat_size,
            strength=animal.combat_strength,
            speed=animal.combat_speed,
            agility=animal.combat_agility,
            defense=animal.combat_defense,
            weapon=animal.combat_weapon,
            endurance=animal.combat_endurance,
        ),
        habitats=tuple(animal.habitats or ()),
        adaptations=tuple(animal.adaptations or ()),
        fighting_style=animal.fighting_style,
    )


def environment_to_profile(environment: Environment) -> EnvironmentProfile:
    return EnvironmentProfile(id=environment.id, name=environment.name, tags=tuple(environment.tags or ()))
