# solar/atmosphere/ — 대기권 레이어 (궁창 / Firmament) v1.4.0

**궁창**은 액체 수권과 기체 수권을 분리하는 압력-온도 경계다.
우물에 물이 고인 상태(SurfaceOcean) 위에, 태양 복사가 가해지면
대기권이 형성되고 바다와 하늘이 구분된다.

궁창은 "하늘"이라는 개체가 아니라, PT(Pressure–Temperature) 공간에서
액체가 안정되는 경계 조건이 충족되는 순간이다.

이 레이어는 `em/solar_luminosity`의 조도(F)와 `core/`의 질량·반지름을 읽는다.
물리 코어를 수정하지 않는 **관측자 모드**로 동작한다.

**모델 스코프**: 0D **단일 대기 컬럼(전지구 평균)**이다.
대기 순환(해들리셀), 구름/강수, 수증기 피드백(Phase 6b)은 별도 모듈로 처리한다.

---

## 개념: 우물 → 바다 → 궁창 → 대기권

### 1. 우물에 물이 고인 상태

`core/SurfaceOcean`은 행성 표면에 분포한 **우물(wells)**이다.
12개 우물이 적도 링 상에 배치되고, 조석 변형(P2 Legendre)과
압력 구배·코리올리 힘에 의해 `depths[]`, `current_vel`, `vorticity`가 갱신된다.

```
중력장 → 객체가 우물에 떨어짐
      → 물(정보)이 우물에 고임
      → SurfaceOcean.depths[], tidal_stretch, vorticity
```

이 상태가 **"아래의 물(바다)"**의 원시 형태다.

### 2. 바다와 하늘의 분리

태양 복사(F)가 가해지기 전:
- T_eq = 254 K (대기 없는 맨땅 평형)
- 물은 액체로 안정적으로 존재할 수 없음 (영하 19°C)

태양 복사 + 대기 온실 효과:
- T_surface = 288 K (영상 15°C)
- **위의 물(수증기)**과 **아래의 물(액체 바다)**이 압력-온도 공간에서 분리됨
- 대기 컬럼이 중력에 의해 유지되는 구조 형성

이것이 **궁창(Firmament)**의 물리적 정의다.

### 3. 대기권 형성 과정

| 단계 | 입력 | 출력 |
|------|------|------|
| 복사 입력 | F(r) [W/m²] from solar_luminosity | 흡수층 도달 |
| 온실 효과 | τ(CO₂, H₂O, CH₄) → ε_a | T_eq → T_surface (+34K) |
| 열적 관성 | C·dT/dt = F_in - F_out | 시간 지연 (τ_th ≈ 2 yr) |
| 대기압 | M_col, g | P_surface [Pa] |
| 물 상태 | T, P | solid / liquid / gas |

온실 효과의 본질은 **단순 온도 상승이 아니다**.
복사 플럭스 재분배 + 시간 지연 + 열용량 효과.
→ 낮/밤 온도차 감소, 계절 완충, 열 저장/방출 지연.

---

## 모듈 구조

```
solar/atmosphere/
├── _constants.py    ← 물리 상수 (SIGMA_SB, K_BOLTZ, AU_M, YR_S, …)
├── greenhouse.py    ← τ(조성) → ε_a → T_surface (1-layer 복사)
├── column.py        ← AtmosphereColumn: 열적 관성 ODE + 대기압 + 물 상태
└── README.md        ← 이 문서
```

### 의존 방향

```
core/EvolutionEngine  pos(t), vel(t), spin_axis, mass, radius
        │
em/solar_luminosity   F(r) = L/(4πr²) [W/m²]
        │
        ▼
atmosphere/           T_surface, P_surface, water_phase
        │
        └── surface_heat_flux()  ← Phase 6b: SurfaceOcean 연동 준비
```

**규칙**: `atmosphere/`는 `core/`와 `em/`을 **읽기만** 한다. 수정하지 않는다.

---

## 지배 방정식

τ(composition)는 간이 파라메트릭 근사이다. CO₂는 ln, H₂O/CH₄는 √ 형태의
휴리스틱이며, 물리 기반 라인-바이-라인 복사전달이 아니다. 값은 교정/확장 가능하며,
후속 버전에서 스펙트럼/밴드 모델로 대체 가능하다.

| 물리량 | 수식 | 모듈 |
|--------|------|------|
| 광학 깊이 | τ = τ_base + α_CO₂·ln(1+CO₂/ref) + α_H₂O·√(H₂O/ref) + α_CH₄·√(CH₄/ref) | greenhouse |
| 대기 emissivity | ε_a = 1 - exp(-τ) | greenhouse |
| 표면 온도 | T_s = [F(1-A)/(f·σ·(1-ε_a/2))]^(1/4) | greenhouse |
| 열적 관성 | C·dT/dt = F_absorbed - F_radiated | column |
| 열 이완 시간 | τ_th = C / (4σT³(1-ε_a/2)) | column |
| 대기압 | P = M_col · g | column |
| 물 상태 | T>273.16 K, P>611.73 Pa → liquid | column |

