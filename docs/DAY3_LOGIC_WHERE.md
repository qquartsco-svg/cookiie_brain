# 셋째날(Phase 7) — 로직·구조가 어디서 진행되는지

**기준 경로**: `/Users/jazzin/Desktop/00_BRAIN/CookiieBrain/`  
아래는 모두 이 루트 기준 상대 경로.

---

## 1. 셋째날 “땅과 바다” 로직이 들어 있는 코드 (실제 구현)

| 경로 | 역할 |
|------|------|
| **solar/surface/surface_schema.py** | 땅·바다 분리 수식. `SurfaceSchema`, `effective_albedo()`. (여기서 셋째날 로직이 돌아감) |
| **solar/surface/__init__.py** | surface 패키지 진입점. 위 모듈 export |
| **solar/__init__.py** | `SurfaceSchema`, `effective_albedo` 를 solar 패키지에서 노출 |

→ **진짜 “셋째날 구조”가 구현된 파일은 `solar/surface/surface_schema.py` 하나.**

---

## 2. 셋째날을 “설명·설계”하는 문서

| 경로 | 역할 |
|------|------|
| **solar/surface/README.md** | surface 레이어 개념, 셋째날 = 땅·바다, A_eff 수식, 검증 요약 |
| **solar/concept/03_surface/README.md** | 개념용. “03 — 땅과 바다”, 셋째날 한 줄 정의 |
| **docs/DAY3_ENVIRONMENT_WHERE_AND_WHAT.md** | 셋째날 환경이 **어느 파일/어디서** 구성되는지 정리 (이 표와 같은 목적) |
| **docs/CREATION_DAYS_AND_PHASES.md** | 창세기 날짜 ↔ Phase 매핑, 셋째날 1단계(땅)/2·3단계(풀·씨·열매) 범위 |
| **docs/VERSION_LOG.md** | v1.6.0 셋째날 항목 |
| **solar/README.md** | solar 전체 구조 안에서 surface(Phase 7 / 셋째날) 위치 |
| **solar/LAYERS.md** | 개념 레이어 순서, 3일 = 땅과 바다 → surface/ |

---

## 3. 셋째날이 맞게 동작하는지 보는 검증(데모)

| 경로 | 역할 |
|------|------|
| **examples/surface_day3_demo.py** | Phase 7 전용 데모. P7-1~P7-4 (알베도, 전 바다/전 육지, surface→atmosphere 연동, 땅 비율↑→냉각) |

→ **셋째날 로직을 “실행해서 확인”하는 곳은 `examples/surface_day3_demo.py`.**

---

## 4. 셋째날 “다음” 단계 (풀·씨·열매, 식생) — 어디서 진행되는지

| 경로 | 역할 |
|------|------|
| **solar/biosphere/** | 셋째날 직후 “척박 → 선구 → 광합성 → 대기 변화 → 호흡 식생” 로직 (Phase 7b). 풀·씨·열매 쪽 구현은 여기서 진행 |
| **docs/BIOSPHERE_LAYER_SPEC.md** | 위 biosphere 레이어 설계·상태변수·수식·포트 정의 |

→ **풀·씨·열매/식생 관련 로직은 `solar/biosphere/` 에서 진행.**

---

## 5. 한 줄 요약

- **땅과 바다만 나누는 셋째날 로직**:  
  **`solar/surface/surface_schema.py`** 에서 진행되고,  
  검증은 **`examples/surface_day3_demo.py`** 에서 함.

- **그 다음(풀·씨·열매·식생)**:  
  **`solar/biosphere/`** 에서 진행함.
