"""
사용자 서비스 테스트
"""

import pytest
from httpx import AsyncClient
from fastapi import status

from app.service.user import UserService
from app.repository.user import UserRepository
from app.schema.user import CreateUserRequest


class TestUserService:
    """사용자 서비스 테스트 클래스"""

    @pytest.mark.asyncio
    async def test_create_user(self, client: AsyncClient, db_session):
        """사용자 생성 서비스 테스트"""
        # 서비스와 리포지토리 생성
        user_repository = UserRepository(db_session)
        user_service = UserService(user_repository)

        # 테스트용 사용자 데이터
        user_data = CreateUserRequest(
            email="service_test@example.com",
            password="StrongPassword123!",
            first_name="서비스",
            last_name="테스트",
            phone="010-5555-5555"
        )

        # 사용자 생성
        result = await user_service.create_user(user_data)
        
        # 결과 확인
        assert result.success is True

        # 중복 이메일 확인
        with pytest.raises(Exception):
            await user_service.create_user(user_data)

    @pytest.mark.asyncio
    async def test_check_email(self, client: AsyncClient, db_session):
        """이메일 중복 확인 서비스 테스트"""
        # 서비스와 리포지토리 생성
        user_repository = UserRepository(db_session)
        user_service = UserService(user_repository)

        # 새 이메일 확인
        result = await user_service.check_email("new_email@example.com")
        assert result.is_unique is True

        # 테스트용 사용자 생성
        user_data = CreateUserRequest(
            email="check_email_test@example.com",
            password="StrongPassword123!",
            first_name="이메일",
            last_name="체크",
            phone="010-7777-7777"
        )
        await user_service.create_user(user_data)

        # 중복 이메일 확인
        result = await user_service.check_email("check_email_test@example.com")
        assert result.is_unique is False

    @pytest.mark.asyncio
    async def test_get_user_info(self, client: AsyncClient, db_session):
        """사용자 정보 조회 서비스 테스트"""
        # 서비스와 리포지토리 생성
        user_repository = UserRepository(db_session)
        user_service = UserService(user_repository)

        # 먼저 회원가입 API로 사용자 생성
        user_data = {
            "email": "user_info_service@example.com",
            "password": "StrongPassword123!",
            "first_name": "정보조회",
            "last_name": "서비스",
            "phone": "010-9999-9999",
        }
        sign_up_response = await client.post("/api/user/sign-up", json=user_data)
        assert sign_up_response.status_code == status.HTTP_200_OK

        # 로그인하여 사용자 ID 얻기
        login_data = {
            "email": "user_info_service@example.com",
            "password": "StrongPassword123!",
        }
        login_response = await client.post("/api/auth/login", json=login_data)
        assert login_response.status_code == status.HTTP_200_OK
        token_data = login_response.json()["access"]
        
        # 토큰에서 user_id 추출
        headers = {"Authorization": f"Bearer {token_data['token']}"}
        user_response = await client.get("/api/user/", headers=headers)
        user_id = user_response.json()["id"]

        # 서비스를 통해 사용자 정보 조회
        user_info = await user_service.get_user_info(user_id)
        
        # 결과 확인
        assert user_info.email == "user_info_service@example.com"
        assert user_info.first_name == "정보조회"
        assert user_info.last_name == "서비스"
        assert user_info.phone == "010-9999-9999"
        assert hasattr(user_info, "total_payment_amount")
        assert hasattr(user_info, "user_level_id") 