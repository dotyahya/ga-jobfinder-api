from backend.schemas.job_request import JobRequest
from backend.schemas.job_relevance import JobRelevance
from openai import AsyncOpenAI
import os
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
        You are a job relevance evaluator. Given the job criteria and job details below, compute a relevance score from 0 to 1, where 1 is a perfect match. Consider:
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
    relevance_threshold = 0.7 

    for job_dict in jobs:

        job_dict_copy = job_dict.copy()
        description = job_dict_copy.get("description", "N/A").lower()
        current_job_nature = job_dict_copy.get("jobNature", "N/A").lower()

        if "remote" in description:
            job_dict_copy["jobNature"] = "Remote"
        elif "onsite" in description or "on-site" in description:
            job_dict_copy["jobNature"] = "Onsite"
        elif "hybrid" in description:
            job_dict_copy["jobNature"] = "Hybrid"
        elif current_job_nature in ["full time", "part time", "full-time", "part-time"]:
            job_dict_copy["jobNature"] = "N/A"

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