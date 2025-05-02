from pydantic_settings import BaseSettings
from typing import Literal, Optional
import os
import secrets

# 환경 모드 상수 정의
ENV_MODE = Literal["dev", "prod"]
DEFAULT_MODE: ENV_MODE = "dev"


class Settings(BaseSettings):
    # JWT 관련 설정
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24시간
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30  # 30일

    # 쿠키 설정
    COOKIE_SECURE: bool = False  # HTTPS만 허용 여부

    # 데이터베이스 관련 설정
    DATABASE_URL: Optional[str] = None

    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    @property
    def DB_URL(self) -> str:
        return f"mysql+aiomysql://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


class DevSettings(Settings):
    COOKIE_SECURE: bool = False  # 개발 환경에서는 HTTP 허용

    class Config:
        env_file = ".env.dev"


class ProdSettings(Settings):
    COOKIE_SECURE: bool = True  # 프로덕션 환경에서는 HTTPS만 허용

    class Config:
        env_file = ".env.prod"


def get_settings(mode: str = os.getenv("ENV", DEFAULT_MODE)) -> Settings:
    mode = mode.lower()
    return ProdSettings() if mode == "prod" else DevSettings()


settings = get_settings()
