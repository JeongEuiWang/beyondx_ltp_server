from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.model.user import UserLevel


class UserLevelRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def get_user_levels(
        self,
    ) -> List[UserLevel]:
        query = select(UserLevel)
        result = await self.db_session.execute(query)
        return result.scalars().all()
