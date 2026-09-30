from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class CombatAttributesOut(BaseModel):
    size: float
    strength: float
    speed: float
    agility: float
    defense: float
    weapon: float
    endurance: float


class AnimalOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    common_name: str
    scientific_name: str
    category: str
    diet: str
    fighting_style: str
    description: str

    avg_weight_kg: float
    max_weight_kg: float
    avg_length_m: float
    top_speed_kmh: float
    bite_force_psi: float | None = None

    natural_weapons: list[str]
    habitats: list[str]
    adaptations: list[str]

    combat_attributes: CombatAttributesOut
    attribute_sources: dict[str, str] = Field(
        description="Per-attribute tag: 'derived' (computed from measured biological "
        "data) or 'estimated' (the project's own informed combat-relevance rating)."
    )
    image_url: str | None = None

    @classmethod
    def from_model(cls, animal) -> "AnimalOut":
        return cls(
            id=animal.id,
            common_name=animal.common_name,
            scientific_name=animal.scientific_name,
            category=animal.category,
            diet=animal.diet,
            fighting_style=animal.fighting_style,
            description=animal.description,
            avg_weight_kg=animal.avg_weight_kg,
            max_weight_kg=animal.max_weight_kg,
            avg_length_m=animal.avg_length_m,
            top_speed_kmh=animal.top_speed_kmh,
            bite_force_psi=animal.bite_force_psi,
            natural_weapons=animal.natural_weapons,
            habitats=animal.habitats,
            adaptations=animal.adaptations,
            combat_attributes=CombatAttributesOut(
                size=animal.combat_size,
                strength=animal.combat_strength,
                speed=animal.combat_speed,
                agility=animal.combat_agility,
                defense=animal.combat_defense,
                weapon=animal.combat_weapon,
                endurance=animal.combat_endurance,
            ),
            attribute_sources=animal.attribute_sources,
            image_url=animal.image_url,
        )
