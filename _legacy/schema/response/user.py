# Repository => Service, Service => API간 전송하는 데이터의 인터페이스를 정의합니다.

from pydantic import BaseModel

class CheckEmailResponse(BaseModel):
    is_email_exists: bool
