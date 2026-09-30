import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { advanceTournament, createTournament, fetchTournament } from '../api/tournaments'
import type { TournamentCreateRequest } from '../types/tournament'

export function useTournament(id: string | null) {
  return useQuery({
    queryKey: ['tournament', id],
    queryFn: () => fetchTournament(id as string),
    enabled: !!id,
  })
}

export function useCreateTournament() {
  return useMutation({ mutationFn: (request: TournamentCreateRequest) => createTournament(request) })
}

export function useAdvanceTournament(id: string | null) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (options?: { numSimulations?: number; seed?: number }) =>
      advanceTournament(id as string, { ...options, resolveAll: true }),
    onSuccess: (data) => {
      queryClient.setQueryData(['tournament', id], data)
    },
  })
}
