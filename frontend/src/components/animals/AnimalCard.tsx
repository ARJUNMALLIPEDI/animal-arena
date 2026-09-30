import clsx from 'clsx'
import type { Animal } from '../../types/animal'
import { CATEGORY_COLOR, CATEGORY_ICON } from './categoryIcon'

export function AnimalCard({
  animal,
  selected,
  onClick,
  corner,
}: {
  animal: Animal
  selected?: boolean
  onClick?: () => void
  corner?: 'a' | 'b'
}) {
  const ringColor = corner === 'a' ? 'ring-corner-a' : corner === 'b' ? 'ring-corner-b' : 'ring-arena-ember'
  return (
    <button
      type="button"
      onClick={onClick}
      className={clsx(
        'group relative flex w-full flex-col overflow-hidden rounded-xl border text-left transition-all',
        'border-arena-border bg-arena-panel hover:border-arena-ember/50',
        selected && `ring-2 ${ringColor} border-transparent`,
      )}
    >
      <div
        className={clsx(
          'flex h-28 items-center justify-center bg-gradient-to-br text-5xl',
          CATEGORY_COLOR[animal.category] ?? 'from-slate-700/40 to-arena-panel',
        )}
      >
        {CATEGORY_ICON[animal.category] ?? '❓'}
      </div>
      <div className="p-3">
        <p className="truncate font-display text-lg leading-tight text-arena-text">{animal.common_name}</p>
        <p className="truncate text-xs italic text-arena-muted">{animal.scientific_name}</p>
        <div className="mt-2 flex flex-wrap gap-1">
          <span className="rounded bg-arena-panel-light px-1.5 py-0.5 text-[10px] uppercase tracking-wide text-arena-muted">
            {animal.category}
          </span>
          <span className="rounded bg-arena-panel-light px-1.5 py-0.5 text-[10px] uppercase tracking-wide text-arena-muted">
            {animal.diet}
          </span>
        </div>
      </div>
    </button>
  )
}
