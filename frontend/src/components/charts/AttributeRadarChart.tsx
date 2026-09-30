import {
  PolarAngleAxis,
  PolarGrid,
  PolarRadiusAxis,
  Radar,
  RadarChart,
  ResponsiveContainer,
  Tooltip,
} from 'recharts'
import { ATTRIBUTE_LABELS, ATTRIBUTE_NAMES, type CombatAttributes } from '../../types/animal'

export function AttributeRadarChart({
  nameA,
  nameB,
  attributesA,
  attributesB,
}: {
  nameA: string
  nameB: string
  attributesA: CombatAttributes
  attributesB: CombatAttributes
}) {
  const data = ATTRIBUTE_NAMES.map((name) => ({
    attribute: ATTRIBUTE_LABELS[name],
    [nameA]: attributesA[name],
    [nameB]: attributesB[name],
  }))

  return (
    <div className="h-72 w-full sm:h-80">
      <ResponsiveContainer width="100%" height="100%">
        <RadarChart data={data} outerRadius="70%">
          <PolarGrid stroke="#2a2a38" />
          <PolarAngleAxis dataKey="attribute" tick={{ fill: '#8b8899', fontSize: 11 }} />
          <PolarRadiusAxis angle={30} domain={[0, 100]} tick={{ fill: '#8b8899', fontSize: 9 }} />
          <Radar name={nameA} dataKey={nameA} stroke="#3ea6ff" fill="#3ea6ff" fillOpacity={0.28} />
          <Radar name={nameB} dataKey={nameB} stroke="#ff4d6d" fill="#ff4d6d" fillOpacity={0.28} />
          <Tooltip
            contentStyle={{ background: '#14141c', border: '1px solid #2a2a38', borderRadius: 8, fontSize: 12 }}
            labelStyle={{ color: '#e8e6f0' }}
          />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  )
}
