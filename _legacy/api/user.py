
from app.schema.request import CheckEmailRequest
from app.schema.response import CheckEmailResponse
from app.core.db.config import sessionDeps
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends
from app.service.user import UserService
router = APIRouter()


@router.get('/check-email', response_model=CheckEmailResponse)
async def check_email(request: CheckEmailRequest, db: AsyncSession = sessionDeps):
    service = UserService(db)

    return await service.check_email(request, db)

@router.post('/', response_model=CheckEmailResponse)
async def sign_up(request: CheckEmailRequest, db: AsyncSession = sessionDeps):
    service = UserService(db)
  
    return await service.check_email(request, db)

# @prouter.get('/')