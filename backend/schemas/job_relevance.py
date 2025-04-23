from pydantic import BaseModel

class JobRelevance(BaseModel):
    job_title: str
    company: str
    experience: str
    description: str
    jobNature: str
    location: str
    salary: str
    apply_link: str

