import asyncio
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models.job import Job
from models.skill import Skill
from services import adzuna, nlp

logger = logging.getLogger(__name__)


async def fetch_and_store(
    keywords: str,
    country: str,
    pages: int,
    db: AsyncSession,
) -> dict:
    """Fetch jobs from Adzuna, deduplicate, extract skills, and persist to DB.

    Raises on page-1 failure so callers can surface a 502; later page
    failures are logged and treated as non-fatal.
    """
    inserted = 0
    skipped = 0
    skills_extracted = 0
    pages_fetched = 0

    for page_num in range(1, pages + 1):
        try:
            raw_jobs = await adzuna.fetch_jobs(keywords, country, page_num)
        except Exception as exc:
            if page_num == 1:
                raise
            logger.warning("Page %d fetch failed (non-fatal): %s", page_num, exc)
            break

        if not raw_jobs:
            break

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
            await asyncio.sleep(0.4)

    return {
        "inserted": inserted,
        "skipped": skipped,
        "skills_extracted": skills_extracted,
        "pages_fetched": pages_fetched,
    }
