from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import init_db
from routers import jobs, skills, resume


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="Job Market Trend Analyzer",
    version="0.1.0",
    description="Pulls job listings from Adzuna, extracts trending skills via spaCy, and analyzes résumé gaps with Claude.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(jobs.router)
app.include_router(skills.router)
app.include_router(resume.router)


@app.get("/health", tags=["meta"])
async def health() -> dict:
    return {"status": "ok"}
