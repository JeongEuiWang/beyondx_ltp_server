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

    @pytest.mark.asyncio
    async def test_get_user_info(self, client: AsyncClient):
        """사용자 정보 조회 테스트"""
        # 먼저 회원가입
        user_data = {
            "email": "info_test@example.com",
            "password": "StrongPassword123!",
            "first_name": "정보",
            "last_name": "조회",
            "phone": "010-8765-4321",
        }
        await client.post("/api/user/sign-up", json=user_data)

        # 로그인하여 토큰 획득
        login_data = {
            "email": "info_test@example.com",
            "password": "StrongPassword123!",
        }
        login_response = await client.post("/api/auth/login", json=login_data)
        access_token = login_response.json()["access"]["token"]

        # 사용자 정보 조회
        response = await client.get(
            "/api/user/",
            headers={"Authorization": f"Bearer {access_token}"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # 응답에 필요한 필드들이 있는지 확인
        assert "id" in data
        assert "email" in data
        assert "first_name" in data
        assert "last_name" in data
        assert "phone" in data
        assert "total_payment_amount" in data
        assert "user_level_id" in data
        
        # 가입한 사용자 정보가 올바른지 확인
        assert data["email"] == "info_test@example.com"
        assert data["first_name"] == "정보"
        assert data["last_name"] == "조회"
        assert data["phone"] == "010-8765-4321"
