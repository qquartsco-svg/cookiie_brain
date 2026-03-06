# JOE Snapshot Schema v0.2

조(JOE) 엔진이 소비·산출하는 **표준 거시 스냅샷** 키 정의.  
Feature Extractor는 물리량을 이 키(무차원 점수/비율)로 환원하고, Aggregator는 CORE_KEYS만 읽어 stress/instability를 산출한다.

---

## CORE_KEYS (PANGEA §4 Aggregator 직접 사용)

| 키 | 타입 | 설명 |
|----|------|------|
| sigma_plate | float [0~1] | 판 구조/텍토닉 proxy. tectonics_score에서 매핑. |
| P_w | float | 내부 유체 압력 proxy (정규화는 Aggregator 내 p_ref 사용) |
| S_rot | float [0~1] | **표준 정의**: clamp01((ω²R)/g). 무차원 회전 안정성. |
| W_surface | float | 표면 수량 (단위 무관, 비율 계산용) |
| W_total | float | 총 수량. W_surface/W_total 로 수권 비율. |
| dW_surface_dt_norm | float [0~1] | 표면 수량 변화율 정규화. |

---

## 확장 키 (Feature Layer가 채움)

### (1) Cosmic / 우주 필드장

| 키 | 타입 | 설명 |
|----|------|------|
| F_star_norm | float | 항성 복사 플럭스 정규화 (지구 궤도 기준). HZ 판정 기반. |
| cosmic_ray_flux_norm | float | 우주선 플럭스 정규화 (차폐 전). |
| stellar_wind_pressure_norm | float | 항성풍 동압 정규화. |
| field_stress_score | float [0~1] | 위 3개 합성. 외부 스트레스/차폐 필요도. |
| in_habitable_zone | bool | F_star 등 기반 HZ 여부. |

### (2) Mass / Gravity / Retention

| 키 | 타입 | 설명 |
|----|------|------|
| g_surface_norm | float | 표면 중력 정규화 (지구 g 기준). |
| v_escape_norm | float | 탈출 속도 정규화 (지구 기준). |
| atm_retention_score | float [0~1] | 대기 유지 가능성 proxy (v_escape vs v_thermal 등). |

### (3) Rotation / Symmetry

| 키 | 타입 | 설명 |
|----|------|------|
| omega_spin_rad_s | float | 자전 각속도 [rad/s]. |
| centrifugal_ratio | float | (ω²R)/g. S_rot의 원시 입력. |
| S_rot | float [0~1] | clamp01(centrifugal_ratio). **표준 정의 고정**. |
| rotation_stable | bool | ω²R < g 여부. |
| obliquity_score | float [0~1] | 축 기울기 proxy. 계절성/기후 변동 가능성. |

### (4) Water feasibility

| 키 | 타입 | 설명 |
|----|------|------|
| liquid_window_score | float [0~1] | 액체물 창 proxy (온도/압력 영역). |
| T_eq_K, T_surface_K | float | 평형/표면 온도 [K]. liquid_window 계산용. |
| P_surface_proxy_norm | float | 표면 압력 proxy 정규화. |
| (기존) W_surface, W_total, dW_surface_dt_norm | - | CORE에 포함. |

### (5) Plate / Interior proxy

| 키 | 타입 | 설명 |
|----|------|------|
| sigma_plate | float | CORE. tectonics_score에서 매핑. |
| P_w | float | CORE. 내부 유체압 proxy. |

---

## 상태 벡터 (Forward/Inference용)

거시 “조 레벨” 상태 x (Forward 동역학 입력/출력, Inference 출력 후보):

- **예시**: M_kg, R_m, omega_spin_rad_s, obliquity_deg, 궤도 요소(e, a, …), W_total, W_surface, sigma_plate, P_w, (선택) F_star_norm, r_au, …
- 스냅샷은 이 상태벡터를 **무차원 점수/비율**로 압축한 뷰이다.

---

## 버전

- **v0.1**: CORE_KEYS 6개만.
- **v0.2**: 확장 키 명시 (field_stress_score, obliquity_score 포함), S_rot 표준 정의 고정, Forward/Inference용 상태 벡터 예시 추가.
