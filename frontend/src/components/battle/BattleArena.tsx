import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import type { Animal } from '../../types/animal'
import { CATEGORY_ICON } from '../animals/categoryIcon'

interface BattleArenaProps {
  animalA: Animal
  animalB: Animal
  /** Present once the simulation result has arrived; null while still running. */
  winnerId: string | null
  onFinished?: () => void
}

/**
 * A stylized, non-graphic battle animation: both contenders slide in from
 * their corners, meet in a flash of light, and the arena settles on the
 * winner. This is purely presentational -- the outcome comes entirely from
 * the simulation engine's result, never decided here.
 */
export function BattleArena({ animalA, animalB, winnerId, onFinished }: BattleArenaProps) {
  const [phase, setPhase] = useState<'approach' | 'clash' | 'settled'>('approach')

  useEffect(() => {
    if (winnerId && phase === 'approach') {
      const t1 = setTimeout(() => setPhase('clash'), 700)
      return () => clearTimeout(t1)
    }
  }, [winnerId, phase])

  useEffect(() => {
    if (phase === 'clash') {
      const t2 = setTimeout(() => {
        setPhase('settled')
        onFinished?.()
      }, 650)
      return () => clearTimeout(t2)
    }
  }, [phase, onFinished])

  const aWins = winnerId === animalA.id
  const bWins = winnerId === animalB.id

  return (
    <div className="relative flex h-64 items-center justify-center overflow-hidden rounded-2xl border border-arena-border bg-arena-bg bg-grid sm:h-72">
      <motion.div
        className="absolute flex flex-col items-center gap-2"
        animate={
          phase === 'approach'
            ? { x: ['-140%', '-18%'] }
            : phase === 'clash'
              ? { x: '-18%', rotate: [0, -6, 6, 0] }
              : { x: aWins ? '-14%' : '-30%', opacity: aWins || phase !== 'settled' ? 1 : 0.35, scale: aWins ? 1.15 : 0.9 }
        }
        transition={phase === 'approach' ? { duration: 0.7, ease: 'easeOut' } : { duration: 0.5 }}
      >
        <span className="text-7xl drop-shadow-[0_0_18px_rgba(62,166,255,0.5)]">{CATEGORY_ICON[animalA.category]}</span>
        <span className="font-display text-sm text-corner-a">{animalA.common_name}</span>
      </motion.div>

      <motion.div
        className="absolute flex flex-col items-center gap-2"
        animate={
          phase === 'approach'
            ? { x: ['140%', '18%'] }
            : phase === 'clash'
              ? { x: '18%', rotate: [0, 6, -6, 0] }
              : { x: bWins ? '14%' : '30%', opacity: bWins || phase !== 'settled' ? 1 : 0.35, scale: bWins ? 1.15 : 0.9 }
        }
        transition={phase === 'approach' ? { duration: 0.7, ease: 'easeOut' } : { duration: 0.5 }}
      >
        <span className="text-7xl drop-shadow-[0_0_18px_rgba(255,77,109,0.5)]">{CATEGORY_ICON[animalB.category]}</span>
        <span className="font-display text-sm text-corner-b">{animalB.common_name}</span>
      </motion.div>

      {phase === 'clash' && (
        <motion.div
          className="absolute h-full w-full bg-white"
          initial={{ opacity: 0 }}
          animate={{ opacity: [0, 0.85, 0] }}
          transition={{ duration: 0.5 }}
        />
      )}

      {phase !== 'settled' && (
        <p className="absolute bottom-3 font-display text-xs uppercase tracking-[0.3em] text-arena-muted">
          {winnerId ? 'Clash!' : 'Entering the arena…'}
        </p>
      )}

      {phase === 'settled' && winnerId && (
        <motion.p
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="absolute bottom-3 font-display text-sm uppercase tracking-[0.3em] text-arena-gold"
        >
          {aWins ? animalA.common_name : animalB.common_name} wins
        </motion.p>
      )}
    </div>
  )
}
