"""
사용자 주소 API 테스트
"""

import pytest
from httpx import AsyncClient
from fastapi import status
from app.model._enum import LocationTypeEnum


class TestUserAddressAPI:
    """사용자 주소 API 테스트 클래스"""

    @pytest.mark.asyncio
    async def test_create_user_address(self, client: AsyncClient):
        """사용자 주소 등록 테스트"""
        user_data = {
            "email": "address_test@example.com",
            "password": "StrongPassword123!",
            "first_name": "길동",
            "last_name": "홍",
            "phone": "010-1234-5678",
        }
        await client.post("/api/user/sign-up", json=user_data)

        login_data = {
            "email": "address_test@example.com",
            "password": "StrongPassword123!",
        }
        login_response = await client.post("/api/auth/login", json=login_data)
        access_token = login_response.json()["access"]["token"]

        address_data = {
            "name": "회사",
            "state": "서울특별시",
            "county": "강남구",
            "city": "삼성동",
            "zip_code": "12345",
            "location_type": LocationTypeEnum.COMMERCIAL.name,
            "address": "테헤란로 123"
        }

        response = await client.post(
            "/api/user/address",
            json=address_data,
            headers={"Authorization": f"Bearer {access_token}"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "id" in data
        assert "user_id" in data
        assert "name" in data
        assert "state" in data
        assert "county" in data
        assert "city" in data
        assert "zip_code" in data
        assert "location_type" in data
        assert "address" in data

    @pytest.mark.asyncio
    async def test_get_user_addresses(self, client: AsyncClient):
        """사용자 주소 목록 조회 테스트"""
        user_data = {
            "email": "address_list_test@example.com",
            "password": "StrongPassword123!",
            "first_name": "주소",
            "last_name": "목록",
            "phone": "010-9876-5432",
        }
        await client.post("/api/user/sign-up", json=user_data)

        login_data = {
            "email": "address_list_test@example.com",
            "password": "StrongPassword123!",
        }
        login_response = await client.post("/api/auth/login", json=login_data)
        access_token = login_response.json()["access"]["token"]

        address_data = {
            "name": "집",
            "state": "서울특별시",
            "county": "송파구",
            "city": "잠실동",
            "zip_code": "54321",
            "location_type": LocationTypeEnum.RESIDENTIAL.name,
            "address": "올림픽로 456"
        }

        await client.post(
            "/api/user/address",
            json=address_data,
            headers={"Authorization": f"Bearer {access_token}"}
        )

        response = await client.get(
            "/api/user/address",
            headers={"Authorization": f"Bearer {access_token}"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        
        assert len(data) >= 1
        
        assert "id" in data[0]
        assert "name" in data[0]
        assert "state" in data[0]
        assert "county" in data[0]
        assert "city" in data[0]
        assert "zip_code" in data[0]
        assert "location_type" in data[0] 