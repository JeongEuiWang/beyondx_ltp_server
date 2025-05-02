from passlib.context import CryptContext

# 비밀번호 해싱을 위한 객체
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    평문 비밀번호와 해시된 비밀번호를 비교하여 일치 여부를 반환합니다.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    평문 비밀번호를 해시하여 반환합니다.
    """
    return pwd_context.hash(password)
