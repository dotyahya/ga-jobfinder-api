import httpx
import json
# import brotli as br
from bs4 import BeautifulSoup

from backend.schemas.job_request import JobRequest
from backend.services.relevance import filter_relevant_jobs



# mimic browser headers to avoid bot detection
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Connection": "keep-alive",
    "Accept-Language": "en-US,en;q=0.9,lt;q=0.8,et;q=0.7,de;q=0.6",
}

# def scrape_indeed_jobs(position, location):
#     # if location has comma or "Pakistan" then remove it
#     if "," in location or "Pakistan" in location:
#         location = location.split(",")[0].strip()

#     position = position.lower()

#     base_url = "https://pk.indeed.com/jobs"
#     params = {
#         "q": position,
#         "l": location,
#     }

#     response = httpx.get(base_url, params=params, headers=HEADERS)
#     print(f"Scraping URL: {response.url}")
#     print("Response:", response)

#     soup = BeautifulSoup(response.text, "html.parser")
#     job_cards = soup.select("div.job_seen_beacon")
    
#     results = []
#     for card in job_cards[:10]:  # limit to top 10 results
#         title = card.find("h2", class_="jobTitle")
#         company = card.find("span", class_="companyName")
#         location_tag = card.find("div", class_="companyLocation")
#         link_tag = card.find("a", href=True)

#         if title and company and location_tag and link_tag:
#             results.append({
#                 "job_title": title.text.strip(),
#                 "company": company.text.strip(),
#                 "experience": "N/A",
#                 "jobNature": "N/A",
#                 "location": location_tag.text.strip(),
#                 "salary": "N/A",
#                 "apply_link": "https://pk.indeed.com" + link_tag['href']
#             })

#     return results


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
                # remove any tags from description_raw such as <li>
                if description_raw:
                    description_raw = BeautifulSoup(description_raw, "html.parser").get_text()

                scraped_job_listings.append({
                    "job_title": job.get("title", "N/A"),
                    "company": job.get("company", "N/A"),
                    "experience": job.get("experience_text", "N/A"),
                    "description": job.get("description_raw", "N/A"),
                    "jobNature": job.get("type", "N/A"),
                    "location": ", ".join(job.get("city_exact", [location_id])),
                    "salary": f"{job.get('salaryN_exact', 'N/A')} - {job.get('salaryT_exact', 'N/A')} {job.get('currency_unit', '')}".strip(),
                    "apply_link": f"https://www.rozee.pk/{job.get('rozeePermaLink', '')}"
                })

            # filter relevant jobs based on criteria using gpt-4o-mini
            relevant_jobs = await filter_relevant_jobs(criteria, scraped_job_listings)

            # remove duplicates based on title and company
            seen = set()
            unique_results = []
            for job in relevant_jobs:
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






