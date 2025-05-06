# 테스트 가이드

## 테스트 구조 및 실행 방법

### 테스트 구조

테스트는 다음과 같은 구조로 구성되어 있습니다:

- `tests/api/`: API 엔드포인트 테스트
- `tests/service/`: 서비스 로직 테스트
- `conftest.py`: 공통 테스트 픽스처

### 테스트 실행 방법

전체 테스트 실행:
```bash
pytest
```

특정 모듈 테스트:
```bash
pytest tests/api/test_quote_api.py
```

특정 테스트 실행:
```bash
pytest tests/service/test_quote_service.py::test_update_quote
```

### quote 관련 테스트

#### API 테스트

`tests/api/test_quote_api.py`에는 다음 테스트가 포함되어 있습니다:

- `test_update_quote_success`: 견적 업데이트 성공 테스트
- `test_update_quote_not_found`: 존재하지 않는 견적 조회 시 404 오류 테스트
- `test_update_quote_max_load_exceeded`: 최대 금액 초과 시 400 오류 테스트

#### 서비스 테스트

`tests/service/test_quote_service.py`에는 다음 테스트가 포함되어 있습니다:

- `test_create_quote`: 견적 생성 테스트
- `test_update_quote`: 견적 업데이트 테스트
- `test_update_accessorials_add_new`: 부가 서비스 추가 테스트
- `test_update_accessorials_remove_all`: 모든 부가 서비스 삭제 테스트

### 테스트 작성 가이드

1. API 테스트 작성 시 고려 사항:
   - 엔드포인트 응답 상태 코드 확인
   - 예외 처리 확인
   - 의존성 주입된 서비스의 호출 확인

2. 서비스 테스트 작성 시 고려 사항:
   - 서비스 로직 정확성 확인
   - 데이터베이스 업데이트 확인
   - 관련 레포지토리 메서드 호출 확인

3. 목(Mock) 객체 활용:
   - 데이터베이스 접근 최소화
   - 서비스 간 의존성 격리

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