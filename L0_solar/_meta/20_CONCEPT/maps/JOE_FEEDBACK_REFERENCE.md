# JOE 엔진 피드백 반영 참조

아래는 “조(JOE) 엔진을 행성 탐사/역추적 물리 엔진으로 키우는 설계” 피드백을 항목별로 정리한 것이며, **팩트(현재 구현) → 역할 고정 → 확장** 순서로 대응을 명시한다.

---

## 0) 팩트: 현재 JOE가 하는 일

| 항목 | 내용 |
|------|------|
| **입력** | `snapshot: dict` (sigma_plate, P_w, S_rot, W_surface, W_total, dW_surface_dt_norm 등) |
| **출력** | planet_stress (0~1), instability (0~1), habitability_label, summary |
| **정체** | **행성 시뮬레이터가 아니라 거시 관찰자/평가기(Observer/Assessor)** |

→ 이 정의를 유지한다. 흔들면 폴더/레이어가 꼬인다.

---

## 1) JOE 정체 — 한 문장 계약

**JOE = (거시 물리 입력) → (표준화된 Macro Snapshot) → (stress/instability/label) 출력하는 “행성 선별 엔진”**

- JOE가 “모든 물리 법칙”을 직접 푸는 것이 아님.
- 물리 디테일을 **표준 스냅샷 키**로 압축하는 단계가 별도로 존재해야 함 → **Feature Extractor Layer**가 그 역할.

**반영 상태**: `snapshot_convention.py`, `feature_layers/`, `aggregator.py` 로 2단계(Feature → Aggregator) 유지.

---

## 2) 역추적 설계 — “역적분”이 아닌 “추정/동화”

| 피드백 | 반영 |
|--------|------|
| 시간을 거꾸로 적분해 유일한 초기 상태를 복원하는 것은 일반적으로 **ill-posed** (해 여러 개/불안정) | 역추적 = **역적분이 아니라 추정/동화(assimilation)** 로 설계 |
| 목표: “초기상태 하나”가 아니라 **초기 후보 분포/범위** + **MAP 추정치(최적 후보)** | `JOE_REVERSE_MODE.md` 및 `forward_inference.py` 계약에 명시 |
| 방법: (1) 정방향 거시 동역학 모델 정의 (2) 관측(현재 지구)에 맞게 초기 파라미터 최적화/필터링/샘플링 | Forward 모드 / Inference 모드 인터페이스로 계약 (함수 시그니처) |

**반영 상태**: `JOE_REVERSE_MODE.md` 갱신, `joe/forward_inference.py` 에 Forward/Inference 시그니처 및 docstring 추가.

---

## 3) JOE 확장 구조 — 2레벨 고정

| 레이어 | 역할 | 현재 구현 |
|--------|------|-----------|
| **(A) Feature Extractor** | 물리 → Macro Snapshot 생성 (우주필드/질량/회전/대기/물/판 proxy → 무차원 점수) | `feature_layers/` (cosmic, mass_rotation, retention, water_plate_proxy) |
| **(B) Coarse Aggregator** | snapshot → stress/instability (PANGEA §4) | `aggregator.py`, standalone `_core.py` |

**결론**: “JOE 확장”은 _core를 키우는 게 아니라 **물리→스냅샷 Feature 계층 추가**가 정답. → 유지됨.

---

## 4) 물리 확장 기능 단위 (스냅샷 키로 환원)

| 기능 | 목표 | 스냅샷 후보 키 | 현재 |
|------|------|----------------|------|
| 4.1 우주 필드장 | 외부 스트레스/차폐 필요도 | F_star_norm, stellar_wind_pressure_norm, cosmic_ray_flux_norm, **field_stress_score** | cosmic: F_star_norm, in_habitable_zone. field_stress_score는 문서/스키마에 명시 |
| 4.2 정지 질량·중력·대기 유지 | 지구형+대기 유지 가능 | g_surface_norm, v_escape_norm, atm_retention_score | mass_rotation, retention 에서 산출 |
| 4.3 회전·대칭 | 주야/계절/기후 순환 가능 | **S_rot = clamp01((ω²R)/g)**, obliquity_score | S_rot 표준 정의 적용, obliquity_score는 스키마에 명시 |
| 4.4 물 예산 | 액체물 창 거시 판단 | liquid_window_score, W_surface/W_total, dW_surface_dt_norm | water_plate_proxy |
| 4.5 판/내부열 proxy | 가능성 점수만 | sigma_plate, P_w | 기존 CORE_KEYS |

**반영 상태**: `snapshot_convention.py` 및 `JOE_SNAPSHOT_SCHEMA_V02.md` 에 field_stress_score, obliquity_score 포함한 스키마 명시.

---

## 5) 역추적 = Forward 모드 + Inference 모드

| 모드 | 입력 | 출력 | 비고 |
|------|------|------|------|
| **Forward** | 초기 거시 상태 x0 (또는 스냅샷) | 시간에 따른 macro snapshot snap(t) 또는 x(t) | 조 레벨 상태벡터: [M, R, ω, ε, e, W_total, W_surface, sigma_plate, P_w, …] |
| **Inference** | 관측 y_now (현재 지구/스냅샷) | x0_hat(최적 후보), confidence/range 또는 후보 집합 | 파라미터 스윕, 베이지안 최적화, EKF/UKF/Particle Filter 등 |

**핵심**: 역추적은 “정답 하나”가 아니라 **조건을 만족하는 초기 후보들의 집합을 좁혀가는 엔진**으로 설계.

**반영 상태**: `joe/forward_inference.py` 에 `forward_dynamics`, `infer_initial_candidates` 시그니처 및 계약 문서.

---

## 6) CONFIG 주입 — 하드코딩 제거

| 요구 | 반영 |
|------|------|
| 가중치/정규화 범위/임계값을 파일 상수로 두지 말 것 | `DEFAULT_CONFIG` dict + 실행 시 `config` 오버라이드 |
| 출력(PlanetAssessment/JoeAssessmentResult)에 **실제 사용된 config** 포함 | `config_used` 필드 포함 |
| “어떤 계수/정규화로 나왔는지” 기록해 재현 가능하게 | aggregator.assess(), explore.assess_planet() 모두 config_used 반환 |

**반영 상태**: `aggregator.py`, standalone `Joe_Engine/_core.py`, `explore.py` 에서 적용 완료.

---

## 7) 폴더 흐름 (선택적 대응)

피드백 제안:  
`solar/01_planet_scout/joe_engine/` | `02_creation_days` | `03_eden` | `04_underworld`

현재:  
`solar/_01_beginnings/joe` | `_02_creation_days` | `_03_eden_os_underworld` | …

→ 서사적 순서(탐사→천지창조→에덴→언더월드)는 동일. 번호/이름만 다름. 필요 시 별도 리네이밍 이슈로 정리.

---

## 8) JOE 출력 계약 (고정)

- **항상**: macro_snapshot + planet_stress + instability + habitability_label (+ config_used)
- **옵션(역추적 확장 시)**: x0_distribution 또는 initial_candidates (역추정 결과)

---

## 관련 문서

- [JOE_REVERSE_MODE.md](JOE_REVERSE_MODE.md) — 역추적 = 추정/동화, Forward·Inference 모드
- [JOE_PHYSICS_EXPANSION.md](JOE_PHYSICS_EXPANSION.md) — 9단계 확장
- [JOE_SNAPSHOT_SCHEMA_V02.md](JOE_SNAPSHOT_SCHEMA_V02.md) — 스냅샷 스키마 v0.2
- solar/_01_beginnings/joe/forward_inference.py — Forward/Inference 인터페이스 계약
