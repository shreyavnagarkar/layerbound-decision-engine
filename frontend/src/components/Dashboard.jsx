import { useEffect, useState } from 'react'
import { api } from '../api/client.js'

function Dashboard({ jobs, refreshKey }) {
  const [jobId, setJobId] = useState('')
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setError('')
    api
      .getDashboard(jobId || undefined)
      .then((data) => {
        if (!cancelled) setStats(data)
      })
      .catch((err) => {
        if (!cancelled) setError(err.message)
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [jobId, refreshKey])

  return (
    <div className="panel">
      <div className="dashboard-header">
        <h2>Dashboard</h2>
        <label className="field inline-field">
          <span>Filter by job</span>
          <select value={jobId} onChange={(e) => setJobId(e.target.value)}>
            <option value="">All jobs</option>
            {jobs.map((j) => (
              <option key={j.job_id} value={j.job_id}>
                {j.job_id}
                {j.title ? ` — ${j.title}` : ''}
              </option>
            ))}
          </select>
        </label>
      </div>

      {loading && <p>Loading…</p>}
      {error && <p className="error-text">{error}</p>}

      {stats && !loading && (
        <>
          <div className="stat-grid">
            <div className="stat-tile">
              <span className="stat-value">{stats.total_evaluations}</span>
              <span className="stat-label">Candidates evaluated</span>
            </div>
            <div className="stat-tile">
              <span className="stat-value">{stats.percent_rejected}%</span>
              <span className="stat-label">Rejected</span>
            </div>
            <div className="stat-tile">
              <span className="stat-value">{stats.percent_hard_rejected}%</span>
              <span className="stat-label">Auto-rejected (hard rule)</span>
            </div>
            <div className="stat-tile">
              <span className="stat-value">
                {stats.average_score !== null ? stats.average_score : '—'}
              </span>
              <span className="stat-label">Average score</span>
            </div>
          </div>

          <div className="dashboard-columns">
            <div>
              <h3>Decisions</h3>
              <ul className="decision-breakdown">
                <li>
                  <span className="dot decision-submit" /> Submit —{' '}
                  {stats.decision_breakdown.submit}
                </li>
                <li>
                  <span className="dot decision-review" /> Review —{' '}
                  {stats.decision_breakdown.review}
                </li>
                <li>
                  <span className="dot decision-reject" /> Reject —{' '}
                  {stats.decision_breakdown.reject}
                </li>
              </ul>
            </div>

            <div>
              <h3>Most common rejection reasons</h3>
              {stats.top_rejection_reasons.length === 0 ? (
                <p className="panel-hint">No rejections yet.</p>
              ) : (
                <ol className="rejection-reasons">
                  {stats.top_rejection_reasons.map((r) => (
                    <li key={r.reason}>
                      {r.reason} <span className="reason-count">×{r.count}</span>
                    </li>
                  ))}
                </ol>
              )}
            </div>
          </div>

          <h3>Recent evaluations</h3>
          {stats.recent_evaluations.length === 0 ? (
            <p className="panel-hint">Nothing evaluated yet.</p>
          ) : (
            <div className="table-wrap">
              <table className="evaluations-table">
                <thead>
                  <tr>
                    <th>Candidate</th>
                    <th>Job</th>
                    <th>Score</th>
                    <th>Decision</th>
                    <th>Submitted</th>
                  </tr>
                </thead>
                <tbody>
                  {stats.recent_evaluations.map((ev) => (
                    <tr key={ev.id}>
                      <td>{ev.candidate_id}</td>
                      <td>{ev.job_id}</td>
                      <td>{ev.score}</td>
                      <td>
                        <span className={`decision-badge decision-${ev.decision.toLowerCase()}`}>
                          {ev.decision}
                        </span>
                      </td>
                      <td>{new Date(ev.created_at).toLocaleString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </>
      )}
    </div>
  )
}

export default Dashboard
