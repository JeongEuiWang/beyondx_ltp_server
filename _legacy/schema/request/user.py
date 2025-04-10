# API => Service, Service => Repository간 전송해야 하는 데이터의 인터페이스를 정의합니다.
from datetime import datetime
from typing import List, Optional, Union

from pydantic import BaseModel

class CheckEmailRequest(BaseModel):
    email: str



