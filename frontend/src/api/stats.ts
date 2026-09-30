import { apiClient } from './client'
import type { Dashboard } from '../types/stats'

export async function fetchDashboard(): Promise<Dashboard> {
  const { data } = await apiClient.get<Dashboard>('/api/stats/dashboard')
  return data
}
