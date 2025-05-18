# LTP 서버 코드 리팩터링 내역

## 최종 목표

- 가독성 및 단일 책임 원칙 준수
- `transactional()` 데코레이터 기능 검증 및 개선 (Unit of Work 패턴으로 대체)
- API <-> 서비스 <-> 리포지토리 간 데이터 인터페이스 정의 및 데이터 변환 방식 일관성 적용

## 주요 변경 사항

### 1. Unit of Work (UoW) 패턴 도입 및 전면 적용

- **목적**: 서비스 계층에서 비즈니스 로직 내 여러 데이터베이스 작업을 단일 트랜잭션으로 묶어 원자성을 보장하고, 트랜잭션 관리 로직을 중앙화하여 코드 가독성 및 유지보수성을 향상시킵니다.
- **`app.db.unit_of_work.UnitOfWork` 클래스 구현**:
    - `AsyncSession`을 생성자에서 주입받습니다.
    - 비동기 컨텍스트 매니저 (`async def __aenter__`, `async def __aexit__`)를 구현하여 `async with` 구문과 함께 사용될 수 있도록 합니다.
    - `__aexit__` 메소드 내에서 예외 발생 여부에 따라 자동으로 `commit()` 또는 `rollback()`을 수행합니다.
    - 관련된 모든 리포지토리 인스턴스들(UserRepository, QuoteRepository 등)을 속성으로 관리하여, 서비스 계층에서 UoW를 통해 일관된 세션을 사용하는 리포지토리에 접근할 수 있도록 합니다.
- **`app.core.dependencies.uow.get_uow` 의존성 주입 함수 생성**:
    - FastAPI의 `Depends` 시스템을 활용합니다.
    - `app.db.session.get_async_session`으로부터 현재 요청에 대한 `AsyncSession`을 받아 `UnitOfWork` 인스턴스를 생성하여 반환합니다.

### 2. 서비스 계층 리팩터링 (모든 서비스: `UserService`, `AuthService`, `QuoteService`, `CostService`, `CargoService`, `RateService` 등)

- 모든 서비스는 생성자에서 `UnitOfWork` 인스턴스를 주입받도록 변경되었습니다.
  ```python
  class XxxService:
      def __init__(self, uow: UnitOfWork):
          self.uow = uow
  ```
- 각 서비스 내에서 데이터베이스 트랜잭션이 필요한 모든 메소드는 `async with self.uow:` 블록으로 감싸도록 수정되었습니다.
- 리포지토리 인스턴스는 `self.uow`를 통해 접근합니다 (예: `self.uow.users`, `self.uow.quotes`).

### 3. 리포지토리 계층 리팩터링 (모든 리포지토리)

- 모든 리포지토리 메소드 내에서 직접 실행하던 `db_session.commit()` 호출을 제거했습니다. 트랜잭션의 커밋과 롤백은 `UnitOfWork`가 전적으로 담당합니다.
- 데이터를 생성/수정/삭제하는 메소드에서는 필요에 따라 `await db_session.flush()`를 호출하여 ORM 객체 상태를 DB와 동기화하고 ID 등의 값을 즉시 가져올 수 있도록 했습니다.

### 4. API 계층 리팩터링 (모든 API 컨트롤러)

- 모든 API 엔드포인트 핸들러 함수들은 `UnitOfWork` 인스턴스를 `Depends(get_uow)`를 통해 직접 주입받도록 수정되었습니다.
- 주입받은 `UnitOfWork` 인스턴스를 사용하여 해당 요청에 대한 서비스(예: `UserService`, `QuoteService` 등)를 직접 인스턴스화합니다.
  ```python
  @router.post("/example")
  async def example_endpoint(
      request_data: SomeRequest,
      uow: UnitOfWork = Depends(get_uow),
      # token_data: TokenData = Depends(...) # 인증 등 다른 의존성
  ):
      example_service = ExampleService(uow)
      return await example_service.process_data(request_data)
  ```
- 중앙 컨테이너(`app.core.dependencies.container`)를 통한 서비스 주입 방식은 UoW 패턴을 사용하는 서비스들에 대해서는 제거되었습니다. 컨테이너는 이제 인증 관련 의존성(`required_authorization`, `refresh_from_cookie`) 및 기타 필요한 범용 의존성을 컨테이너에 등록하는 역할만 수행합니다.

