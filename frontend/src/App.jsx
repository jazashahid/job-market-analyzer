import { useState, useEffect, useCallback } from 'react'
import Dashboard from './components/Dashboard.jsx'
import JobList from './components/JobList.jsx'
import ResumeAnalyzer from './components/ResumeAnalyzer.jsx'
import { fetchJobs, listJobs, getTrendingSkills, getSkillHistory } from './services/api.js'

export default function App() {
  const [keyword, setKeyword] = useState('software engineer')
  const [trendingSkills, setTrendingSkills] = useState([])
  const [skillHistory, setSkillHistory] = useState([])
  const [jobs, setJobs] = useState([])
  const [totalJobs, setTotalJobs] = useState(0)
  const [jobPage, setJobPage] = useState(1)
  const [isLoading, setIsLoading] = useState(true)
  const [isFetching, setIsFetching] = useState(false)
  const [fetchStatus, setFetchStatus] = useState(null)
  const [error, setError] = useState(null)

  const loadDashboard = useCallback(async () => {
    const [skillsRes, historyRes] = await Promise.all([
      getTrendingSkills(20),
      getSkillHistory(5),
    ])
    setTrendingSkills(skillsRes.data.skills)
    setSkillHistory(historyRes.data.history)
  }, [])

  const loadJobs = useCallback(async (page = 1) => {
    const res = await listJobs(page, 20)
    setJobs(res.data.jobs)
    setTotalJobs(res.data.total)
  }, [])

  useEffect(() => {
    const init = async () => {
      setIsLoading(true)
      try {
        await Promise.all([loadDashboard(), loadJobs(1)])
      } catch {
        // DB is empty on first launch — charts will show their empty state
      } finally {
        setIsLoading(false)
      }
    }
    init()
  }, [loadDashboard, loadJobs])

  const handleFetch = async () => {
    if (!keyword.trim()) return
    setIsFetching(true)
    setFetchStatus(null)
    setError(null)
    try {
      const res = await fetchJobs(keyword.trim())
      setFetchStatus(res.data)
      setJobPage(1)
      await Promise.all([loadDashboard(), loadJobs(1)])
    } catch (err) {
      setError(err.response?.data?.detail ?? 'Could not reach the Adzuna API. Check your credentials and network.')
    } finally {
      setIsFetching(false)
    }
  }

  const handlePageChange = async (newPage) => {
    setJobPage(newPage)
    await loadJobs(newPage)
  }

  return (
    <div className="app">
      <header className="header">
        <div className="header-brand">
          <span className="header-logo">◈</span>
          <div>
            <div className="header-title">Job Market Analyzer</div>
            <div className="header-subtitle">Skill trends · Powered by Adzuna + Claude</div>
          </div>
        </div>

        <div className="header-controls">
          <input
            className="input header-search"
            type="text"
            placeholder="Keyword (e.g. data scientist, frontend engineer)"
            value={keyword}
            onChange={e => setKeyword(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && !isFetching && handleFetch()}
          />
          <button
            className="btn btn-primary"
            onClick={handleFetch}
            disabled={isFetching || !keyword.trim()}
          >
            {isFetching ? 'Fetching…' : 'Fetch Jobs'}
          </button>
        </div>
      </header>

      <main className="main">
        {error && <div className="banner banner-error">{error}</div>}

        {fetchStatus && (
          <div className="banner banner-success">
            {fetchStatus.inserted} new jobs added &nbsp;·&nbsp;
            {fetchStatus.skipped} already in DB &nbsp;·&nbsp;
            {fetchStatus.skills_extracted} skills extracted
          </div>
        )}

        <section className="section">
          <div className="section-label">Trends</div>
          <Dashboard
            trendingSkills={trendingSkills}
            skillHistory={skillHistory}
            totalJobs={totalJobs}
            isLoading={isLoading}
          />
        </section>

        <section className="section">
          <div className="section-label">Job Listings</div>
          <JobList
            jobs={jobs}
            total={totalJobs}
            page={jobPage}
            onPageChange={handlePageChange}
            isLoading={isLoading}
          />
        </section>

        <section className="section">
          <div className="section-label">Resume Analyzer</div>
          <ResumeAnalyzer />
        </section>
      </main>
    </div>
  )
}
