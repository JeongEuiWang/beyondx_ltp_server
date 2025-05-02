# 테스트 가이드

## 테스트 구조

```
tests/
├── api/                # API 엔드포인트 테스트
│   ├── __init__.py
│   └── test_user.py    # 사용자 관련 API 테스트
├── service/            # 서비스 계층 테스트
│   ├── __init__.py
│   └── test_auth_service.py  # 인증 서비스 테스트
├── conftest.py         # pytest 설정 및 공통 픽스처
├── __init__.py
└── README.md           # 테스트 가이드
```

## 테스트 실행 방법

### 전체 테스트 실행
```bash
# 프로젝트 루트 디렉토리에서 실행
pytest tests/
```

### 특정 테스트 모듈 실행
```bash
# API 테스트만 실행
pytest tests/api/

# 서비스 테스트만 실행
pytest tests/service/
```

### 특정 테스트 클래스 또는 메서드 실행
```bash
# 특정 테스트 파일 실행
pytest tests/api/test_user.py

# 특정 테스트 클래스 실행
pytest tests/api/test_user.py::TestUserRegister

# 특정 테스트 메서드 실행
pytest tests/api/test_user.py::TestUserRegister::test_register_success
```

### 테스트 실행 옵션
```bash
# 자세한 출력 보기
pytest -v tests/

# 실패한 테스트만 표시
pytest -xvs tests/

# 코드 커버리지 측정
pytest --cov=src tests/
```

## 주요 테스트 케이스

### 회원가입 (Register) API
- `test_register_success`: 정상적인 회원가입 성공 테스트
- `test_register_duplicate_email`: 중복 이메일 회원가입 실패 테스트
- `test_register_invalid_email`: 유효하지 않은 이메일 형식 테스트
- `test_register_missing_required_fields`: 필수 필드 누락 테스트
- `test_register_password_too_short`: 짧은 비밀번호 테스트

### 인증 서비스 (AuthService)
- `test_register_success`: 회원가입 서비스 성공 테스트
- `test_register_duplicate_email`: 중복 이메일 회원가입 실패 테스트
- `test_check_email_available`: 이메일 중복 확인 (사용 가능) 테스트
- `test_check_email_unavailable`: 이메일 중복 확인 (사용 불가) 테스트 