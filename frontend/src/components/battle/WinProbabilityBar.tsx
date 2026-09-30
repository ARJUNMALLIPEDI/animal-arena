import { motion } from 'framer-motion'
import type { Animal } from '../../types/animal'

export function WinProbabilityBar({
  animalA,
  animalB,
  winPctA,
  winPctB,
  draws,
}: {
  animalA: Animal
  animalB: Animal
  winPctA: number
  winPctB: number
  draws: number
}) {
  return (
    <div>
      <div className="mb-2 flex items-end justify-between font-display text-3xl sm:text-4xl">
        <span className="text-corner-a">{winPctA.toFixed(1)}%</span>
        <span className="text-corner-b">{winPctB.toFixed(1)}%</span>
      </div>
      <div className="flex h-4 w-full overflow-hidden rounded-full border border-arena-border bg-arena-panel">
        <motion.div
          className="h-full bg-corner-a"
          initial={{ width: 0 }}
          animate={{ width: `${winPctA}%` }}
          transition={{ duration: 0.9, ease: 'easeOut' }}
        />
        <motion.div
          className="h-full bg-corner-b"
          initial={{ width: 0 }}
          animate={{ width: `${winPctB}%` }}
          transition={{ duration: 0.9, ease: 'easeOut' }}
        />
      </div>
      <div className="mt-2 flex justify-between text-xs text-arena-muted">
        <span>{animalA.common_name}</span>
        {draws > 0 && <span>{draws} draws</span>}
        <span>{animalB.common_name}</span>
      </div>
    </div>
  )
}
