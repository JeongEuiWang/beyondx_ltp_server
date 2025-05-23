from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..model.user import UserLevel


class UserLevelRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def get_level_by_id(
        self,
        id: int,
    ) -> UserLevel | None:
        query = select(UserLevel).where(UserLevel.id == id)
        result = await self.db_session.execute(query)
        return result.scalar_one_or_none()
