"""SQLAlchemy async engine and session for PostgreSQL."""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from core.config import get_settings

settings = get_settings()

# Convert postgresql:// to postgresql+asyncpg:// if needed
database_url = settings.database_url
if database_url.startswith("postgresql://") and "+asyncpg" not in database_url:
    database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)

# Pool options only for PostgreSQL (SQLite doesn't support them)
engine_kwargs: dict = {
    "echo": settings.debug,
    "pool_pre_ping": True,
}
if "postgresql" in database_url or "asyncpg" in database_url:
    engine_kwargs["pool_size"] = 10
    engine_kwargs["max_overflow"] = 20

engine = create_async_engine(database_url, **engine_kwargs)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    """SQLAlchemy declarative base."""

    pass


async def init_db() -> None:
    """Initialize database (create tables if not exist)."""
    async with engine.begin() as conn:
        from models import audit_log, user  # noqa: F401

        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """Close database connections."""
    await engine.dispose()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting async database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
