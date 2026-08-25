const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

class ApiError extends Error {
  constructor(message, status, detail) {
    super(message)
    this.status = status
    this.detail = detail
  }
}

async function request(path, options = {}) {
  const response = await fetch(`${API_URL}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })

  if (!response.ok) {
    let detail = response.statusText
    try {
      const body = await response.json()
      if (Array.isArray(body.detail)) {
        // FastAPI's automatic request-validation errors come back as a list
        // of {loc, msg, type} objects rather than a plain string.
        detail = body.detail
          .map((e) => `${(e.loc || []).slice(-1)[0] ?? 'field'}: ${e.msg}`)
          .join('; ')
      } else if (body.detail) {
        detail = body.detail
      }
    } catch {
      // response wasn't JSON - fall back to statusText
    }
    throw new ApiError(`Request to ${path} failed: ${detail}`, response.status, detail)
  }

  if (response.status === 204) return null
  return response.json()
}

export const api = {
  health: () => request('/health'),

  listJobs: () => request('/jobs'),
  getJob: (jobId) => request(`/jobs/${encodeURIComponent(jobId)}`),
  upsertJob: (jobConfig) =>
    request('/jobs', { method: 'POST', body: JSON.stringify(jobConfig) }),
  deleteJob: (jobId) =>
    request(`/jobs/${encodeURIComponent(jobId)}`, { method: 'DELETE' }),

  evaluate: (candidate, jobConfig) =>
    request('/evaluate', {
      method: 'POST',
      body: JSON.stringify(
        jobConfig ? { candidate, job_config: jobConfig } : { candidate }
      ),
    }),

  listEvaluations: ({ jobId, decision, limit = 50, offset = 0 } = {}) => {
    const params = new URLSearchParams()
    if (jobId) params.set('job_id', jobId)
    if (decision) params.set('decision', decision)
    params.set('limit', limit)
    params.set('offset', offset)
    return request(`/evaluations?${params.toString()}`)
  },

  getDashboard: (jobId) => {
    const params = new URLSearchParams()
    if (jobId) params.set('job_id', jobId)
    const qs = params.toString()
    return request(`/dashboard${qs ? `?${qs}` : ''}`)
  },
}

export { ApiError }
