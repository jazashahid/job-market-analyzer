from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from database import get_db
from models.skill import Skill
from models.job import Job
from schemas.skill import TrendingSkillsResponse, SkillCount, SkillHistoryResponse, SkillHistoryPoint

router = APIRouter(prefix="/skills", tags=["skills"])


@router.get("/trending", response_model=TrendingSkillsResponse, summary="Top N skills by frequency")
async def trending_skills(
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> TrendingSkillsResponse:
    rows = await db.execute(
        select(Skill.skill_name, func.count(Skill.id).label("cnt"))
        .group_by(Skill.skill_name)
        .order_by(func.count(Skill.id).desc())
        .limit(limit)
    )
    skills = [SkillCount(skill_name=r.skill_name, count=r.cnt) for r in rows]
    total_jobs = await db.scalar(select(func.count()).select_from(Job))
    return TrendingSkillsResponse(skills=skills, total_jobs_analyzed=total_jobs or 0)


@router.get("/history", response_model=SkillHistoryResponse, summary="Daily skill frequency for top-N skills")
async def skill_history(
    top_n: int = Query(5, ge=1, le=20, description="Track the top-N most frequent skills over time"),
    db: AsyncSession = Depends(get_db),
) -> SkillHistoryResponse:
    # Resolve which skills are in the top-N
    top_rows = await db.execute(
        select(Skill.skill_name)
        .group_by(Skill.skill_name)
        .order_by(func.count(Skill.id).desc())
        .limit(top_n)
    )
    top_skills = [r.skill_name for r in top_rows]

    if not top_skills:
        return SkillHistoryResponse(history=[])

    # Aggregate by date using SQLite's date() function
    rows = await db.execute(
        select(
            func.date(Skill.extracted_at).label("day"),
            Skill.skill_name,
            func.count(Skill.id).label("cnt"),
        )
        .where(Skill.skill_name.in_(top_skills))
        .group_by("day", Skill.skill_name)
        .order_by("day")
    )

    history = [
        SkillHistoryPoint(date=str(r.day), skill_name=r.skill_name, count=r.cnt)
        for r in rows
    ]
    return SkillHistoryResponse(history=history)
