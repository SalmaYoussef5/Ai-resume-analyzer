from typing import Optional, List
from pydantic import BaseModel, EmailStr


class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class JobCreate(BaseModel):
    title: str
    description: str
    required_skills: str   
    location: Optional[str] = None
    category: Optional[str] = None


class JobUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    required_skills: Optional[str] = None
    location: Optional[str] = None
    category: Optional[str] = None


class JobOut(BaseModel):
    id: int
    title: str
    description: str
    required_skills: str
    location: Optional[str]
    category: Optional[str]
    posted_by_id: int

    class Config:
        from_attributes = True


class ResumeOut(BaseModel):
    id: int
    file_name: str
    technical_skills: List[str] = []
    soft_skills: List[str] = []
    education: List[str] = []
    experience: List[str] = []
    summary: Optional[str] = None


class MatchOut(BaseModel):
    job_id: int
    job_title: str
    match_score: float
    explanation: str

    class Config:
        from_attributes = True


class ImprovementOut(BaseModel):
    missing_skills: List[str]
    advice: str


class CareerQuestion(BaseModel):
    question: str
    resume_id: Optional[int] = None


class CareerAnswerOut(BaseModel):
    answer: str
