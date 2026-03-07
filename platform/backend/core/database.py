"""SQLAlchemy async engine and session for PostgreSQL / Neon."""

import os
import ssl
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from core.config import get_settings

settings = get_settings()

database_url = settings.database_url
if database_url.startswith("postgresql://") and "+asyncpg" not in database_url:
    database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql+asyncpg://", 1)

is_serverless = os.environ.get("VERCEL") == "1"
is_sqlite = "sqlite" in database_url

engine_kwargs: dict = {
    "echo": settings.debug,
    "pool_pre_ping": True,
}

if not is_sqlite:
    if is_serverless:
        engine_kwargs["pool_size"] = 1
        engine_kwargs["max_overflow"] = 2
        engine_kwargs["pool_recycle"] = 300
    else:
        engine_kwargs["pool_size"] = 10
        engine_kwargs["max_overflow"] = 20

    is_neon = ".neon." in database_url or "neon.tech" in database_url
    if is_neon or "sslmode=require" in database_url:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        engine_kwargs["connect_args"] = {"ssl": ctx}
        database_url = database_url.replace("?sslmode=require", "").replace("&sslmode=require", "")

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
