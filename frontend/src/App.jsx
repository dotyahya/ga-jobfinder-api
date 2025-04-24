import React, { useState, useEffect } from 'react';
import './App.css';
import { checkHealth } from './api/api';
import JobForm from './components/JobForm';
import JobResults from './components/JobResults';

const App = () => {
  const [healthStatus, setHealthStatus] = useState('Checking...');
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    checkHealth()
      .then(status => setHealthStatus(status))
      .catch(() => setHealthStatus('❌'));
  }, []);

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>Job Finder</h1>
        <span className="health-status">API: {healthStatus}</span>
      </header>
      <JobForm setJobs={setJobs} loading={loading} setLoading={setLoading} setError={setError} />
      {error && <p className="error">{error}</p>}
      <JobResults jobs={jobs} loading={loading} />
    </div>
  );
};

export default App;