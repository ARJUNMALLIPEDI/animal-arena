import { useState } from 'react'
import clsx from 'clsx'
import { useCommentary } from '../../hooks/useCommentary'
import type { CommentaryStyle } from '../../types/matchup'
import { LoadingSpinner } from '../common/LoadingSpinner'

const STYLES: { id: CommentaryStyle; label: string; icon: string }[] = [
  { id: 'scientific', label: 'Scientific', icon: '🔬' },
  { id: 'sports', label: 'Sports Commentator', icon: '🎙️' },
  { id: 'documentary', label: 'Documentary', icon: '🎬' },
]

export function CommentaryPanel({ matchupId }: { matchupId: string }) {
  const [style, setStyle] = useState<CommentaryStyle>('scientific')
  const commentary = useCommentary()

  const handleGenerate = (nextStyle: CommentaryStyle) => {
    setStyle(nextStyle)
    commentary.mutate({ matchupId, style: nextStyle })
  }

  return (
    <div className="rounded-2xl border border-arena-border bg-arena-panel p-4 sm:p-6">
      <h4 className="mb-3 text-xs font-semibold uppercase tracking-widest text-arena-muted">AI Commentary</h4>
      <div className="mb-4 flex flex-wrap gap-2">
        {STYLES.map((s) => (
          <button
            key={s.id}
            onClick={() => handleGenerate(s.id)}
            className={clsx(
              'flex items-center gap-1.5 rounded-full border px-3 py-1.5 text-sm transition-colors',
              style === s.id && commentary.data
                ? 'border-arena-ember bg-arena-ember/15 text-arena-ember'
                : 'border-arena-border text-arena-muted hover:text-arena-text',
            )}
          >
            <span>{s.icon}</span>
            {s.label}
          </button>
        ))}
      </div>

      {commentary.isPending && <LoadingSpinner label="Generating commentary..." />}
      {commentary.isError && <p className="text-sm text-corner-b">Failed to generate commentary.</p>}
      {commentary.data && (
        <div className="rounded-lg bg-arena-panel-light p-4">
          <p className="text-sm leading-relaxed text-arena-text">{commentary.data.text}</p>
          {!commentary.data.generated_by_llm && (
            <p className="mt-2 text-[11px] text-arena-muted">
              Generated from simulation data directly (no LLM API key configured).
            </p>
          )}
        </div>
      )}
      {!commentary.data && !commentary.isPending && (
        <p className="text-sm text-arena-muted">Pick a commentary style to have it explain this result.</p>
      )}
    </div>
  )
}