### 5. `transactional` 데코레이터 제거

- `app.core.decorator.py` 파일과 내부의 `transactional` 데코레이터를 삭제했습니다.
- UoW 패턴이 도입됨에 따라 서비스 계층에서의 트랜잭션 관리는 `UnitOfWork`의 컨텍스트 매니저가 담당하게 되어, 기존 데코레이터는 불필요해졌습니다.

### 6. 의존성 주입 설정 변경 (`app.core.dependencies.__init__.py`)

- UoW 패턴을 사용하도록 리팩터링된 모든 서비스 및 이와 직접적으로 관련된 리포지토리들의 컨테이너 등록 로직을 제거했습니다.
- `configure_dependencies` 함수는 이제 주로 인증 관련 의존성(`required_authorization`, `refresh_from_cookie`) 및 기타 필요한 범용 의존성을 컨테이너에 등록하는 역할만 수행합니다.

### 7. 데이터 인터페이스 및 변환

- **API <-> 서비스**: 주로 Pydantic 스키마 (DTO)를 사용하여 데이터를 주고받습니다.
- **서비스 <-> 리포지토리**:
    - 서비스가 리포지토리 호출 시: DTO 또는 원시 타입/모델 객체를 전달합니다.
    - 리포지토리가 서비스에 반환 시: SQLAlchemy 모델 객체를 반환합니다.
- **모델 -> DTO 변환**: `app.schema._base.BaseSchema`에 `model_config = ConfigDict(from_attributes=True)` 설정이 이미 적용되어 있어, SQLAlchemy 모델 객체에서 Pydantic 스키마(DTO)로의 변환이 용이합니다 (예: `UserResponse.model_validate(user_model)`).
- 서비스 계층은 리포지토리로부터 받은 모델 객체를 API 응답을 위한 DTO로 변환하는 책임을 가집니다.

## 향후 개선 및 고려 사항

- **리포지토리 입력 데이터 타입**: 리포지토리 메소드가 DTO 대신 모델 객체나 원시 타입만을 받도록 좀 더 엄격하게 제한하여 계층 간 결합도를 낮추는 것을 고려할 수 있습니다. (일부 적용되었으나 전체적으로 검토 가능)
- **외부 서비스 호출 트랜잭션 관리**: `QuoteService`의 `submit_quote` 메소드에서 PDF 생성 및 이메일 발송과 같은 외부 서비스 호출은 DB 트랜잭션 커밋 이후에 수행되도록 분리했습니다. 만약 외부 호출 실패 시 DB 롤백이 필요하다면, Saga 패턴 또는 별도의 보상 트랜잭션 로직을 고려하거나, 해당 외부 호출도 UoW 컨텍스트 내에 포함시키되 타임아웃 및 예외 처리에 각별히 주의해야 합니다.
- **`cost_builder` 모듈**: 현재 `CostService` 내에서 사용되는 `cost_builder` 관련 클래스들은 DB 접근이 없으므로 UoW와 직접적인 관련은 없지만, 복잡한 계산 로직을 포함하고 있으므로 필요시 추가적인 가독성 개선 및 테스트 커버리지 확보를 고려할 수 있습니다.
- **`bol.py` 및 `email.py`**: 이 서비스들은 현재 독립적으로 작동하며, DB 트랜잭션과는 직접적인 연관이 없습니다. 이들의 설정 및 오류 처리 방식은 필요에 따라 검토될 수 있습니다.
- **에러 핸들링**: `UnitOfWork`의 `__aexit__` 등에서 발생하는 DB 관련 예외에 대한 로깅 및 사용자 알림 전략을 구체화할 수 있습니다.
- **테스트 코드 업데이트**: 변경된 아키텍처에 맞춰 단위 테스트 및 통합 테스트 코드를 반드시 업데이트해야 합니다. 

### 8. 단일 책임 원칙 (SRP) 준수 분석 및 개선 (진행중)

