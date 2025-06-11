"""
운임(Rate) API 테스트
"""

import pytest
from httpx import AsyncClient
from fastapi import status


class TestRateAPI:
    """운임 API 테스트 클래스"""

    @pytest.mark.asyncio
    async def test_get_locations_by_region_id(self, client: AsyncClient):
        """지역 ID로 위치 목록 조회 테스트"""
        region_id = 1
        response = await client.get(f"/api/rate/location/{region_id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        
        if data:
            assert "id" in data[0]
            assert "name" in data[0]
            assert "city" in data[0]
            assert "zip_code" in data[0]
    
    @pytest.mark.asyncio
    async def test_get_locations_by_city(self, client: AsyncClient):
        """도시명으로 위치 목록 필터링 테스트"""
        region_id = 1
        city = "TestCity"
        response = await client.get(f"/api/rate/location/{region_id}?city={city}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        
        if data:
            for location in data:
                assert location["city"] == city
    
    @pytest.mark.asyncio
    async def test_get_locations_by_zip_code(self, client: AsyncClient):
        """우편번호로 위치 목록 필터링 테스트"""
        region_id = 1
        zip_code = "12345"
        response = await client.get(f"/api/rate/location/{region_id}?zip_code={zip_code}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        
        if data:
            for location in data:
                assert location["zip_code"] == zip_code 