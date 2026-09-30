import type { Animal } from '../../types/animal'
import { ATTRIBUTE_LABELS, ATTRIBUTE_NAMES } from '../../types/animal'
import type { MatchupResult } from '../../types/matchup'
import { ComparisonStatBar } from '../animals/StatBar'
import { WinProbabilityBar } from './WinProbabilityBar'

export function ResultPanel({ result, animalA, animalB }: { result: MatchupResult; animalA: Animal; animalB: Animal }) {
  return (
    <div className="space-y-6 rounded-2xl border border-arena-border bg-arena-panel p-4 sm:p-6">
      <WinProbabilityBar
        animalA={animalA}
        animalB={animalB}
        winPctA={result.win_pct_a}
        winPctB={result.win_pct_b}
        draws={result.draws}
      />

      <div className="grid grid-cols-3 gap-3 text-center text-xs sm:text-sm">
        <Stat label="Simulations" value={result.num_simulations.toLocaleString()} />
        <Stat label="Avg. Rounds" value={`${result.avg_rounds.toFixed(1)} ± ${result.std_rounds.toFixed(1)}`} />
        <Stat label="Combat Score" value={`${result.ces_a.toFixed(0)} vs ${result.ces_b.toFixed(0)}`} />
      </div>

      <div>
        <h4 className="mb-3 text-center text-xs font-semibold uppercase tracking-widest text-arena-muted">
          Effective Attribute Comparison
        </h4>
        <div className="space-y-2.5">
          {ATTRIBUTE_NAMES.map((name) => (
            <ComparisonStatBar
              key={name}
              label={ATTRIBUTE_LABELS[name]}
              valueA={result.effective_attributes_a[name]}
              valueB={result.effective_attributes_b[name]}
            />
          ))}
        </div>
        <p className="mt-2 text-center text-[11px] text-arena-muted">
          Values reflect environment modifiers (and any what-if overrides) already applied.
        </p>
      </div>

      <div>
        <h4 className="mb-2 text-xs font-semibold uppercase tracking-widest text-arena-muted">Key Factors</h4>
        <ul className="space-y-1.5">
          {result.key_factors.map((factor) => (
            <li key={factor.attribute} className="flex items-center gap-2 text-sm">
              <span
                className={`h-2 w-2 shrink-0 rounded-full ${factor.favored_animal === 'a' ? 'bg-corner-a' : 'bg-corner-b'}`}
              />
              <span className="text-arena-text">
                {ATTRIBUTE_LABELS[factor.attribute]} favored{' '}
                <span className={factor.favored_animal === 'a' ? 'text-corner-a' : 'text-corner-b'}>
                  {factor.favored_animal === 'a' ? animalA.common_name : animalB.common_name}
                </span>
              </span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  )
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg bg-arena-panel-light py-2">
      <p className="font-display text-lg text-arena-text">{value}</p>
      <p className="text-[10px] uppercase tracking-wider text-arena-muted">{label}</p>
    </div>
  )
}
