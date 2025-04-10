from app.entity import User
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db.config import transactional
class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, user: User) -> User:
        user = self.model(user)
        self.db.add(user)
        await self.db.flush()
        return user