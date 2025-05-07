from fastapi import APIRouter, Response

from ..service._deps import authServiceDeps
from ..core.auth import TokenData, cookieAuthDeps
from ..core.jwt import decode_token
from ..core.exceptions import AuthException
from ..schema.auth import LoginRequest, LoginResponse, RefreshTokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
async def login(
    auth_service: authServiceDeps,
    request: LoginRequest,
    response: Response,
):
    return await auth_service.login(request, response)


@router.get("/refresh", response_model=RefreshTokenResponse)
async def refresh(
    auth_service: authServiceDeps,
    refresh_token: cookieAuthDeps,
    response: Response,
):
    if not refresh_token:
        raise AuthException(message="유효하지 않은 접근입니다.")

    try:
        payload = decode_token(refresh_token)
        user_id = int(payload.get("sub"))
        role_id = payload.get("role_id")

        token_data = TokenData(user_id=user_id, role_id=role_id)
        return await auth_service.refresh_token(token_data, response)
    except Exception:
        raise AuthException(message="유효하지 않은 접근입니다.")


# @router.post("/logout")
# async def logout(response: Response):
#     """
#     로그아웃 - refresh token 쿠키 삭제
#     """
#     response.delete_cookie(key="ltp_refresh_token")
#     return {"detail": "Successfully logged out"}
