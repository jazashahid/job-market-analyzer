import {
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer,
} from 'recharts'

const COLORS = ['#7FA882', '#C4A09D', '#A89FC0', '#C4A96E', '#82B4C8', '#A5C9B8', '#D4B4A5']

function SkeletonChart() {
  return (
    <div className="skeleton-chart" style={{ height: 380 }}>
      {/* Fake horizontal grid lines */}
      {[...Array(5)].map((_, i) => (
        <div key={i} className="skeleton skeleton-grid-line" />
      ))}
      {/* Fake x-axis labels */}
      <div className="skeleton-x-labels">
        {[70, 60, 55, 65, 50].map((w, i) => (
          <div key={i} className="skeleton" style={{ width: w, height: 11 }} />
        ))}
      </div>
      {/* Fake legend */}
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
      <LineChart data={data} margin={{ top: 4, right: 28, bottom: 4, left: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#EDE9E4" />
        <XAxis
          dataKey="date"
          tick={{ fontSize: 11, fill: '#999' }}
          axisLine={false}
          tickLine={false}
        />
        <YAxis
          tick={{ fontSize: 11, fill: '#999' }}
          axisLine={false}
          tickLine={false}
          width={32}
        />
        <Tooltip
          contentStyle={{
            background: '#fff',
            border: '1px solid #E4DDD6',
            borderRadius: 8,
            fontSize: 12,
            boxShadow: '0 4px 12px rgba(0,0,0,0.08)',
          }}
        />
        <Legend
          wrapperStyle={{ fontSize: 11, paddingTop: 14, color: '#555' }}
          iconType="circle"
          iconSize={8}
        />
        {skills.map((skill, i) => (
          <Line
            key={skill}
            type="monotone"
            dataKey={skill}
            stroke={COLORS[i % COLORS.length]}
            strokeWidth={2}
            dot={{ r: 3, fill: COLORS[i % COLORS.length], strokeWidth: 0 }}
            activeDot={{ r: 5, strokeWidth: 0 }}
          />
        ))}
      </LineChart>
    </ResponsiveContainer>
  )
}
