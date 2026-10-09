from unittest.mock import AsyncMock

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from config import settings
from database import Base, get_db
from main import app

assert "test" in settings.test_database_url.lower(), (
    "Safety check failed: database URL must contain 'test'"
)
test_engine = create_async_engine(settings.test_database_url)


TestSessionLocal = async_sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)


@pytest_asyncio.fixture
async def setup_database():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session(setup_database):
    async with TestSessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def mock_send_email(monkeypatch):
    mock = AsyncMock()
    monkeypatch.setattr("routers.users.send_password_reset_email", mock)
    return mock
