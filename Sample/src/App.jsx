

// export default App;
import { useState } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [query, setQuery] = useState("");
  const [location, setLocation] = useState("");
  const [education, setEducation] = useState("");
  const [skills, setSkills] = useState("");
  const [stipend, setStipend] = useState("");
  const [mode, setMode] = useState("");
  const [duration, setDuration] = useState("");
  const [sector, setSector] = useState("");
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const fetchJobs = async () => {
    setLoading(true);
    setError("");
    setJobs([]);
    try {
      // ✅ Fetch recommendations from backend
      const res = await axios.get("http://localhost:5000/api/recommendations", {
        params: {
          q: query,
          country: "in",
          max_results: 300,
          location,
          job_type: mode,
          education,
          skills,
          stipend,
          mode,
          duration,
          sector,
        },
      });
      if (res.data.success) setJobs(res.data.results);
      else setError("No recommended internships found.");
    } catch (err) {
      setError("Failed to fetch recommendations. Please check your backend.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <header className="header">
        <h1>Internship and Job - Recommender</h1>
        <p className="subtitle">Find internships tailored just for you </p>
      </header>

      {/* 🧾 User Input Form */}
      <div className="form-container">
        <div className="form-group">
          <label>Search</label>
          <input
            type="text"
            value={query}
            placeholder="e.g. software intern"
            onChange={(e) => setQuery(e.target.value)}
          />
        </div>

        <div className="form-group">
          <label>Location</label>
          <input
            type="text"
            value={location}
            placeholder="e.g. Chennai, Bangalore..."
            onChange={(e) => setLocation(e.target.value)}
          />
        </div>

        <div className="form-group">
          <label>Qualification</label>
          <select
            value={education}
            onChange={(e) => setEducation(e.target.value)}
          >
            <option value="">Other</option>
            <option value="be">BE</option>
            <option value="btech">BTech</option>
            <option value="me">ME</option>
            <option value="mba">MBA</option>
            <option value="bba">BBA</option>
            <option value="bsc">BSc</option>
            <option value="msc">MSc</option>
          </select>
        </div>

        <div className="form-group">
          <label>Skills</label>
          <input
            type="text"
            value={skills}
            placeholder="e.g. React, Python, UI/UX..."
            onChange={(e) => setSkills(e.target.value)}
          />
        </div>

        <div className="form-group">
          <label>Mode of Work</label>
          <select value={mode} onChange={(e) => setMode(e.target.value)}>
            <option value="">Hybrid</option>
            <option value="full_time">Full Time</option>
            <option value="part_time">Part Time</option>
          </select>
        </div>

        <div className="form-group">
          <label>Internship Duration</label>
          <select
            value={duration}
            onChange={(e) => setDuration(e.target.value)}
          >
            <option value="">No Preference</option>
            <option value="1 month">1 Month</option>
            <option value="2 months">2 Months</option>
            <option value="3 months">3 Months</option>
            <option value="6 months">6 Months</option>
          </select>
        </div>

        <div className="form-group">
          <label>Sector of Interest</label>
          <select value={sector} onChange={(e) => setSector(e.target.value)}>
            <option value="">Select sector</option>
            <option value="it">Information Technology</option>
            <option value="marketing">Marketing</option>
            <option value="finance">Finance</option>
            <option value="design">Design / UI-UX</option>
            <option value="data">Data & Analytics</option>
            <option value="management">Management</option>
            <option value="education">Education</option>
            <option value="engineering">Engineering</option>
          </select>
        </div>

        <button onClick={fetchJobs} disabled={loading}>
          {loading ? "🔍 Finding Best Matches..." : "Get Recommended Internships"}
        </button>
      </div>

      {/* ⚠️ Error message */}
      {error && <div className="error">{error}</div>}

      {/* 🏆 Recommended results */}
      {jobs.length > 0 && (
        <h2 className="results-title">
           Top Recommendations for You
        </h2>
      )}

      <div className="job-grid">
        {jobs.map((job, index) => (
          <div key={index} className="job-card">
            <h3>{job.title}</h3>
            <p className="company">{job.company?.display_name || "Unknown"}</p>
            <p className="location">
              📍 {job.location?.display_name || "Location not available"}
            </p>
            <p className="snippet">
              {job.description
                ? job.description.slice(0, 120) + "..."
                : "No description available."}
            </p>
            <a
              href={job.redirect_url}
              target="_blank"
              rel="noreferrer"
              className="apply-btn"
            >
              View Details →
            </a>
          </div>
        ))}
      </div>

      {!loading && jobs.length === 0 && !error && (
        <p className="empty-text">No matching internships found. Try changing filters.</p>
      )}
      
    </div>
  );
}

export default App;
