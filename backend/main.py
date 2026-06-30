from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from starlette.requests import Request

from database import init_db
from limiter import limiter
from routers import jobs, skills, resume
from services.scheduler import start_scheduler, stop_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    start_scheduler()
    yield
    stop_scheduler()


app = FastAPI(
    title="Job Market Trend Analyzer",
    version="0.1.0",
    description="Pulls job listings from Adzuna, extracts trending skills via spaCy, and analyzes résumé gaps with Claude.",
    lifespan=lifespan,
)

app.state.limiter = limiter


async def _json_rate_limit_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    return JSONResponse(
        status_code=429,
        content={"error": f"Rate limit exceeded: {exc.detail}. Please wait before retrying."},
    )


app.add_exception_handler(RateLimitExceeded, _json_rate_limit_handler)

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
