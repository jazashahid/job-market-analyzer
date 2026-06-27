import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer,
} from 'recharts'

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
        margin={{ top: 12, right: 36, bottom: 12, left: 8 }}
      >
        <defs>
          <linearGradient id="barGradient" x1="0" y1="0" x2="1" y2="0">
            <stop offset="0%" stopColor="#7FA882" stopOpacity={1} />
            <stop offset="100%" stopColor="#B4D4B8" stopOpacity={0.6} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="0" stroke="#F0EDE8" horizontal={true} vertical={false} />
        <XAxis
          type="number"
          tick={{ fontSize: 11, fill: '#A0A0A0' }}
          axisLine={false}
          tickLine={false}
          tickMargin={4}
        />
        <YAxis
          type="category"
          dataKey="skill_name"
          width={92}
          tick={{ fontSize: 11, fill: '#555' }}
          axisLine={false}
          tickLine={false}
          tickMargin={6}
        />
        <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(127,168,130,0.07)' }} />
        <Bar dataKey="count" fill="url(#barGradient)" radius={[0, 4, 4, 0]} maxBarSize={16} />
      </BarChart>
    </ResponsiveContainer>
  )
}
