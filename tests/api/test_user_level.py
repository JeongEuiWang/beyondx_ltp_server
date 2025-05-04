"""
사용자 레벨 API 테스트
"""

import pytest
from httpx import AsyncClient
from fastapi import status


class TestUserLevelAPI:
    """사용자 레벨 API 테스트 클래스"""

    @pytest.mark.asyncio
    async def test_get_user_levels(self, client: AsyncClient):
        """사용자 레벨 목록 조회 테스트"""
        response = await client.get("/api/user/levels")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        
        # 데이터가 있는지 확인은 DB 상태에 따라 다를 수 있으므로,
        # 응답 형식이 올바른지만 확인
        if data:
            assert "id" in data[0]
            assert "user_level" in data[0]
            assert "required_amount" in data[0]
            assert "discount_rate" in data[0] 