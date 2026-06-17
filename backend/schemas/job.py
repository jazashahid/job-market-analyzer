from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class JobRead(BaseModel):
    id: int
    adzuna_id: str
    title: str
    company: Optional[str] = None
    location: Optional[str] = None
    description: str
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    category: Optional[str] = None
    url: str
    fetched_at: datetime

    model_config = {"from_attributes": True}


class JobListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    jobs: List[JobRead]
