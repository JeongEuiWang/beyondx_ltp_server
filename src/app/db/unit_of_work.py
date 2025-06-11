from sqlalchemy.ext.asyncio import AsyncSession

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


class UnitOfWork:
    def __init__(self, session: AsyncSession):
        self._session = session

        self.user: UserRepository = UserRepository(self._session)
        self.user_level: UserLevelRepository = UserLevelRepository(self._session)
        self.user_address: UserAddressRepository = UserAddressRepository(
            self._session
        )
        self.cargo: CargoRepository = CargoRepository(self._session)
        self.rate_area: RateAreaRepository = RateAreaRepository(self._session)
        self.rate_area_cost: RateAreaCostRepository = RateAreaCostRepository(
            self._session
        )
        self.rate_location: RateLocationRepository = RateLocationRepository(
            self._session
        )
        self.quote: QuoteRepository = QuoteRepository(self._session)
        self.quote_location: QuoteLocationRepository = QuoteLocationRepository(
            self._session
        )
        self.quote_location_accessorial: QuoteLocationAccessorialRepository = (
            QuoteLocationAccessorialRepository(self._session)
        )
        self.quote_cargo: QuoteCargoRepository = QuoteCargoRepository(self._session)

    @property
    def session(self) -> AsyncSession:
        return self._session

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            await self._session.rollback()
            raise
        else:
            try:
                await self._session.commit()
            except Exception:
                await self._session.rollback()
                raise
