import { useState } from 'react'
import clsx from 'clsx'
import { ATTRIBUTE_LABELS, ATTRIBUTE_NAMES } from '../../types/animal'
import { useMatchupStore } from '../../store/matchupStore'
import type { Animal } from '../../types/animal'

export function WhatIfPanel({ animalA, animalB }: { animalA: Animal | null; animalB: Animal | null }) {
  const [open, setOpen] = useState(false)
  const {
    equalizeAttributes,
    toggleEqualize,
    overridesA,
    overridesB,
    setOverride,
    numSimulations,
    setNumSimulations,
    seed,
    setSeed,
    resetWhatIf,
  } = useMatchupStore()

  const hasActiveWhatIf = equalizeAttributes.length > 0 || Object.keys(overridesA).length > 0 || Object.keys(overridesB).length > 0

  return (
    <div className="rounded-xl border border-arena-border bg-arena-panel">
      <button
        onClick={() => setOpen((o) => !o)}
        className="flex w-full items-center justify-between px-4 py-3 text-sm font-medium text-arena-text"
      >
        <span>
          What-If Mode {hasActiveWhatIf && <span className="ml-1 text-arena-ember">● active</span>}
        </span>
        <span className="text-arena-muted">{open ? '−' : '+'}</span>
      </button>
      {open && (
        <div className="space-y-4 border-t border-arena-border px-4 py-4">
          <div>
            <p className="mb-2 text-xs font-semibold uppercase tracking-wider text-arena-muted">
              Equalize attributes (average both animals)
            </p>
            <div className="flex flex-wrap gap-1.5">
              {ATTRIBUTE_NAMES.map((name) => (
                <button
                  key={name}
                  onClick={() => toggleEqualize(name)}
                  className={clsx(
                    'rounded-full border px-2.5 py-1 text-xs transition-colors',
                    equalizeAttributes.includes(name)
                      ? 'border-arena-ember bg-arena-ember/15 text-arena-ember'
                      : 'border-arena-border text-arena-muted hover:text-arena-text',
                  )}
                >
                  {ATTRIBUTE_LABELS[name]}
                </button>
              ))}
            </div>
          </div>

          {animalA && (
            <OverrideRow animal={animalA} corner="a" overrides={overridesA} setOverride={setOverride} />
          )}
          {animalB && (
            <OverrideRow animal={animalB} corner="b" overrides={overridesB} setOverride={setOverride} />
          )}

          <div className="grid grid-cols-2 gap-3">
            <label className="text-xs text-arena-muted">
              Simulations
              <input
                type="number"
                min={100}
                max={50000}
                step={500}
                value={numSimulations}
                onChange={(e) => setNumSimulations(Number(e.target.value))}
                className="mt-1 w-full rounded-lg border border-arena-border bg-arena-panel-light px-2 py-1.5 text-sm text-arena-text focus:border-arena-ember focus:outline-none"
              />
            </label>
            <label className="text-xs text-arena-muted">
              Seed (optional, for reproducibility)
              <input
                type="number"
                value={seed ?? ''}
                placeholder="random"
                onChange={(e) => setSeed(e.target.value === '' ? null : Number(e.target.value))}
                className="mt-1 w-full rounded-lg border border-arena-border bg-arena-panel-light px-2 py-1.5 text-sm text-arena-text focus:border-arena-ember focus:outline-none"
              />
            </label>
          </div>

          {hasActiveWhatIf && (
            <button onClick={resetWhatIf} className="text-xs text-arena-muted underline hover:text-arena-text">
              Reset what-if overrides
            </button>
          )}
        </div>
      )}
    </div>
  )
}

function OverrideRow({
  animal,
  corner,
  overrides,
  setOverride,
}: {
  animal: Animal
  corner: 'a' | 'b'
  overrides: Partial<Record<(typeof ATTRIBUTE_NAMES)[number], number>>
  setOverride: (side: 'a' | 'b', attribute: string, value: number | undefined) => void
}) {
  return (
    <div>
      <p className={`mb-2 text-xs font-semibold uppercase tracking-wider ${corner === 'a' ? 'text-corner-a' : 'text-corner-b'}`}>
        Override {animal.common_name}'s attributes
      </p>
      <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
        {ATTRIBUTE_NAMES.map((name) => (
          <label key={name} className="text-[11px] text-arena-muted">
            {ATTRIBUTE_LABELS[name]}
            <input
              type="number"
              min={0}
              max={100}
              placeholder={String(animal.combat_attributes[name])}
              value={overrides[name] ?? ''}
              onChange={(e) =>
                setOverride(corner, name, e.target.value === '' ? undefined : Number(e.target.value))
              }
              className="mt-0.5 w-full rounded border border-arena-border bg-arena-panel-light px-1.5 py-1 text-xs text-arena-text focus:border-arena-ember focus:outline-none"
            />
          </label>
        ))}
      </div>
    </div>
  )
}
