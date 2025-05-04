from fastapi import Depends
from typing import Annotated
from app.service.user import UserService
from app.service.auth import AuthService
from app.repository._deps import (
    userRepositoryDeps,
    userAddressRepositoryDeps,
    rateRepositoryDeps,
)
from app.service.user_address import UserAddressService
from app.service.rate import RateService


# Service 의존성
async def get_auth_service(
    user_repository: userRepositoryDeps,
) -> AuthService:
    return AuthService(user_repository)


async def get_user_service(user_repository: userRepositoryDeps) -> UserService:
    return UserService(user_repository)


async def get_user_address_service(
    user_address_repository: userAddressRepositoryDeps,
) -> UserAddressService:
    return UserAddressService(user_address_repository)


async def get_rate_service(rate_repository: rateRepositoryDeps) -> RateService:
    return RateService(rate_repository)


authServiceDeps = Annotated[AuthService, Depends(get_auth_service)]
userServiceDeps = Annotated[UserService, Depends(get_user_service)]
userAddressServiceDeps = Annotated[
    UserAddressService, Depends(get_user_address_service)
]
rateServiceDeps = Annotated[RateService, Depends(get_rate_service)]
