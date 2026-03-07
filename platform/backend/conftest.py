"""Pytest configuration and fixtures."""

import os

import pytest

# Use file-based SQLite for tests (in-memory creates separate DB per connection)
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test_db.sqlite"

# Clear settings cache so tests get test config
from core.config import get_settings

get_settings.cache_clear()

pytest_plugins = ["pytest_asyncio"]


@pytest.fixture(scope="session")
def event_loop_policy():
    """Use default event loop policy for asyncio."""
    import asyncio
    return asyncio.DefaultEventLoopPolicy()


@pytest.fixture(scope="session", autouse=True)
def init_test_db():
    """Ensure database tables exist before any test runs."""
    import asyncio
    from core.database import init_db

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(init_db())
    loop.close()
