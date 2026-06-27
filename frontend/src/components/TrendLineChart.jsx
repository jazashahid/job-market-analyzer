import {
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer,
} from 'recharts'

const COLORS = ['#7FA882', '#C4A09D', '#A89FC0', '#C4A96E', '#82B4C8', '#A5C9B8', '#D4B4A5']

function SkeletonChart() {
  return (
    <div className="skeleton-chart" style={{ height: 380 }}>
      {[...Array(5)].map((_, i) => (
        <div key={i} className="skeleton skeleton-grid-line" />
      ))}
      <div className="skeleton-x-labels">
        {[70, 60, 55, 65, 50].map((w, i) => (
          <div key={i} className="skeleton" style={{ width: w, height: 11 }} />
        ))}
      </div>
      <div style={{ display: 'flex', gap: 16, marginTop: 20 }}>
        {[50, 62, 44].map((w, i) => (
          <div key={i} className="skeleton" style={{ width: w, height: 11 }} />
        ))}
      </div>
    </div>
  )
}

function pivotHistory(history) {
  const byDate = {}
  const skillSet = new Set()
  history.forEach(({ date, skill_name, count }) => {
    if (!byDate[date]) byDate[date] = { date }
    byDate[date][skill_name] = count
    skillSet.add(skill_name)
  })
  const data = Object.values(byDate).sort((a, b) => a.date.localeCompare(b.date))
  return { data, skills: [...skillSet] }
}

function CustomTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null
  return (
    <div className="chart-tooltip">
      <div className="chart-tooltip-label">{label}</div>
      {payload.map(p => (
        <div key={p.dataKey} className="chart-tooltip-value" style={{ color: p.color }}>
          {p.dataKey}: {p.value}
        </div>
      ))}
    </div>
  )
}

export default function TrendLineChart({ history, isLoading }) {
  if (isLoading) return <SkeletonChart />

  if (!history.length) {
    return (
      <div className="chart-empty">
        <span style={{ fontSize: 28, opacity: 0.25 }}>◬</span>
        <p>No history yet.</p>
        <p className="text-muted">Trends build as you fetch jobs across multiple days.</p>
      </div>
    )
  }

  const { data, skills } = pivotHistory(history)

  return (
    <ResponsiveContainer width="100%" height={380}>
      <LineChart data={data} margin={{ top: 12, right: 36, bottom: 28, left: 16 }}>
        <CartesianGrid strokeDasharray="0" stroke="#F0EDE8" horizontal={true} vertical={false} />
        <XAxis
          dataKey="date"
          tick={{ fontSize: 10, fill: '#A0A0A0' }}
          axisLine={false}
          tickLine={false}
          tickMargin={8}
          label={{ value: 'Date', position: 'insideBottom', offset: -14, fontSize: 10, fill: '#A0A0A0' }}
        />
        <YAxis
          tick={{ fontSize: 10, fill: '#A0A0A0' }}
          axisLine={false}
          tickLine={false}
          width={32}
          label={{ value: 'Mentions', angle: -90, position: 'insideLeft', offset: 14, fontSize: 10, fill: '#A0A0A0' }}
        />
        <Tooltip content={<CustomTooltip />} />
        <Legend
          wrapperStyle={{ fontSize: 11, paddingTop: 14, color: '#A0A0A0' }}
          iconType="circle"
          iconSize={7}
        />
        {skills.map((skill, i) => (
          <Line
            key={skill}
            type="monotone"
            dataKey={skill}
            stroke={COLORS[i % COLORS.length]}
            strokeWidth={2}
            dot={{ r: 1.5, fill: COLORS[i % COLORS.length], strokeWidth: 0 }}
            activeDot={{ r: 4, strokeWidth: 1.5, stroke: '#fff' }}
            connectNulls={true}
          />
        ))}
      </LineChart>
    </ResponsiveContainer>
  )
}
