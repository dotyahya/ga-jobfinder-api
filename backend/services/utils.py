import httpx
from dotenv import load_dotenv
import os

load_dotenv()

# rapid api key
RAPID_API_KEY = os.environ.get("RAPID_API_KEY")
if not RAPID_API_KEY:
    raise ValueError("RAPID_API_KEY not found in environment variables.")

else:
    print("RapidAPI key loaded successfully.")

country_codes = {
    "Pakistan": "pk",
    "India": "in",
    "United States": "us",
    "United Kingdom": "uk",
    "Canada": "ca",
}


# region: old code
# def get_linkedin_jobs(position: str, location: str) -> httpx.Response:
#     # separate the location into city and country
#     if "," in location:
#         city, country = location.split(",")
#         city = city.strip()
#         country = country.strip()
#         if country in country_codes:
#             country = country_codes[country]
#         else:
#             country = "pk"
        
#     base_url = "https://jsearch.p.rapidapi.com/search"
#     # base_url = "https://linkedin-job-search-api.p.rapidapi.com/active-jb-7d"

#     querystring = {"query": f"{position} jobs in {city}","page":"1","num_pages":"1","country":{country},"date_posted":"week"}

#     headers = {
#         "x-rapidapi-key": RAPID_API_KEY,
#         "x-rapidapi-host": "jsearch.p.rapidapi.com"
#     }

#     response = httpx.get(base_url, params=querystring, headers=headers)

#     print(response.url)

#     return response

# def get_linkedin_job_ids(position: str, location: str) -> set[str]:
#     job_ids = set()
#     response = get_linkedin_jobs(position, location)
#     jobs_listing = response.json()

#     job_ids = set()

#     for job in jobs_listing.get("data", []):
#         job_ids.add(job["job_id"])


#     return job_ids
# endregion

def get_jobs(position: str, location: str) -> httpx.Response:
    """
    Fetches job listings from the JSearch API based on the provided position and location.
    Job listings are from various sources including LinkedIn, Indeed, Glassdoor, and few others.
    API is rate limited to 200 requests per month.
    """
    # separate the location into city and country
    if "," in location:
        city, country = location.split(",")
        city = city.strip()
        country = country.strip()
        if country in country_codes:
            country = country_codes[country]
        else:
            country = "pk"
        
    base_url = "https://jsearch.p.rapidapi.com/search" # API Rate Limited to 200 req/mo

    querystring = {"query": f"{position} jobs in {city}","page":"1","num_pages":"1","country":{country},"date_posted":"week"}

    headers = {
        "x-rapidapi-key": RAPID_API_KEY,
        "x-rapidapi-host": "jsearch.p.rapidapi.com"
    }

    response = httpx.get(base_url, params=querystring, headers=headers)

    print(response.url)

    return response