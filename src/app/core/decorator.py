import functools
from sqlalchemy.ext.asyncio import AsyncSession

def transactional():
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(self, *args, **kwargs):
            if not hasattr(self, 'db') or self.db is None:
                raise ValueError("No Session Found")
            
            db = self.db
            try:
                result = await func(self, *args, **kwargs)
                await db.commit()
                return result
            except Exception as e:
                await db.rollback()
                raise e
        return wrapper
    return decorator