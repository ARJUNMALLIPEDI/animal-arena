import { apiClient } from './client'
import type { CommentaryResult, CommentaryStyle, MatchupResult, SimulateRequest } from '../types/matchup'

export async function simulateMatchup(request: SimulateRequest): Promise<MatchupResult> {
  const { data } = await apiClient.post<MatchupResult>('/api/matchups/simulate', request)
  return data
}

export async function fetchMatchupHistory(limit = 20): Promise<MatchupResult[]> {
  const { data } = await apiClient.get<MatchupResult[]>('/api/matchups', { params: { limit } })
  return data
}

export async function fetchMatchup(id: string): Promise<MatchupResult> {
  const { data } = await apiClient.get<MatchupResult>(`/api/matchups/${id}`)
  return data
}

export async function fetchCommentary(
  matchupId: string,
  style: CommentaryStyle,
  forceRefresh = false,
): Promise<CommentaryResult> {
  const { data } = await apiClient.post<CommentaryResult>('/api/commentary', {
    matchup_id: matchupId,
    style,
    force_refresh: forceRefresh,
  })
  return data
}
