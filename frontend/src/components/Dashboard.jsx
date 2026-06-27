import SkillsBarChart from './SkillsBarChart.jsx'
import TrendLineChart from './TrendLineChart.jsx'

export default function Dashboard({ trendingSkills, skillHistory, totalJobs, isLoading }) {
  const topSkill = trendingSkills[0]?.skill_name ?? '—'
  const skillsTracked = trendingSkills.length

  return (
    <div>
      <div className="stat-row">
        {/* Featured card — top skill gets more visual weight */}
        <StatCard
          label="Top skill in demand"
          value={topSkill}
          featured
          isLoading={isLoading}
          skeletonWidth="45%"
          skeletonHeight={38}
        />
        <StatCard
          label="Jobs indexed"
          value={totalJobs.toLocaleString()}
          isLoading={isLoading}
          skeletonWidth="60%"
          skeletonHeight={22}
        />
        <StatCard
          label="Skills tracked"
          value={skillsTracked}
          isLoading={isLoading}
          skeletonWidth="50%"
          skeletonHeight={22}
        />
      </div>

      <div className="chart-row">
        <div className="card">
          <div className="card-title">Trending skills</div>
          <SkillsBarChart skills={trendingSkills} isLoading={isLoading} />
        </div>
        <div className="card">
          <div className="card-title">Frequency over time</div>
          <TrendLineChart history={skillHistory} isLoading={isLoading} />
        </div>
      </div>
    </div>
  )
}

function StatCard({ label, value, featured, isLoading, skeletonWidth, skeletonHeight }) {
  return (
    <div className={`card stat-card${featured ? ' stat-card--featured' : ''}`}>
      <div className="stat-label">{label}</div>
      {isLoading
        ? <div className="skeleton" style={{ height: skeletonHeight, width: skeletonWidth, marginTop: 6 }} />
        : <div className="stat-value">{value}</div>
      }
    </div>
  )
}
