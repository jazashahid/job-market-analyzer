import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler

logger = logging.getLogger(__name__)

_scheduler = AsyncIOScheduler()

# Tracks the most recent manual fetch query so the cron job reuses it.
# Defaults to a sensible value until the user performs their first fetch.
_last_query: dict = {"keywords": "software engineer", "country": "us", "pages": 1}


def update_last_query(keywords: str, country: str, pages: int) -> None:
    _last_query.update({"keywords": keywords, "country": country, "pages": pages})


async def _daily_fetch() -> None:
    # Lazy imports to avoid circular dependencies at module load time.
    from database import AsyncSessionLocal
    from services.fetch_service import fetch_and_store

    kw = _last_query["keywords"]
    country = _last_query["country"]
    pages = _last_query["pages"]

    logger.info("Cron: daily fetch starting — keywords=%r country=%s pages=%d", kw, country, pages)
    try:
        async with AsyncSessionLocal() as db:
            result = await fetch_and_store(kw, country, pages, db)
        logger.info(
            "Cron: daily fetch done — inserted=%d skipped=%d skills_extracted=%d",
            result["inserted"],
            result["skipped"],
            result["skills_extracted"],
        )
    except Exception:
        logger.exception("Cron: daily fetch failed")


def start_scheduler() -> None:
    _scheduler.add_job(
        _daily_fetch,
        "interval",
        hours=24,
        id="daily_fetch",
        replace_existing=True,
    )
    _scheduler.start()
    logger.info("Scheduler started — daily job fetch runs every 24 hours")


def stop_scheduler() -> None:
    if _scheduler.running:
        _scheduler.shutdown(wait=False)
        logger.info("Scheduler stopped")
