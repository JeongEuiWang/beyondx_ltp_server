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

### 3.1. Gmail SMTP 및 앱 비밀번호 설정 (선택 사항)

견적 제출 시 이메일 알림 기능을 사용하려면 SMTP 설정이 필요합니다. Gmail을 사용하는 경우, 보안상의 이유로 계정 비밀번호 대신 **앱 비밀번호**를 사용해야 합니다.

1.  **Google 계정 관리**([https://myaccount.google.com/](https://myaccount.google.com/))에 접속합니다.
2.  왼쪽 메뉴에서 **보안** 탭으로 이동합니다.
3.  `Google에 로그인하는 방법` 섹션에서 **2단계 인증**을 사용 설정합니다. (이미 설정되어 있다면 다음 단계로 넘어갑니다.)
4.  2단계 인증 설정 후, 다시 **보안** 탭으로 돌아와 검색창에서 **앱 비밀번호**를 입력 후 검색합니다.
5.  앱 이름을 입력하고 **만들기** 를 클릭합니다.
6.  생성된 **16자리 앱 비밀번호**를 복사합니다. 이 비밀번호는 이 창을 닫으면 다시 볼 수 없으니 즉시 `.env.dev` 파일에 반영하세요.
7.  복사한 앱 비밀번호를 `.env.dev` 파일의 `SMTP_EMAIL_PASSWORD` 값으로 사용하고, `SMTP_EMAIL_USERNAME`과 `SMTP_SENDER_EMAIL`에 사용할 Gmail 주소를 입력합니다.

```dotenv
# .env.dev 예시
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_EMAIL_USERNAME=your_gmail_address@gmail.com
SMTP_EMAIL_PASSWORD=xxxxxxxxxxxxxxxx # 여기에 생성된 16자리 앱 비밀번호를 입력
SMTP_SENDER_EMAIL=your_gmail_address@gmail.com
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

## 🗃️ 데이터베이스 스키마

### 테이블 설명

| 테이블명                    | 설명                                                                   |
| --------------------------- | ---------------------------------------------------------------------- |
| `User`                      | 사용자 기본 정보 (이메일, 이름, 연락처 등)를 저장합니다.               |
| `Role`                      | 사용자의 역할(일반 사용자, 관리자 등)을 정의합니다.                    |
| `UserLevel`                 | 사용자의 등급과 등급별 할인율 정보를 관리합니다.                       |
| `UserAddress`               | 사용자가 등록한 주소록 정보를 관리합니다.                         |
| `Quote`                     | 사용자가 요청한 견적의 종합 정보(총액, 상태 등)를 저장합니다.           |
| `QuoteLocation`             | 견적의 출발지 및 도착지 상세 정보(주소, 요청 시간 등)를 저장합니다.    |
| `QuoteCargo`                | 견적에 포함된 각 화물의 상세 정보(크기, 무게, 수량 등)를 저장합니다.     |
| `QuoteLocationAccessorial`  | 특정 위치(출발/도착)에 요청된 추가 서비스 목록을 저장하는 매핑 테이블입니다. |
| `CargoTransportation`       | 이용 가능한 화물 운송 수단(트럭 종류 등) 마스터 데이터입니다.          |
| `CargoAccessorial`          | 리프트게이트, 내부 배송 등 추가 서비스 마스터 데이터입니다.            |
| `CargoPackage`              | 표준 화물 포장 유형(팔레트, 박스 등) 마스터 데이터입니다.               |
| `RateRegion`                | 운임 계산을 위한 대규모 지역(예: Texas)을 정의합니다.                  |
| `RateArea`                  | `RateRegion` 내의 세부 구역(예: Area A, B, C)을 정의합니다.             |
| `RateAreaCost`              | `RateArea` 별 무게 구간에 따른 단가를 정의합니다.                      |
| `RateLocation`              | 우편번호(Zip Code)를 특정 `RateArea`에 매핑하는 테이블입니다.          |

### 운임 데이터 초기화

운임 계산에 필요한 핵심 데이터(지역, 구역, 위치, 비용)는 Alembic 마이그레이션 스크립트를 통해 데이터베이스에 초기 적재됩니다.

`src/app/db/migrations/versions/80eb89b88ed6_insert_region_area_location.py` 스크립트는 이 과정을 담당하는 대표적인 예시입니다. 이 스크립트는 **운영사에서 제공하는 위치 데이터 CSV 파일**(예: `src/app/db/migrations/resource/Texas/Texas_location.csv`)을 읽어들입니다.

그 후, 파일의 내용을 기반으로 각 우편번호(Zip Code)를 적절한 운임 구역(`RateArea`)에 매핑하고, 구역별 무게에 따른 비용(`RateAreaCost`) 정보를 데이터베이스에 일괄적으로 삽입합니다. 새로운 지역이나 운임 정책이 추가될 경우, 이와 유사한 방식으로 CSV 파일을 준비하고 신규 마이그레이션 스크립트를 작성하여 데이터베이스를 업데이트할 수 있습니다.

## 서비스 계층 (비즈니스 로직)

`src/app/service` 디렉토리는 애플리케이션의 핵심 비즈니스 로직을 포함하고 있습니다. 각 서비스 모듈은 특정 도메인의 책임을 맡아 API 계층과 데이터베이스 계층을 연결합니다.

| 서비스 파일             | 설명                                                                                                                                                            |
| ----------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `auth.py`               | **인증 서비스**: 사용자의 이메일/비밀번호를 검증하고, 성공 시 JWT Access Token과 Refresh Token을 발급합니다. 또한 쿠키를 이용해 안전하게 토큰을 관리하고, 로그아웃 처리를 담당합니다. |
| `user.py`               | **사용자 관리 서비스**: 신규 사용자 등록, 이메일 중복 확인, 사용자 정보 조회 및 주소록(생성, 조회, 수정, 삭제) 관련 비즈니스 로직을 처리합니다.                        |
| `rate.py`               | **운임 정보 서비스**: 도시명 또는 우편번호를 기반으로 데이터베이스에서 관련 운임 지역 정보를 조회합니다.                                                         |
| `cargo.py`              | **화물 기준정보 서비스**: 운송 수단, 추가 서비스, 포장 종류 등 견적 생성에 필요한 각종 마스터 데이터를 조회하는 기능을 제공합니다.                                 |
| `cost.py`               | **비용 계산 서비스**: 견적의 핵심 로직으로, 빌더 패턴(`cost_builder`)을 사용하여 복잡한 운임 비용을 계산합니다. 기본료, 추가 서비스 비용, 사용자 등급별 할인 등을 각각의 빌더가 계산하여 총비용을 산출합니다. |
| `quote.py`              | **견적 관리 서비스**: `CostService`를 통해 계산된 비용을 바탕으로 견적을 생성, 조회, 수정, 삭제합니다. 또한 사용자가 견적을 '제출(Submit)'하거나 관리자가 '확정(Confirm)'하는 등 견적의 전체 상태를 관리합니다. |
| `email.py`              | **이메일 발송 서비스**: SMTP를 통해 사용자에게 이메일을 발송합니다. 견적이 제출되었을 때, 사용자에게 알림을 보내는 역할을 합니다. |

## 🗃️ API 엔드포인트 상세

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

## 추가 전달사항
LTP.apidog.json은 이 프로젝트에 대한 apidog export json 파일입니다.
apidog 설치 후 import한 후 환경 변수 설정을 하시면 즉시 테스트가 가능합니다.
