import { useState } from 'react'

const PAGE_SIZE = 20

function formatSalary(min, max) {
  if (!min && !max) return '—'
  const fmt = n => `$${Math.round(n / 1000)}k`
  if (min && max) return `${fmt(min)} – ${fmt(max)}`
  if (min) return `≥ ${fmt(min)}`
  return `≤ ${fmt(max)}`
}

export default function JobList({ jobs, total, page, onPageChange, isLoading }) {
  const [filter, setFilter] = useState('')

  const filtered = filter
    ? jobs.filter(j =>
        j.title.toLowerCase().includes(filter.toLowerCase()) ||
        (j.company ?? '').toLowerCase().includes(filter.toLowerCase()) ||
        (j.location ?? '').toLowerCase().includes(filter.toLowerCase())
      )
    : jobs

  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE))

  return (
    <div className="card">
      <div className="table-controls">
        <input
          className="input"
          type="text"
          placeholder="Filter by title, company, or location…"
          value={filter}
          onChange={e => setFilter(e.target.value)}
        />
        <span className="table-meta">
          {total.toLocaleString()} job{total !== 1 ? 's' : ''} in DB
        </span>
      </div>

      {isLoading ? (
        <div className="table-empty">Loading…</div>
      ) : total === 0 ? (
        <div className="table-empty">
          No jobs yet.{' '}
          <span className="text-muted">
            Enter a keyword above and click <strong>Fetch Jobs</strong> to pull listings from Adzuna.
          </span>
        </div>
      ) : filtered.length === 0 ? (
        <div className="table-empty text-muted">No jobs match that filter.</div>
      ) : (
        <div className="table-wrap">
          <table className="table">
            <thead>
              <tr>
                <th>Title</th>
                <th>Company</th>
                <th>Location</th>
                <th>Category</th>
                <th>Salary</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map(job => (
                <tr key={job.id}>
                  <td>
                    <a
                      href={job.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="job-link"
                    >
                      {job.title}
                    </a>
                  </td>
                  <td>{job.company ?? '—'}</td>
                  <td>{job.location ?? '—'}</td>
                  <td>{job.category ?? '—'}</td>
                  <td>{formatSalary(job.salary_min, job.salary_max)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {totalPages > 1 && (
        <div className="pagination">
          <button
            className="btn btn-ghost"
            onClick={() => onPageChange(page - 1)}
            disabled={page <= 1}
          >
            ← Prev
          </button>
          <span className="pagination-info">Page {page} of {totalPages}</span>
          <button
            className="btn btn-ghost"
            onClick={() => onPageChange(page + 1)}
            disabled={page >= totalPages}
          >
            Next →
          </button>
        </div>
      )}
    </div>
  )
}
