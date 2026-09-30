import clsx from 'clsx'

export function LoadingSpinner({ label, className }: { label?: string; className?: string }) {
  return (
    <div className={clsx('flex flex-col items-center justify-center gap-3 py-10 text-arena-muted', className)}>
      <div className="h-8 w-8 animate-spin rounded-full border-2 border-arena-border border-t-arena-ember" />
      {label && <p className="text-sm">{label}</p>}
    </div>
  )
}
