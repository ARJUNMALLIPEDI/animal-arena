import { apiClient } from './client'
import type { Tournament, TournamentCreateRequest } from '../types/tournament'

export async function createTournament(request: TournamentCreateRequest): Promise<Tournament> {
  const { data } = await apiClient.post<Tournament>('/api/tournaments', request)
  return data
}

export async function fetchTournament(id: string): Promise<Tournament> {
  const { data } = await apiClient.get<Tournament>(`/api/tournaments/${id}`)
  return data
}

export async function advanceTournament(
  id: string,
  options?: { numSimulations?: number; seed?: number; resolveAll?: boolean },
): Promise<Tournament> {
  const { data } = await apiClient.post<Tournament>(`/api/tournaments/${id}/advance`, null, {
    params: {
      num_simulations: options?.numSimulations,
      seed: options?.seed,
      resolve_all: options?.resolveAll ?? true,
    },
  })
  return data
}
