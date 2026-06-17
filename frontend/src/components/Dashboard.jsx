import SkillsBarChart from './SkillsBarChart.jsx'
import TrendLineChart from './TrendLineChart.jsx'

export default function Dashboard({ trendingSkills, skillHistory, totalJobs, isLoading }) {
  const topSkill = trendingSkills[0]?.skill_name ?? '—'
  const skillsTracked = trendingSkills.length

  return (
    <div>
      <div className="stat-row">
        <StatCard
          label="Total Jobs"
          value={isLoading ? '…' : totalJobs.toLocaleString()}
          accent="sage"
        />
        <StatCard
          label="Top Skill"
          value={isLoading ? '…' : topSkill}
          accent="rose"
        />
        <StatCard
          label="Skills Tracked"
          value={isLoading ? '…' : skillsTracked}
          accent="lavender"
        />
      </div>

      <div className="chart-row">
        <div className="card">
          <div className="card-title">Trending Skills</div>
          <SkillsBarChart skills={trendingSkills} isLoading={isLoading} />
        </div>
        <div className="card">
          <div className="card-title">Skill Frequency Over Time</div>
          <TrendLineChart history={skillHistory} isLoading={isLoading} />
        </div>
      </div>
    </div>
  )
}

function StatCard({ label, value, accent }) {
  return (
    <div className={`card stat-card stat-card--${accent}`}>
      <div className="stat-label">{label}</div>
      <div className="stat-value">{value}</div>
    </div>
  )
}
