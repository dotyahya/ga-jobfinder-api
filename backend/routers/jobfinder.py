from fastapi import APIRouter
from backend.schemas.job_request import JobRequest
from backend.schemas.job_response import JobResponse
from backend.services.scraper import scrape_rozee_jobs, scrape_jobs

router = APIRouter()

# @router.post("/search")
# def find_jobs(request: JobRequest):
#     return {
#         "message": "Job search initiated",
#         "criteria": request.model_dump()
#     }

@router.post("/search", response_model=JobResponse)
async def find_jobs(request: JobRequest):
    # jobs = scrape_indeed_jobs(request.position, request.location)
    # return {
    #     "relevant_jobs": jobs
    # }

    # jobs = scrape_rozee_jobs(request.position, request.location)
    # return {
    #     "relevant_jobs": jobs
    # }

    criteria = JobRequest(**request.model_dump())
    # relevant_jobs = await scrape_rozee_jobs(criteria)
    relevant_jobs = await scrape_jobs(criteria)
    return relevant_jobs