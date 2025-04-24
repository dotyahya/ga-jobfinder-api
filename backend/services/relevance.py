from backend.schemas.job_request import JobRequest
from backend.schemas.job_relevance import JobRelevance
from openai import AsyncOpenAI
import os
import re
from dotenv import load_dotenv

load_dotenv() 

# async to cater multiple API calls instead of having to wait for each one to finish
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in environment variables.")

else:
    print("OpenAI API key loaded successfully.")
    openai_client = AsyncOpenAI(api_key=api_key)


async def compute_relevance_score(criteria: JobRequest, job: JobRelevance) -> float:
    prompt = f"""
        You are a job relevance evaluator. Given the job criteria and job details below, compute a relevance score from 0 to 1, where 1 is a perfect match. 
        
        Consider:
        - Semantic similarity between the position and job title.
        - Compatibility of experience levels (e.g., "6 years" vs. "5-7 years", "Fresher" vs. "0-1 year").
        - Overlap between the salary range (e.g., "70,000 PKR to 120,000 PKR") and job salary.
        - Alignment of job nature (e.g., "onsite", "remote", "hybrid"; treat "Full-Time"/"Part-Time" as neutral unless specified).
        - Proximity of location (e.g., "Islamabad, Pakistan" vs. job location).
        - Overlap of skills (e.g., "full stack, NestJS, Next.js, Firebase") with those mentioned or implied in the job description.

        **Job Criteria**:
        - Position: {criteria.position}
        - Experience: {criteria.experience}
        - Salary: {criteria.salary}
        - Job Nature: {criteria.jobNature}
        - Location: {criteria.location}
        - Skills: {criteria.skills}

        **Job Details**:
        - Job Title: {job.job_title}
        - Company: {job.company}
        - Experience: {job.experience}
        - Description: {job.description}
        - Job Nature: {job.jobNature}
        - Location: {job.location}
        - Salary: {job.salary}
        - Apply Link: {job.apply_link}

        **Instructions**:
        - Prioritize the job description for skill overlap and additional context (e.g., specific technologies or requirements).
        - If data is missing (e.g., "N/A" for salary, experience, or description), assign a neutral score for that criterion.
        - Weigh each criterion approximately equally, adjusting for semantic and contextual relevance.
        - Return only a numerical score between 0 and 1 (e.g., 0.85), with no text or explanation.
    """

    try:
        response = await openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a precise job relevance evaluator."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=10,
            temperature=0.3
        )
        score_text = response.choices[0].message.content.strip()
        score = float(score_text) if score_text.replace(".", "").isdigit() else 0.5
        return max(0.0, min(1.0, score))
    except Exception as e:
        print(f"OpenAI API error: {e}")
        return 0.5 # default

async def filter_relevant_jobs(criteria: JobRequest, jobs: list[dict]) -> list[dict]:
    relevant_jobs = []
    relevance_threshold = 0.65 # can be adjusted

    for job_dict in jobs:

        job_dict_copy = job_dict.copy()
        job_dict_copy["jobNature"] = fix_job_nature(job_dict_copy)

        # if N/A found in experience or salary
        if job_dict_copy.get("experience") == "N/A" or job_dict_copy.get("salary") == "N/A":
            job_dict_copy = await fix_missing_fields(job_dict_copy)

        job = JobRelevance(**job_dict_copy)
        score = await compute_relevance_score(criteria, job)
        print(f"Relevance score for {job.job_title} at {job.company}: {score}")
        if score >= relevance_threshold:
            relevant_jobs.append({
                "job_title": job.job_title,
                "company": job.company,
                "experience": job.experience,
                "jobNature": job.jobNature,
                "location": job.location,
                "salary": job.salary,
                "apply_link": job.apply_link,
                "relevance_score": score # will be removed in final output
            })

    print(f"Relevant jobs: {relevant_jobs}")

    # sort by relevance score (highest first)
    relevant_jobs.sort(key=lambda x: x["relevance_score"], reverse=True)
    for job in relevant_jobs:
        job.pop("relevance_score", None)

    return relevant_jobs


def fix_job_nature(job: dict) -> str:
    description = job.get("description", "N/A").lower()
    current_job_nature = job.get("jobNature", "N/A").lower()

    if "remote" in description:
        job["jobNature"] = "Remote"
    elif "onsite" in description or "on-site" in description:
        job["jobNature"] = "Onsite"
    elif "hybrid" in description:
        job["jobNature"] = "Hybrid"
    elif current_job_nature in ["full time", "part time", "full-time", "part-time"]:
        job["jobNature"] = "N/A"

    return job["jobNature"]

