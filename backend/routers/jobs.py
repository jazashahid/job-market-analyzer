from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from database import get_db
from models.job import Job
from schemas.job import JobListResponse
from services.fetch_service import fetch_and_store
from services.scheduler import update_last_query

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("/fetch", summary="Pull new listings from Adzuna and extract skills")
async def fetch_jobs(
    keywords: str = Query("software engineer", description="Search terms sent to Adzuna"),
    country: str = Query("us", description="Two-letter country code, e.g. us, gb, au"),
    pages: int = Query(1, ge=1, le=10, description="Number of Adzuna pages to fetch (50 results each)"),
    db: AsyncSession = Depends(get_db),
) -> dict:
    update_last_query(keywords, country, pages)
    try:
        return await fetch_and_store(keywords, country, pages, db)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Adzuna API error: {exc}") from exc


@router.get("", response_model=JobListResponse, summary="List stored job listings (paginated)")
async def list_jobs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, le=100),
    role: Optional[str] = Query(None, description="Filter by job title (case-insensitive partial match)"),
    db: AsyncSession = Depends(get_db),
) -> JobListResponse:
    offset = (page - 1) * page_size

    base = select(Job)
    count_base = select(func.count()).select_from(Job)

    if role:
        base = base.where(Job.title.ilike(f"%{role}%"))
        count_base = count_base.where(Job.title.ilike(f"%{role}%"))

    total = await db.scalar(count_base)
    result = await db.execute(
        base.order_by(Job.fetched_at.desc()).offset(offset).limit(page_size)
    )
    jobs = result.scalars().all()
    return JobListResponse(total=total or 0, page=page, page_size=page_size, jobs=list(jobs))
