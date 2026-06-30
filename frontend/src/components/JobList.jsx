const PAGE_SIZE = 20
const SKELETON_ROWS = 7
// Column widths vary to look like real data
const SKELETON_COLS = [
  [75, 68, 55, 60, 80],
  [60, 45, 70, 50, 40],
  [80, 55, 48, 70, 35],
  [65, 70, 62, 45, 50],
  [55, 48, 75, 55, 45],
  [72, 60, 50, 65, 38],
  [68, 52, 65, 48, 42],
]

function SkeletonRow({ widths }) {
  return (
    <tr>
      {widths.map((w, i) => (
        <td key={i} className="skeleton-td">
          <div className="skeleton" style={{ height: 13, width: `${w}%`, borderRadius: 4 }} />
        </td>
      ))}
    </tr>
  )
}

function formatSalary(min, max) {
  if (!min && !max) return '—'
  const fmt = n => `$${Math.round(n / 1000)}k`
  if (min && max) return `${fmt(min)} – ${fmt(max)}`
  if (min) return `≥ ${fmt(min)}`
  return `≤ ${fmt(max)}`
}

export default function JobList({ jobs, total, page, onPageChange, roleFilter, onRoleChange, isLoading }) {
  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE))

  return (
    <div className="card">
      <div className="table-controls">
        <input
          className="input"
          type="text"
          placeholder="Filter by job title…"
          value={roleFilter}
          onChange={e => onRoleChange(e.target.value)}
          disabled={isLoading}
        />
        {isLoading
          ? <div className="skeleton" style={{ width: 120, height: 14 }} />
          : <span className="table-meta">{total.toLocaleString()} job{total !== 1 ? 's' : ''} in DB</span>
        }
      </div>

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
            {isLoading ? (
              SKELETON_COLS.slice(0, SKELETON_ROWS).map((widths, i) => (
                <SkeletonRow key={i} widths={widths} />
              ))
            ) : total === 0 ? (
              <tr>
                <td colSpan={5}>
                  <div className="table-empty">
                    No jobs yet.{' '}
                    <span className="text-muted">
                      Enter a keyword above and click <strong>Fetch Jobs</strong> to pull listings from Adzuna.
                    </span>
                  </div>
                </td>
              </tr>
            ) : jobs.length === 0 ? (
              <tr>
                <td colSpan={5} className="table-empty text-muted">No jobs match that filter.</td>
              </tr>
            ) : (
              jobs.map(job => (
                <tr key={job.id}>
                  <td>
                    <a href={job.url} target="_blank" rel="noopener noreferrer" className="job-link">
                      {job.title}
                    </a>
                  </td>
                  <td>{job.company ?? '—'}</td>
                  <td>{job.location ?? '—'}</td>
                  <td>{job.category ?? '—'}</td>
                  <td>{formatSalary(job.salary_min, job.salary_max)}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {!isLoading && totalPages > 1 && (
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
