# LTP 서버 - 견적 산출 로직 종합 테스트 케이스

이 문서는 견적 산출 로직의 모든 구성 요소를 독립적으로 검증하기 위한 종합 테스트 케이스를 제공합니다. 각 테스트 케이스는 특정 규칙이나 조건을 정확히 실행하도록 설계되었습니다.

## 시스템 데이터 공통 가정

모든 테스트 케이스는 아래의 시스템 데이터가 DB에 설정되어 있다고 가정합니다.

- **유류할증료 (FSC):** 35% (`0.35`)
- **기준 요율 지역:** 별도 명시가 없는 한, 모든 계산은 **`Area 1` (A 지역)**의 요율을 기준으로 합니다.
  - `min_load`: $25.00
  - `max_load`: $225.00
  - `max_load_weight`: 5000 lbs
- **`Area 1` 무게별 운임 단가:**
  - 1-1000 lbs: $0.0525 / lb
  - 1001-2000 lbs: $0.0500 / lb
  - 2001-3000 lbs: $0.0475 / lb
  - 3001-5000 lbs: $0.0450 / lb

---

## A. 기본 운임 (Base Cost) 테스트

### A-1: 기준 운임 (LTL, 최소 운임 적용)

- **목표:** 계산된 LTL 운임이 `min_load`보다 낮을 때, `min_load`가 적용되는지 검증합니다. (가장 기본적인 케이스)
- **입력 데이터:**
  ```json
  {
    "cargo_transportation_id": 1,
    "is_priority": false,
    "user_id": 1, 
    "from_location": { "location_type": "COMMERCIAL", "accessorials": [], "request_datetime": "2024-10-22T10:00:00" },
    "to_location": { "location_type": "COMMERCIAL", "accessorials": [], "request_datetime": "2024-10-22T14:00:00" },
    "cargo_list": [
      { "quantity": 1, "weight": 100, "width": 20, "height": 20, "length": 20 }
    ]
  }
  ```
- **계산 과정:**
  1.  **운임 무게:** `max(실제 100 lbs, 부피 49 lbs) = 100 lbs`.
  2.  **기본 운임:** `100 lbs * $0.0525/lb = $5.25`.
  3.  **최소 운임 비교:** `$5.25` < `$25.00`. 운임은 **$25.00**로 조정됨.
  4.  **FSC 적용:** `$25.00 * 1.35 = $33.75`.
- **예상 결과:**
  - **Base Price:** `$33.75`
  - **Extra Price:** `$0.00`
  - **Total Price:** `$33.75`

### A-2: FTL 운임

- **목표:** `cargo_transportation_id=2` (FTL)일 때, 화물 무게와 무관하게 `max_load`가 적용되는지 검증합니다.
- **입력 데이터:**
  ```json
  {
    "cargo_transportation_id": 2,
    "is_priority": false,
    "user_id": 1,
    "from_location": { /* A-1과 동일 */ },
    "to_location": { /* A-1과 동일 */ },
    "cargo_list": [
      { "quantity": 1, "weight": 100, "width": 10, "height": 10, "length": 10 }
    ]
  }
  ```
- **계산 과정:**
  1.  **기본 운임:** FTL이므로 `Area 1`의 `max_load`인 **$225.00**로 결정됩니다.
  2.  **FSC 적용:** `$225.00 * 1.35 = $303.75`.
- **예상 결과:**
  - **Base Price:** `$303.75`
  - **Extra Price:** `$0.00`
  - **Total Price:** `$303.75`

### A-3: LTL - 부피 무게 기준 운임

- **목표:** 부피가 큰 화물의 운임이 부피 무게를 기준으로 계산되며, `min_load`를 초과하는 경우를 검증합니다.
- **입력 데이터:**
  ```json
  {
    "cargo_transportation_id": 1,
    "is_priority": false,
    "user_id": 1,
    "from_location": { /* A-1과 동일 */ },
    "to_location": { /* A-1과 동일 */ },
    "cargo_list": [
      { "quantity": 1, "weight": 50, "width": 50, "height": 40, "length": 40 }
    ]
  }
  ```