열용량 C ≈ 2.1×10⁸ J/(m²·K)는 해양 혼합층을 포함한 **유효 열용량**이다.
혼합층 깊이·대륙비율에 따라 달라지는 값으로 취급한다.

---

## 코드 상태공간

### AtmosphereColumn

```python
AtmosphereColumn(
    body_name="Earth",
    surface_gravity=9.81,
    albedo=0.306,
    redistribution=4.0,
    composition=AtmosphereComposition(),   # 동적 상태 변수
    heat_capacity=2.1e8,                   # [J/(m²·K)] 혼합층·대륙비율에 따른 유효값
    T_surface_init=288.0,
)

# 내부 상태:
#   T_surface [K]        — ODE로 진화
#   composition         — CO₂, H₂O, CH₄ 등 (외부에서 수정 가능)
#   _tau, _eps_a        — 조성으로부터 유도

# 메서드 → 출력:
.step(F_solar_si, dt_yr)     → 시간 진화 (linearized implicit)
.state(F_solar_si)           → AtmosphereState 스냅샷
.surface_pressure()         → P [Pa]
.thermal_timescale_s()      → τ_th [s]
.water_phase()              → "solid" / "liquid" / "gas"
.habitable()                → liquid water 존재 여부
.surface_heat_flux()       → [W/m²] (SurfaceOcean 연동용 출력 포트)
.equilibrium_temp(F)        → 평형 T_surface
.bare_eq_temp(F)            → T_eq (대기 없음)
```

### AtmosphereComposition

```python
AtmosphereComposition(
    N2=0.78,
    O2=0.0,
    CO2=400e-6,    # 400 ppm
    H2O=0.01,      # 1%
    CH4=1.8e-6,
    column_mass=1.0332e4,   # [kg/m²]
)

# 고정 상수가 아님. outgassing, 광분해, 생물 등에 의해 갱신 가능.
```

---

## 사용 예시

```python
from solar import SolarLuminosity, AtmosphereColumn, AtmosphereComposition
from solar.core import EvolutionEngine, Body3D
import numpy as np

sun = SolarLuminosity(mass_solar=1.0)
engine = EvolutionEngine()
engine.add_body(Body3D("Sun", mass=1.0, pos=np.zeros(3), vel=np.zeros(3)))
engine.add_body(Body3D("Earth", mass=3e-6, pos=np.array([1,0,0]),
                       vel=np.array([0, 2*np.pi, 0])))

atm = AtmosphereColumn(body_name="Earth", T_surface_init=288.0)

for _ in range(100):
    engine.step(0.01)
    r_au = np.linalg.norm(engine.bodies[1].pos)
    F = sun.irradiance_si(r_au)
    atm.step(F, 0.01)

st = atm.state(F)
print(f"T_surface = {st.T_surface:.1f} K")
print(f"P = {st.P_surface:.0f} Pa")
print(f"Water: {st.water_phase}, Habitable: {st.habitable}")
```

---

## 검증 (Phase 6a)

| 항목 | 결과 |
|------|------|
| T_eq (bare) | 254 K |
| T_surface (Earth) | 288 K |
| Greenhouse ΔT | +34 K |
| τ_IR (current) | 1.56 |
| ε_a | 0.79 |
| P_surface | 101,357 Pa |
| Water (Earth) | liquid |
| Mars | P=632 Pa, T=210 K, solid |
| Faint Young Sun (70%) | T=289 K, habitable |
| Core dE/E | 4.06×10⁻¹² |

---

## Phase 6b: 수순환 (Water Cycle) — v1.5.0

- `water_cycle.py`: Clausius-Clapeyron, evaporation_rate, latent_heat_flux
- `AtmosphereColumn(use_water_cycle=True)`: 잠열 + H₂O 피드백
- `EvolutionEngine.step(ocean_extras={"Earth": {"heat_flux": ...}})`
- `SurfaceOcean.update(..., heat_flux=...)` → depths 수정

검증: `examples/water_cycle_demo.py` (5항목 ALL PASS)

---

## 관련 문서

- [solar/em/](../em/) — 광도, 자기장, 태양풍, 자기권
- [solar/core/](../core/) — EvolutionEngine, SurfaceOcean (우물)
- [docs/VERSION_LOG.md](../../docs/VERSION_LOG.md) — v1.4.0 기록
