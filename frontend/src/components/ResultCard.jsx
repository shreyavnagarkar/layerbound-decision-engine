const DECISION_CLASS = {
  Submit: 'decision-submit',
  Review: 'decision-review',
  Reject: 'decision-reject',
}

function ResultCard({ result }) {
  if (!result) return null

  return (
    <div className={`panel result-card ${DECISION_CLASS[result.decision] || ''}`}>
      <div className="result-header">
        <div>
          <h2>{result.candidate_id}</h2>
          <span className="result-subtitle">Job: {result.job_id}</span>
        </div>
        <div className="result-badges">
          <span className="score-badge">{result.score}</span>
          <span className={`decision-badge ${DECISION_CLASS[result.decision] || ''}`}>
            {result.decision}
          </span>
        </div>
      </div>

      <p className="result-summary">{result.summary}</p>

      {result.issues?.length > 0 && (
        <div className="result-section">
          <h3>Issues</h3>
          <ul>
            {result.issues.map((issue) => (
              <li key={issue}>{issue}</li>
            ))}
          </ul>
        </div>
      )}

      {result.missing_info?.length > 0 && (
        <div className="result-section">
          <h3>Missing information</h3>
          <ul>
            {result.missing_info.map((field) => (
              <li key={field}>{field.replaceAll('_', ' ')}</li>
            ))}
          </ul>
        </div>
      )}

      <div className="result-section">
        <h3>Next steps</h3>
        <ul>
          {result.next_steps.map((step) => (
            <li key={step}>{step}</li>
          ))}
        </ul>
      </div>

      {result.score_breakdown?.length > 0 && (
        <details className="result-section">
          <summary>Score breakdown</summary>
          <table className="breakdown-table">
            <tbody>
              {result.score_breakdown.map((item, idx) => (
                <tr key={idx}>
                  <td>{item.label}</td>
                  <td className={item.points < 0 ? 'points-negative' : 'points-positive'}>
                    {item.points > 0 ? '+' : ''}
                    {item.points}
                  </td>
                  <td className="breakdown-note">{item.note}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </details>
      )}
    </div>
  )
}

export default ResultCard
