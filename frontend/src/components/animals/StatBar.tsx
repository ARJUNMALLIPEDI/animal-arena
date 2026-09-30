export function StatBar({ label, value, max = 100 }: { label: string; value: number; max?: number }) {
  const pct = Math.max(0, Math.min(100, (value / max) * 100))
  return (
    <div>
      <div className="mb-1 flex items-center justify-between text-xs">
        <span className="text-arena-muted">{label}</span>
        <span className="font-mono text-arena-text">{value.toFixed(0)}</span>
      </div>
      <div className="h-1.5 w-full overflow-hidden rounded-full bg-arena-border">
        <div
          className="h-full rounded-full bg-gradient-to-r from-arena-ember-dark to-arena-ember transition-all duration-700"
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  )
}

/** A two-sided bar for comparing the same attribute across two animals,
 * used on the matchup result screen. */
export function ComparisonStatBar({
  label,
  valueA,
  valueB,
  max = 100,
}: {
  label: string
  valueA: number
  valueB: number
  max?: number
}) {
  const pctA = Math.max(0, Math.min(100, (valueA / max) * 100))
  const pctB = Math.max(0, Math.min(100, (valueB / max) * 100))
  const aFavored = valueA > valueB
  const bFavored = valueB > valueA

  return (
    <div className="grid grid-cols-[1fr_auto_1fr] items-center gap-3">
      <div className="flex items-center justify-end gap-2">
        <span className={aFavored ? 'font-mono text-sm font-semibold text-corner-a' : 'font-mono text-sm text-arena-muted'}>
          {valueA.toFixed(0)}
        </span>
        <div className="h-1.5 w-24 overflow-hidden rounded-full bg-arena-border sm:w-32">
          <div
            className="ml-auto h-full rounded-full bg-corner-a transition-all duration-700"
            style={{ width: `${pctA}%` }}
          />
        </div>
      </div>
      <span className="w-20 text-center text-[11px] font-medium uppercase tracking-wider text-arena-muted">{label}</span>
      <div className="flex items-center gap-2">
        <div className="h-1.5 w-24 overflow-hidden rounded-full bg-arena-border sm:w-32">
          <div className="h-full rounded-full bg-corner-b transition-all duration-700" style={{ width: `${pctB}%` }} />
        </div>
        <span className={bFavored ? 'font-mono text-sm font-semibold text-corner-b' : 'font-mono text-sm text-arena-muted'}>
          {valueB.toFixed(0)}
        </span>
      </div>
    </div>
  )
}
