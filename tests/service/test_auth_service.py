"""
인증 서비스 테스트
"""

import pytest
from httpx import AsyncClient
from fastapi import status
from jose import jwt
from app.core.config import settings


class TestAuthService:
    """인증 서비스 테스트 클래스"""

    @pytest.mark.asyncio
    async def test_password_verify(self, client: AsyncClient):
        """비밀번호 검증 테스트"""
        # 회원가입
        user_data = {
            "email": "verify_test@example.com",
            "password": "StrongPassword123!",
            "first_name": "비밀번호",
            "last_name": "검증",
            "phone": "010-1212-3434",
        }
        await client.post("/api/user/sign-up", json=user_data)

        # 올바른 비밀번호로 로그인
        correct_login = {
            "email": "verify_test@example.com",
            "password": "StrongPassword123!",
        }
        response = await client.post("/api/auth/login", json=correct_login)
        assert response.status_code == status.HTTP_200_OK

        # 잘못된 비밀번호로 로그인
        wrong_login = {
            "email": "verify_test@example.com",
            "password": "WrongPassword123!",
        }
        response = await client.post("/api/auth/login", json=wrong_login)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_jwt_token_creation(self, client: AsyncClient):
        """JWT 토큰 생성 테스트"""
        # 회원가입
        user_data = {
            "email": "jwt_test@example.com",
            "password": "StrongPassword123!",
            "first_name": "토큰",
            "last_name": "테스트",
            "phone": "010-8989-7878",
        }
        await client.post("/api/user/sign-up", json=user_data)

        # 로그인하여 토큰 획득
        login_data = {"email": "jwt_test@example.com", "password": "StrongPassword123!"}
        response = await client.post("/api/auth/login", json=login_data)

        data = response.json()
        assert "access" in data

        # 토큰 검증
        token = data["access"]["token"]
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )

        # 페이로드에 필요한 정보가 있는지 확인
        assert "sub" in payload
        assert "role_id" in payload
        assert "exp" in payload

    @pytest.mark.asyncio
    async def test_token_expiration_check(self, client: AsyncClient):
        """토큰 만료시간 확인 테스트"""
        # 회원가입 및 로그인
        user_data = {
            "email": "expire_test@example.com",
            "password": "StrongPassword123!",
            "first_name": "만료",
            "last_name": "테스트",
            "phone": "010-5656-4545",
        }
        await client.post("/api/user/sign-up", json=user_data)

        # 로그인하여 토큰 획득
        login_data = {
            "email": "expire_test@example.com",
            "password": "StrongPassword123!",
        }
        response = await client.post("/api/auth/login", json=login_data)

        data = response.json()
        token = data["access"]["token"]
        expires_at = data["access"]["expires_at"]

        # 만료시간이 설정되어 있는지 확인
        assert expires_at is not None

        # 페이로드의 만료시간 확인
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        assert "exp" in payload
