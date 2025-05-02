from fastapi import Depends
from ..db.session import sessionDeps
from ..repository.user import UserRepository
from ..repository.user_address import UserAddressRepository
from ..repository.rate import RateRepository
from typing import Annotated


# Repository 의존성
def get_user_repository(session=sessionDeps) -> UserRepository:
    return UserRepository(db_session=session)


def get_user_address_repository(session=sessionDeps) -> UserAddressRepository:
    return UserAddressRepository(db_session=session)


def get_rate_repository(session=sessionDeps) -> RateRepository:
    return RateRepository(db_session=session)


userRepositoryDeps = Annotated[UserRepository, Depends(get_user_repository)]
userAddressRepositoryDeps = Annotated[
    UserAddressRepository, Depends(get_user_address_repository)
]
rateRepositoryDeps = Annotated[RateRepository, Depends(get_rate_repository)]
