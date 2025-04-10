from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from app.core.config import settings
from typing import Annotated
from fastapi import Depends
from typing import AsyncGenerator
import logging

logger = logging.getLogger(__name__)

print(settings)

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session

async def create_all():
   
    from app.entity import ( 
        CargoShippingMethod, 
        CargoType, 
        Quote, 
        QuoteLocation, 
        QuoteCargo,
        Client, 
        ClientLevel, 
        ClientAddress,
        ServiceAreaType, 
        ServiceTimezone, 
        ServiceRegion, 
        ServiceAreaCode,
        User, 
        Role
    )

    async with engine.begin() as conn:
        logger.info("Creating all tables if they don't exist")
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()

engine = create_async_engine (
    settings.DB_URL,
    pool_pre_ping=True
)

async_session = async_sessionmaker(engine, expire_on_commit=False)

sessionDeps = Annotated[AsyncSession, Depends(get_async_session, use_cache=True)]

Base = declarative_base()



