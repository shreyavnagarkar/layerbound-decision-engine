import { useState } from 'react'
import TriStateField from './TriStateField.jsx'

const emptyCandidate = {
  candidate_id: '',
  job_id: '',
  has_driving_licence: null,
  willing_to_work_shifts: null,
  can_commute: null,
  expected_salary: '',
  notice_period_days: '',
  fit_score: '',
}

function CandidateForm({ jobs, onEvaluate, evaluating, error }) {
  const [form, setForm] = useState(emptyCandidate)

  const update = (field, value) => setForm((prev) => ({ ...prev, [field]: value }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    const payload = {
      candidate_id: form.candidate_id,
      job_id: form.job_id,
      has_driving_licence: form.has_driving_licence,
      willing_to_work_shifts: form.willing_to_work_shifts,
      can_commute: form.can_commute,
      expected_salary: form.expected_salary === '' ? null : Number(form.expected_salary),
      notice_period_days:
        form.notice_period_days === '' ? null : Number(form.notice_period_days),
      fit_score: form.fit_score === '' ? null : Number(form.fit_score),
    }
    await onEvaluate(payload)
  }

  return (
    <div className="panel">
      <h2>Evaluate a candidate</h2>
      <p className="panel-hint">
        Enter what the candidate told you. Fields left as &ldquo;Not specified&rdquo;
        or blank are scored as missing information, not assumed in their favour.
      </p>

      <form onSubmit={handleSubmit} className="form-grid">
        <label className="field">
          <span>Candidate ID *</span>
          <input
            required
            value={form.candidate_id}
            onChange={(e) => update('candidate_id', e.target.value)}
            placeholder="CAND-001"
          />
        </label>

        <label className="field">
          <span>Job *</span>
          {jobs.length > 0 ? (
            <select
              required
              value={form.job_id}
              onChange={(e) => update('job_id', e.target.value)}
            >
              <option value="">Select a job…</option>
              {jobs.map((j) => (
                <option key={j.job_id} value={j.job_id}>
                  {j.job_id}
                  {j.title ? ` — ${j.title}` : ''}
                </option>
              ))}
            </select>
          ) : (
            <input
              required
              value={form.job_id}
              onChange={(e) => update('job_id', e.target.value)}
              placeholder="No jobs set up yet — type a job ID"
            />
          )}
        </label>

        <TriStateField
          label="Has driving licence?"
          name="has_driving_licence"
          value={form.has_driving_licence}
          onChange={(v) => update('has_driving_licence', v)}
        />
        <TriStateField
          label="Willing to work shifts?"
          name="willing_to_work_shifts"
          value={form.willing_to_work_shifts}
          onChange={(v) => update('willing_to_work_shifts', v)}
        />
        <TriStateField
          label="Can commute to the role?"
          name="can_commute"
          value={form.can_commute}
          onChange={(v) => update('can_commute', v)}
        />

        <label className="field">
          <span>Expected salary (£)</span>
          <input
            type="number"
            min="0"
            value={form.expected_salary}
            onChange={(e) => update('expected_salary', e.target.value)}
            placeholder="Leave blank if unknown"
          />
        </label>

        <label className="field">
          <span>Notice period (days)</span>
          <input
            type="number"
            min="0"
            value={form.notice_period_days}
            onChange={(e) => update('notice_period_days', e.target.value)}
            placeholder="Leave blank if unknown"
          />
        </label>

        <label className="field">
          <span>General fit score (1–10)</span>
          <input
            type="number"
            min="1"
            max="10"
            value={form.fit_score}
            onChange={(e) => update('fit_score', e.target.value)}
            placeholder="Recruiter's judgement"
          />
        </label>

        {error && <p className="error-text">{error}</p>}

        <button type="submit" disabled={evaluating}>
          {evaluating ? 'Evaluating…' : 'Evaluate candidate'}
        </button>
      </form>
    </div>
  )
}

export default CandidateForm
