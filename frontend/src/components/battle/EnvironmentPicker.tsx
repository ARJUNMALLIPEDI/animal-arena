import clsx from 'clsx'
import { useEnvironments } from '../../hooks/useAnimals'

const ENV_ICON: Record<string, string> = {
  savanna: '🌾',
  forest: '🌲',
  desert: '🏜️',
  arctic: '❄️',
  ocean: '🌊',
  mountain: '⛰️',
  open_plains: '🏞️',
}

export function EnvironmentPicker({ value, onChange }: { value: string; onChange: (id: string) => void }) {
  const { data: environments, isLoading } = useEnvironments()

  if (isLoading || !environments) {
    return <div className="h-16 animate-pulse rounded-xl bg-arena-panel" />
  }

  return (
    <div className="flex flex-wrap justify-center gap-2">
      {environments.map((env) => (
        <button
          key={env.id}
          onClick={() => onChange(env.id)}
          title={env.description}
          className={clsx(
            'flex items-center gap-1.5 rounded-full border px-3 py-1.5 text-sm transition-colors',
            value === env.id
              ? 'border-arena-ember bg-arena-ember/15 text-arena-ember'
              : 'border-arena-border bg-arena-panel text-arena-muted hover:text-arena-text',
          )}
        >
          <span>{ENV_ICON[env.id] ?? '🌍'}</span>
          {env.name}
        </button>
      ))}
    </div>
  )
}
