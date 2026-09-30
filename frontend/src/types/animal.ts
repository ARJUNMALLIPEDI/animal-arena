export interface CombatAttributes {
  size: number
  strength: number
  speed: number
  agility: number
  defense: number
  weapon: number
  endurance: number
}

export const ATTRIBUTE_LABELS: Record<keyof CombatAttributes, string> = {
  size: 'Size',
  strength: 'Strength',
  speed: 'Speed',
  agility: 'Agility',
  defense: 'Defense',
  weapon: 'Weaponry',
  endurance: 'Endurance',
}

export const ATTRIBUTE_NAMES: (keyof CombatAttributes)[] = [
  'size',
  'strength',
  'speed',
  'agility',
  'defense',
  'weapon',
  'endurance',
]

export interface Animal {
  id: string
  common_name: string
  scientific_name: string
  category: string
  diet: string
  fighting_style: string
  description: string
  avg_weight_kg: number
  max_weight_kg: number
  avg_length_m: number
  top_speed_kmh: number
  bite_force_psi: number | null
  natural_weapons: string[]
  habitats: string[]
  adaptations: string[]
  combat_attributes: CombatAttributes
  attribute_sources: Record<string, 'derived' | 'estimated'>
  image_url: string | null
}

export interface Environment {
  id: string
  name: string
  description: string
  tags: string[]
}
