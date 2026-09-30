import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'

export function WinDistributionChart({
  nameA,
  nameB,
  winsA,
  winsB,
  draws,
}: {
  nameA: string
  nameB: string
  winsA: number
  winsB: number
  draws: number
}) {
  const data = [
    { name: nameA, value: winsA, fill: '#3ea6ff' },
    { name: nameB, value: winsB, fill: '#ff4d6d' },
    ...(draws > 0 ? [{ name: 'Draws', value: draws, fill: '#8b8899' }] : []),
  ]

  return (
    <div className="h-56 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} layout="vertical" margin={{ left: 24 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#2a2a38" horizontal={false} />
          <XAxis type="number" tick={{ fill: '#8b8899', fontSize: 11 }} />
          <YAxis type="category" dataKey="name" tick={{ fill: '#e8e6f0', fontSize: 12 }} width={110} />
          <Tooltip
            contentStyle={{ background: '#14141c', border: '1px solid #2a2a38', borderRadius: 8, fontSize: 12 }}
            labelStyle={{ color: '#e8e6f0' }}
            formatter={(value) => Number(value).toLocaleString()}
          />
          <Bar dataKey="value" radius={[0, 6, 6, 0]}>
            {data.map((entry) => (
              <Cell key={entry.name} fill={entry.fill} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
