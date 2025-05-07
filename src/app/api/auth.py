from fastapi import APIRouter, Response
from ..service import AuthService
from ..core.jwt import decode_token
from ..core.exceptions import AuthException
from ..schema.auth import LoginRequest, LoginResponse, RefreshTokenResponse
from ..core.dependencies import container

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    response: Response,
    auth_service: AuthService = container.get("auth_service")
):
    return await auth_service.login(request, response)


@router.get("/refresh", response_model=RefreshTokenResponse)
async def refresh(
    response: Response,
    auth_service: AuthService = container.get("auth_service"),
    refresh_token: str = container.get("refresh_from_cookie"),
):
    if not refresh_token:
        raise AuthException(message="유효하지 않은 접근입니다.")

    try:
        payload = decode_token(refresh_token)
        user_id = int(payload.get("sub"))
        role_id = payload.get("role_id")

        return await auth_service.refresh_token(user_id, role_id, response)
    except Exception:
        raise AuthException(message="유효하지 않은 접근입니다.")


# @router.post("/logout")
# async def logout(response: Response):
#     """
#     로그아웃 - refresh token 쿠키 삭제
#     """
#     response.delete_cookie(key="ltp_refresh_token")
#     return {"detail": "Successfully logged out"}
