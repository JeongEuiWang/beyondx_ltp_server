from sqlalchemy.ext.asyncio import AsyncSession

# 각 리포지토리 import
from ..repository import (
    UserRepository,
    UserLevelRepository,
    UserAddressRepository,
    CargoRepository,
    RateAreaRepository,
    RateAreaCostRepository,
    RateLocationRepository,
    QuoteRepository,
    QuoteLocationRepository,
    QuoteLocationAccessorialRepository,
    QuoteCargoRepository,
)

# ... 다른 필요한 리포지토리들을 여기에 추가합니다.


class UnitOfWork:
    def __init__(self, session: AsyncSession):
        self._session = session
        # 리포지토리들을 속성으로 초기화
        self.users: UserRepository = UserRepository(self._session)
        self.user_levels: UserLevelRepository = UserLevelRepository(self._session)
        self.user_addresses: UserAddressRepository = UserAddressRepository(
            self._session
        )
        self.cargos: CargoRepository = CargoRepository(self._session)
        self.rate_areas: RateAreaRepository = RateAreaRepository(self._session)
        self.rate_area_costs: RateAreaCostRepository = RateAreaCostRepository(
            self._session
        )
        self.rate_locations: RateLocationRepository = RateLocationRepository(
            self._session
        )
        self.quotes: QuoteRepository = QuoteRepository(self._session)
        self.quote_locations: QuoteLocationRepository = QuoteLocationRepository(
            self._session
        )
        self.quote_location_accessorials: QuoteLocationAccessorialRepository = (
            QuoteLocationAccessorialRepository(self._session)
        )
        self.quote_cargos: QuoteCargoRepository = QuoteCargoRepository(self._session)
        # ... 다른 리포지토리 인스턴스 생성

    @property
    def session(self) -> AsyncSession:
        return self._session

    async def __aenter__(self):
        # begin_nested()는 일반적으로 필요하지 않으며, get_async_session에서 제공하는
        # 세션의 컨텍스트 내에서 작동합니다.
        # await self._session.begin_nested() # 필요한 경우 활성화
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            await self._session.rollback()
            # 오류 로깅 또는 특정 예외 처리를 여기에 추가할 수 있습니다.
            raise # 원래 예외를 다시 발생시키려면 주석 해제 (FastAPI 미들웨어가 처리하도록)
        else:
            try:
                await self._session.commit()
            except Exception:  # 커밋 중 발생할 수 있는 예외 (예: DB 연결 끊김)
                await self._session.rollback()
                raise
        # 세션 닫기는 get_async_session의 finally 블록 또는 async with async_session()에서 처리됩니다.
        # 여기서는 commit/rollback만 책임집니다.


# 더 이상 명시적인 commit/rollback 메소드는 UnitOfWork 외부에서 호출될 필요가 없습니다.
# 필요하다면 유지할 수 있지만, __aexit__에서 처리하는 것이 컨텍스트 매니저의 의도입니다.
#    async def commit(self):
#        await self._session.commit()
#
#    async def rollback(self):
#        await self._session.rollback()
