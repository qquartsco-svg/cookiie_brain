# 반응 동역학 레이어 — 최소 사양

**피드백 반영**: 데이터 구조상 "물리 레이어 → 반응 동역학 → 인지 기어" 연결이 실제로 가능한지 명시.

---

## 1. 상태공간 정의

### CookiieBrain 환경 출력 (현재)

| 변수 | 의미 | extension |
|------|------|-----------|
| F_solar | 복사 조도 [W/m²] | solar_environment.bodies[name].F_solar |
| T_surface | 표면 온도 [K] | solar_environment.bodies[name].T_surface |
| P_surface | 압력 [Pa] | solar_environment.bodies[name].P_surface |
| albedo | 유효 알베도 | (surface_schema에서) |
| surface_heat_flux | 표면 열플럭스 [W/m²] | (column.surface_heat_flux) |
| surface_ocean_depths | 우물 수심 (12개) | (core.SurfaceOcean) |
| vorticity | 위도별 와도 | (core.SurfaceOcean) |
| habitable | 액체 물 가능 | solar_environment.bodies[name].habitable |

### 반응 동역학 레이어 — 최소 입력 벡터

| 입력 | 의미 | 환경 출처 |
|------|------|-----------|
| **temperature_field** | T(x) 또는 T_scalar | T_surface (0D) → 확장 시 격자 |
| **energy_flux** | 에너지 유입 [W/m²] | surface_heat_flux, F_solar |
| **chemical_gradient** | 농도 구배 (옵션) | (미구축) pH, 전기화학 |
| **concentration_vector** | [A, B, …] 초기/현재 | 반응 상태 |
| **diffusion_coefficient** | D_i [m²/s] | 파라미터 |
| **boundary_condition** | periodic / closed / flux | 파라미터 |

### 반응 동역학 레이어 — 최소 상태 벡터

```
state:
  concentration_vector  [n_species]   농도
  energy_input          float         환경에서 받는 유입
  diffusion             D_i           확산계수
  reaction_matrix       R_ij          반응 네트워크 (또는 ODE 계수)
  boundary_condition    enum           periodic | closed | flux
```

---

## 2. 현실 점검: ODE vs PDE

| 구분 | 반응 ODE만 | 반응-확산 PDE |
|------|------------|---------------|
| 공간 | 없음 (0D) | 격자 (1D/2D) |
| 확산 | ❌ | ∂c/∂t = D∇²c |
| 경계 | — | 필수 |
| 창발 | limit cycle만 | 공간 패턴, spiral |

**결론**: 반응 ODE만 넣으면 **불충분**.  
경계가 없으면 농도는 확산으로 평탄화 → 자가순환 유지 불가.  
**반응-확산 PDE** 구조가 필요.

---

## 3. 창발 판정 기준 (엔지니어링)

철학적 "창발" 대신 **측정 가능한 지표**:

| 지표 | 의미 | 구현 |
|------|------|------|
| **limit_cycle** | 자가 유지 진동 | 궤적 폐곡선, 주기성 |
| **entropy_production_rate** | dS/dt (비평형 지표) | σ = J·F (유량×구동력) |
| **Lyapunov_exponent** | 초기 조건 민감도 | λ > 0 → chaos |
| **autocatalytic_loop** | A → B → A 폐루프 | 반응 네트워크 그래프 분석 |

---

## 4. 분기점 — 최소 반응계 선택

> **자가순환을 만들 최소 반응계는 무엇인가?**

| 후보 | 특징 | 공간 필요 |
|------|------|-----------|
| **Brusselator** | 자가촉매, oscillatory | ODE 가능, PDE 시 패턴 |
| **Gray-Scott** | 2종 피드백 | PDE (공간 패턴) |
| **간단한 autocatalytic** | A + B → 2A | ODE |
| **pH gradient 기반** | 전기화학 구배 | 격자 + 구배 |

**선택 기준**:
- 구현 단순성
- 환경(T, F) 파라미터 연결 용이성
- 창발 판정(limit cycle 등) 계산 가능성
- 확장 시 PDE로 자연스럽게 넘어갈 수 있는지

---

## 5. 데이터 구조 연결 검증

```
solar_environment (dict)
    │ F_solar, T_surface, surface_heat_flux, habitable
    ▼
reaction_dynamics (dict)
    │ concentration_vector, energy_input, oscillating, limit_cycle
    ▼
cognitive / Engines (GlobalState 읽기)
    │ state.get_extension("reaction_dynamics")
```

**질문**: 이 연결이 **데이터 구조상** 가능한가?  
**답**: 예. extension은 dict. reaction_dynamics는 concentration_vector, energy_input 등을 담으면 됨.  
**조건**: energy_input을 solar_environment에서 읽어와야 함. 호출 순서가 solar → reaction 이어야 함.
