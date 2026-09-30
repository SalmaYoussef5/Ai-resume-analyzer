import os
import json
import uuid
import shutil
from typing import List

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session

from database import get_db
from models import Resume, User, Job, Recommendation
from schemas import ResumeOut, MatchOut
from auth import get_current_user
from utils.file_parser import extract_text
from agents.resume_analyzer_agent import analyze_resume
from agents.job_matching_agent import match_resume_to_jobs

router = APIRouter(prefix="/resumes", tags=["Resumes"])

UPLOAD_DIR = "uploaded_resumes"
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {".pdf", ".docx"}


def build_resume_response(resume: Resume) -> ResumeOut:
    skills = json.loads(resume.skills) if resume.skills else {}
    return ResumeOut(
        id=resume.id,
        file_name=resume.file_name,
        technical_skills=skills.get("technical_skills", []),
        soft_skills=skills.get("soft_skills", []),
        education=json.loads(resume.education) if resume.education else [],
        experience=json.loads(resume.experience) if resume.experience else [],
        summary=resume.summary,
    )


def _get_owned_resume(resume_id: int, db: Session, current_user: User) -> Resume:
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    if resume.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only access your own resumes")
    return resume


@router.post("/upload", response_model=ResumeOut, status_code=status.HTTP_201_CREATED)
def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are allowed")

    safe_filename = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(UPLOAD_DIR, safe_filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        extracted_text = extract_text(file_path, file.filename)
    except Exception as e:
        os.remove(file_path)
        raise HTTPException(status_code=400, detail=f"Could not read the file: {str(e)}")

    if not extracted_text.strip():
        os.remove(file_path)
        raise HTTPException(
            status_code=400,
            detail="Could not extract any text from this file (it might be a scanned image)",
        )

    try:
            analysis = analyze_resume(extracted_text)
    except Exception as e:
            raise HTTPException(status_code=502, detail=f"AI analysis failed: {str(e)}")
    new_resume = Resume(
        user_id=current_user.id,
        file_name=file.filename,
        file_path=file_path,
        extracted_text=extracted_text,
        skills=json.dumps(
            {
                "technical_skills": analysis.get("technical_skills", []),
                "soft_skills": analysis.get("soft_skills", []),
            }
        ),
        education=json.dumps(analysis.get("education", [])),
        experience=json.dumps(analysis.get("experience", [])),
        summary=analysis.get("summary", ""),
    )
    db.add(new_resume)
    db.commit()
    db.refresh(new_resume)

    return build_resume_response(new_resume)


@router.get("/", response_model=List[ResumeOut])
def get_my_resumes(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    resumes = db.query(Resume).filter(Resume.user_id == current_user.id).all()
    return [build_resume_response(r) for r in resumes]


@router.get("/{resume_id}", response_model=ResumeOut)
def get_resume(
    resume_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    resume = _get_owned_resume(resume_id, db, current_user)
    return build_resume_response(resume)


@router.delete("/{resume_id}")
def delete_resume(
    resume_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    resume = _get_owned_resume(resume_id, db, current_user)

    if os.path.exists(resume.file_path):
        os.remove(resume.file_path)

    db.delete(resume)
    db.commit()
    return {"message": "Resume deleted successfully"}


@router.post("/{resume_id}/match", response_model=List[MatchOut])
def match_resume(
    resume_id: int,
    top_k: int = 3,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    resume = _get_owned_resume(resume_id, db, current_user)

    jobs = db.query(Job).all()
    if not jobs:
        raise HTTPException(status_code=400, detail="No jobs available to match against yet")

    matches = match_resume_to_jobs(resume, jobs, top_k=top_k)

    db.query(Recommendation).filter(Recommendation.resume_id == resume.id).delete()
    for match in matches:
        db.add(
            Recommendation(
                resume_id=resume.id,
                job_id=match["job_id"],
                match_score=match["match_score"],
                explanation=match["explanation"],
            )
        )
    db.commit()

    return matches


@router.get("/{resume_id}/matches", response_model=List[MatchOut])
def get_saved_matches(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    resume = _get_owned_resume(resume_id, db, current_user)

    recommendations = (
        db.query(Recommendation)
        .filter(Recommendation.resume_id == resume.id)
        .order_by(Recommendation.match_score.desc())
        .all()
    )

    if not recommendations:
        raise HTTPException(
            status_code=404,
            detail="No matches found yet for this resume. Call POST /resumes/{id}/match first.",
        )

    return [
        MatchOut(
            job_id=r.job_id,
            job_title=r.job.title,
            match_score=r.match_score,
            explanation=r.explanation,
        )
        for r in recommendations
    ]
