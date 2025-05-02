import asyncio
import pytest
import os
from typing import AsyncGenerator, Generator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport

from app.core.config import settings
from app.db.base import Base
from app.main import app
from app.db.session import get_async_session

# 테스트용 SQLite 데이터베이스 경로
TEST_DB_PATH = "test_db.sqlite"
TEST_DB_URL = f"sqlite+aiosqlite:///{TEST_DB_PATH}"

# 비동기 엔진과 세션 생성 (SQLite 사용)
test_engine = create_async_engine(
    TEST_DB_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Pytest용 이벤트 루프 생성"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def setup_database() -> AsyncGenerator[None, None]:
    """테스트 데이터베이스 설정 및 테이블 생성"""
    # 테이블 생성
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    # 테스트 후 정리
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    # SQLite 파일 삭제
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)


@pytest.fixture
async def db_session(setup_database) -> AsyncGenerator[AsyncSession, None]:
    """테스트에서 사용할 독립된 데이터베이스 세션"""
    async with TestingSessionLocal() as session:
        yield session
        # 각 테스트 후 롤백
        await session.rollback()


@pytest.fixture
async def client(db_session) -> AsyncGenerator[AsyncClient, None]:
    """테스트 클라이언트"""

    # DB 세션 의존성 오버라이드
    async def override_get_async_session() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_async_session] = override_get_async_session

    # ASGITransport 사용하여 AsyncClient 생성
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    # 테스트 후 의존성 복원
    app.dependency_overrides.clear()


@pytest.fixture
def sync_client(db_session) -> Generator[TestClient, None, None]:
    """동기식 테스트 클라이언트 (일부 테스트에 필요할 수 있음)"""

    # DB 세션 의존성 오버라이드
    async def override_get_async_session() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_async_session] = override_get_async_session

    with TestClient(app=app) as client:
        yield client

    # 테스트 후 의존성 복원
    app.dependency_overrides.clear()
