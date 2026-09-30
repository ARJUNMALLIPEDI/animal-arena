import type { Animal } from '../../types/animal'
import { CATEGORY_ICON, CATEGORY_COLOR } from '../animals/categoryIcon'

export function ContenderSlot({
  animal,
  corner,
  onPick,
}: {
  animal: Animal | undefined | null
  corner: 'a' | 'b'
  onPick: () => void
}) {
  const cornerColor = corner === 'a' ? 'text-corner-a border-corner-a/40' : 'text-corner-b border-corner-b/40'

  if (!animal) {
    return (
      <button
        onClick={onPick}
        className={`flex h-56 w-full flex-col items-center justify-center gap-2 rounded-2xl border-2 border-dashed ${cornerColor} bg-arena-panel/50 transition-colors hover:bg-arena-panel`}
      >
        <span className="text-4xl">+</span>
        <span className="font-display text-lg tracking-wide">Pick Contender {corner.toUpperCase()}</span>
      </button>
    )
  }

  return (
    <button
      onClick={onPick}
      className={`group relative flex h-56 w-full flex-col items-center justify-center gap-2 overflow-hidden rounded-2xl border-2 bg-gradient-to-br p-4 text-center transition-transform hover:scale-[1.01] ${cornerColor} ${
        CATEGORY_COLOR[animal.category] ?? 'from-slate-700/40 to-arena-panel'
      }`}
    >
      <span className="absolute right-3 top-3 rounded bg-black/40 px-2 py-0.5 text-[10px] uppercase tracking-wider text-arena-text/80">
        Change
      </span>
      <span className="text-6xl">{CATEGORY_ICON[animal.category] ?? '❓'}</span>
      <span className="font-display text-2xl leading-tight text-arena-text">{animal.common_name}</span>
      <span className="text-xs italic text-arena-text/70">{animal.scientific_name}</span>
    </button>
  )
}
