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
from app.core.auth import get_current_user, TokenData
from app.model.user import UserLevel, Role
from app.model._enum import UserLevelEnum, RoleEnum

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"

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


@pytest.fixture(scope="function")
async def setup_database() -> AsyncGenerator[None, None]:
    """테스트 데이터베이스 설정 및 테이블 생성"""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        
    async with TestingSessionLocal() as session:
        default_level = UserLevel(
            id=1,
            user_level=UserLevelEnum.DEFAULT,
            required_amount=0,
            discount_rate=0
        )
        silver_level = UserLevel(
            id=2,
            user_level=UserLevelEnum.SILVER,
            required_amount=1000000,
            discount_rate=0.03
        )
        gold_level = UserLevel(
            id=3,
            user_level=UserLevelEnum.GOLD,
            required_amount=5000000,
            discount_rate=0.05
        )
        vip_level = UserLevel(
            id=4,
            user_level=UserLevelEnum.VIP,
            required_amount=10000000,
            discount_rate=0.1
        )
        
        admin_role = Role(id=1, role=RoleEnum.ADMIN)
        user_role = Role(id=2, role=RoleEnum.USER)
        
        session.add_all([
            default_level, silver_level, gold_level, vip_level,
            admin_role, user_role
        ])
        await session.commit()

    yield

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def db_session(setup_database) -> AsyncGenerator[AsyncSession, None]:
    """테스트에서 사용할 독립된 데이터베이스 세션"""
    async with TestingSessionLocal() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def client(db_session) -> AsyncGenerator[AsyncClient, None]:
    """테스트 클라이언트"""
    from app.main import app
    from app.core.auth import get_current_user, TokenData

    async def override_get_async_session() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    async def override_auth():
        return TokenData(user_id=1, role_id=1)
    
    app.dependency_overrides[get_async_session] = override_get_async_session
    
    app.dependency_overrides[get_current_user] = override_auth

    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, 
        base_url="http://test", 
        follow_redirects=True
    ) as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def sync_client(db_session) -> Generator[TestClient, None, None]:
    """동기식 테스트 클라이언트 (일부 테스트에 필요할 수 있음)"""
    from app.main import app

    async def override_get_async_session() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_async_session] = override_get_async_session

    with TestClient(app=app) as client:
        yield client

    app.dependency_overrides.clear()
