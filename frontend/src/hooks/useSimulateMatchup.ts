import { useMutation, useQueryClient } from '@tanstack/react-query'
import { simulateMatchup } from '../api/matchups'
import type { SimulateRequest } from '../types/matchup'

export function useSimulateMatchup() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (request: SimulateRequest) => simulateMatchup(request),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['matchup-history'] })
      queryClient.invalidateQueries({ queryKey: ['dashboard'] })
    },
  })
}
