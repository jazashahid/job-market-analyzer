import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from 'recharts'

// Approximate widths descend to suggest a real ranking
const SKELETON_WIDTHS = [88, 76, 68, 61, 55, 50, 45, 41, 37, 33]

function SkeletonBars() {
  return (
    <div className="skeleton-bars" style={{ padding: '8px 0' }}>
      {SKELETON_WIDTHS.map((w, i) => (
        <div key={i} className="skeleton-bar-row">
          <div className="skeleton skeleton-bar-label" style={{ width: 100, height: 13 }} />
          <div className="skeleton skeleton-bar-fill" style={{ width: `${w}%` }} />
        </div>
      ))}
    </div>
  )
}

function CustomTooltip({ active, payload }) {
  if (!active || !payload?.length) return null
  return (
    <div className="chart-tooltip">
      <div className="chart-tooltip-label">{payload[0].payload.skill_name}</div>
      <div className="chart-tooltip-value">{payload[0].value} job mentions</div>
    </div>
  )
}

export default function SkillsBarChart({ skills, isLoading }) {
  if (isLoading) return <SkeletonBars />

  if (!skills.length) {
    return (
      <div className="chart-empty">
        <span style={{ fontSize: 28, opacity: 0.25 }}>◫</span>
        <p>No skills data yet.</p>
        <p className="text-muted">Fetch job listings to extract trending skills.</p>
      </div>
    )
  }

  return (
    <ResponsiveContainer width="100%" height={380}>
      <BarChart
        layout="vertical"
        data={skills.slice(0, 15)}
        margin={{ top: 4, right: 28, bottom: 4, left: 0 }}
      >
        <CartesianGrid strokeDasharray="3 3" stroke="#EDE9E4" horizontal={false} />
        <XAxis
          type="number"
          tick={{ fontSize: 11, fill: '#999' }}
          axisLine={false}
          tickLine={false}
        />
        <YAxis
          type="category"
          dataKey="skill_name"
          width={108}
          tick={{ fontSize: 12, fill: '#555' }}
          axisLine={false}
          tickLine={false}
        />
        <Tooltip content={<CustomTooltip />} cursor={{ fill: '#F3F0EB' }} />
        <Bar dataKey="count" fill="#7FA882" radius={[0, 5, 5, 0]} maxBarSize={18} />
      </BarChart>
    </ResponsiveContainer>
  )
}
