from pydantic_settings import BaseSettings
from typing import Literal
import os

# 환경 모드 상수 정의
ENV_MODE = Literal["dev", "prod"]
DEFAULT_MODE: ENV_MODE = "dev"

class Settings(BaseSettings):
    """기본 설정 클래스. 데이터베이스 연결 정보를 관리합니다."""
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    @property
    def DB_URL(self) -> str:
        """DB_URL 속성은 데이터베이스 연결 정보를 기반으로 동적으로 생성됩니다."""
        return f"mysql+aiomysql://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    class Config:
        env_file = ".env"

class DevSettings(Settings):
    """개발 환경 설정 클래스"""
    class Config:
        env_file = ".env.dev"

class ProdSettings(Settings):
    """운영 환경 설정 클래스"""
    class Config:
        env_file = ".env.prod"

def get_settings(mode: str = os.getenv("ENV", DEFAULT_MODE)) -> Settings:
    mode = mode.lower()
    return ProdSettings() if mode == "prod" else DevSettings()

settings = get_settings()