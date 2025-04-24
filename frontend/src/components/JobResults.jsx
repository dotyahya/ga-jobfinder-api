import React from 'react';

const JobCard = ({ job }) => (
  <div className="job-card">
    <h3>{job.job_title}</h3>
    <p>Company: {job.company}</p>
    <p>Experience: {job.experience}</p>
    <p>Location: {job.location}</p>
    <p>Salary: {job.salary}</p>
    <p>Type: {job.jobNature}</p>
    <a href={job.apply_link} target="_blank" rel="noopener noreferrer">
      Apply Now
    </a>
  </div>
);

const JobResults = ({ jobs, loading }) => (
  <div>
    {loading ? (
      <p className="no-jobs">Loading...</p>
    ) : jobs.length > 0 ? (
      jobs.map((job, index) => <JobCard key={index} job={job} />)
    ) : (
      <p className="no-jobs">No jobs found. Try different criteria.</p>
    )}
  </div>
);

export default JobResults;