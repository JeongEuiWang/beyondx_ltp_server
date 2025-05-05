import functools
from sqlalchemy.ext.asyncio import AsyncSession


def transactional():
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(self, *args, **kwargs):
            if not hasattr(self, "db") or self.db is None:
                # 현재 self.db는 외부에서 설정되지 않고 있습니다
                # 서비스 클래스에 db 속성이 없으면 에러 발생
                raise ValueError("No DB Session Found")

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
