import { create } from 'zustand'
import type { AttributeOverrides } from '../types/matchup'

interface MatchupState {
  animalAId: string | null
  animalBId: string | null
  environmentId: string
  numSimulations: number
  seed: number | null
  equalizeAttributes: string[]
  overridesA: AttributeOverrides
  overridesB: AttributeOverrides

  setAnimalA: (id: string | null) => void
  setAnimalB: (id: string | null) => void
  setEnvironment: (id: string) => void
  setNumSimulations: (n: number) => void
  setSeed: (seed: number | null) => void
  toggleEqualize: (attribute: string) => void
  setOverride: (side: 'a' | 'b', attribute: string, value: number | undefined) => void
  resetWhatIf: () => void
  swap: () => void
}

export const useMatchupStore = create<MatchupState>((set) => ({
  animalAId: null,
  animalBId: null,
  environmentId: 'savanna',
  numSimulations: 10000,
  seed: null,
  equalizeAttributes: [],
  overridesA: {},
  overridesB: {},

  setAnimalA: (id) => set({ animalAId: id }),
  setAnimalB: (id) => set({ animalBId: id }),
  setEnvironment: (id) => set({ environmentId: id }),
  setNumSimulations: (n) => set({ numSimulations: n }),
  setSeed: (seed) => set({ seed }),
  toggleEqualize: (attribute) =>
    set((state) => ({
      equalizeAttributes: state.equalizeAttributes.includes(attribute)
        ? state.equalizeAttributes.filter((a) => a !== attribute)
        : [...state.equalizeAttributes, attribute],
    })),
  setOverride: (side, attribute, value) =>
    set((state) => {
      const key = side === 'a' ? 'overridesA' : 'overridesB'
      const next = { ...state[key] }
      if (value === undefined) delete (next as Record<string, number | undefined>)[attribute]
      else (next as Record<string, number | undefined>)[attribute] = value
      return { [key]: next } as Partial<MatchupState>
    }),
  resetWhatIf: () => set({ equalizeAttributes: [], overridesA: {}, overridesB: {} }),
  swap: () =>
    set((state) => ({
      animalAId: state.animalBId,
      animalBId: state.animalAId,
      overridesA: state.overridesB,
      overridesB: state.overridesA,
    })),
}))
