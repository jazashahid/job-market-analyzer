from datetime import datetime, timezone
from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Skill(Base):
    __tablename__ = "skills"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"), index=True)
    skill_name: Mapped[str] = mapped_column(String(128), index=True)
    extracted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
