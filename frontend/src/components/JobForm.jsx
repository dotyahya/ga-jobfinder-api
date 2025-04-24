import React, { useState } from 'react';
import { findJob } from '../api/api';

const JobForm = ({ setJobs, loading, setLoading, setError }) => {
  const [formData, setFormData] = useState({
    position: '',
    experience: '',
    salary: '',
    jobNature: 'onsite',
    location: '',
    skills: '',
  });
  const [formError, setFormError] = useState('');

  const handleChange = e => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    setFormError(''); // clear error on input change
  };

  const handleSubmit = async e => {
    e.preventDefault();

    // validate form data: all fields are required
    const { position, experience, salary, jobNature, location, skills } = formData;
    if (!position || !experience || !salary || !jobNature || !location || !skills) {
      setFormError('All fields are required.');
      return;
    }

    setLoading(true);
    setError('');
    setJobs([]);
    setFormError('');

    try {
      const data = await findJob(formData);
      setJobs(data.relevant_jobs || []);
    } catch (err) {
      setError('Failed to fetch jobs');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form className="job-form" onSubmit={handleSubmit}>
      {formError && <p className="error">{formError}</p>}
      <div className="form-grid">
        <input
          type="text"
          name="position"
          placeholder="Position (e.g., Full Stack Engineer)"
          value={formData.position}
          onChange={handleChange}
          required
        />
        <input
          type="text"
          name="experience"
          placeholder="Experience (e.g., 2 years)"
          value={formData.experience}
          onChange={handleChange}
          required
        />
        <input
          type="text"
          name="salary"
          placeholder="Salary (e.g., 70,000 PKR to 120,000 PKR)"
          value={formData.salary}
          onChange={handleChange}
          required
        />
        <select name="jobNature" value={formData.jobNature} onChange={handleChange} required>
          <option value="onsite">Onsite</option>
          <option value="remote">Remote</option>
          <option value="hybrid">Hybrid</option>
        </select>
        <input
          type="text"
          name="location"
          placeholder="Location (e.g., Peshawar, Pakistan)"
          value={formData.location}
          onChange={handleChange}
          required
        />
        <input
          type="text"
          name="skills"
          placeholder="Skills (e.g., MERN, Node.js, React.js)"
          value={formData.skills}
          onChange={handleChange}
          required
        />
      </div>
      <button type="submit" disabled={loading}>
        {loading ? 'Searching...' : 'Search Jobs'}
      </button>
    </form>
  );
};

export default JobForm;