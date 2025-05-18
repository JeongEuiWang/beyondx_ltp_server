from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.session import get_async_session
from ..db.unit_of_work import UnitOfWork


async def get_uow(session: AsyncSession = Depends(get_async_session)) -> UnitOfWork:
    """UnitOfWork 의존성 주입 함수"""
    return UnitOfWork(session) 