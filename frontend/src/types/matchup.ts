import type { CombatAttributes } from './animal'

export interface KeyFactor {
  attribute: keyof CombatAttributes
  favored_animal: 'a' | 'b'
  magnitude: number
  description: string
}

export interface MatchupResult {
  id: string
  animal_a_id: string
  animal_b_id: string
  environment_id: string
  num_simulations: number
  seed: number | null
  animal_a_wins: number
  animal_b_wins: number
  draws: number
  win_pct_a: number
  win_pct_b: number
  avg_rounds: number
  std_rounds: number
  ces_a: number
  ces_b: number
  effective_attributes_a: CombatAttributes
  effective_attributes_b: CombatAttributes
  key_factors: KeyFactor[]
  what_if_overrides: {
    equalize_attributes: string[]
    overrides_a: Partial<CombatAttributes>
    overrides_b: Partial<CombatAttributes>
  } | null
  created_at: string
}

export interface AttributeOverrides extends Partial<CombatAttributes> {}

export interface SimulateRequest {
  animal_a_id: string
  animal_b_id: string
  environment_id: string
  num_simulations?: number
  seed?: number | null
  equalize_attributes?: string[]
  overrides_a?: AttributeOverrides
  overrides_b?: AttributeOverrides
}

export type CommentaryStyle = 'scientific' | 'sports' | 'documentary'

export interface CommentaryResult {
  matchup_id: string
  style: CommentaryStyle
  text: string
  created_at: string
  generated_by_llm: boolean
}
