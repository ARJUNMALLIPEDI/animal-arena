import { apiClient } from './client'
import type { Animal, Environment } from '../types/animal'

export async function fetchAnimals(params?: { category?: string; habitat?: string; search?: string }): Promise<Animal[]> {
  const { data } = await apiClient.get<Animal[]>('/api/animals', { params })
  return data
}

export async function fetchAnimal(id: string): Promise<Animal> {
  const { data } = await apiClient.get<Animal>(`/api/animals/${id}`)
  return data
}

export async function fetchEnvironments(): Promise<Environment[]> {
  const { data } = await apiClient.get<Environment[]>('/api/environments')
  return data
}
