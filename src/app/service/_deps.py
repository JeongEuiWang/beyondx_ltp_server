from fastapi import Depends
from typing import Annotated
from ..service.user import UserService
from ..service.auth import AuthService
from ..repository._deps import (
    userRepositoryDeps,
    userAddressRepositoryDeps,
    cargoRepositoryDeps,
    userLevelRepositoryDeps,
    quoteRepositoryDeps,
    quoteLocationRepositoryDeps,
    quoteLocationAccessorialRepositoryDeps,
    quoteCargoRepositoryDeps,
    rateLocationRepositoryDeps,
    rateAreaCostRepositoryDeps,
    rateAreaRepositoryDeps,
)
from ..service.rate import RateService
from ..service.cargo import CargoService
from ..service.quote import QuoteService
from ..service.cost import CostService
from ..repository._deps import sessionDeps


# Service 의존성
async def get_auth_service(
    user_repository: userRepositoryDeps,
    user_level_repository: userLevelRepositoryDeps,
) -> AuthService:
    return AuthService(user_repository, user_level_repository)


async def get_user_service(
    user_repository: userRepositoryDeps,
    user_level_repository: userLevelRepositoryDeps,
    user_address_repository: userAddressRepositoryDeps,
) -> UserService:
    return UserService(
        user_repository,
        user_level_repository,
        user_address_repository,
    )


async def get_rate_service(rate_location_repository: rateLocationRepositoryDeps) -> RateService:
    return RateService(rate_location_repository)


async def get_cargo_service(cargo_repository: cargoRepositoryDeps) -> CargoService:
    return CargoService(cargo_repository)


async def get_quote_service(
    quote_repository: quoteRepositoryDeps,
    quote_location_repository: quoteLocationRepositoryDeps,
    quote_location_accessorial_repository: quoteLocationAccessorialRepositoryDeps,
    quote_cargo_repository: quoteCargoRepositoryDeps,
    session: sessionDeps,
) -> QuoteService:
    service = QuoteService(
        quote_repository,
        quote_location_repository,
        quote_location_accessorial_repository,
        quote_cargo_repository,
    )
    service.db = session  # DB 세션 설정
    return service


async def get_cost_service(
    rate_area_repository: rateAreaRepositoryDeps,
    rate_area_cost_repository: rateAreaCostRepositoryDeps,
    user_repository: userRepositoryDeps,
    user_level_repository: userLevelRepositoryDeps,
) -> CostService:
    return CostService(rate_area_repository, rate_area_cost_repository, user_repository, user_level_repository)


authServiceDeps = Annotated[AuthService, Depends(get_auth_service)]
userServiceDeps = Annotated[UserService, Depends(get_user_service)]
rateServiceDeps = Annotated[RateService, Depends(get_rate_service)]
cargoServiceDeps = Annotated[CargoService, Depends(get_cargo_service)]
quoteServiceDeps = Annotated[QuoteService, Depends(get_quote_service)]
costServiceDeps = Annotated[CostService, Depends(get_cost_service)]
