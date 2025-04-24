import httpx
import json
# import brotli as br
from bs4 import BeautifulSoup

from backend.schemas.job_request import JobRequest
from backend.services.relevance import filter_relevant_jobs
from backend.services.utils import get_jobs

from dotenv import load_dotenv
import os

load_dotenv()

# rapid api key
RAPID_API_KEY = os.environ.get("RAPID_API_KEY")
if not RAPID_API_KEY:
    raise ValueError("RAPID_API_KEY not found in environment variables.")

else:
    print("RapidAPI key loaded successfully.")


# mimic browser headers to avoid bot detection
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Connection": "keep-alive",
    "Accept-Language": "en-US,en;q=0.9,lt;q=0.8,et;q=0.7,de;q=0.6",
}


async def scrape_jobs(criteria: JobRequest) -> dict[str, list[dict]]:
    # job_ids = get_linkedin_job_ids(criteria.position, criteria.location)

    # base_url = "https://jsearch.p.rapidapi.com/job-details"

    # headers = {
    #     "x-rapidapi-key": RAPID_API_KEY,
    #     "x-rapidapi-host": "jsearch.p.rapidapi.com"
    # }

    # scrape jobs from rozee.pk
    jobs_rozee = await scrape_rozee_jobs(criteria)

    async with httpx.AsyncClient() as client:
        try:

            scraped_job_listings = []

            jobs = get_jobs(criteria.position, criteria.location)
            jobs_listing = jobs.json()

            for job in jobs_listing.get("data", []):
                scraped_job_listings.append({
                    "job_title": job.get("job_title", "N/A"),
                    "company": job.get("employer_name", "N/A"),
                    "experience": job.get("job_experience", "N/A"),
                    "description": job.get("job_description", "N/A"),
                    "jobNature": "remote" if job.get("job_is_remote") is True else "onsite",
                    "location": job.get("job_location", "N/A"),
                    "salary": f"{job.get('job_salary', 'N/A')}" if job.get("job_salary") else "N/A",
                    "apply_link": job.get("job_apply_link", "N/A")
                })

            # append rozee jobs to scraped jobs listings
            scraped_job_listings.extend(jobs_rozee["relevant_jobs"])

            print(scraped_job_listings)

            relevant_jobs = await filter_relevant_jobs(criteria, scraped_job_listings)


            # for job_id in job_ids:
            #     querystring = {
            #         "job_id": job_id
            #     }
            #     response = await client.get(base_url, params=querystring, headers=headers)
            #     content = response.content

            #     data = json.loads(content.decode("utf-8"))
            #     print(data)

            return {
                "relevant_jobs": relevant_jobs
            }

        except Exception as e:
            print(f"Unexpected error: {e}")
            return {
                "relevant_jobs": []
            }


# Rozee.pk 
async def scrape_rozee_jobs(criteria: JobRequest) -> dict[str, list[dict]]:
    # if location has Islamabad the set as 1180, Karachi as 1184, Lahore as 1185, Peshawar as 1188
    if "Islamabad" in criteria.location:
        location_id = "1180"
    elif "Karachi" in criteria.location:
        location_id = "1184"
    elif "Lahore" in criteria.location:
        location_id = "1185"
    elif "Peshawar" or "Khyber-Pakhtunkhwa" in criteria.location:
        location_id = "1188"

    base_url = "https://www.rozee.pk/services/job/jobSearch"

    form_data = {
        "filters[q]": criteria.position,
        "filters[fc]": location_id,
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(base_url, data=form_data, headers=HEADERS)

            content = response.content

            data = json.loads(content.decode("utf-8"))
            jobs = data.get("response", {}).get("jobs", {}).get("basic", [])

            scraped_job_listings = []
            for job in jobs[:10]:  # Limit to first 10 jobs
                description_raw = job.get("description_raw", "N/A")
                # remove any tags from description_raw such as <li>, but is this necessary?
                if description_raw:
                    description_raw = BeautifulSoup(description_raw, "html.parser").get_text()

                scraped_job_listings.append({
                    "job_title": job.get("title", "N/A"),
                    "company": job.get("company", "N/A"),
                    "experience": job.get("experience_text", "N/A"),
                    "description": f"{description_raw}" if description_raw else "N/A",
                    "jobNature": job.get("type", "N/A"),
                    "location": ", ".join(job.get("city_exact", [location_id])),
                    "salary": f"{job.get('salaryN_exact', 'N/A')} - {job.get('salaryT_exact', 'N/A')} {job.get('currency_unit', '')}".strip(),
                    "apply_link": f"https://www.rozee.pk/{job.get('rozeePermaLink', '')}"
                })

            # TODO: remove this after moving logic to get_jobs()
            # filter relevant jobs based on criteria using gpt-4o-mini
            # relevant_jobs = await filter_relevant_jobs(criteria, scraped_job_listings)

            # remove duplicates based on title and company
            seen = set()
            unique_results = []
            for job in scraped_job_listings:
                identifier = (job["job_title"], job["company"])
                if identifier not in seen:
                    seen.add(identifier)
                    unique_results.append(job)

            return {
                "relevant_jobs": unique_results
            }

        except Exception as e:
            print(f"Unexpected error: {e}")
            return {"relevant_jobs": []}






