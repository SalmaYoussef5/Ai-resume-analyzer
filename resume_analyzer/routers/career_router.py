from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Resume, Job, User
from schemas import ImprovementOut, CareerQuestion, CareerAnswerOut
from auth import get_current_user
from agents.career_advisor_agent import suggest_improvements, answer_career_question

router = APIRouter(prefix="/career", tags=["Career Advisor"])


def _get_owned_resume(resume_id: int, db: Session, current_user: User) -> Resume:
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    if resume.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only access your own resumes")
    return resume


@router.post("/resumes/{resume_id}/improve", response_model=ImprovementOut)
def improve_resume(
    resume_id: int,
    job_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    resume = _get_owned_resume(resume_id, db, current_user)

    target_job = None
    if job_id is not None:
        target_job = db.query(Job).filter(Job.id == job_id).first()
        if not target_job:
            raise HTTPException(status_code=404, detail="Target job not found")

    result = suggest_improvements(resume, target_job=target_job)
    return result


@router.post("/ask", response_model=CareerAnswerOut)
def ask_career_question(
    payload: CareerQuestion,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    resume = None
    if payload.resume_id is not None:
        resume = _get_owned_resume(payload.resume_id, db, current_user)

    answer = answer_career_question(payload.question, resume=resume)
    return {"answer": answer}
