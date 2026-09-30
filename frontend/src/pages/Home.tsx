import { useState } from 'react'
import { motion } from 'framer-motion'
import { useMatchupStore } from '../store/matchupStore'
import { useAnimal } from '../hooks/useAnimals'
import { useSimulateMatchup } from '../hooks/useSimulateMatchup'
import { ContenderSlot } from '../components/battle/ContenderSlot'
import { VersusBadge } from '../components/battle/VersusBadge'
import { EnvironmentPicker } from '../components/battle/EnvironmentPicker'
import { WhatIfPanel } from '../components/battle/WhatIfPanel'
import { BattleArena } from '../components/battle/BattleArena'
import { ResultPanel } from '../components/battle/ResultPanel'
import { AnimalSelector } from '../components/animals/AnimalSelector'
import { AttributeRadarChart } from '../components/charts/AttributeRadarChart'
import { WinDistributionChart } from '../components/charts/WinDistributionChart'
import { CommentaryPanel } from '../components/commentary/CommentaryPanel'
import { ErrorMessage } from '../components/common/ErrorMessage'
import { extractErrorMessage } from '../api/client'
import type { Animal } from '../types/animal'

export function Home() {
  const {
    animalAId,
    animalBId,
    environmentId,
    numSimulations,
    seed,
    equalizeAttributes,
    overridesA,
    overridesB,
    setAnimalA,
    setAnimalB,
    setEnvironment,
    swap,
  } = useMatchupStore()

  const { data: animalA } = useAnimal(animalAId)
  const { data: animalB } = useAnimal(animalBId)

  const [pickerOpen, setPickerOpen] = useState<'a' | 'b' | null>(null)
  const [arenaSettled, setArenaSettled] = useState(false)
  const simulate = useSimulateMatchup()

  const canSimulate = !!animalAId && !!animalBId && animalAId !== animalBId

  const handleSimulate = () => {
    if (!canSimulate) return
    setArenaSettled(false)
    simulate.mutate({
      animal_a_id: animalAId!,
      animal_b_id: animalBId!,
      environment_id: environmentId,
      num_simulations: numSimulations,
      seed: seed ?? undefined,
      equalize_attributes: equalizeAttributes,
      overrides_a: overridesA,
      overrides_b: overridesB,
    })
  }

  const handleSelect = (side: 'a' | 'b') => (animal: Animal) => {
    if (side === 'a') setAnimalA(animal.id)
    else setAnimalB(animal.id)
  }

  return (
    <div className="mx-auto max-w-5xl px-4 py-8 sm:px-6 sm:py-12">
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-10 text-center"
      >
        <h1 className="font-display text-5xl leading-none tracking-wide text-arena-text sm:text-7xl">
          ANIMAL <span className="text-arena-ember text-glow-ember">ARENA</span>
        </h1>
        <p className="mt-3 text-lg text-arena-muted sm:text-xl">
          Who would <span className="italic text-arena-text">actually</span> win?
        </p>
        <p className="mx-auto mt-2 max-w-xl text-xs text-arena-muted">
          Pick two animals, choose an environment, and run a statistical combat simulation — thousands of
          probabilistic encounters, not a guess.
        </p>
      </motion.div>

      <div className="mb-6 grid grid-cols-1 items-center gap-4 sm:grid-cols-[1fr_auto_1fr]">
        <ContenderSlot animal={animalA} corner="a" onPick={() => setPickerOpen('a')} />
        <VersusBadge />
        <ContenderSlot animal={animalB} corner="b" onPick={() => setPickerOpen('b')} />
      </div>

      <div className="mb-6 flex justify-center">
        <button onClick={swap} className="text-xs text-arena-muted underline hover:text-arena-text">
          ⇄ swap contenders
        </button>
      </div>

      <div className="mb-6">
        <p className="mb-2 text-center text-xs font-semibold uppercase tracking-widest text-arena-muted">Environment</p>
        <EnvironmentPicker value={environmentId} onChange={setEnvironment} />
      </div>

      <div className="mb-6">
        <WhatIfPanel animalA={animalA ?? null} animalB={animalB ?? null} />
      </div>

      <div className="mb-8 flex justify-center">
        <button
          onClick={handleSimulate}
          disabled={!canSimulate || simulate.isPending}
          className="rounded-full bg-arena-ember px-10 py-3 font-display text-xl tracking-widest text-arena-bg shadow-[0_0_30px_rgba(255,90,46,0.4)] transition-transform hover:scale-105 disabled:cursor-not-allowed disabled:opacity-40 disabled:hover:scale-100"
        >
          {simulate.isPending ? 'SIMULATING…' : 'SIMULATE BATTLE'}
        </button>
      </div>

      {!canSimulate && animalAId && animalBId && animalAId === animalBId && (
        <ErrorMessage message="Pick two different animals to simulate a matchup." />
      )}
      {simulate.isError && <ErrorMessage message={extractErrorMessage(simulate.error)} />}

      {(simulate.isPending || simulate.data) && animalA && animalB && (
        <div className="mb-6">
          <BattleArena
            animalA={animalA}
            animalB={animalB}
            winnerId={
              simulate.data ? (simulate.data.win_pct_a >= simulate.data.win_pct_b ? animalA.id : animalB.id) : null
            }
            onFinished={() => setArenaSettled(true)}
          />
        </div>
      )}

      {simulate.data && animalA && animalB && arenaSettled && (
        <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
          <ResultPanel result={simulate.data} animalA={animalA} animalB={animalB} />

          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
            <div className="rounded-2xl border border-arena-border bg-arena-panel p-4 sm:p-6">
              <h4 className="mb-3 text-center text-xs font-semibold uppercase tracking-widest text-arena-muted">
                Attribute Radar
              </h4>
              <AttributeRadarChart
                nameA={animalA.common_name}
                nameB={animalB.common_name}
                attributesA={simulate.data.effective_attributes_a}
                attributesB={simulate.data.effective_attributes_b}
              />
            </div>
            <div className="rounded-2xl border border-arena-border bg-arena-panel p-4 sm:p-6">
              <h4 className="mb-3 text-center text-xs font-semibold uppercase tracking-widest text-arena-muted">
                Simulation Outcomes
              </h4>
              <WinDistributionChart
                nameA={animalA.common_name}
                nameB={animalB.common_name}
                winsA={simulate.data.animal_a_wins}
                winsB={simulate.data.animal_b_wins}
                draws={simulate.data.draws}
              />
            </div>
          </div>

          <CommentaryPanel matchupId={simulate.data.id} />
        </motion.div>
      )}

      <AnimalSelector
        open={pickerOpen === 'a'}
        onClose={() => setPickerOpen(null)}
        onSelect={handleSelect('a')}
        excludeId={animalBId}
        corner="a"
      />
      <AnimalSelector
        open={pickerOpen === 'b'}
        onClose={() => setPickerOpen(null)}
        onSelect={handleSelect('b')}
        excludeId={animalAId}
        corner="b"
      />
    </div>
  )
}
