from pydantic import BaseModel

class JobEntry(BaseModel):
    job_title: str
    company: str
    experience: str
    jobNature: str
    location: str
    salary: str
    apply_link: str

class JobResponse(BaseModel):
    relevant_jobs: list[JobEntry]
