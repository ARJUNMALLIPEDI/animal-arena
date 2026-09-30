export interface AnimalWinRate {
  animal_id: string
  common_name: string
  total_matchups: number
  wins: number
  win_pct: number
}

export interface Dashboard {
  total_matchups: number
  total_tournaments: number
  total_simulations_run: number
  most_simulated_animals: AnimalWinRate[]
  recent_matchups: string[]
}
