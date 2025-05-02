from fastapi import Depends
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from typing import Annotated, AsyncGenerator
from app.core.config import settings

engine = create_async_engine(settings.DB_URL, pool_pre_ping=True, echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session


sessionDeps = Annotated[AsyncSession, Depends(get_async_session)]
