from fastapi import APIRouter, Request
from backend.schemas.job_request import JobRequest
from backend.schemas.job_response import JobResponse
from backend.services.scraper import scrape_jobs
from backend.services.rate_limiter import limiter

router = APIRouter()

# @router.post("/search")
# def find_jobs(request: JobRequest):
#     return {
#         "message": "Job search initiated",
#         "criteria": request.model_dump()
#     }

@router.post("/search", response_model=JobResponse)
@limiter.limit("5/month")
async def find_jobs(job_request: JobRequest, request: Request):
    # jobs = scrape_indeed_jobs(request.position, request.location)
    # return {
    #     "relevant_jobs": jobs
    # }

    # jobs = scrape_rozee_jobs(request.position, request.location)
    # return {
    #     "relevant_jobs": jobs
    # }

    criteria = JobRequest(**job_request.model_dump())
    # relevant_jobs = await scrape_rozee_jobs(criteria)
    relevant_jobs = await scrape_jobs(criteria)
    return relevant_jobs