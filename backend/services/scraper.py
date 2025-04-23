import httpx
import json
import brotli as br
from bs4 import BeautifulSoup

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


def scrape_rozee_jobs(position, location):
    # if location has Islamabad the set as 1180, Karachi as 1184, Lahore as 1185, Peshawar as 1188
    if "Islamabad" in location:
        location = "1180"
    elif "Karachi" in location:
        location = "1184"
    elif "Lahore" in location:
        location = "1185"
    elif "Peshawar" or "Khyber-Pakhtunkhwa" in location:
        location = "1188"

    base_url = "https://www.rozee.pk/services/job/jobSearch"

    form_data = {
        "filters[q]": position,
        "filters[fc]": location,
    }

    response = httpx.post(base_url, data=form_data, headers=HEADERS)

    content = response.content

    data = json.loads(content.decode("utf-8"))
    jobs = data.get("response", {}).get("jobs", {}).get("basic", [])
    
    results = []
    for job in jobs[:10]:  # Limit to first 10 jobs
        results.append({
            "job_title": job.get("title", "N/A"),
            "company": job.get("company", "N/A"),
            "experience": job.get("experience_text", "N/A"),
            "jobNature": job.get("type", "N/A"),
            "location": ", ".join(job.get("city_exact", [location])),
            "salary": f"{job.get('salaryN_exact', 'N/A')} - {job.get('salaryT_exact', 'N/A')} {job.get('currency_unit', '')}".strip(),
            "apply_link": f"https://www.rozee.pk/{job.get('rozeePermaLink', '')}"
        })

    # remove duplicates based on title and company
    seen = set()
    unique_results = []
    for job in results:
        identifier = (job["job_title"], job["company"])
        if identifier not in seen:
            seen.add(identifier)
            unique_results.append(job)

    return unique_results

