# BeyondX Local Trucking Platform API Server

이 프로젝트는 FastAPI 기반의 LTL(Less-than-truckload) 화물 운송 플랫폼을 위한 백엔드 API 서버입니다. 

## 기술 스택

-   **Backend**: Python, FastAPI
-   **Database**: MySQL (MariaDB) with SQLAlchemy, Alembic for migrations
-   **Authentication**: JWT (JSON Web Tokens)
-   **Dependency Management**: Poetry
-   **Testing**: Pytest
-   **Configuration**: Pydantic

## 프로젝트 구조

```
ltp_server/
├── alembic.ini          # Alembic 마이그레이션 설정
├── Makefile             # 프로젝트 관리용 Make 명령어
├── pyproject.toml       # 프로젝트 의존성 및 메타데이터 (Poetry)
├── run.py               # 애플리케이션 실행 스크립트
├── src
│   └── app
│       ├── api          # API 엔드포인트 라우터
│       ├── core         # 핵심 로직 (인증, 설정, 예외 처리 등)
│       ├── db           # 데이터베이스 세션, 마이그레이션
│       ├── model        # SQLAlchemy 데이터베이스 모델
│       ├── repository   # 데이터베이스 접근 로직
│       ├── schema       # Pydantic 스키마 (데이터 유효성 검사)
│       ├── service      # 비즈니스 로직
│       └── main.py      # FastAPI 애플리케이션 메인 파일
└── tests                # Pytest 테스트 코드
```

## 설치 및 설정

### 1. 사전 요구사항

-   Python 3.12+
-   Poetry
-   MySQL (또는 MariaDB) 서버

### 2. 프로젝트 클론

```bash
git clone <repository-url>
cd ltp_server
```

### 3. 환경 변수 설정

프로젝트 루트 디렉토리에 `.env.dev` 파일을 생성하고 아래 내용을 채워주세요. 이 파일은 개발 환경에서 사용됩니다.

```dotenv
# .env.dev

# Database Settings
DB_HOST=localhost
DB_PORT=3306
DB_USER=your_db_user
DB_PASS=your_db_password
DB_NAME=your_db_name

# JWT Settings (Optional - a default secret key will be generated if not provided)
# SECRET_KEY=your_super_secret_key
# ALGORITHM=HS256
# ACCESS_TOKEN_EXPIRE_MINUTES=1440
# REFRESH_TOKEN_EXPIRE_DAYS=30

# SMTP Settings for email functionalities
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_EMAIL_USERNAME=your_email@gmail.com
SMTP_EMAIL_PASSWORD=your_email_password
SMTP_SENDER_EMAIL=your_email@gmail.com
```

### 4. 의존성 설치

`Makefile`에 정의된 `build` 명령어를 사용하여 필요한 패키지를 설치합니다.

```bash
make build
```

### 5. 데이터베이스 마이그레이션

Alembic을 사용하여 데이터베이스 스키마를 최신 상태로 마이그레이션합니다.

```bash
make migration-dev
```

## 서버 실행

### 개발 환경

아래 명령어를 실행하면 `localhost:8000`에서 개발 서버가 실행됩니다. 파일이 변경될 때마다 자동으로 재시작됩니다.

```bash
make dev
```

### 프로덕션 환경

프로덕션 환경에서는 아래 명령어를 사용합니다.

```bash
make prod
```


## API 엔드포인트 상세


### Auth (`/api/auth`)

| Method | Endpoint      | Description                  |
| :----- | :------------ | :--------------------------- |
| `POST` | `/login`      | 사용자 로그인 (토큰 발급)    |
| `POST` | `/refresh`    | Access Token 갱신            |
| `POST` | `/logout`     | 사용자 로그아웃              |

### User (`/api/user`)

| Method   | Endpoint                | Description                  |
| :------- | :---------------------- | :--------------------------- |
| `POST`   | `/`                     | 신규 사용자 생성 (회원가입)  |
| `GET`    | `/check-email`          | 이메일 중복 확인             |
| `GET`    | `/me`                   | 내 정보 조회 (인증 필요)     |
| `POST`   | `/address`              | 주소 추가 (인증 필요)        |
| `GET`    | `/address`              | 내 주소 목록 조회 (인증 필요)|
| `PUT`    | `/address/{address_id}` | 주소 수정 (인증 필요)        |
| `DELETE` | `/address/{address_id}` | 주소 삭제 (인증 필요)        |

### Rate (`/api/rate`)

| Method | Endpoint    | Description                               |
| :----- | :---------- | :---------------------------------------- |
| `GET`  | `/location` | 도시 또는 우편번호로 요율 지역 정보 조회  |

### Cargo (`/api/cargo`)

| Method | Endpoint         | Description              |
| :----- | :--------------- | :----------------------- |
| `GET`  | `/transportation`| 운송 수단 목록 조회      |
| `GET`  | `/accessorial`   | 추가 서비스 목록 조회    |
| `GET`  | `/package`       | 화물 포장 유형 목록 조회 |

### Quote (`/api/quote`)

| Method | Endpoint            | Description                                  |
| :----- | :------------------ | :------------------------------------------- |
| `POST` | `/`                 | 신규 견적 생성 (인증 필요)                   |
| `GET`  | `/`                 | 내 견적 목록 조회 (인증 필요)                |
| `GET`  | `/{quote_id}`       | 특정 견적 상세 조회 (인증 필요)              |
| `PUT` | `/{quote_id}`       | 견적 수정 (인증 필요)                        |
| `POST` | `/{quote_id}/submit`| 견적을 운송 요청으로 제출 (인증 필요)        |
| `POST` | `/{quote_id}/confirm`| (관리자) 운송 요청 승인 (인증 필요)          |
| `GET`  | `/admin`            | (관리자) 모든 견적 목록 조회 (인증 필요)     |

