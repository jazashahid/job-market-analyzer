from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from database import get_db
from models.job import Job
from models.skill import Skill
from schemas.job import JobRead, JobListResponse
from services import adzuna, nlp

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("/fetch", summary="Pull new listings from Adzuna and extract skills")
async def fetch_jobs(
    keywords: str = Query("software engineer", description="Search terms sent to Adzuna"),
    country: str = Query("us", description="Two-letter country code, e.g. us, gb, au"),
    page: int = Query(1, ge=1),
    results_per_page: int = Query(50, le=50),
    db: AsyncSession = Depends(get_db),
) -> dict:
    try:
        raw_jobs = await adzuna.fetch_jobs(keywords, country, page, results_per_page)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Adzuna API error: {exc}") from exc

    inserted = 0
    skipped = 0
    skills_extracted = 0

    for raw in raw_jobs:
        # Idempotent: skip listings we already have
        existing = await db.scalar(select(Job).where(Job.adzuna_id == raw["adzuna_id"]))
        if existing:
            skipped += 1
            continue

        job = Job(**raw)
        db.add(job)
        await db.flush()  # assigns job.id before commit

        skills = nlp.extract_skills(raw["description"])
        for skill_name in skills:
            db.add(Skill(job_id=job.id, skill_name=skill_name))
        skills_extracted += len(skills)
        inserted += 1

    await db.commit()

    return {
        "inserted": inserted,
        "skipped": skipped,
        "skills_extracted": skills_extracted,
    }


@router.get("", response_model=JobListResponse, summary="List stored job listings (paginated)")
async def list_jobs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, le=100),
    db: AsyncSession = Depends(get_db),
) -> JobListResponse:
    offset = (page - 1) * page_size
    total = await db.scalar(select(func.count()).select_from(Job))
    result = await db.execute(
        select(Job).order_by(Job.fetched_at.desc()).offset(offset).limit(page_size)
    )
    jobs = result.scalars().all()
    return JobListResponse(total=total or 0, page=page, page_size=page_size, jobs=list(jobs))