- **목표**: 각 클래스 및 모듈이 하나의 명확한 책임만을 갖도록 하여 코드의 가독성, 유지보수성, 테스트 용이성을 향상시킵니다.
- **주요 서비스 분석 결과 (1차)**:
    - **`QuoteService`**: 견적 관련 주요 로직(생성, 조회, 수정, 제출) 및 외부 서비스(PDF 생성, 이메일 발송) 호출 오케스트레이션 역할을 수행합니다. 외부 서비스 자체는 별도 모듈(`bol.py`, `email.py`)로 분리되어 있어 SRP를 비교적 잘 준수하고 있는 것으로 판단됩니다.
    - **`CostService`**: 다양한 비용 계산 로직을 각 빌더 클래스(`BaseCostBuilder` 등)로 분리하여 SRP를 잘 활용하고 있습니다. `CostService`는 이 빌더들을 사용하여 전체 비용 계산 과정을 오케스트레이션하며, 필요한 DB 조회도 수행합니다. 현재 구조는 "비용 계산 서비스"라는 단일 책임을 잘 수행하고 있으며, 선택적으로 DB 조회 로직을 빌더 외부로 완전히 분리하여 빌더의 순수 계산 책임을 강화할 수 있으나, 필수는 아닙니다.
    - **`UserService`**: 사용자 및 사용자 주소 관련 기능을 제공하며, SRP를 비교적 잘 준수하고 있습니다. 주소 관련 로직이 매우 복잡해질 경우 `UserAddressService`로의 분리를 고려할 수 있습니다.
    - **`AuthService`**: 로그인, 토큰  πιστοποίηση (인증)이라는 명확한 책임을 수행하며 SRP를 잘 준수하고 있습니다. 쿠키 설정을 API 계층으로 옮기는 것은 선택적 개선 사항입니다.
- **향후 진행**:
    - 나머지 서비스 (`CargoService`, `RateService` 등) 및 리포지토리 계층, `cost_builder` 모듈 등에 대한 SRP 분석을 계속 진행합니다.
    - 분석 결과에 따라 필요한 코드 수정을 적용하고, 최종 결과를 본 문서에 업데이트합니다.

- **추가 서비스 및 빌더 분석 결과 (2차)**:
    - **`CargoService` 및 `RateService`**: "화물 기본 정보 제공" 및 "요율 지역 정보 제공"이라는 명확한 단일 책임을 수행하며 SRP를 잘 준수합니다.
    - **`cost_builder` 모듈 (`BaseCostBuilder`, `ExtraCostBuilder`, `LocationCostBuilder`, `DiscountBuilder`)**: 각 빌더 클래스는 특정 비용 계산이라는 명확한 책임을 가지며 SRP를 잘 준수하고 있습니다.

- **리포지토리 계층 분석 결과 (2차)**:
    - 대부분의 리포지토리는 순수 데이터 영속성 관리(CRUD) 책임을 잘 수행하며 SRP를 준수합니다.
    - `UserAddressRepository.create_user_address`의 `commit()` 호출을 `flush()`로 수정했습니다.
    - **`QuoteRepository`의 `get_quotes` 및 `get_quote_by_id` 메소드**: 기존에는 조회된 모델 객체에 `from_location`, `to_location` 등의 속성을 동적으로 할당하고 내부 데이터를 DTO와 유사한 형태로 변형하는 로직이 포함되어 있었습니다. 이는 리포지토리의 핵심 책임을 벗어난다고 판단하여, 해당 데이터 변환 로직을 제거하고 순수한 SQLAlchemy 모델 객체를 반환하도록 수정했습니다.
    - **`QuoteService` 수정**: `QuoteRepository` 변경에 따라, `get_quotes` 및 `get_quote_by_id` 메소드 내에서 리포지토리로부터 받은 순수 모델 객체를 사용하여 응답 DTO (`GetQuotesResponse`, `GetQuoteDetailsResponse`)로 변환하는 책임을 명시적으로 수행하도록 수정했습니다. 또한 `submit_quote` 메소드에서 외부 서비스(BOL 생성)에 전달할 데이터를 구성할 때도 순수 모델 객체를 기준으로 하도록 변경하여 일관성을 확보했습니다.
    - 이 변경으로 서비스 계층은 데이터 변환 및 DTO 조립의 책임을, 리포지토리 계층은 순수한 데이터 영속성의 책임을 더욱 명확히 갖게 되었습니다.

- **향후 진행 (최종 점검)**:
    - API 계층 및 `core`, `db`, `model`, `schema` 등 기타 지원 모듈들이 각자의 역할에 충실한지 최종적으로 검토합니다.
    - 모든 변경사항을 종합하여 본 문서를 최종 업데이트합니다.

