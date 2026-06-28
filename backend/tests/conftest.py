"""
Shared pytest fixtures for the Job Market Analyzer backend.

Strategy:
- Force DATABASE_URL to an in-memory SQLite before any app module is imported,
  so database.py picks it up when Settings() is first instantiated.
- Build a separate _test_engine with StaticPool so every connection (the seeding
  session AND the sessions created inside request handlers) lands on the exact
  same in-memory database.
- Override the get_db dependency to use _test_engine's session factory.
- ASGITransport does NOT trigger the FastAPI lifespan, so init_db() never runs
  during tests; we create and drop tables ourselves around each test.
- Reset the slowapi rate-limit storage after each test so limits don't bleed
  across tests.
"""

import os

# Must be set BEFORE any app module is imported (database.py reads this at
# module level when Settings() is first instantiated).
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ.setdefault("ADZUNA_APP_ID", "test_app_id")
os.environ.setdefault("ADZUNA_APP_KEY", "test_app_key")
os.environ.setdefault("ANTHROPIC_API_KEY", "test_anthropic_key")

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool

_TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# StaticPool forces all async connections to share a single underlying
# SQLite connection, which is necessary for the in-memory DB to be visible
# across different AsyncSession objects within the same test.
_test_engine = create_async_engine(
    _TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
_TestSessionLocal = async_sessionmaker(
    _test_engine, expire_on_commit=False, class_=AsyncSession
)


@pytest_asyncio.fixture(autouse=True)
async def _tables():
    """Create tables before each test, drop them after."""
    from database import Base
    from models import job as _job_model  # noqa: F401 — register with Base.metadata
    from models import skill as _skill_model  # noqa: F401

    async with _test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with _test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(autouse=True)
async def _reset_limiter():
    """Clear slowapi's in-memory counters after each test."""
    yield
    try:
        from limiter import limiter
        limiter._storage.reset()
    except Exception:
        pass


@pytest_asyncio.fixture
async def db_session():
    """Direct AsyncSession on the test DB for seeding data."""
    async with _TestSessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def client():
    """
    HTTP test client wired to the FastAPI app.

    get_db is overridden so every request handler uses _test_engine instead
    of the production engine defined in database.py.
    """
    from main import app
    from database import get_db

    async def _override_get_db():
        async with _TestSessionLocal() as session:
            yield session

    app.dependency_overrides[get_db] = _override_get_db
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac
    app.dependency_overrides.clear()
