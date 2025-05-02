# env_check.py
import os
import sys
from pathlib import Path
from dotenv import dotenv_values, find_dotenv

def check_env_files():
    """환경 변수 파일이 존재하는지 확인하고 데이터베이스 관련 설정을 확인합니다."""
    print("===== 환경 변수 파일 확인 =====")
    
    # 현재 환경 모드 확인
    env_mode = os.getenv("ENV", "dev")
    print(f"현재 환경 모드: {env_mode}")
    
    # .env 파일 확인
    env_files = [
        ".env",
        f".env.{env_mode}",
        ".env.local",
        f".env.{env_mode}.local"
    ]
    
    for env_file in env_files:
        file_path = Path(env_file)
        if file_path.exists():
            print(f"\n✅ {env_file} 파일 존재")
            # 파일 내용 확인 (민감 정보는 일부만 표시)
            config = dotenv_values(env_file)
            print(f"{env_file} 내용:")
            for key, value in config.items():
                # 민감 정보는 일부만 표시
                if key in ["DB_PASS", "SECRET_KEY"] and value:
                    masked_value = value[:3] + "*" * (len(value) - 3) if len(value) > 3 else "***"
                    print(f"  {key}={masked_value}")
                else:
                    print(f"  {key}={value}")
        else:
            print(f"\n❌ {env_file} 파일 없음")
    
    # 데이터베이스 환경 변수 확인
    db_vars = ["DB_HOST", "DB_PORT", "DB_USER", "DB_PASS", "DB_NAME"]
    missing_vars = []
    
    print("\n===== 데이터베이스 환경 변수 확인 =====")
    for var in db_vars:
        value = os.getenv(var)
        if value:
            if var == "DB_PASS":
                masked_value = value[:3] + "*" * (len(value) - 3) if len(value) > 3 else "***"
                print(f"✅ {var}={masked_value}")
            else:
                print(f"✅ {var}={value}")
        else:
            missing_vars.append(var)
            print(f"❌ {var}=없음")
    
    if missing_vars:
        print(f"\n⚠️ 다음 환경 변수가 설정되어 있지 않습니다: {', '.join(missing_vars)}")
        print("환경 변수 파일(.env 또는 .env.dev)을 확인하거나 직접 설정하세요.")
    else:
        print("\n✅ 모든 필수 데이터베이스 환경 변수가 설정되어 있습니다.")
    
    return len(missing_vars) == 0

def main():
    """환경 설정 확인 메인 함수"""
    print("===== 환경 설정 확인 시작 =====")
    env_ok = check_env_files()
    
    if not env_ok:
        print("\n⚠️ 환경 변수 설정에 문제가 있습니다. 위 내용을 확인하세요.")
    else:
        print("\n✅ 환경 변수 설정이 완료되었습니다.")
        print("이제 'python debug.py'를 실행하여 데이터베이스 연결을 테스트하세요.")
    
    print("\n===== 환경 설정 확인 완료 =====")

if __name__ == "__main__":
    main() 