import { useMemo, useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { useAnimals } from '../../hooks/useAnimals'
import { AnimalCard } from './AnimalCard'
import { LoadingSpinner } from '../common/LoadingSpinner'
import type { Animal } from '../../types/animal'

export function AnimalSelector({
  open,
  onClose,
  onSelect,
  excludeId,
  corner,
}: {
  open: boolean
  onClose: () => void
  onSelect: (animal: Animal) => void
  excludeId?: string | null
  corner: 'a' | 'b'
}) {
  const [search, setSearch] = useState('')
  const [category, setCategory] = useState<string>('all')
  const { data: animals, isLoading, error } = useAnimals()

  const categories = useMemo(() => {
    if (!animals) return []
    return Array.from(new Set(animals.map((a) => a.category))).sort()
  }, [animals])

  const filtered = useMemo(() => {
    if (!animals) return []
    return animals.filter((a) => {
      if (a.id === excludeId) return false
      if (category !== 'all' && a.category !== category) return false
      if (search && !a.common_name.toLowerCase().includes(search.toLowerCase())) return false
      return true
    })
  }, [animals, excludeId, category, search])

  return (
    <AnimatePresence>
      {open && (
        <motion.div
          className="fixed inset-0 z-50 flex items-end justify-center bg-black/70 backdrop-blur-sm sm:items-center"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={onClose}
        >
          <motion.div
            className="flex max-h-[85vh] w-full max-w-4xl flex-col rounded-t-2xl border border-arena-border bg-arena-bg p-4 sm:rounded-2xl sm:p-6"
            initial={{ y: 40, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            exit={{ y: 40, opacity: 0 }}
            onClick={(e) => e.stopPropagation()}
          >
            <div className="mb-4 flex items-center justify-between">
              <h2 className="font-display text-2xl text-arena-text">
                Choose Contender <span className={corner === 'a' ? 'text-corner-a' : 'text-corner-b'}>{corner.toUpperCase()}</span>
              </h2>
              <button onClick={onClose} className="text-arena-muted hover:text-arena-text" aria-label="Close">
                ✕
              </button>
            </div>

            <div className="mb-4 flex flex-col gap-2 sm:flex-row">
              <input
                autoFocus
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search animals..."
                className="flex-1 rounded-lg border border-arena-border bg-arena-panel px-3 py-2 text-sm text-arena-text placeholder:text-arena-muted focus:border-arena-ember focus:outline-none"
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

            <div className="overflow-y-auto pr-1">
              {isLoading && <LoadingSpinner label="Loading roster..." />}
              {error && <p className="text-sm text-corner-b">Failed to load animals.</p>}
              {!isLoading && filtered.length === 0 && (
                <p className="py-8 text-center text-sm text-arena-muted">No animals match your search.</p>
              )}
              <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-4">
                {filtered.map((animal) => (
                  <AnimalCard
                    key={animal.id}
                    animal={animal}
                    onClick={() => {
                      onSelect(animal)
                      onClose()
                    }}
                  />
                ))}
              </div>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}
