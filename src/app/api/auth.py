from fastapi import APIRouter, Depends, HTTPException, status, Response, Cookie
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Annotated, Optional

from ..schema.auth import LoginRequest, LoginResponse, RefreshTokenResponse
from ..service._deps import authServiceDeps
from ..core.auth import TokenData, cookieAuthDeps
from ..core.jwt import decode_token


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest, auth_service: authServiceDeps, response: Response
):
    """
    사용자 로그인 API
    """
    return await auth_service.login(request, response)


@router.get("/refresh", response_model=RefreshTokenResponse)
async def refresh(
    auth_service: authServiceDeps,
    refresh_token: cookieAuthDeps,
    response: Response,
):
    """
    쿠키의 refresh token을 사용하여 새 토큰 발급
    """
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not found in cookie",
        )

    try:
        payload = decode_token(refresh_token)
        user_id = int(payload.get("sub"))
        role_id = payload.get("role_id")

        token_data = TokenData(user_id=user_id, role_id=role_id)
        return await auth_service.refresh_token(token_data, response)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid refresh token: {str(e)}",
        )


@router.post("/logout")
async def logout(response: Response):
    """
    로그아웃 - refresh token 쿠키 삭제
    """
    response.delete_cookie(key="ltp_refresh_token")
    return {"detail": "Successfully logged out"}
