import type { Animal } from '../../types/animal'
import { ATTRIBUTE_LABELS, ATTRIBUTE_NAMES } from '../../types/animal'
import { StatBar } from './StatBar'
import { CATEGORY_ICON, CATEGORY_COLOR } from './categoryIcon'

export function AnimalProfileCard({ animal }: { animal: Animal }) {
  return (
    <div className="overflow-hidden rounded-xl border border-arena-border bg-arena-panel">
      <div
        className={`flex h-32 items-center justify-center bg-gradient-to-br text-6xl ${
          CATEGORY_COLOR[animal.category] ?? 'from-slate-700/40 to-arena-panel'
        }`}
      >
        {CATEGORY_ICON[animal.category] ?? '❓'}
      </div>
      <div className="p-4">
        <h3 className="font-display text-2xl text-arena-text">{animal.common_name}</h3>
        <p className="mb-3 text-sm italic text-arena-muted">{animal.scientific_name}</p>
        <p className="mb-4 text-sm text-arena-text/90">{animal.description}</p>

        <div className="mb-4 grid grid-cols-2 gap-x-4 gap-y-1 text-xs text-arena-muted">
          <span>
            Avg weight: <span className="text-arena-text">{animal.avg_weight_kg.toLocaleString()} kg</span>
          </span>
          <span>
            Max weight: <span className="text-arena-text">{animal.max_weight_kg.toLocaleString()} kg</span>
          </span>
          <span>
            Length: <span className="text-arena-text">{animal.avg_length_m} m</span>
          </span>
          <span>
            Top speed: <span className="text-arena-text">{animal.top_speed_kmh} km/h</span>
          </span>
          {animal.bite_force_psi != null && (
            <span>
              Bite force: <span className="text-arena-text">{animal.bite_force_psi.toLocaleString()} psi</span>
            </span>
          )}
          <span>
            Diet: <span className="text-arena-text capitalize">{animal.diet}</span>
          </span>
        </div>

        <div className="mb-4 space-y-2">
          {ATTRIBUTE_NAMES.map((name) => (
            <StatBar key={name} label={ATTRIBUTE_LABELS[name]} value={animal.combat_attributes[name]} />
          ))}
        </div>

        <p className="mb-3 text-[11px] text-arena-muted">
          <span className="font-semibold text-arena-text">Size</span> and{' '}
          <span className="font-semibold text-arena-text">Speed</span> are derived from measured weight/speed data.
          Other combat attributes are the project's own estimated combat-relevance ratings, not measured values.
        </p>

        <div className="flex flex-wrap gap-1.5">
          {animal.natural_weapons.map((w) => (
            <span key={w} className="rounded-full bg-arena-panel-light px-2 py-0.5 text-[11px] text-arena-text">
              {w}
            </span>
          ))}
        </div>
      </div>
    </div>
  )
}
