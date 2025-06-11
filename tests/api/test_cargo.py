"""
화물(Cargo) API 테스트
"""

import pytest
from httpx import AsyncClient
from fastapi import status


class TestCargoAPI:
    """화물 API 테스트 클래스"""

    @pytest.mark.asyncio
    async def test_get_cargo_transportation(self, client: AsyncClient):
        """화물 운송 유형 조회 테스트"""
        response = await client.get("/api/cargo/transportation")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        
        if data:
            assert "id" in data[0]
            assert "name" in data[0]
            assert "description" in data[0]
    
    @pytest.mark.asyncio
    async def test_get_cargo_accessorial(self, client: AsyncClient):
        """화물 부가 서비스 조회 테스트"""
        response = await client.get("/api/cargo/accessorial")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        
        if data:
            assert "id" in data[0]
            assert "name" in data[0]
            assert "description" in data[0]
            assert "price" in data[0] 