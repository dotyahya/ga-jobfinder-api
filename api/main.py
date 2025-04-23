from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class JobRequest(BaseModel):
    position: str
    experience: str
    salary: str
    jobNature: str
    location: str
    skills: str

@app.post("/find-jobs")
def find_jobs(request: JobRequest):
    return {
        "message": "Job search initiated",
        "criteria": request.model_dump()
    }
