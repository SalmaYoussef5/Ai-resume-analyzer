import os
import json
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

from rag.retriever import retrieve

load_dotenv()
client = InferenceClient(api_key=os.getenv("HF_TOKEN"), provider="auto")
MODEL_NAME = "meta-llama/Llama-3.1-8B-Instruct"


def _get_resume_skills(resume) -> set:
    skills = json.loads(resume.skills) if resume.skills else {}
    technical = skills.get("technical_skills", [])
    soft = skills.get("soft_skills", [])
    return {s.strip().lower() for s in technical + soft}


def suggest_improvements(resume, target_job=None) -> dict:
    
    resume_skills = _get_resume_skills(resume)

    missing_skills = []
    if target_job is not None:
        required = {s.strip().lower() for s in target_job.required_skills.split(",")}
        missing_skills = sorted(required - resume_skills)

  
    if missing_skills:
        query = f"How to learn and improve in: {', '.join(missing_skills)}. Relevant courses and roadmap."
    else:
        query = f"Career improvement advice for someone with skills: {', '.join(resume_skills)}. Resume writing tips."

    context_chunks = retrieve(query, top_k=5)
    context = "\n---\n".join(context_chunks)

    prompt = f"""
You are a Career Advisor AI. Use ONLY the context below (a knowledge base of
career roadmaps, skill descriptions, learning resources, and resume writing
guidelines) to give the candidate practical advice. Do not invent courses or
facts that are not supported by the context.

Context:
\"\"\"
{context}
\"\"\"

Candidate's current skills: {', '.join(resume_skills) if resume_skills else 'Not specified'}
Missing skills for target role: {', '.join(missing_skills) if missing_skills else 'None specified - give general improvement advice'}

Write a short, practical response covering:
1. Key weaknesses or gaps
2. Specific improvements to make
3. Recommended certifications (only if mentioned in the context)
4. Recommended learning resources (only if mentioned in the context)
"""

    completion = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
    )

    return {
        "missing_skills": missing_skills,
        "advice": completion.choices[0].message.content.strip(),
    }


def answer_career_question(question: str, resume=None) -> str:
    
    context_chunks = retrieve(question, top_k=4)
    context = "\n---\n".join(context_chunks)

    resume_context = ""
    if resume is not None:
        skills = _get_resume_skills(resume)
        resume_context = f"\nThe candidate asking this has these skills: {', '.join(skills)}."

    prompt = f"""
You are a Career Advisor AI. Answer the user's career-related question using
the context below when relevant. If the context doesn't fully cover the
question, you may use your general knowledge, but prioritize the context.

Context:
\"\"\"
{context}
\"\"\"
{resume_context}

Question: {question}
"""

    completion = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
    )
    return completion.choices[0].message.content.strip()
