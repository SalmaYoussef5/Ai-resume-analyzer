from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from database import engine, Base
from routers import auth_router, jobs_router, resumes_router, career_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Resume Analyzer",
    description="Backend API for analyzing resumes and recommending jobs using AI Agents + RAG",
    version="0.6.0",
)

app.include_router(auth_router.router)
app.include_router(jobs_router.router)
app.include_router(resumes_router.router)
app.include_router(career_router.router)


app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
