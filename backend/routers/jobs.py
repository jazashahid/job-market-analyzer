import asyncio
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from database import get_db
from models.job import Job
from models.skill import Skill
from schemas.job import JobListResponse
from services import adzuna, nlp

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("/fetch", summary="Pull new listings from Adzuna and extract skills")
async def fetch_jobs(
    keywords: str = Query("software engineer", description="Search terms sent to Adzuna"),
    country: str = Query("us", description="Two-letter country code, e.g. us, gb, au"),
    pages: int = Query(1, ge=1, le=10, description="Number of Adzuna pages to fetch (50 results each)"),
    db: AsyncSession = Depends(get_db),
) -> dict:
    inserted = 0
    skipped = 0
    skills_extracted = 0
    pages_fetched = 0

    for page_num in range(1, pages + 1):
        try:
            raw_jobs = await adzuna.fetch_jobs(keywords, country, page_num)
        except Exception as exc:
            if page_num == 1:
                raise HTTPException(status_code=502, detail=f"Adzuna API error: {exc}") from exc
            break  # Later pages failing is non-fatal; commit what we have

        if not raw_jobs:
            break  # Adzuna returned empty — no more results exist

        for raw in raw_jobs:
            existing = await db.scalar(select(Job).where(Job.adzuna_id == raw["adzuna_id"]))
            if existing:
                skipped += 1
                continue

            job = Job(**raw)
            db.add(job)
            await db.flush()

            skills = nlp.extract_skills(raw["description"])
            for skill_name in skills:
                db.add(Skill(job_id=job.id, skill_name=skill_name))
            skills_extracted += len(skills)
            inserted += 1

        await db.commit()
        pages_fetched += 1

        if page_num < pages:
            await asyncio.sleep(0.4)  # polite gap between Adzuna requests

    return {
        "inserted": inserted,
        "skipped": skipped,
        "skills_extracted": skills_extracted,
        "pages_fetched": pages_fetched,
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