- **계산 과정:**
  1.  **운임 무게:** 실제 무게(`50 lbs`) < 부피 무게(`(50*40*40)/166 = 482 lbs`). 총 운임 무게는 `482 lbs`.
  2.  **기본 운임:** `482 lbs * $0.0525/lb = $25.31` (반올림).
  3.  **최소 운임 비교:** `$25.31` > `$25.00`. 운임은 그대로 유지됨.
  4.  **FSC 적용:** `$25.31 * 1.35 = $34.17` (반올림).
- **예상 결과:**
  - **Base Price:** `$34.17`
  - **Total Price:** `$34.17`

### A-4: LTL - 여러 화물 무게 합산

- **목표:** 여러 화물의 운임 무게가 정확히 합산되어 `min_load`를 초과하는 총 운임이 계산되는지 검증합니다.
- **입력 데이터:**
  ```json
  {
    "cargo_transportation_id": 1,
    "is_priority": false,
    "user_id": 1,
    "from_location": { /* A-1과 동일 */ },
    "to_location": { /* A-1과 동일 */ },
    "cargo_list": [
      { "quantity": 1, "weight": 300, "width": 20, "height": 20, "length": 20 },
      { "quantity": 1, "weight": 200, "width": 50, "height": 40, "length": 40 }
    ]
  }
  ```
- **계산 과정:**
  1.  **운임 무게:** `max(300, 48.193) + max(200, 481.928) = 300 + 481.928 = 781.928 lbs`. (소수점 올림 처리)
  2.  **기본 운임:** `781.928 lbs * $0.0525/lb = $41.05122`.
  3.  **FSC 적용:** `$41.05122 * 1.35 = 55.419147`. 최종 올림 처리 후 **$55.420**.
- **예상 결과:**
  - **Base Price:** `$55.420`
  - **Total Price:** `$55.420`

---
## B. 위치 및 부가 서비스 (Extra/Location Cost) 테스트

**기준 비용:** 모든 테스트는 **A-1 케이스(총액 $33.75)**에 추가 비용이 더해지는 상황을 가정합니다.

### B-1: 주거지(Residential) 비용

- **목표:** `location_type`이 `RESIDENTIAL`일 때 고정 비용($25)이 추가되는지 검증합니다.
- **입력 데이터:**
  ```json
  {
    "cargo_transportation_id": 1, "is_priority": false, "user_id": 1,
    "from_location": { "location_type": "RESIDENTIAL", "accessorials": [], "request_datetime": "2024-10-22T10:00:00" },
    "to_location": { "location_type": "COMMERCIAL", "accessorials": [], "request_datetime": "2024-10-22T14:00:00" },
    "cargo_list": [{ "quantity": 1, "weight": 100, "width": 20, "height": 20, "length": 20 }]
  }
  ```
- **예상 결과:**
  - **Base Price:** `$33.75`
  - **Extra Price:** `$25.00`
  - **Total Price:** `$58.75`

### B-2: 리프트 게이트(Lift Gate) 비용

- **목표:** `accessorials`에 `Lift Gate`가 있을 때 고정 비용($25)이 추가되는지 검증합니다.
- **입력 데이터:**
  ```json
  {
    "cargo_transportation_id": 1, "is_priority": false, "user_id": 1,
    "from_location": { "location_type": "COMMERCIAL", "accessorials": [{"cargo_accessorial_id": 3, "name": "Lift Gate"}], "request_datetime": "2024-10-22T10:00:00" },
    "to_location": { "location_type": "COMMERCIAL", "accessorials": [], "request_datetime": "2024-10-22T14:00:00" },
    "cargo_list": [{ "quantity": 1, "weight": 100, "width": 20, "height": 20, "length": 20 }]
  }
  ```
- **예상 결과:**
  - **Base Price:** `$33.75`
  - **Extra Price:** `$25.00`
  - **Total Price:** `$58.75`

### B-3: 주말(Weekend) 비용

