from fastapi import FastAPI
from backend.schemas.job_request import JobRequest


app = FastAPI()

@app.get("/healthz")
def check_health():
    return {"status": "ok"}

@app.post("/find-jobs")
def find_jobs(request: JobRequest):
    return {
        "message": "Job search initiated",
        "criteria": request.model_dump()
    }
