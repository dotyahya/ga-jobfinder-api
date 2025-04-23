from fastapi import APIRouter
from backend.schemas.job_request import JobRequest

router = APIRouter()

@router.post("/search")
def find_jobs(request: JobRequest):
    return {
        "message": "Job search initiated",
        "criteria": request.model_dump()
    }
