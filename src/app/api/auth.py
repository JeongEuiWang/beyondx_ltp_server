from fastapi import APIRouter, Response, Depends
from ..service import AuthService
from ..core.jwt import decode_token
from ..core.exceptions import AuthException
from ..schema.auth import LoginRequest, LoginResponse, RefreshTokenResponse
from ..core.uow import get_uow
from ..db.unit_of_work import UnitOfWork
from ..core.auth import get_refresh_token_from_cookie
router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    response: Response,
    uow: UnitOfWork = Depends(get_uow),
):
    auth_service = AuthService(uow)
    return await auth_service.login(request, response)


@router.post("/refresh", response_model=RefreshTokenResponse)
async def refresh(
    response: Response,
    uow: UnitOfWork = Depends(get_uow),
    refresh_token: str = Depends(get_refresh_token_from_cookie),
):
    if not refresh_token:
        raise AuthException(message="유효하지 않은 접근입니다.")

    try:
        payload = decode_token(refresh_token)
        user_id = int(payload.get("sub"))
        role_id = payload.get("role_id")
        
        auth_service = AuthService(uow)
        return await auth_service.refresh_token(user_id, role_id, response)
    except Exception:
        raise AuthException(message="유효하지 않은 접근입니다.")
