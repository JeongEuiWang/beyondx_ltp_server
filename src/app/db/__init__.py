from app.db.session import engine
from app.db.base import Base


async def create_table():
  async with engine.begin() as conn:
    await conn.run_sync(Base.meta.create_all)
