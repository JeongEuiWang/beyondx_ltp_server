from .container import container
from ...db.session import get_async_session
from ...repository import *
from ...service import *
from ...core.auth import get_refresh_token_from_cookie, required_authorization


def configure_dependencies():

    # 1. 데이터베이스 세션
    configure_db_session()

    # 2. 레포지토리
    configure_repositories()

    # 3. 서비스
    configure_services()

    # 4. 인증
    configure_authorization()


def configure_db_session():
    container.register("db_session", get_async_session)


def configure_repositories():
    container.register(
        "user_repository",
        lambda: UserRepository(db_session=container.get("db_session")),
    )

    container.register(
        "user_address_repository",
        lambda: UserAddressRepository(db_session=container.get("db_session")),
    )

    container.register(
        "user_level_repository",
        lambda: UserLevelRepository(db_session=container.get("db_session")),
    )

    container.register(
        "cargo_repository",
        lambda: CargoRepository(db_session=container.get("db_session")),
    )

    container.register(
        "rate_area_repository",
        lambda: RateAreaRepository(db_session=container.get("db_session")),
    )

    container.register(
        "rate_area_cost_repository",
        lambda: RateAreaCostRepository(db_session=container.get("db_session")),
    )

    container.register(
        "rate_location_repository",
        lambda: RateLocationRepository(db_session=container.get("db_session")),
    )

    container.register(
        "quote_repository",
        lambda: QuoteRepository(db_session=container.get("db_session")),
    )

    container.register(
        "quote_location_repository",
        lambda: QuoteLocationRepository(db_session=container.get("db_session")),
    )

    container.register(
        "quote_location_accessorial_repository",
        lambda: QuoteLocationAccessorialRepository(
            db_session=container.get("db_session")
        ),
    )

    container.register(
        "quote_cargo_repository",
        lambda: QuoteCargoRepository(db_session=container.get("db_session")),
    )


def configure_services():
    container.register(
        "user_service",
        lambda: UserService(
            user_repository=container.get("user_repository"),
            user_address_repository=container.get("user_address_repository"),
            user_level_repository=container.get("user_level_repository"),
        ),
    )

    container.register(
        "cargo_service",
        lambda: CargoService(cargo_repository=container.get("cargo_repository")),
    )

    container.register(
        "rate_service",
        lambda: RateService(
            rate_area_repository=container.get("rate_area_repository"),
            rate_area_cost_repository=container.get("rate_area_cost_repository"),
            rate_location_repository=container.get("rate_location_repository"),
        ),
    )

    container.register(
        "cost_service",
        lambda: CostService(
            quote_repository=container.get("quote_repository"),
            quote_location_repository=container.get("quote_location_repository"),
            quote_location_accessorial_repository=container.get(
                "quote_location_accessorial_repository"
            ),
            quote_cargo_repository=container.get("quote_cargo_repository"),
        ),
    )

    container.register(
        "auth_service",
        lambda: AuthService(user_repository=container.get("user_repository")),
    )

    container.register(
        "quote_service",
        lambda: QuoteService(
            quote_repository=container.get("quote_repository"),
            quote_location_repository=container.get("quote_location_repository"),
            quote_location_accessorial_repository=container.get(
                "quote_location_accessorial_repository"
            ),
            quote_cargo_repository=container.get("quote_cargo_repository"),
        ),
    )


def configure_authorization():
    container.register("required_authorization", required_authorization)
    container.register("refresh_from_cookie", get_refresh_token_from_cookie)
