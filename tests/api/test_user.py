"""
사용자 등록(회원가입) API 테스트
"""

import pytest
from httpx import AsyncClient
from fastapi import status


class TestUserRegister:
    """회원가입 API 테스트 클래스"""

    @pytest.mark.asyncio
    async def test_sign_up_success(self, client: AsyncClient):
        user_data = {
            "email": "test@example.com",
            "password": "StrongPassword123!",
            "first_name": "길동",
            "last_name": "홍",
            "phone": "010-1234-5678",
        }

        response = await client.post("/api/user/sign-up", json=user_data)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    @pytest.mark.asyncio
    async def test_check_email_available(self, client: AsyncClient):
        response = await client.get("/api/user/check-email?email=available@example.com")

        assert response.status_code == 200
        data = response.json()
        assert data["is_unique"] is True

    @pytest.mark.asyncio
    async def test_check_email_unavailable(self, client: AsyncClient):
        """이미 사용 중인 이메일 확인 테스트"""
        # 먼저 회원가입으로 사용자 생성
        user_data = {
            "email": "taken@example.com",
            "password": "StrongPassword123!",
            "first_name": "길동",
            "last_name": "홍",
            "phone": "010-1234-5678",
        }
        await client.post("/api/user/sign-up", json=user_data)

        # 이미 가입된 이메일로 확인 요청
        response = await client.get("/api/user/check-email?email=taken@example.com")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert data["detail"]["is_unique"] is False
