import asyncio
import pathlib
import sys
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# 모델 임포트를 위한 경로 추가
sys.path.append(str(pathlib.Path(__file__).resolve().parents[3]))

# SQLAlchemy 모델 임포트
from app.db.base import Base
from app.model.user import User
from app.model.client import Client, ClientAddress, ClientLevel
from app.model.cargo import CargoTransportation, CargoAccessorial, CargoPackage
from app.model.rate import RateArea, RateRegion, RateLocation
from app.model.quote import Quote, QuoteLocation, QuoteLocationAccessorial
# 모든 모델 임포트

from app.core.config import get_settings

SETTINGS = get_settings()

config = context.config
fileConfig(config.config_file_name)

# SQLAlchemy 메타데이터 연결
target_metadata = Base.metadata

config.set_main_option("sqlalchemy.url", str(SETTINGS.DB_URL))


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_async_migrations)


def do_async_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
    )
    with context.begin_transaction():
        context.run_migrations()
    


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())



