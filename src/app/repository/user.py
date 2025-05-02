from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..model.user import User


class UserRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def get_user_by_email(self, email: str):
        """이메일로 사용자 조회"""
        query = select(User).where(User.email == email)
        result = await self.db_session.execute(query)
        return result.scalar_one_or_none()

    async def get_user_by_id(self, user_id: int):
        """ID로 사용자 조회"""
        query = select(User).where(User.id == user_id)
        result = await self.db_session.execute(query)
        return result.scalar_one_or_none()

    async def create_user(self, user_data, hashed_password: str):
        """사용자 생성"""
        default_role_id = 1
        default_user_level_id = 1

        new_user = User(
            email=user_data.email,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            phone=user_data.phone,
            password=hashed_password,
            role_id=default_role_id,
            user_level_id=default_user_level_id,
        )
        self.db_session.add(new_user)
        await self.db_session.commit()

        return new_user
