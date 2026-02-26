# 02 — 궁창 (바다-하늘 분리)

**개념**: 궁창 위의 물과 궁창 아래의 물이 나뉘는 단계.  
대기(기체)·바다(액체) 분리, 온실 효과, 수순환.

---

## 성경 창조 의미

> *"하나님이 궁창을 만드사 궁창 위의 물과 궁창 아래의 물로 나뉘게 하시니라"* (창 1:7)  
> **둘째날**. “궁창” = 바다(액체)와 하늘(기체)의 **경계**.  
> 엔진에서는 대기 column이 그 경계를 구현: PT(압력·온도)에 따른 `water_phase()`, 증발·응결(수순환).

---

## 실제 파일 구성

| 경로 (solar/ 기준) | 역할 |
|--------------------|------|
| **atmosphere/column.py** | `AtmosphereColumn`: T_surface, P_surface, albedo, greenhouse, `step(F, dt)`, `state()`, `water_phase()`, `habitable` |
| **atmosphere/greenhouse.py** | τ(조성)→ε_a, `equilibrium_surface_temp(F, albedo, ...)` |
| **atmosphere/water_cycle.py** | 증발·응결·잠열, `latent_heat_flux`, `saturation_mixing_ratio` |
| **atmosphere/_constants.py** | 대기·물 상수 |
| **atmosphere/__init__.py** | atmosphere 패키지 export |

---

## 엔지니어링 — 환경설정 관점

- **상태변수**: `T_surface` [K], `P_surface` [Pa], composition(τ, ε_a), `water_phase` (liquid/vapor/ice)
- **입력**: `../em/` 의 `F_solar`; `../surface/` 의 `effective_albedo()` (옵션).  
  column 생성 시 `albedo=...`, `T_surface_init=...` 등으로 설정.
- **출력**: `state()` → T_surface, P_surface, habitable, water_phase; `surface_heat_flux()` (SurfaceOcean 연동용).
- **의존**: em/, surface/ **읽기 전용**. core/ (질량·반지름)은 호출자가 넘김.

---

## 다음 레이어

→ **03_surface**: 땅과 바다 분리(지표면 분화).
