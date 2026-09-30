import { useMemo, useState } from 'react'
import { useAnimals } from '../hooks/useAnimals'
import { useAdvanceTournament, useCreateTournament, useTournament } from '../hooks/useTournament'
import { EnvironmentPicker } from '../components/battle/EnvironmentPicker'
import { BracketView } from '../components/tournament/BracketView'
import { LoadingSpinner } from '../components/common/LoadingSpinner'
import { ErrorMessage } from '../components/common/ErrorMessage'
import { extractErrorMessage } from '../api/client'
import { CATEGORY_ICON } from '../components/animals/categoryIcon'
import clsx from 'clsx'
import type { Animal } from '../types/animal'

const SIZES = [4, 8, 16]

export function TournamentPage() {
  const { data: animals } = useAnimals()
  const [selectedIds, setSelectedIds] = useState<string[]>([])
  const [bracketSize, setBracketSize] = useState(8)
  const [environmentId, setEnvironmentId] = useState('savanna')
  const [name, setName] = useState('Apex Predator Cup')
  const [tournamentId, setTournamentId] = useState<string | null>(null)

  const createTournament = useCreateTournament()
  const { data: tournament, isLoading: loadingTournament } = useTournament(tournamentId)
  const advance = useAdvanceTournament(tournamentId)

  const animalsById = useMemo(() => {
    const map: Record<string, Animal> = {}
    animals?.forEach((a) => (map[a.id] = a))
    return map
  }, [animals])

  const toggleAnimal = (id: string) => {
    setSelectedIds((prev) => {
      if (prev.includes(id)) return prev.filter((x) => x !== id)
      if (prev.length >= bracketSize) return prev
      return [...prev, id]
    })
  }

  const handleCreate = () => {
    createTournament.mutate(
      { name, environment_id: environmentId, animal_ids: selectedIds, num_simulations: 3000 },
      { onSuccess: (t) => setTournamentId(t.id) },
    )
  }

  const handleReset = () => {
    setTournamentId(null)
    setSelectedIds([])
  }

  if (tournamentId) {
    return (
      <div className="mx-auto max-w-6xl px-4 py-8 sm:px-6">
        <div className="mb-6 flex items-center justify-between">
          <h1 className="font-display text-3xl text-arena-text sm:text-4xl">{tournament?.name ?? 'Tournament'}</h1>
          <button onClick={handleReset} className="text-xs text-arena-muted underline hover:text-arena-text">
            New tournament
          </button>
        </div>

        {loadingTournament && <LoadingSpinner label="Loading bracket..." />}

        {tournament && (
          <>
            <div className="mb-6 flex flex-wrap items-center justify-between gap-3 rounded-xl border border-arena-border bg-arena-panel p-4">
              <div className="text-sm text-arena-muted">
                Status: <span className="text-arena-text capitalize">{tournament.status.replace('_', ' ')}</span> ·{' '}
                {tournament.participant_ids.length} animals · {tournament.environment_id.replace('_', ' ')}
              </div>
              {tournament.status !== 'completed' && (
                <button
                  onClick={() => advance.mutate({ numSimulations: 3000 })}
                  disabled={advance.isPending}
                  className="rounded-full bg-arena-ember px-5 py-2 text-sm font-semibold text-arena-bg disabled:opacity-50"
                >
                  {advance.isPending ? 'Simulating rounds…' : 'Run Tournament'}
                </button>
              )}
            </div>
            {advance.isError && <ErrorMessage message={extractErrorMessage(advance.error)} />}
            <BracketView tournament={tournament} animalsById={animalsById} />
          </>
        )}
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-5xl px-4 py-8 sm:px-6">
      <div className="mb-6 text-center">
        <h1 className="font-display text-4xl text-arena-text sm:text-5xl">Tournament Mode</h1>
        <p className="mt-2 text-sm text-arena-muted">
          Pick a bracket size and select that many animals to generate a single-elimination tournament.
        </p>
      </div>

      <div className="mb-6 flex flex-col items-center gap-3">
        <input
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Tournament name"
          className="w-full max-w-sm rounded-lg border border-arena-border bg-arena-panel px-3 py-2 text-center text-sm text-arena-text focus:border-arena-ember focus:outline-none"
        />
        <div className="flex gap-2">
          {SIZES.map((size) => (
            <button
              key={size}
              onClick={() => {
                setBracketSize(size)
                setSelectedIds((prev) => prev.slice(0, size))
              }}
              className={clsx(
                'rounded-full border px-4 py-1.5 text-sm',
                bracketSize === size
                  ? 'border-arena-ember bg-arena-ember/15 text-arena-ember'
                  : 'border-arena-border text-arena-muted hover:text-arena-text',
              )}
            >
              {size} animals
            </button>
          ))}
        </div>
        <EnvironmentPicker value={environmentId} onChange={setEnvironmentId} />
      </div>

      <p className="mb-3 text-center text-sm text-arena-text">
        Selected {selectedIds.length} / {bracketSize}
      </p>

      <div className="mb-8 grid grid-cols-3 gap-2 sm:grid-cols-4 md:grid-cols-6">
        {animals?.map((animal) => {
          const isSelected = selectedIds.includes(animal.id)
          return (
            <button
              key={animal.id}
              onClick={() => toggleAnimal(animal.id)}
              className={clsx(
                'flex flex-col items-center gap-1 rounded-lg border p-2 text-center transition-colors',
                isSelected ? 'border-arena-ember bg-arena-ember/10' : 'border-arena-border bg-arena-panel hover:border-arena-ember/40',
              )}
            >
              <span className="text-2xl">{CATEGORY_ICON[animal.category]}</span>
              <span className="truncate text-[11px] text-arena-text">{animal.common_name}</span>
            </button>
          )
        })}
      </div>

      {createTournament.isError && <ErrorMessage message={extractErrorMessage(createTournament.error)} />}

      <div className="flex justify-center">
        <button
          onClick={handleCreate}
          disabled={selectedIds.length !== bracketSize || createTournament.isPending}
          className="rounded-full bg-arena-ember px-10 py-3 font-display text-xl tracking-widest text-arena-bg shadow-[0_0_30px_rgba(255,90,46,0.4)] disabled:cursor-not-allowed disabled:opacity-40"
        >
          {createTournament.isPending ? 'CREATING…' : 'CREATE BRACKET'}
        </button>
      </div>
    </div>
  )
}