- **최종 점검 결과 (3차)**:
    - **API 계층 (`src/app/api`)**: 각 컨트롤러는 HTTP 요청/응답 처리, 경로 정의, 서비스 계층으로의 작업 위임이라는 명확한 책임을 가지며 SRP를 잘 준수합니다.
    - **`core` 모듈 (`src/app/core`)**: 인증, 설정, 예외 처리, 보안, 유틸리티 등 각 하위 모듈이 범용적인 핵심 기능 단위로 책임을 잘 분담하고 있습니다.
    - **`db` 모듈 (`src/app/db`)**: DB 세션 관리, Unit of Work 구현 등 DB 관련 책임을 명확히 수행합니다.
    - **`model` 모듈 (`src/app/model`)**: SQLAlchemy 모델 정의를 통해 데이터 구조 표현이라는 책임을 다합니다.
    - **`schema` 모듈 (`src/app/schema`)**: Pydantic 스키마 정의를 통해 API 및 서비스 계층의 데이터 인터페이스(계약) 정의라는 책임을 명확히 수행합니다.

- **단일 책임 원칙 (SRP) 리팩터링 최종 요약**:
    - 전반적으로 `@src` 내부의 주요 모듈 및 클래스들은 단일 책임 원칙을 잘 준수하고 있었습니다.
    - 가장 의미 있는 변경은 `QuoteRepository`의 조회 메소드에서 데이터 변환 및 가공 로직을 제거하고, 해당 책임을 `QuoteService`로 이전하여 각 계층의 역할을 더욱 명확히 한 것입니다.
    - `UserAddressRepository`의 불필요한 `commit()` 호출을 수정하는 등 소소한 개선도 이루어졌습니다.
    - 이 리팩터링을 통해 각 컴포넌트의 책임이 더 명확해져 코드의 가독성, 유지보수성, 테스트 용이성이 향상될 것으로 기대합니다.

### 9. 데이터 반환 인터페이스 일관성 확보 (진행중)

- **문제점**: `QuoteService`에서 DTO 변환 로직 수정 후, API 응답 및 내부 함수 호출(예: `create_structured_bill_of_lading`) 시 데이터 구조가 기존 또는 기대하는 인터페이스와 다를 수 있는 가능성이 제기됨.
- **조치 사항**:
    - `src/app/schema/quote/response.py`의 `GetQuotesResponse`, `GetQuoteDetailsResponse` 등 실제 응답 스키마 정의를 기준으로 `QuoteService`의 DTO 변환 로직을 재검토 및 수정함.
    - `get_quotes`, `get_quote_by_id` 메소드가 반환하는 DTO가 스키마 정의(`from_location`, `to_location`, `cargo` 필드 등)와 정확히 일치하도록 모델 객체에서 스키마 객체로의 변환 로직을 명확히 함. Pydantic의 `model_validate` 및 `model_dump`를 활용하여 구성.
    - `submit_quote` 메소드에서 `create_structured_bill_of_lading` 함수에 전달하는 `quote_json_payload` 구성 시에도 스키마 정의를 참고하여, 모델 객체로부터 필요한 데이터를 추출하고 올바른 형태로 직렬화(Enum, datetime 등)하여 전달하도록 수정함.
    - `QuoteRepository.create_quote` 메소드의 시그니처를 `CreateQuoteRequest` 스키마를 받도록 변경하고, 내부 로직도 수정함. 관련 임포트 경로 수정.
    - `QuoteLocationAccessorialRepository.create_quote_location_accessorial` 메소드가 `List[QuoteLocationAccessorialSchema]`를 입력으로 받도록 수정하고, 내부 로직도 이에 맞게 변경함.
    - `QuoteService` 내 `EmailSender` 관련 임포트 및 호출부 주석을 해제함 (실제 구현이 있다고 가정).
- **결과**: API 응답 및 내부 데이터 전달 인터페이스의 일관성을 확보하고, 스키마 정의에 부합하는 정확한 데이터 구조를 사용하도록 개선함.
- **주의**: `create_structured_bill_of_lading` 함수가 요구하는 정확한 payload 스펙(특히 Decimal, datetime, Enum 필드의 직렬화 방식)에 대한 최종 확인 및 그에 따른 `submit_quote` 내부 payload 구성 로직의 미세 조정이 필요할 수 있음. 