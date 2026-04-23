import { useState } from "react";

function App() {
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [formData, setFormData] = useState({
    candidate: {
      candidate_id: "cand-001",
      job_id: "job-001",
      has_driving_licence: true,
      willing_to_work_shifts: true,
      can_commute: true,
      expected_salary: 42000,
      notice_period_days: 45,
      fit_score: 7,
    },
    job_config: {
      job_id: "job-001",
      requires_driving_licence: true,
      requires_shift_flexibility: true,
      requires_commute: true,
      salary_min: 30000,
      salary_max: 40000,
      max_notice_days: 60,
    },
  });

  const handleInputChange = (section, field, value) => {
    setFormData((prev) => ({
      ...prev,
      [section]: {
        ...prev[section],
        [field]: value,
      },
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setResult(null);

    try {
      const res = await fetch("http://127.0.0.1:8000/evaluate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formData),
      });

      if (!res.ok) {
        const text = await res.text();
        throw new Error(`Request failed: ${res.status} ${text}`);
      }

      const data = await res.json();
      setResult(data);
    } catch (err) {
      setError(err.message || "Something went wrong");
    }
  };

  return (
    <div style={{ padding: "40px", fontFamily: "Arial, sans-serif" }}>
      <h1>Layerbound Demo</h1>

      <form onSubmit={handleSubmit}>
        <h2>Candidate Information</h2>
        <label>
          Candidate ID: <input type="text" value={formData.candidate.candidate_id} onChange={(e) => handleInputChange('candidate', 'candidate_id', e.target.value)} />
        </label><br />
        <label>
          Job ID: <input type="text" value={formData.candidate.job_id} onChange={(e) => handleInputChange('candidate', 'job_id', e.target.value)} />
        </label><br />
        <label>
          Has Driving Licence: <input type="checkbox" checked={formData.candidate.has_driving_licence} onChange={(e) => handleInputChange('candidate', 'has_driving_licence', e.target.checked)} />
        </label><br />
        <label>
          Willing to Work Shifts: <input type="checkbox" checked={formData.candidate.willing_to_work_shifts} onChange={(e) => handleInputChange('candidate', 'willing_to_work_shifts', e.target.checked)} />
        </label><br />
        <label>
          Can Commute: <input type="checkbox" checked={formData.candidate.can_commute} onChange={(e) => handleInputChange('candidate', 'can_commute', e.target.checked)} />
        </label><br />
        <label>
          Expected Salary: <input type="number" value={formData.candidate.expected_salary} onChange={(e) => handleInputChange('candidate', 'expected_salary', parseInt(e.target.value))} />
        </label><br />
        <label>
          Notice Period Days: <input type="number" value={formData.candidate.notice_period_days} onChange={(e) => handleInputChange('candidate', 'notice_period_days', parseInt(e.target.value))} />
        </label><br />
        <label>
          Fit Score: <input type="number" value={formData.candidate.fit_score} onChange={(e) => handleInputChange('candidate', 'fit_score', parseInt(e.target.value))} />
        </label><br />

        <h2>Job Configuration</h2>
        <label>
          Job ID: <input type="text" value={formData.job_config.job_id} onChange={(e) => handleInputChange('job_config', 'job_id', e.target.value)} />
        </label><br />
        <label>
          Requires Driving Licence: <input type="checkbox" checked={formData.job_config.requires_driving_licence} onChange={(e) => handleInputChange('job_config', 'requires_driving_licence', e.target.checked)} />
        </label><br />
        <label>
          Requires Shift Flexibility: <input type="checkbox" checked={formData.job_config.requires_shift_flexibility} onChange={(e) => handleInputChange('job_config', 'requires_shift_flexibility', e.target.checked)} />
        </label><br />
        <label>
          Requires Commute: <input type="checkbox" checked={formData.job_config.requires_commute} onChange={(e) => handleInputChange('job_config', 'requires_commute', e.target.checked)} />
        </label><br />
        <label>
          Salary Min: <input type="number" value={formData.job_config.salary_min} onChange={(e) => handleInputChange('job_config', 'salary_min', parseInt(e.target.value))} />
        </label><br />
        <label>
          Salary Max: <input type="number" value={formData.job_config.salary_max} onChange={(e) => handleInputChange('job_config', 'salary_max', parseInt(e.target.value))} />
        </label><br />
        <label>
          Max Notice Days: <input type="number" value={formData.job_config.max_notice_days} onChange={(e) => handleInputChange('job_config', 'max_notice_days', parseInt(e.target.value))} />
        </label><br />

        <button type="submit">Evaluate Candidate</button>
      </form>

      {error && (
        <p style={{ marginTop: "20px", color: "red" }}>
          {error}
        </p>
      )}

      {result && (
        <div style={{ marginTop: "20px" }}>
          <h2>Evaluation Result</h2>
          <pre style={{ textAlign: "left" }}>
            {JSON.stringify(result, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}

export default App;