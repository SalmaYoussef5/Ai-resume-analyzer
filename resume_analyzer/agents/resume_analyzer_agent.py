import os
import json
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()
client = InferenceClient(api_key=os.getenv("HF_TOKEN"), provider="auto")

MODEL_NAME = "Qwen/Qwen2.5-7B-Instruct"


def analyze_resume(resume_text: str) -> dict:
    
    prompt = f"""
You are a Resume Analyzer AI. Analyze the following resume text and return ONLY
a valid JSON object (no markdown formatting, no explanation, no code fences)
with exactly this structure:

{{
  "technical_skills": ["skill1", "skill2"],
  "soft_skills": ["skill1", "skill2"],
  "education": ["degree - institution - year"],
  "experience": ["job title - company - duration"],
  "summary": "A short 2-3 sentence professional summary of this candidate"
}}

Resume text:
\"\"\"
{resume_text[:6000]}
\"\"\"
"""

    completion = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = completion.choices[0].message.content.strip()

    if raw.startswith("```"):
        raw = raw.strip("`")
        if raw.startswith("json"):
            raw = raw[4:]

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {
            "technical_skills": [],
            "soft_skills": [],
            "education": [],
            "experience": [],
            "summary": raw,
        }
