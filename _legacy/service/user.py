from app.repository.user import UserRepository
from app.core.db.config import sessionDeps
from sqlalchemy.ext.asyncio import AsyncSession
from app.schema.request import CheckEmailRequest
from app.schema.response import CheckEmailResponse

class UserService:
    def __init__(self, db: AsyncSession = sessionDeps):
      self.repository = UserRepository(db)

    async def check_email(self, request: CheckEmailRequest) -> CheckEmailResponse:
        
        return await self.repository.check_email(request, self.db)
