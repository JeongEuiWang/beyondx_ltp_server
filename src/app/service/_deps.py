from fastapi import Depends
from typing import Annotated
from app.service.user import UserService
from app.service.auth import AuthService
from app.repository._deps import (
    userRepositoryDeps,
    userAddressRepositoryDeps,
    rateRepositoryDeps,
    cargoRepositoryDeps,
    userLevelRepositoryDeps,
    quoteRepositoryDeps,
    quoteLocationRepositoryDeps,
    quoteCargoRepositoryDeps,
)
from app.service.rate import RateService
from app.service.cargo import CargoService
from app.service.quote import QuoteService
from app.service.cost import CostService
from app.repository._deps import sessionDeps


# Service 의존성
async def get_auth_service(
    user_repository: userRepositoryDeps,
) -> AuthService:
    return AuthService(user_repository)


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


async def get_rate_service(rate_repository: rateRepositoryDeps) -> RateService:
    return RateService(rate_repository)


async def get_cargo_service(cargo_repository: cargoRepositoryDeps) -> CargoService:
    return CargoService(cargo_repository)


async def get_quote_service(
    quote_repository: quoteRepositoryDeps,
    quote_location_repository: quoteLocationRepositoryDeps,
    quote_cargo_repository: quoteCargoRepositoryDeps,
    session: sessionDeps,
) -> QuoteService:
    service = QuoteService(
        quote_repository, quote_location_repository, quote_cargo_repository
    )
    service.db = session  # DB 세션 설정
    return service


async def get_cost_service(
    rate_repository: rateRepositoryDeps,
    user_repository: userRepositoryDeps,
    user_level_repository: userLevelRepositoryDeps,
) -> CostService:
    return CostService(rate_repository, user_repository, user_level_repository)


authServiceDeps = Annotated[AuthService, Depends(get_auth_service)]
userServiceDeps = Annotated[UserService, Depends(get_user_service)]
rateServiceDeps = Annotated[RateService, Depends(get_rate_service)]
cargoServiceDeps = Annotated[CargoService, Depends(get_cargo_service)]
quoteServiceDeps = Annotated[QuoteService, Depends(get_quote_service)]
costServiceDeps = Annotated[CostService, Depends(get_cost_service)]
