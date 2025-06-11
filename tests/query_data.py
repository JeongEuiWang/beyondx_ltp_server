import asyncio
import os
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

DATABASE_URL = settings.DB_URL

async def get_data():
    engine = create_async_engine(DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        result = await session.execute(text("SELECT id, name FROM cargo_transportation LIMIT 5"))
        print("=== Cargo Transportation ===")
        for row in result:
            print(f"ID: {row[0]}, Name: {row[1]}")
        
        result = await session.execute(text("SELECT id, name, description FROM cargo_accessorial LIMIT 5"))
        print("\n=== Cargo Accessorial ===")
        for row in result:
            print(f"ID: {row[0]}, Name: {row[1]}, Description: {row[2]}")
        
        result = await session.execute(text("SELECT DISTINCT zip_code FROM rate_area LIMIT 5"))
        print("\n=== ZIP Codes ===")
        for row in result:
            print(f"ZIP Code: {row[0]}")

if __name__ == "__main__":
    asyncio.run(get_data()) 