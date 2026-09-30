import clsx from 'clsx'
import type { TournamentMatch } from '../../types/tournament'
import type { Animal } from '../../types/animal'

export function BracketMatchNode({
  match,
  animalsById,
}: {
  match: TournamentMatch
  animalsById: Record<string, Animal>
}) {
  const a = match.animal_a_id ? animalsById[match.animal_a_id] : null
  const b = match.animal_b_id ? animalsById[match.animal_b_id] : null

  return (
    <div className="w-48 rounded-lg border border-arena-border bg-arena-panel text-xs shadow-sm">
      <Slot name={a?.common_name} isWinner={!!match.winner_id && match.winner_id === match.animal_a_id} corner="a" />
      <div className="h-px bg-arena-border" />
      <Slot name={b?.common_name} isWinner={!!match.winner_id && match.winner_id === match.animal_b_id} corner="b" />
    </div>
  )
}

function Slot({ name, isWinner, corner }: { name?: string; isWinner: boolean; corner: 'a' | 'b' }) {
  return (
    <div
      className={clsx(
        'flex items-center justify-between px-2.5 py-2',
        isWinner && 'bg-arena-ember/10 font-semibold text-arena-ember',
        !isWinner && 'text-arena-text',
      )}
    >
      <span className="truncate">{name ?? <span className="text-arena-muted">TBD</span>}</span>
      {isWinner && <span className="text-arena-gold">👑</span>}
      {!name && <span className={corner === 'a' ? 'text-corner-a' : 'text-corner-b'} />}
    </div>
  )
}
