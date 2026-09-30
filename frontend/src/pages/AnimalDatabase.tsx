import { useMemo, useState } from 'react'
import { useAnimals } from '../hooks/useAnimals'
import { AnimalCard } from '../components/animals/AnimalCard'
import { AnimalProfileCard } from '../components/animals/AnimalProfileCard'
import { LoadingSpinner } from '../components/common/LoadingSpinner'
import type { Animal } from '../types/animal'

export function AnimalDatabase() {
  const { data: animals, isLoading, error } = useAnimals()
  const [search, setSearch] = useState('')
  const [category, setCategory] = useState('all')
  const [selected, setSelected] = useState<Animal | null>(null)

  const categories = useMemo(() => {
    if (!animals) return []
    return Array.from(new Set(animals.map((a) => a.category))).sort()
  }, [animals])

  const filtered = useMemo(() => {
    if (!animals) return []
    return animals.filter((a) => {
      if (category !== 'all' && a.category !== category) return false
      if (search && !a.common_name.toLowerCase().includes(search.toLowerCase())) return false
      return true
    })
  }, [animals, category, search])

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6">
      <div className="mb-6 text-center">
        <h1 className="font-display text-4xl text-arena-text sm:text-5xl">The Bestiary</h1>
        <p className="mt-2 text-sm text-arena-muted">
          {animals?.length ?? '...'} animals, each with measured biological data plus a documented combat-attribute
          model.
        </p>
      </div>

      <div className="mb-6 flex flex-col gap-2 sm:flex-row sm:justify-center">
        <input
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search animals..."
          className="rounded-lg border border-arena-border bg-arena-panel px-3 py-2 text-sm text-arena-text placeholder:text-arena-muted focus:border-arena-ember focus:outline-none sm:w-64"
        />
        <select
          value={category}
          onChange={(e) => setCategory(e.target.value)}
          className="rounded-lg border border-arena-border bg-arena-panel px-3 py-2 text-sm text-arena-text focus:border-arena-ember focus:outline-none"
        >
          <option value="all">All categories</option>
          {categories.map((c) => (
            <option key={c} value={c}>
              {c}
            </option>
          ))}
        </select>
      </div>

      {isLoading && <LoadingSpinner label="Loading the bestiary..." />}
      {error && <p className="text-center text-sm text-corner-b">Failed to load animals.</p>}

      <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5">
        {filtered.map((animal) => (
          <AnimalCard key={animal.id} animal={animal} onClick={() => setSelected(animal)} />
        ))}
      </div>

      {selected && (
        <div
          className="fixed inset-0 z-50 flex items-end justify-center bg-black/70 backdrop-blur-sm sm:items-center"
          onClick={() => setSelected(null)}
        >
          <div className="max-h-[85vh] w-full max-w-md overflow-y-auto" onClick={(e) => e.stopPropagation()}>
            <AnimalProfileCard animal={selected} />
            <button
              onClick={() => setSelected(null)}
              className="mt-3 w-full rounded-lg border border-arena-border py-2 text-sm text-arena-muted hover:text-arena-text"
            >
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