- **목표:** `request_datetime`이 주말일 때 비용($100)이 추가되는지 검증합니다.
- **입력 데이터:**
  ```json
  {
    "cargo_transportation_id": 1, "is_priority": false, "user_id": 1,
    "from_location": { "location_type": "COMMERCIAL", "accessorials": [], "request_datetime": "2024-10-26T10:00:00" }, // 토요일
    "to_location": { "location_type": "COMMERCIAL", "accessorials": [], "request_datetime": "2024-10-26T14:00:00" },
    "cargo_list": [{ "quantity": 1, "weight": 100, "width": 20, "height": 20, "length": 20 }]
  }
  ```
- **예상 결과:**
  - **Base Price:** `$33.75`
  - **Extra Price:** `$100.00`
  - **Total Price:** `$133.75`

### B-4: 우선 처리(Priority) 비용

- **목표:** `is_priority`가 `true`이고 시간이 업무 시간일 때 비용($100)이 추가되는지 검증합니다.
- **입력 데이터:**
  ```json
  {
    "cargo_transportation_id": 1, "is_priority": true, "user_id": 1,
    "from_location": { "location_type": "COMMERCIAL", "accessorials": [], "request_datetime": "2024-10-22T10:00:00" },
    "to_location": { "location_type": "COMMERCIAL", "accessorials": [], "request_datetime": "2024-10-22T14:00:00" },
    "cargo_list": [{ "quantity": 1, "weight": 100, "width": 20, "height": 20, "length": 20 }]
  }
  ```
- **예상 결과:**
  - **Base Price:** `$33.75`
  - **Extra Price:** `$100.00`
  - **Total Price:** `$133.75`

---
## C. 할인 (Discount) 테스트

### C-1: 사용자 등급 할인

- **목표:** 할인 등급의 사용자가 최종 금액에서 올바르게 할인을 받는지 검증합니다. (Gold 등급, 할인율 10% 가정)
- **입력 데이터:**
  - **사용자:** Gold 등급 (e.g., `user_id` 2)
  - **견적 요청:** **B-1 케이스**와 동일 (`기본운임` + `주거지 수수료` = `$58.75`)
- **계산 과정:**
  1.  **할인 전 총액:** `$58.75`.
  2.  **할인액:** `$58.75 * 0.10 = $5.88` (반올림).
  3.  **최종 금액:** `$58.75 - $5.88 = $52.87`.
- **예상 결과:**
  - **Base Price:** `$33.75`
  - **Extra Price:** `$25.00`
  - **Total Price (할인 후):** `$52.87`

---
## D. 복합 시나리오 테스트

### D-1: 종합 테스트

- **목표:** 여러 규칙이 복합적으로 적용될 때, 각 비용이 누락 없이 합산되고 할인까지 정확히 적용되는지 검증합니다.
- **입력 데이터:**
  ```json
  {
    "cargo_transportation_id": 1,
    "is_priority": true,
    "user_id": 2, // Gold 등급 사용자 (10% 할인)
    "from_location": {
      "location_type": "RESIDENTIAL",
      "accessorials": [],
      "request_datetime": "2024-10-22T10:00:00"
    },
    "to_location": {
      "location_type": "COMMERCIAL",
      "accessorials": [{"cargo_accessorial_id": 3, "name": "Lift Gate"}],
      "request_datetime": "2024-10-26T14:00:00"
    },
    "cargo_list": [
      { "quantity": 1, "weight": 300, "width": 20, "height": 20, "length": 20 },
      { "quantity": 1, "weight": 200, "width": 50, "height": 40, "length": 40 }
    ]
  }
  ```
- **계산 과정:**
  1.  **기본 운임 (Base Price):** $55.43 (A-4 케이스 참고)
  2.  **추가 비용 (Extra Price):**
      - 주거지(From): `$25.00`
      - 리프트게이트(To): `$25.00`
      - 우선처리(From): `$100.00`
      - 주말(To): `$100.00`
      - 우선처리(To): `$100.00`
      - **총 Extra Price:** `$350.00`
  3.  **할인 전 총액:** `$55.43 + $350.00 = $405.43`
  4.  **할인:** `$405.43 * 0.10 = $40.54` (반올림)
  5.  **최종 금액:** `$405.43 - $40.54 = $364.89`
- **예상 결과:**
  - **Base Price:** `$55.43`
  - **Extra Price:** `$350.00`
  - **Total Price:** `$364.89` 