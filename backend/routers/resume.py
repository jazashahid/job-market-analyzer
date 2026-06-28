from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from database import get_db
from limiter import limiter
from models.skill import Skill
from services import anthropic_client

router = APIRouter(prefix="/resume", tags=["resume"])


class ResumeAnalyzeRequest(BaseModel):
    resume_text: str = Field(..., min_length=50, description="Full text of the résumé")
    top_n_skills: int = Field(30, ge=5, le=50, description="How many trending skills to compare against")


class ResumeAnalyzeResponse(BaseModel):
    match_score: int
    summary: str
    skills_you_have: List[str]
    skills_you_need: List[str]
    recommendations: List[str]


@router.post(
    "/analyze",
    response_model=ResumeAnalyzeResponse,
    summary="Analyze résumé against trending skills via Anthropic",
)
@limiter.limit("5/minute")
async def analyze_resume(
    request: Request,
    body: ResumeAnalyzeRequest,
    db: AsyncSession = Depends(get_db),
) -> ResumeAnalyzeResponse:
    # Fetch the current top trending skills from the DB
    rows = await db.execute(
        select(Skill.skill_name)
        .group_by(Skill.skill_name)
        .order_by(func.count(Skill.id).desc())
        .limit(body.top_n_skills)
    )
    trending = [r.skill_name for r in rows]

    if not trending:
        raise HTTPException(
            status_code=404,
            detail="No skills data found. Fetch job listings first via GET /jobs/fetch.",
        )

    try:
        result = await anthropic_client.analyze_resume_gap(body.resume_text, trending)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Anthropic API error: {exc}") from exc

    return ResumeAnalyzeResponse(**result)
