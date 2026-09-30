from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models import Job, User
from schemas import JobCreate, JobUpdate, JobOut
from auth import get_current_user

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.get("/", response_model=List[JobOut])
def get_jobs(
    title: Optional[str] = None,
    location: Optional[str] = None,
    category: Optional[str] = None,
    skill: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(Job)

    if title:
        query = query.filter(Job.title.ilike(f"%{title}%"))
    if location:
        query = query.filter(Job.location.ilike(f"%{location}%"))
    if category:
        query = query.filter(Job.category.ilike(f"%{category}%"))
    if skill:
        query = query.filter(Job.required_skills.ilike(f"%{skill}%"))

    return query.all()


@router.get("/{job_id}", response_model=JobOut)
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.post("/", response_model=JobOut, status_code=status.HTTP_201_CREATED)
def create_job(
    job: JobCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    new_job = Job(**job.model_dump(), posted_by_id=current_user.id)
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    return new_job


@router.put("/{job_id}", response_model=JobOut)
def update_job(
    job_id: int,
    updated: JobUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.posted_by_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only edit jobs you posted")

    for key, value in updated.model_dump(exclude_unset=True).items():
        setattr(job, key, value)

    db.commit()
    db.refresh(job)
    return job


@router.delete("/{job_id}")
def delete_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.posted_by_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only delete jobs you posted")

    db.delete(job)
    db.commit()
    return {"message": "Job deleted successfully"}
