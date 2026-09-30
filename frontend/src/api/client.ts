import axios from 'axios'

// Every request goes through this one axios instance -- no component ever
// constructs a URL or calls fetch/axios directly. Base URL is injected at
// build time via Vite env vars, defaulting to the local dev backend.
export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000',
  headers: { 'Content-Type': 'application/json' },
})

export interface ApiErrorShape {
  detail: string | { msg: string; loc: (string | number)[] }[]
}

export function extractErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const data = error.response?.data as ApiErrorShape | undefined
    if (data?.detail) {
      if (typeof data.detail === 'string') return data.detail
      return data.detail.map((d) => d.msg).join(', ')
    }
    return error.message
  }
  return 'Unknown error'
}
