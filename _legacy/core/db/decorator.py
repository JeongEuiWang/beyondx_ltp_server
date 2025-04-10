from functools import wraps
from app.core.db import async_session

def transactional(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        async with async_session() as session:
            try:
                kwargs['db'] = session  # 세션 주입
                result = await func(*args, **kwargs)
                await session.commit()  # 비동기 커밋
                return result
            except Exception as e:
                await session.rollback()  # 비동기 롤백
                raise e
    return wrapper