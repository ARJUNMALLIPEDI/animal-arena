import { useQuery } from '@tanstack/react-query'
import { fetchDashboard } from '../api/stats'
import { fetchMatchupHistory } from '../api/matchups'
import { LoadingSpinner } from '../components/common/LoadingSpinner'
import { TopAnimalsChart } from '../components/charts/TopAnimalsChart'

export function Dashboard() {
  const { data: dashboard, isLoading } = useQuery({ queryKey: ['dashboard'], queryFn: fetchDashboard })
  const { data: history } = useQuery({ queryKey: ['matchup-history'], queryFn: () => fetchMatchupHistory(15) })

  return (
    <div className="mx-auto max-w-5xl px-4 py-8 sm:px-6">
      <div className="mb-6 text-center">
        <h1 className="font-display text-4xl text-arena-text sm:text-5xl">Statistics Dashboard</h1>
        <p className="mt-2 text-sm text-arena-muted">Aggregated across every matchup simulated this session.</p>
      </div>

      {isLoading && <LoadingSpinner label="Loading stats..." />}

      {dashboard && (
        <>
          <div className="mb-8 grid grid-cols-3 gap-3">
            <StatTile label="Matchups Simulated" value={dashboard.total_matchups.toLocaleString()} />
            <StatTile label="Tournaments Run" value={dashboard.total_tournaments.toLocaleString()} />
            <StatTile label="Total Encounters" value={dashboard.total_simulations_run.toLocaleString()} />
          </div>

          {dashboard.most_simulated_animals.length > 0 && (
            <div className="mb-8 rounded-2xl border border-arena-border bg-arena-panel p-4 sm:p-6">
              <h4 className="mb-3 text-xs font-semibold uppercase tracking-widest text-arena-muted">
                Win Rate by Most-Simulated Animal
              </h4>
              <TopAnimalsChart data={dashboard.most_simulated_animals} />
            </div>
          )}

          {dashboard.total_matchups === 0 && (
            <p className="text-center text-sm text-arena-muted">
              No matchups yet — head to the Arena and simulate one to populate the dashboard.
            </p>
          )}
        </>
      )}

      {history && history.length > 0 && (
        <div className="rounded-2xl border border-arena-border bg-arena-panel p-4 sm:p-6">
          <h4 className="mb-3 text-xs font-semibold uppercase tracking-widest text-arena-muted">Recent Matchups</h4>
          <ul className="divide-y divide-arena-border">
            {history.map((m) => (
              <li key={m.id} className="flex items-center justify-between py-2 text-sm">
                <span className="text-arena-text">
                  {m.animal_a_id.replace(/_/g, ' ')} vs {m.animal_b_id.replace(/_/g, ' ')}
                </span>
                <span className="text-arena-muted">
                  {m.win_pct_a.toFixed(0)}% / {m.win_pct_b.toFixed(0)}% · {m.environment_id.replace('_', ' ')}
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}

function StatTile({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-arena-border bg-arena-panel py-4 text-center">
      <p className="font-display text-2xl text-arena-ember sm:text-3xl">{value}</p>
      <p className="mt-1 text-[10px] uppercase tracking-wider text-arena-muted">{label}</p>
    </div>
  )
}
