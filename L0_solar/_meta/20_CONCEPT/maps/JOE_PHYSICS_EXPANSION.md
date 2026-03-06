# 조(JOE) 물리 확장 방향

조 엔진은 **물리 법칙에 기반해 행성이 지구화(테라포밍)될 수 있는지** 단계적으로 평가하는 엔진이다.  
현재 구현은 **PANGEA §4** 수식으로 `planet_stress`, `instability`만 산출한다.  
아래는 **확장 시** 반영할 물리 단계와 변수·계약이다. (구현 로드맵)

---

## 현재 구현 (solar._01_beginnings.joe)

**입력 스냅샷** (dict):  
`sigma_plate`, `P_w`, `S_rot`, `W_surface`, `W_total`, `dW_surface_dt_norm`, `omega_spin_rad_s`, `obliquity_deg`, `GEL_surface_eden_m`, `W_canopy_ref_km3` 등.

**출력**:  
`(planet_stress, instability)` — FirmamentLayer.step(instability=...) 및 파이프라인으로 전달.

**수식**: PANGEA §4 가중 합 → [0,1] 정규화.

---

## 확장 방향 (Physics-First Planet Evaluation)

조를 **실제 행성 탐사 엔진 모듈**로 확장할 때, 아래 단계를 순서대로 반영할 수 있다.

| 단계 | 이름 | 검사 항목 / 변수 | 비고 |
|------|------|-------------------|------|
| **1** | Cosmic Field Scan | 중력장, 복사(F_star = L/(4πr²)), 자기장 환경, 우주선 flux. Habitable Zone 여부. | 현재 joe에는 미구현. 스냅샷에 F_star, r_au 등 추가 가능. |
| **2** | Mass & Rotation Stability | M, R, ω, ρ. g=GM/R², v_escape=√(2GM/R). centrifugal=ω²R < g (붕괴 방지). | S_rot, obliquity 일부 대응. 확장 시 M,R,ω 명시. |
| **3** | Planet Formation | 판 구조, 내부 열. Rayleigh number Ra. Plate tectonics 가능성. | sigma_plate, P_w 가 여기 대응. |
| **4** | Atmospheric Retention | v_escape > 6×v_thermal. v_thermal=√(3kT/m). 대기 탈출/유지. | 스냅샷에 T, m_mean 등 추가 가능. |
| **5** | Surface Hydrology | 273K < T_surface < 373K. 물 총량, 증발률. | W_surface, W_total, dW 현재 사용 중. |
| **6** | Magnetic & Radiation Shield | 다이너모 조건. R_mp (자기권 반경). | day1/em, magnetosphere 등과 연동. |
| **7** | Climate Stability | Milankovitch. insolation, eccentricity, obliquity, precession. | day4/cycles와 연동. |
| **8** | Biosphere Potential | 물·탄소·에너지·안정 환경. biosphere_score. | day3/biosphere, day6와 연동. |
| **9** | Terraforming Potential | climate + atmosphere + water + radiation 가중치. terraform_index. | 최종 출력으로 확장 가능. |

---

## 확장 시 입출력 계약 (권장)

- **입력**: 단계별 스냅샷(dict).  
  예: `cosmic_field`, `mass_rotation`, `formation`, `atmosphere`, `hydrology`, `magnetosphere`, `climate`, `biosphere`, `terraforming` 각각 dict 또는 공통 스냅샷에 키 추가.
- **출력**:  
  - 기존: `(planet_stress, instability)`  
  - 확장: `habitability_label` (high/moderate/low/extreme), `terraform_index`, 단계별 점수(선택).

독립 엔진 **Joe_Engine**과 계약을 맞추면, 본편(solar) joe는 그 엔진을 호출하거나 동일 수식 로컬 구현을 유지할 수 있다.

---

## 관련 문서

- [TERRAFORMING_EXPLORER_FLOW.md](TERRAFORMING_EXPLORER_FLOW.md) — 조 → 모 → 체루빔 흐름  
- docs/PLANET_DYNAMICS_ENGINE.md — JOE 공식 명칭·Observer 철학  
- docs/PANGEA_ROTATION_AND_WATER_BUDGET.md — L0~L3, 물 예산
