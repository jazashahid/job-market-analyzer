import { useState, useEffect, useCallback } from 'react'
import Dashboard from './components/Dashboard.jsx'
import JobList from './components/JobList.jsx'
import ResumeAnalyzer from './components/ResumeAnalyzer.jsx'
import { fetchJobs, listJobs, getTrendingSkills, getSkillHistory } from './services/api.js'

export default function App() {
  const [keyword, setKeyword] = useState('software engineer')
  const [pages, setPages] = useState(3)
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
      const res = await fetchJobs(keyword.trim(), 'us', pages)
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
      <div className="topbar">
        <header className="header">
          <span className="header-wordmark">Job Market Analyzer</span>
        </header>

        <div className="toolbar">
          <div className="search-wrap">
            <svg className="search-icon" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
            </svg>
            <input
              className="input"
              type="text"
              placeholder="e.g. data scientist, frontend engineer"
              value={keyword}
              onChange={e => setKeyword(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && !isFetching && handleFetch()}
            />
          </div>
          <select
            className="input pages-select"
            value={pages}
            onChange={e => setPages(Number(e.target.value))}
            disabled={isFetching}
          >
            <option value={1}>1 page · 50 jobs</option>
            <option value={2}>2 pages · 100 jobs</option>
            <option value={3}>3 pages · 150 jobs</option>
            <option value={5}>5 pages · 250 jobs</option>
            <option value={10}>10 pages · 500 jobs</option>
          </select>
          <button
            className="btn btn-primary"
            onClick={handleFetch}
            disabled={isFetching || !keyword.trim()}
          >
            {isFetching ? 'Fetching…' : 'Fetch Jobs'}
          </button>
        </div>
      </div>

      <main className="main">
        {error && <div className="banner banner-error">{error}</div>}

        {fetchStatus && (
          <div className="banner banner-success">
            {fetchStatus.inserted} new jobs added &nbsp;·&nbsp;
            {fetchStatus.skipped} already in DB &nbsp;·&nbsp;
            {fetchStatus.skills_extracted} skills extracted &nbsp;·&nbsp;
            {fetchStatus.pages_fetched} page{fetchStatus.pages_fetched !== 1 ? 's' : ''} fetched
          </div>
        )}

        <section className="section">
          <Dashboard
            trendingSkills={trendingSkills}
            skillHistory={skillHistory}
            totalJobs={totalJobs}
            isLoading={isLoading}
          />
        </section>

        <section className="section">
          <div className="section-label">Job listings</div>
          <JobList
            jobs={jobs}
            total={totalJobs}
            page={jobPage}
            onPageChange={handlePageChange}
            isLoading={isLoading}
          />
        </section>

        <section className="section">
          <div className="section-label">Resume analyzer</div>
          <ResumeAnalyzer />
        </section>
      </main>
    </div>
  )
}
