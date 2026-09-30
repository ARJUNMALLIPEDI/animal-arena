import type { MatchupResult } from './matchup'

export interface TournamentMatch {
  id: string
  round_number: number
  match_index: number
  animal_a_id: string | null
  animal_b_id: string | null
  winner_id: string | null
  matchup: MatchupResult | null
}

export interface Tournament {
  id: string
  name: string
  environment_id: string
  status: 'pending' | 'in_progress' | 'completed'
  participant_ids: string[]
  matches: TournamentMatch[]
  champion_id: string | null
  created_at: string
}

export interface TournamentCreateRequest {
  name: string
  environment_id: string
  animal_ids: string[]
  num_simulations?: number
  seed?: number | null
}
