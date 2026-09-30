import os
import json
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

from rag.embeddings import get_embedding, cosine_similarity

load_dotenv()
client = InferenceClient(api_key=os.getenv("HF_TOKEN"), provider="auto")
MODEL_NAME = "meta-llama/Llama-3.1-8B-Instruct"


def build_resume_text(resume) -> str:
    skills = json.loads(resume.skills) if resume.skills else {}
    technical = ", ".join(skills.get("technical_skills", []))
    soft = ", ".join(skills.get("soft_skills", []))
    return f"{resume.summary or ''}\nTechnical skills: {technical}\nSoft skills: {soft}"


def build_job_text(job) -> str:
    return f"{job.title}. Required skills: {job.required_skills}. {job.description}"


def explain_match(resume_text: str, job) -> str:
    prompt = f"""
You are a Career Matching Assistant. In 2-3 short sentences, explain why this
candidate could be a good fit for this job based on the overlap between their
profile and the job requirements. Then mention 1-2 skills they might be
missing for this specific role, if any. Be concise and direct.

Candidate profile:
\"\"\"{resume_text}\"\"\"

Job title: {job.title}
Required skills: {job.required_skills}
Job description: {job.description}
"""

    completion = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
    )
    return completion.choices[0].message.content.strip()


def match_resume_to_jobs(resume, jobs: list, top_k: int = 3) -> list[dict]:
   
    if not jobs:
        return []

    resume_text = build_resume_text(resume)
    resume_embedding = get_embedding(resume_text)

    scored_jobs = []
    for job in jobs:
        job_embedding = get_embedding(build_job_text(job))
        score = cosine_similarity(resume_embedding, job_embedding)
        scored_jobs.append((job, score))

    scored_jobs.sort(key=lambda pair: pair[1], reverse=True)
    top_matches = scored_jobs[:top_k]

    results = []
    for job, score in top_matches:
        explanation = explain_match(resume_text, job)
        results.append(
            {
                "job_id": job.id,
                "job_title": job.title,
                "match_score": round(max(score, 0) * 100, 1),
                "explanation": explanation,
            }
        )

    return results
