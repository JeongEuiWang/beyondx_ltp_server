from fastapi import HTTPException

from app.repository.user_level import UserLevelRepository
from app.schema.user_level import UserLevelResponse
from typing import List

class UserLevelService:
    def __init__(self, user_level_repository: UserLevelRepository):
        self.user_level_repository = user_level_repository

    async def get_user_levels(self) -> List[UserLevelResponse]:
        user_levels = await self.user_level_repository.get_user_levels()
        return [UserLevelResponse.model_validate(user_level) for user_level in user_levels]
