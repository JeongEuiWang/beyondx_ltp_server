from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..model.user import User
from ..schema.user import CreateUserRequest

class UserRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def get_user_by_email(self, email: str) -> User | None:
        query = select(User).where(User.email == email)
        result = await self.db_session.execute(query)
        return result.scalar_one_or_none()

    async def get_user_by_id(self, user_id: int) -> User | None :
        query = select(User).where(User.id == user_id)
        result = await self.db_session.execute(query)
        return result.scalar_one_or_none()

    async def create_user(self, request: CreateUserRequest, hashed_password: str) -> User:
        default_role_id = 1
        default_user_level_id = 1

        new_user = User(
            email=request.email,
            first_name=request.first_name,
            last_name=request.last_name,
            phone=request.phone,
            password=hashed_password,
            role_id=default_role_id,
            user_level_id=default_user_level_id,
        )
        self.db_session.add(new_user)
        await self.db_session.flush()

        return new_user
