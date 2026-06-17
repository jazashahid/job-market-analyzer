from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, Float, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    adzuna_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(256))
    company: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    location: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    description: Mapped[str] = mapped_column(Text)
    salary_min: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    salary_max: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    category: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    url: Mapped[str] = mapped_column(String(512))
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
