import { useState } from 'react'

const emptyJob = {
  job_id: '',
  title: '',
  requires_driving_licence: false,
  requires_shift_flexibility: false,
  requires_commute: false,
  salary_min: 0,
  salary_max: 0,
  max_notice_days: 60,
  score_threshold_submit: 80,
  score_threshold_review: 50,
}

function JobForm({ jobs, onSave, saving, error }) {
  const [form, setForm] = useState(emptyJob)
  const [editingExisting, setEditingExisting] = useState(false)

  const update = (field, value) => setForm((prev) => ({ ...prev, [field]: value }))

  const loadJob = (jobId) => {
    if (!jobId) {
      setForm(emptyJob)
      setEditingExisting(false)
      return
    }
    const job = jobs.find((j) => j.job_id === jobId)
    if (job) {
      setForm(job)
      setEditingExisting(true)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    const ok = await onSave({
      ...form,
      salary_min: Number(form.salary_min),
      salary_max: Number(form.salary_max),
      max_notice_days: Number(form.max_notice_days),
      score_threshold_submit: Number(form.score_threshold_submit),
      score_threshold_review: Number(form.score_threshold_review),
    })
    if (ok) {
      setForm(emptyJob)
      setEditingExisting(false)
    }
  }

  return (
    <div className="panel">
      <h2>Job setup</h2>
      <p className="panel-hint">
        Define what this role requires before evaluating candidates against it.
        Every candidate submission references a job by its ID.
      </p>

      {jobs.length > 0 && (
        <label className="field">
          <span>Load existing job to edit</span>
          <select onChange={(e) => loadJob(e.target.value)} defaultValue="">
            <option value="">— New job —</option>
            {jobs.map((j) => (
              <option key={j.job_id} value={j.job_id}>
                {j.job_id}
                {j.title ? ` — ${j.title}` : ''}
              </option>
            ))}
          </select>
        </label>
      )}

      <form onSubmit={handleSubmit} className="form-grid">
        <label className="field">
          <span>Job ID *</span>
          <input
            required
            disabled={editingExisting}
            value={form.job_id}
            onChange={(e) => update('job_id', e.target.value)}
            placeholder="JOB-001"
          />
        </label>

        <label className="field">
          <span>Job title</span>
          <input
            value={form.title}
            onChange={(e) => update('title', e.target.value)}
            placeholder="Warehouse Operative"
          />
        </label>

        <fieldset className="field checkbox-group">
          <legend>Mandatory requirements (auto-reject if unmet)</legend>
          <label>
            <input
              type="checkbox"
              checked={form.requires_driving_licence}
              onChange={(e) => update('requires_driving_licence', e.target.checked)}
            />
            Requires driving licence
          </label>
          <label>
            <input
              type="checkbox"
              checked={form.requires_shift_flexibility}
              onChange={(e) => update('requires_shift_flexibility', e.target.checked)}
            />
            Requires shift flexibility
          </label>
          <label>
            <input
              type="checkbox"
              checked={form.requires_commute}
              onChange={(e) => update('requires_commute', e.target.checked)}
            />
            Requires ability to commute
          </label>
        </fieldset>

        <label className="field">
          <span>Minimum salary (£) *</span>
          <input
            required
            type="number"
            min="0"
            value={form.salary_min}
            onChange={(e) => update('salary_min', e.target.value)}
          />
        </label>

        <label className="field">
          <span>Maximum salary (£) *</span>
          <input
            required
            type="number"
            min="0"
            value={form.salary_max}
            onChange={(e) => update('salary_max', e.target.value)}
          />
        </label>

        <label className="field">
          <span>Max acceptable notice period (days) *</span>
          <input
            required
            type="number"
            min="0"
            value={form.max_notice_days}
            onChange={(e) => update('max_notice_days', e.target.value)}
          />
        </label>

        <label className="field">
          <span>Score threshold — Submit *</span>
          <input
            required
            type="number"
            min="0"
            max="100"
            value={form.score_threshold_submit}
            onChange={(e) => update('score_threshold_submit', e.target.value)}
          />
        </label>

        <label className="field">
          <span>Score threshold — Review *</span>
          <input
            required
            type="number"
            min="0"
            max="100"
            value={form.score_threshold_review}
            onChange={(e) => update('score_threshold_review', e.target.value)}
          />
        </label>

        {error && <p className="error-text">{error}</p>}

        <button type="submit" disabled={saving}>
          {saving ? 'Saving…' : editingExisting ? 'Update job' : 'Create job'}
        </button>
      </form>
    </div>
  )
}

export default JobForm
