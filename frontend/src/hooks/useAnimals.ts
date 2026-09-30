import { useQuery } from '@tanstack/react-query'
import { fetchAnimal, fetchAnimals, fetchEnvironments } from '../api/animals'

export function useAnimals(params?: { category?: string; habitat?: string; search?: string }) {
  return useQuery({
    queryKey: ['animals', params],
    queryFn: () => fetchAnimals(params),
    staleTime: 5 * 60_000,
  })
}

export function useAnimal(id: string | null) {
  return useQuery({
    queryKey: ['animal', id],
    queryFn: () => fetchAnimal(id as string),
    enabled: !!id,
    staleTime: 5 * 60_000,
  })
}

export function useEnvironments() {
  return useQuery({
    queryKey: ['environments'],
    queryFn: fetchEnvironments,
    staleTime: 30 * 60_000,
  })
}
