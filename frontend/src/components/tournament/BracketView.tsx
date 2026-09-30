import type { Tournament } from '../../types/tournament'
import type { Animal } from '../../types/animal'
import { BracketMatchNode } from './BracketMatchNode'

export function BracketView({ tournament, animalsById }: { tournament: Tournament; animalsById: Record<string, Animal> }) {
  const rounds = Array.from(new Set(tournament.matches.map((m) => m.round_number))).sort((a, b) => a - b)
  const roundLabel = (round: number, total: number) => {
    const remaining = total - round + 1
    if (remaining === 1) return 'Final'
    if (remaining === 2) return 'Semifinals'
    if (remaining === 3) return 'Quarterfinals'
    return `Round ${round}`
  }

  return (
    <div className="flex gap-8 overflow-x-auto pb-4">
      {rounds.map((round) => {
        const matches = tournament.matches
          .filter((m) => m.round_number === round)
          .sort((a, b) => a.match_index - b.match_index)
        return (
          <div key={round} className="flex shrink-0 flex-col">
            <p className="mb-3 text-center text-xs font-semibold uppercase tracking-widest text-arena-muted">
              {roundLabel(round, rounds.length)}
            </p>
            <div
              className="flex flex-1 flex-col justify-around gap-4"
              style={{ paddingTop: `${(2 ** (round - 1) - 1) * 24}px`, paddingBottom: `${(2 ** (round - 1) - 1) * 24}px` }}
            >
              {matches.map((match) => (
                <div key={match.id} style={{ marginBottom: `${(2 ** round - 1) * 8}px` }}>
                  <BracketMatchNode match={match} animalsById={animalsById} />
                </div>
              ))}
            </div>
          </div>
        )
      })}

      {tournament.champion_id && animalsById[tournament.champion_id] && (
        <div className="flex shrink-0 flex-col items-center justify-center">
          <p className="mb-3 text-center text-xs font-semibold uppercase tracking-widest text-arena-gold">Champion</p>
          <div className="flex h-28 w-40 flex-col items-center justify-center gap-1 rounded-xl border-2 border-arena-gold bg-arena-gold/10 text-center">
            <span className="text-3xl">🏆</span>
            <span className="font-display text-lg text-arena-gold">{animalsById[tournament.champion_id].common_name}</span>
          </div>
        </div>
      )}
    </div>
  )
}
