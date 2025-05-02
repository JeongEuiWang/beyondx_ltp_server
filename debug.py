# debug_db.py
import asyncio
import sys
from src.app.db.session import get_async_session, engine
from src.app.repository.user import UserRepository
from sqlalchemy import select, text
from src.app.model.user import User
from src.app.core.config import settings

async def check_db_connection():
    """데이터베이스 연결 상태를 확인합니다."""
    print("\n===== 데이터베이스 연결 정보 =====")
    print(f"현재 환경 모드: {getattr(settings, 'ENV', '정보 없음')}")
    print(f"데이터베이스 URL: {settings.DB_URL}")
    print(f"데이터베이스 호스트: {settings.DB_HOST}")
    print(f"데이터베이스 포트: {settings.DB_PORT}")
    print(f"데이터베이스 이름: {settings.DB_NAME}")
    print(f"데이터베이스 사용자: {settings.DB_USER}")
    
    try:
        # 연결 테스트
        async with engine.connect() as conn:
            # 간단한 쿼리 실행하여 연결 확인
            result = await conn.execute(text("SELECT 1"))
            value = result.scalar()
            if value == 1:
                print("\n✅ 데이터베이스 연결 성공!")
            else:
                print("\n❌ 데이터베이스 연결 테스트 실패")
            
            # 서버 버전 확인
            result = await conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"데이터베이스 서버 버전: {version}")
            
            # 현재 데이터베이스 확인
            result = await conn.execute(text("SELECT database()"))
            current_db = result.scalar()
            print(f"현재 연결된 데이터베이스: {current_db}")
            
    except Exception as e:
        print(f"\n❌ 데이터베이스 연결 오류: {str(e)}")
        print(f"오류 유형: {type(e).__name__}")
        print("데이터베이스 연결 설정을 확인하세요.")
        return False
    
    return True

async def check_db_tables():
    """데이터베이스 테이블 상태와 사용자 정보를 확인합니다."""
    print("\n===== 데이터베이스 테이블 정보 =====")
    try:
        async with engine.connect() as conn:
            # 테이블 목록 조회
            result = await conn.execute(text(
                "SELECT table_name FROM information_schema.tables "
                f"WHERE table_schema = '{settings.DB_NAME}'"))
            tables = [row[0] for row in result.fetchall()]
            
            print(f"테이블 목록: {', '.join(tables) if tables else '테이블 없음'}")
            
            # User 테이블이 있는지 확인
            if 'user' in [t.lower() for t in tables]:
                print("\n===== 사용자 정보 =====")
                async for session in get_async_session():
                    repo = UserRepository(session)
                    # 데이터베이스에 저장된 모든 사용자 출력
                    result = await session.execute(select(User))
                    users = result.scalars().all()
                    print(f"총 사용자 수: {len(users)}")
                    for user in users:
                        print(f"사용자: {user.email}, {user.first_name} {user.last_name}")
            else:
                print("\n⚠️ User 테이블이 없습니다. 마이그레이션이 필요할 수 있습니다.")
                
    except Exception as e:
        print(f"\n❌ 테이블 정보 조회 오류: {str(e)}")
        return False
    
    return True

async def main():
    """데이터베이스 연결 및 상태를 확인합니다."""
    print("===== 데이터베이스 연결 테스트 시작 =====")
    
    # 데이터베이스 연결 확인
    connection_ok = await check_db_connection()
    if not connection_ok:
        print("\n❌ 데이터베이스 연결에 실패했습니다. 환경 변수와 네트워크 설정을 확인하세요.")
        sys.exit(1)
    
    # 테이블 및 데이터 확인
    tables_ok = await check_db_tables()
    if not tables_ok:
        print("\n⚠️ 테이블 정보 조회에 실패했습니다.")
    
    print("\n===== 데이터베이스 연결 테스트 완료 =====")

if __name__ == "__main__":
    asyncio.run(main())