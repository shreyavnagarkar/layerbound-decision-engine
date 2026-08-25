import { useCallback, useEffect, useState } from 'react'
import './App.css'
import { api } from './api/client.js'
import JobForm from './components/JobForm.jsx'
import CandidateForm from './components/CandidateForm.jsx'
import ResultCard from './components/ResultCard.jsx'
import Dashboard from './components/Dashboard.jsx'

const TABS = [
  { id: 'jobs', label: 'Job setup' },
  { id: 'evaluate', label: 'Evaluate candidate' },
  { id: 'dashboard', label: 'Dashboard' },
]

function App() {
  const [activeTab, setActiveTab] = useState('evaluate')
  const [jobs, setJobs] = useState([])
  const [jobsError, setJobsError] = useState('')

  const [savingJob, setSavingJob] = useState(false)
  const [jobFormError, setJobFormError] = useState('')

  const [evaluating, setEvaluating] = useState(false)
  const [evaluateError, setEvaluateError] = useState('')
  const [lastResult, setLastResult] = useState(null)
  const [dashboardRefreshKey, setDashboardRefreshKey] = useState(0)

  const loadJobs = useCallback(() => {
    api
      .listJobs()
      .then(setJobs)
      .catch((err) => setJobsError(err.message))
  }, [])

  useEffect(() => {
    loadJobs()
  }, [loadJobs])

  const handleSaveJob = async (jobConfig) => {
    setSavingJob(true)
    setJobFormError('')
    try {
      await api.upsertJob(jobConfig)
      await loadJobs()
      return true
    } catch (err) {
      setJobFormError(err.message)
      return false
    } finally {
      setSavingJob(false)
    }
  }

  const handleEvaluate = async (candidate) => {
    setEvaluating(true)
    setEvaluateError('')
    setLastResult(null)
    try {
      const result = await api.evaluate(candidate)
      setLastResult(result)
      setDashboardRefreshKey((k) => k + 1)
    } catch (err) {
      setEvaluateError(err.message)
    } finally {
      setEvaluating(false)
    }
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>Layerbound Intake Evaluation</h1>
        <p className="app-subtitle">
          Score candidate responses, flag hard-rule failures, and see intake trends at
          a glance.
        </p>
      </header>

      <nav className="tabs">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            className={`tab-button ${activeTab === tab.id ? 'active' : ''}`}
            onClick={() => setActiveTab(tab.id)}
          >
            {tab.label}
          </button>
        ))}
      </nav>

      {jobsError && (
        <p className="error-text banner-error">
          Couldn&rsquo;t reach the API ({jobsError}). Is the backend running?
        </p>
      )}

      <main className="app-main">
        {activeTab === 'jobs' && (
          <JobForm jobs={jobs} onSave={handleSaveJob} saving={savingJob} error={jobFormError} />
        )}

        {activeTab === 'evaluate' && (
          <>
            <CandidateForm
              jobs={jobs}
              onEvaluate={handleEvaluate}
              evaluating={evaluating}
              error={evaluateError}
            />
            <ResultCard result={lastResult} />
          </>
        )}

        {activeTab === 'dashboard' && <Dashboard jobs={jobs} refreshKey={dashboardRefreshKey} />}
      </main>
    </div>
  )
}

export default App
