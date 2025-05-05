from fastapi import Depends
from ..db.session import sessionDeps
from ..repository.user import UserRepository
from ..repository.user_address import UserAddressRepository
from ..repository.rate import RateRepository
from ..repository.cargo import CargoRepository
from ..repository.user_level import UserLevelRepository
from ..repository.quote import QuoteRepository
from ..repository.quote_location import QuoteLocationRepository
from ..repository.quote_cargo import QuoteCargoRepository
from typing import Annotated


# Repository 의존성
def get_user_repository(session: sessionDeps) -> UserRepository:
    return UserRepository(db_session=session)


def get_user_address_repository(session: sessionDeps) -> UserAddressRepository:
    return UserAddressRepository(db_session=session)


def get_user_level_repository(session: sessionDeps) -> UserLevelRepository:
    return UserLevelRepository(db_session=session)


def get_rate_repository(session: sessionDeps) -> RateRepository:
    return RateRepository(db_session=session)
  

def get_cargo_repository(session: sessionDeps) -> CargoRepository:
    return CargoRepository(db_session=session)


def get_quote_repository(session: sessionDeps) -> QuoteRepository:
    return QuoteRepository(db_session=session)  


def get_quote_location_repository(session: sessionDeps) -> QuoteLocationRepository:
    return QuoteLocationRepository(db_session=session)


def get_quote_cargo_repository(session: sessionDeps) -> QuoteCargoRepository:
    return QuoteCargoRepository(db_session=session)
  
  
userRepositoryDeps = Annotated[UserRepository, Depends(get_user_repository)]
userAddressRepositoryDeps = Annotated[
    UserAddressRepository, Depends(get_user_address_repository)
]
rateRepositoryDeps = Annotated[RateRepository, Depends(get_rate_repository)]
cargoRepositoryDeps = Annotated[CargoRepository, Depends(get_cargo_repository)]
userLevelRepositoryDeps = Annotated[UserLevelRepository, Depends(get_user_level_repository)]
quoteRepositoryDeps = Annotated[QuoteRepository, Depends(get_quote_repository)]
quoteLocationRepositoryDeps = Annotated[QuoteLocationRepository, Depends(get_quote_location_repository)]
quoteCargoRepositoryDeps = Annotated[QuoteCargoRepository, Depends(get_quote_cargo_repository)]