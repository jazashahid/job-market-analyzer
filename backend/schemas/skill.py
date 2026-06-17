from typing import List
from pydantic import BaseModel


class SkillCount(BaseModel):
    skill_name: str
    count: int


class TrendingSkillsResponse(BaseModel):
    skills: List[SkillCount]
    total_jobs_analyzed: int


class SkillHistoryPoint(BaseModel):
    date: str
    skill_name: str
    count: int


class SkillHistoryResponse(BaseModel):
    history: List[SkillHistoryPoint]
