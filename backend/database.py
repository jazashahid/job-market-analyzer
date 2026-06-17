from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from pydantic_settings import BaseSettings
from typing import AsyncGenerator

# Resolve .env from the project root regardless of the working directory
_ENV_FILE = Path(__file__).parent.parent / ".env"


class Settings(BaseSettings):
    ADZUNA_APP_ID: str = ""
    ADZUNA_APP_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/jobs.db"

    model_config = {"env_file": str(_ENV_FILE), "env_file_encoding": "utf-8", "extra": "ignore"}


settings = Settings()

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False},
)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


async def init_db() -> None:
    # Import models so SQLAlchemy registers them with Base before create_all
    from models import job, skill  # noqa: F401
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
