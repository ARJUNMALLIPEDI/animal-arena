import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import type { AnimalWinRate } from '../../types/stats'

export function TopAnimalsChart({ data }: { data: AnimalWinRate[] }) {
  const chartData = [...data].sort((a, b) => b.win_pct - a.win_pct).map((d) => ({ ...d, name: d.common_name }))

  return (
    <div className="h-72 w-full sm:h-80">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={chartData} layout="vertical" margin={{ left: 24 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#2a2a38" horizontal={false} />
          <XAxis type="number" domain={[0, 100]} tick={{ fill: '#8b8899', fontSize: 11 }} unit="%" />
          <YAxis type="category" dataKey="name" tick={{ fill: '#e8e6f0', fontSize: 11 }} width={120} />
          <Tooltip
            contentStyle={{ background: '#14141c', border: '1px solid #2a2a38', borderRadius: 8, fontSize: 12 }}
            labelStyle={{ color: '#e8e6f0' }}
            formatter={(value, _name, item) => [
              `${value}% (${item.payload.wins}/${item.payload.total_matchups})`,
              'Win rate',
            ]}
          />
          <Bar dataKey="win_pct" radius={[0, 6, 6, 0]} fill="#ff5a2e" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