async def fix_missing_fields(job: dict) -> dict:
    job_copy = job.copy()
    description = job_copy.get("description", "N/A").lower()

    # regex pattern for experience
    experience_patterns = [
        r"(\d+)\s*(?:to|-)\s*(\d+)\s*(?:years?|yrs)",  #  captures "3 to 5 years", "3-5 yrs"
        r"(\d+)\s*(?:years?|yrs)\s*(?:of)?\s*experience",  # captures "5 years of experience"
        r"(\d+)\s*\+?\s*(?:years?|yrs)",  # "5+ years"
    ]

    # regex pattern for salary 
    salary_patterns = [
        # "Salary: Rs. 100,000.00 - Rs. 200,000.00"
        r"(?:salary|pay)[:\s]*rs\.?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*(?:to|-)\s*rs\.?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*(pkr|usd|cad|rs\.?|rupees)?",

        # "Salary: Rs. 100,000.00"
        r"(?:salary|pay)[:\s]*rs\.?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*(pkr|usd|cad|rs\.?|rupees)?",

        # "Salary: 100000 - 150000 CAD"
        r"(?:salary|pay)[:\s]*(\d{4,7})\s*(?:to|-)\s*(\d{4,7})\s*(pkr|usd|cad|rs\.?|rupees)?",

        # "Salary: 100000"
        r"(?:salary|pay)[:\s]*(\d{4,7})\s*(pkr|usd|cad|rs\.?|rupees)?",

        # "Pay: 100k - 150k"
        r"(?:salary|pay)[:\s]*(\d{1,3}k)\s*(?:to|-)\s*(\d{1,3}k)\s*(pkr|usd|cad|rs\.?|rupees)?",

        # "Salary: 100k"
        r"(?:salary|pay)[:\s]*(\d{1,3}k)\s*(pkr|usd|cad|rs\.?|rupees)?",

        # No "salary" or "pay" label, for instance:, "Rs. 100,000 - 200,000"
        r"rs\.?\s*(\d{1,3}(?:,\d{3})*|\d{5,7})\s*(?:to|-)\s*(?:rs\.?\s*)?(\d{1,3}(?:,\d{3})*|\d{5,7})\s*(pkr|usd|cad|rs\.?|rupees)?",

        # "100000 - 150000 PKR"
        r"(\d{4,7})\s*(?:to|-)\s*(\d{4,7})\s*(pkr|usd|cad|rs\.?|rupees)?",

        # "100k - 150k"
        r"(\d{1,3}k)\s*(?:to|-)\s*(\d{1,3}k)\s*(pkr|usd|cad|rs\.?|rupees)?",
    ]

    if job_copy.get("experience") == "N/A":
        for pattern in experience_patterns:
            match = re.search(pattern, description)
            if match:
                if pattern == r"(\d+)\s*(?:to|-)\s*(\d+)\s*(?:years?|yrs)":
                    job_copy["experience"] = f"{match.group(1)}-{match.group(2)} years"
                elif pattern in [
                    r"(\d+)\s*(?:years?|yrs)\s*(?:of)?\s*experience",
                    r"(\d+)\s*\+?\s*(?:years?|yrs)",
                ]:
                    job_copy["experience"] = f"{match.group(1)} years"
                break
    
    # etxract and normalize salary
    if job_copy.get("salary") == "N/A":
        for pattern in salary_patterns:
            match = re.search(pattern, description)
            if match:
                currency = match.group(3) if len(match.groups()) >= 3 and match.group(3) else "PKR"
                if currency in ["rs.", "rupees", "pkr"]:
                    currency = "PKR"  # normalize Rs./Rupees to PKR
                if "to" in pattern or "-" in pattern:
                    low, high = match.group(1), match.group(2)
                    # norm shorthand ( "100k -> "100,000")
                    if "k" in low:
                        low = f"{int(low.replace('k', '')) * 1000:,}"
                        high = f"{int(high.replace('k', '')) * 1000:,}"
                    low = low.replace(".00", "") # remove decimal part if any to be consistent
                    high = high.replace(".00", "")
                    job_copy["salary"] = f"{low} - {high} {currency}"
                else:
                    value = match.group(1)
                    if "k" in value:
                        value = f"{int(value.replace('k', '')) * 1000:,}"
                    value = value.replace(".00", "")
                    job_copy["salary"] = f"{value} {currency}"
                break

    return job_copy


    