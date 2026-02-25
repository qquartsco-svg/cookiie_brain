# Cookiie Brain

**상태 공간 장(Field) 동역학 통합 엔진**

```
Version : 1.3.0
License : PHAM-OPEN v2.0
Python  : 3.8+
Author  : GNJz (Qquarts)
Repo    : https://github.com/qquartsco-svg/cookiie_brain
```

---

## 이 프로젝트가 하는 일

태양계를 떠올려 보세요.
태양이 장(場)을 만들고, 행성이 그 안에서 궤도를 돌고, 달이 조석 리듬을 만듭니다.

이 엔진은 **같은 수학적 구조**를 상태 공간 위에서 구현합니다.

- **태양 (1/r 중심장)** = 장기기억. 모든 상태를 묶는 장거리 인력.
- **지구 (Gaussian 우물)** = 개별 기억. 국소적 끌림, 상태를 가두는 매질.
- **달 (조석력)** = 리듬. 주기적 교란이 우물 안에 유속/대류/와도를 만든다.
- **공 (상태 벡터)** = 현재 상태. 세 스케일의 힘을 동시에 받으며 움직인다.

**핵심 통찰 — 동역학적 동형(Dynamical Isomorphism):**
```
천체에 대입하면 → 항법 알고리즘
인지에 대입하면 → 사고 전이 모델
제어에 대입하면 → 안정 궤도 제어
```
"태양계 = 뇌"가 아니라, **같은 동역학 구조를 공유한다.**

정답을 주는 시스템이 아니라, 각자의 해답을 찾아갈 수 있는 **구조**를 만드는 것이 목적입니다.

---

## What This Project Does

Think of the solar system.
The Sun creates a field, planets orbit within it, and the Moon drives tidal rhythms.

This engine implements the **same mathematical structure** on a state space.

- **Sun (1/r central field)** = long-term memory. Binds all states with long-range gravity.
- **Earth (Gaussian well)** = individual memory. Local attractor trapping the state.
- **Moon (tidal force)** = rhythm. Periodic perturbation generating flow and vorticity inside wells.
- **Ball (state vector)** = current state. Subject to all three scales of force simultaneously.

**Key insight — Dynamical Isomorphism:**
The same equation structure applies to celestial navigation, cognitive dynamics, and control theory.
It is not that "the solar system = the brain," but that they **share the same dynamical structure.**

**Full equation of motion (v0.8.0):**

```
m ẍ = -∇V_sun(x)       Tier 1: central gravity (1/r, long-range)
    + -∇V_wells(x,t)    Tier 2: well attraction (Gaussian, dynamic)
    + -∇V_moon(x,t)     Tier 3: tidal force (periodic perturbation)
    + ωJv                Phase A: Coriolis rotation
    - γv                 damping
    + I(x,v,t)           Hippo energy injection
    + σξ(t)              Phase C: thermal fluctuation

3D N-body (v1.2.2):
  F_i = Σ_{j≠i} G·m_j·(r_j - r_i) / |r_j - r_i|³
  τ = (3GM/r³)(C-A)(ŝ·r̂)(r̂×ŝ)   → precession
  B(r) = B₀·(R/r)³·[3(m̂·r̂)r̂ - m̂] → magnetic dipole
  P_sw(r) = P₀·(r₀/r)²            → solar wind
  r_mp = R·(k·B₀²/P_sw)^(1/6)     → magnetopause
  L = M^α                          → mass-luminosity
  F(r) = L/(4πr²)                  → irradiance
  T_eq = [F(1-A)/(4σ)]^¼           → equilibrium temp
```

Full concept (English): [docs/FULL_CONCEPT_AND_STATUS_EN.md](docs/FULL_CONCEPT_AND_STATUS_EN.md)

---

## 핵심 수식

```
Tier 1 (태양):  V_sun(r)    = -G·M / (r + ε)               장거리 구속
Tier 2 (지구):  V_wells(x,t) = -Σ A_i(t)·exp(-‖x-c_i‖²/(2σ²))  국소 끌림
Tier 3 (달):    V_moon(x,t) = -G_m·M_m / (‖x-x_moon(t)‖ + ε)   주기적 교란
조석 텐서:      T_ij = ∂²V_moon / ∂x_i∂x_j                      조석 구조

전체 운동 방정식:
  m ẍ = -∇V_sun - ∇V_wells - ∇V_moon + ωJv - γv + I(x,v,t) + σξ(t)

에너지 밸런스:    E = ½‖v‖² + V_sun + V_wells + V_moon
기억 강화:        A_i += η · proximity(x, c_i) · dt
기억 망각:        A_i *= exp(-λ · dt)
FDT:             σ² = 2γT/m
```

수학적 기초 · 구현 상세: [PotentialFieldEngine CONCEPT](https://github.com/qquartsco-svg/PotentialField_Engine/blob/main/docs/CONCEPT.md)

---

## 엔진 파이프라인

```
WellFormationEngine           episodes → W, b (Hopfield 가중치)
       ↓
┌── 3계층 중력 합성 (v0.7.0~) ────────────────────────────────┐
│  Tier 1: CentralBody         V_sun(r) = -GM/(r+ε)           │
│  Tier 2: GaussianWell        V_wells(x,t)                   │
│  Tier 3: OrbitalMoon         V_moon(x,t) 타원공전+조석       │
│           └ TidalField        → injection_func               │
└──────────────────────────────────────────────────────────────┘
       ↓
PotentialFieldEngine          V_total, g(x) → 상태 업데이트 (적분)
       │  ├ Strang splitting + exact rotation (Phase A)
       │  └ O-U exact 반스텝 (Phase C 요동)
       ↓
HippoMemoryEngine (v0.6.0)   기억 생애주기 + 에너지 배분 (태양)
       │  ├ MemoryStore:      우물 생성 · 강화 · 감쇠 · 소멸
       │  ├ EnergyBudgeter:   I(x,v,t) = 탐색 + 정착 + 리콜
       │  └ pot_changed → PFE 리빌드
       ↓
OceanSimulator (v0.7.1)      바다 내 다중 tracer (대류/유속/와도)
       ↓
BrainAnalyzer (v0.5.0)       Layer 1+5+6 통합 분석 → 피드백
```

---

## 빠른 시작

```python
from cookiie_brain_engine import CookiieBrainEngine
from brain_core.global_state import GlobalState
import numpy as np

brain = CookiieBrainEngine(
    enable_well_formation=True,
    enable_potential_field=True,
    potential_field_config={
        "enable_phase_a": True,       # 자전 활성화
        "phase_a_mode": "minimal",    # 코리올리형 R(v)=ωJv
        "phase_a_omega": 1.0,         # 회전 각속도
    },
)

state = GlobalState(
    state_vector=np.array([1.0, 0.0, 0.0, 0.5]),  # [x, v]
    energy=0.0,
)
state.set_extension("episodes", episodes)

for _ in range(1000):
    state = brain.update(state)
```

사용 예제: [examples/](examples/)

---

## Phase A — 자전

골짜기 바닥에 도달한 공이 그냥 멈추면, 상태는 고정점이 됩니다.
자전을 넣으면 공이 골짜기 안에서 계속 돌게 되어, **위상(타이밍)** 이 생깁니다.

핵심 아이디어: 힘을 속도에 수직으로 걸면, 방향만 바뀌고 에너지는 변하지 않습니다.
(자석 위의 전자가 원을 그리는 것과 같은 원리 — 코리올리 힘)

```
R(x, v) = ωJv                   # 힘이 항상 속도에 수직
v · R = v · (ωJv) = 0           # → 에너지 보존 (수학적 보장)
```

**적분**: Strang splitting (Boris 방식)
- 회전을 수치적으로 "정확히" 적용 (`exp(ωJdt)`) → 속력 `|v|` 완벽 보존
- 장기 시뮬레이션에서도 에너지 drift 없음 (검증: < 0.01%)

검증 실행:
```bash
python examples/phase_a_minimal_verification.py
```

수학적 기초 · 단계 로드맵: [trunk/Phase_A/](trunk/Phase_A/)

---

## Phase C — 요동

결정론적 시스템에서는 같은 초기 조건이면 항상 같은 결과입니다.
요동을 넣으면 공이 **확률적으로** 장벽을 넘을 수 있습니다.
감쇠로 갇힌 기억에서 우연히 다른 기억으로 전이하는 것 — 이것이 창의적 연상의 물리적 모델입니다.

```
m ẍ = -∇V(x) + ωJv - γv + I(x,v,t) + σξ(t)

σ : 노이즈 세기
ξ : 백색 노이즈 (매 순간 랜덤 방향)
```

**요동-소산 정리 (FDT):** σ를 직접 설정하는 대신, 온도 T를 설정하면 물리 법칙이 σ를 결정한다:
```
σ² = 2γT/m    (kB = 1)
정상 분포: P(x,v) ∝ exp(-E/T)
```

**적분**: Strang splitting + O-U exact 반스텝 (감쇠+노이즈 정확 결합)
- σ=0이면 기존 결정론적 동작과 100% 동일

검증 실행:
```bash
python examples/fluctuation_verification.py   # 요동 기본 (4항목)
python examples/fdt_verification.py            # FDT 등분배 (5항목)
```

---

## Layer 1 — 통계역학 정식화

Phase C(요동/FDT)로 줄기(trunk)가 완성되었습니다.
그 위에 첫 번째 토양인 Layer 1을 쌓습니다.

시뮬레이션 궤적을 확률·열역학 언어로 번역합니다:

- **Kramers 탈출률**: 우물 사이 전이가 얼마나 자주 일어나는가
- **전이 행렬**: 전이 패턴에 방향성이 있는가 (순환 흐름, 상세 균형)
- **엔트로피 생산률**: 시스템이 에너지를 얼마나 비가역적으로 소산하는가

```python
from analysis.Layer_1 import kramers_rate, TransitionAnalyzer, entropy_production_rate
```

검증 실행:
```bash
python examples/layer1_verification.py   # 5항목 ALL PASS
```

상세: [analysis/Layer_1/README.md](analysis/Layer_1/README.md) · [analysis/Layer_1/README_EN.md](analysis/Layer_1/README_EN.md)

## Layer 2 — 다체/장론

Layer 1 위에 N-body 다체 동역학을 쌓습니다.
단일 입자에서 "장(field)"은 의미가 없습니다. 입자가 여러 개여야 비로소 장이 됩니다.

- **InteractionForce**: 쌍체 상호작용 (중력, 스프링, 쿨롱 등)
- **ExternalForce**: 입자별 외부 퍼텐셜
- **NBodyGauge**: 입자별 코리올리 회전
- **Newton 제3법칙**: F_ij = -F_ji 구조적 보장 → 운동량 보존

```python
from analysis.Layer_2 import InteractionForce, NBodyState, spring_interaction
```

검증 실행:
```bash
python examples/layer2_verification.py   # 5항목 ALL PASS
```

상세: [analysis/Layer_2/README.md](analysis/Layer_2/README.md)

## Layer 3 — 게이지/기하학

Layer 2 위에 위치 의존 게이지(자기장형 힘)와 기하학적 분석을 쌓습니다.
trunk의 전역 Coriolis 회전 ω가, 공간의 각 위치마다 다른 회전 B(x)로 확장됩니다.

- **MagneticForce**: F = B(x)·J·v — 속도에 수직 (F·v = 0, 에너지 보존 구조적 보장)
- **NBodyMagneticForce**: N 입자 각각에 위치 의존 B(x) 적용
- **GeometryAnalyzer**: 자기 선속, 선속 기반 위상 축적(Abelian), E×B drift, 국소 곡률
- **극한 일관성**: B(x) = const → CoriolisGauge, B(x) = 0 → 자유 입자

```python
from analysis.Layer_3 import MagneticForce, GeometryAnalyzer
```

검증 실행:
```bash
python examples/layer3_verification.py   # 5항목 ALL PASS
```

상세: [analysis/Layer_3/README.md](analysis/Layer_3/README.md)

## Layer 4 — 비평형 일 정리

Layer 1(평형 열역학) 위에 임의의 비평형 과정을 위한 정확한 등식을 쌓습니다.
시간 의존 프로토콜 λ(t)로 퍼텐셜을 변화시키고, 일(W) 측정에서 자유 에너지를 추출합니다.

- **Jarzynski 등식**: `⟨e^{-W/T}⟩ = e^{-ΔF/T}` — 정확한 등식 (근사 아님)
- **제2법칙**: `⟨W⟩ ≥ ΔF` — Jensen 부등식
- **Crooks 정리**: 정방향/역방향 일 분포의 대칭 관계

```python
from analysis.Layer_4 import JarzynskiEstimator, moving_trap, stiffness_change
```

검증 실행:
```bash
python examples/layer4_verification.py   # 5항목 ALL PASS
```

상세: [analysis/Layer_4/README.md](analysis/Layer_4/README.md)

## Layer 5 — 확률역학

궤적(Langevin) 관점에서 확률 밀도(Fokker-Planck) 관점으로 전환합니다.
Nelson 확률역학의 forward/backward 속도 분해를 포함합니다.

- **Fokker-Planck**: `∂ρ/∂t = ∇·(∇V·ρ/(mγ)) + D∇²ρ`, 정상 분포 `ρ_eq ∝ exp(−V/T)`
- **Nelson 분해**: `v = v_current + v_osmotic`, 평형에서 `v_+ = 0`
- **확률류**: `J = bρ − D∇ρ`, 평형에서 `J = 0` (detailed balance)

```python
from analysis.Layer_5 import FokkerPlanckSolver1D, NelsonDecomposition
```

검증 실행:
```bash
python examples/layer5_verification.py   # 5항목 ALL PASS
```

상세: [analysis/Layer_5/README.md](analysis/Layer_5/README.md)

## Layer 6 — 정보 기하학

매개변수 공간의 기하학적 구조를 Fisher 정보 계량으로 분석합니다.
Layer 3(물리 공간 게이지)의 매개변수 공간 확장입니다.

- **Fisher 계량**: `g_μν = (1/T²) Cov(∂_μV, ∂_νV)` — 매개변수 변화에 대한 분포 민감도
- **가우스 곡률**: K — 비자명한 내재적 곡률 (구면/쌍곡면/평탄)
- **측지선 거리**: 분포 변화의 통계적 비용 (항상 ≥ 유클리드)

1D 고전계에서 naive Berry phase = 0 (A = ∇f → curl = 0)이지만,
Fisher 계량의 곡률은 비자명하다 — 이것이 양자 Fubini-Study 계량의 고전 극한이다.

```python
from analysis.Layer_6 import FisherMetricCalculator, ParameterSpace
```

검증 실행:
```bash
python examples/layer6_verification.py   # 5항목 ALL PASS
```

상세: [analysis/Layer_6/README.md](analysis/Layer_6/README.md)

---

## HippoMemoryEngine — 태양 (v0.6.0)

Layer 1~6까지 분석 도구는 완성되었지만, **기억을 누가 만드는가?** 가 비어 있었습니다.
우물을 수동으로 배치하는 것은 태양 없는 태양계 — 행성은 있는데 궤도를 유지시키는 에너지원이 없는 상태입니다.

HippoMemoryEngine은 **인지과학의 해마(Hippocampus) = 솔라시스템의 태양** 역할을 합니다.
지형이 스스로 변하는 살아있는 시스템으로의 전환입니다.

### 핵심 변화: V(x) → V(x,t)

| 이전 (v0.5.0) | 이후 (v0.6.0) |
|---------------|---------------|
| 우물을 수동 배치하면 영원히 고정 | 우물이 스스로 생성·강화·감쇠·소멸 |
| I(x,v,t) = 외부에서 수동 설정 | I(x,v,t) = 탐색/정착/리콜 자동 합성 |
| V(x) 정적 지형 | V(x,t) 동적 지형 (PFE 자동 리빌드) |

### 세 관점 대응

| 솔라시스템 | 인지과학 | hippo 코드 |
|-----------|---------|------------|
| 태양 | 해마 | `HippoMemoryEngine` |
| 행성 탄생 | 기억 형성 | `MemoryStore.encode()` |
| 핵반응 | 장기강화 LTP | `A += η · proximity · dt` |
| 행성 소멸 | 기억 망각 | `A *= exp(-λ·dt)` → `A < A_min` → 삭제 |
| 태양풍 | 주의 분산 | `EnergyBudgeter._explore()` |
| 중력 포획 | 주의 집중 | `EnergyBudgeter._exploit()` |
| 궤도 재진입 | 기억 인출 | `EnergyBudgeter._recall()` |

### 통합 흐름

```
외부 입력 (자극/경험)
    ↓
┌── HippoMemoryEngine ──────────────────────┐
│  MemoryStore           EnergyBudgeter      │
│   encode() → 우물 생성    _explore() → 탐색  │
│   step()   → 강화/감쇠    _exploit() → 정착  │
│   prune()  → 소멸         _recall()  → 리콜  │
│                ↓                            │
│           I(x,v,t) + pot_changed            │
└────────────────┬───────────────────────────┘
                 ↓
         CookiieBrainEngine
    (pot_changed → PFE 리빌드)
                 ↓
         궤적 (x, v, t) 생성
                 ↓
         BrainAnalyzer
    (Layer 1+5+6 분석 → 피드백)
```

### 사용

```python
from cookiie_brain_engine import CookiieBrainEngine

brain = CookiieBrainEngine(
    enable_well_formation=True,
    enable_potential_field=True,
    enable_hippo_memory=True,   # 태양 활성화
)

# 기억 인코딩
brain.hippo_memory_engine.encode(np.array([3.0]))
brain.hippo_memory_engine.encode(np.array([-2.0]))

# 시뮬레이션 → 우물이 자동으로 강화/감쇠/소멸
for _ in range(1000):
    state = brain.update(state)

# 리콜 (특정 기억을 향해 끌어당김)
brain.hippo_memory_engine.recall(np.array([2.8]))
```

검증 실행:
```bash
python examples/hippo_memory_verification.py        # 7항목 ALL PASS
python examples/integrated_pipeline_verification.py  # 7항목 ALL PASS
```

상세: [hippo/README.md](hippo/README.md) · 개념 문서: [docs/HIPPO_MEMORY_CONCEPT.md](docs/HIPPO_MEMORY_CONCEPT.md)

---

## 3계층 중력 동역학 (v0.7.0~v0.7.1)

HippoMemoryEngine(태양)이 우물을 만들었지만, 감쇠 때문에 상태점이 우물 바닥에 **가라앉았습니다.**
태양계에서 행성이 태양에 떨어지지 않는 이유: **1/r 중력 + 각운동량 보존 + 조석 리듬.**

### 3계층 구조

| Tier | 비유 | 수식 | 역할 |
|------|------|------|------|
| Tier 1 | 태양 | V = -GM/(r+ε) | 장거리 구속 (1/r, 느리게 감소) |
| Tier 2 | 지구/바다 | V = -A exp(-\|\|x-c\|\|²/2σ²) | 국소 끌림 (기존 우물) |
| Tier 3 | 달 | V = -G_m M_m/(\|\|x-x_moon(t)\|\|+ε) | 주기적 교란 (조석 흐름) |

### v0.7.1 달의 물리

- **타원 공전**: Kepler 방정식으로 이심률 있는 궤도
- **자전**: 달의 자체 회전 (또는 tidal locking)
- **사중극**: 비구형 질량 분포 효과
- **조석 텐서**: T_ij = ∂²V/∂x_i∂x_j — 조석력의 공간 구조

### OceanSimulator — 바다 시뮬레이션

우물 안에 다중 tracer 입자를 놓고 모든 힘(우물+조석+코리올리+감쇠+노이즈)을 합성하여
**대류, 난류, 유속 패턴**을 관찰합니다.

```python
from trunk.Phase_A.tidal import CentralBody, OrbitalMoon, TidalField, OceanSimulator

sun = CentralBody(position=np.array([0.0, 0.0]), mass=10.0)
moon = OrbitalMoon(host_center=np.array([5.0, 0.0]),
                   orbit_radius=1.5, orbit_frequency=2.0,
                   mass=0.3, eccentricity=0.2)
tidal = TidalField(central=sun, moons=[moon])

ocean = OceanSimulator(well_center=np.array([5.0, 0.0]),
                       well_amplitude=3.0, well_sigma=1.0,
                       tidal_field=tidal, n_tracers=20)
result = ocean.simulate(total_time=50.0, dt=0.01)
```

검증 실행:
```bash
python examples/tidal_orbit_verification.py   # 17항목 ALL PASS
```

상세: [docs/TIDAL_DYNAMICS_CONCEPT.md](docs/TIDAL_DYNAMICS_CONCEPT.md)

---

## 3D 진화 엔진 — solar/ (v1.3.0)

**점 객체 탄생 → 전체 태양계 N-body + 자기권 방어막 → 빛이 있으라.**

하나의 점에서 시작해, 중력 방정식만으로 자전·공전·세차·조석·해류가 자연 발생.
그 위에 자기쌍극자·태양풍·자기권·태양 광도 전자기 레이어와 인지 관성 기억(Ring Attractor)을
기어 분리 구조로 적층. 빛이 켜지고 형태와 온도가 존재하기 시작한다.

### 주요 검증 결과

| 항목 | 결과 | 버전 |
|------|------|------|
| 10-body 태양계 100년 안정 | 전 행성 궤도 편차 < 1% | v1.0.0 |
| 세차 주기 | 24,763yr (NASA 25,772yr, **3.9% 오차**) | v1.0.0 |
| 에너지 보존 | dE/E = 3.20×10⁻¹⁰ | v1.0.0 |
| 자기쌍극자 1/r³ 감쇠 | 오차 0.00% | v1.1.0 |
| 태양풍 1/r² 감쇠 | 5행성 오차 0.00% | v1.2.0 |
| 마그네토포즈 | 7.58 R_E (실측 ~10 R_E) | v1.2.0 |
| 차폐율 | 0.78 | v1.2.0 |
| 태양 광도 L = M^4.0 | 1.0000 L☉ (오차 0.00) | v1.3.0 |
| 지구 평형 온도 | 254 K (NASA 255 K, **0.4%**) | v1.3.0 |
| 복사 역제곱 법칙 | 8행성 0.000% | v1.3.0 |
| Ring Attractor 위상 추적 | 평균 0.12° 오차 | v0.9.0 |

### 기어 분리 구조 (레이어 아키텍처)

```
인지 층 — RingAttractorEngine (관성 기억, φ ∈ S¹)
    │ spin_axis → Ring 위상 매핑 (관측자 모드)
전자기 층 — em/ (광도 + 자기쌍극자 + 태양풍 + 자기권)
    │ L = M^α → F ∝ 1/r² → T_eq (빛이 있으라)
    │ spin_axis, pos 읽기 (관측자 모드, 물리 수정 없음)
물리 층 — EvolutionEngine (10-body 중력 + 스핀-궤도 토크)
    │ build_solar_system()
데이터 층 — data/ (NASA/JPL 실측 상수, frozen)
```

의존 규칙: `data/ → core/ ← em/`, `core/ ← cognitive/`, 상호 참조 금지.

### 사용

```python
from solar import EvolutionEngine, Body3D, build_solar_system

engine = EvolutionEngine()
for d in build_solar_system():
    if "_moon_config" in d:
        cfg = d["_moon_config"]
        engine.giant_impact(cfg["target"], **{k: v for k, v in cfg.items() if k != "target"})
    else:
        engine.add_body(Body3D(**d))

for _ in range(500_000):
    engine.step(0.0002, ocean=False)
```

### 검증

```bash
python examples/let_there_be_light_demo.py   # 빛이 있으라 — 태양 광도 (~2초)
python examples/full_solar_system_demo.py    # 10-body 100년 (~8분)
python examples/planet_evolution_demo.py     # 3체 세차 (~13초)
python examples/em_layer_demo.py             # EM 전자기 통합
python examples/spin_ring_coupling_demo.py   # Ring Attractor 커플링
```

검증 로그:
- [LET_THERE_BE_LIGHT_LOG.txt](docs/LET_THERE_BE_LIGHT_LOG.txt) — 빛이 있으라 ALL PASS
- [FULL_SOLAR_SYSTEM_LOG.txt](docs/FULL_SOLAR_SYSTEM_LOG.txt) — 10-body 100년
- [EM_LAYER_LOG.txt](docs/EM_LAYER_LOG.txt) — 전자기 레이어 ALL PASS
- [PRECESSION_VERIFICATION_LOG.txt](docs/PRECESSION_VERIFICATION_LOG.txt) — 3체 세차

상세: [solar/README.md](solar/README.md) · [docs/COGNITIVE_SOLAR_SYSTEM.md](docs/COGNITIVE_SOLAR_SYSTEM.md)

---

## BrainAnalyzer — 통합 분석 (v0.5.0)

trunk 궤적을 Layer 1 + 5 + 6에 자동으로 통과시켜 한 장의 리포트를 생성합니다.

```python
from analysis.brain_analyzer import BrainAnalyzer

analyzer = BrainAnalyzer(wells, temperature=1.0, gamma=0.1, mass=1.0)
report = analyzer.full_report(trajectory_x, trajectory_v, dt=0.01)
# report["layer1"]: 전이 확률, 엔트로피 생산률
# report["layer5"]: 확률 밀도, Nelson 분해
# report["layer6"]: Fisher 계량, 곡률
```

CookiieBrainEngine의 `run_and_analyze()`로 시뮬레이션 + 분석을 한번에 실행할 수 있습니다.

---

## 설계 원칙

- **state 불변**: `new_state = state.copy()` 후 반환. 원본 안 건드림
- **하드코딩 금지**: 물리 상수, 경로 전부 파라미터화
- **엔진은 상태를 perturb할 뿐, 지배하지 않음**
- **GlobalState 하나로 모든 엔진 연결**: extensions 규약으로 데이터 교환

상세: [docs/](docs/)
전체 개념 · 현재 상태 (한국어): [docs/FULL_CONCEPT_AND_STATUS.md](docs/FULL_CONCEPT_AND_STATUS.md)
Full concept (English): [docs/FULL_CONCEPT_AND_STATUS_EN.md](docs/FULL_CONCEPT_AND_STATUS_EN.md)

---

## Extensions 규약

```python
# WellFormation
state.get_extension("well_formation")  # {"W": ..., "b": ..., "well_result": ...}

# PotentialField
state.get_extension("potential_field")  # {"potential", "field", "kinetic_energy",
                                        #  "potential_energy", "total_energy"}

# Cerebellum
state.get_extension("cerebellum")      # {"correction", "target_state"}

# HippoMemory (v0.6.0)
state.get_extension("hippo_memory")    # {"injection", "pot_changed",
                                        #  "store_info", "budgeter_info"}
```

---

## 표준 API

```python
engine.update(state) -> GlobalState    # 필수
engine.get_energy(state) -> float      # 선택
engine.get_state() -> dict             # 선택
engine.reset()                         # 선택
```

---

## 파일 구조

```
CookiieBrain/
├── cookiie_brain_engine.py     # 통합 오케스트레이션 엔진 (v0.7.2)
├── README.md
├── ARCHITECTURE.md             # 5-Layer 아키텍처 명세
├── QUICK_START.md
│
├── solar/                      # ── L2 Field: 중력장 + 3D 진화 (v1.3.0) ──
│   ├── core/                   #   물리 코어 (N-body+토크+해양)
│   │   ├── evolution_engine.py #   ★ EvolutionEngine
│   │   ├── central_body.py     #   CentralBody (태양: 1/r)
│   │   ├── orbital_moon.py     #   OrbitalMoon (달: 타원공전+조석)
│   │   └── tidal_field.py      #   TidalField (합성기)
│   ├── data/                   #   NASA/JPL 실측 상수 (frozen)
│   │   └── solar_system_data.py#   8행성+태양+달 + build_solar_system()
│   ├── em/                     #   전자기 레이어 (관측자 모드)
│   │   ├── solar_luminosity.py #   ★ 빛이 있으라 L = M^α, F ∝ 1/r²
│   │   ├── magnetic_dipole.py  #   자기쌍극자 B ∝ 1/r³
│   │   ├── solar_wind.py       #   태양풍 P ∝ 1/r²
│   │   ├── magnetosphere.py    #   자기권 (dipole vs P_sw 균형)
│   │   └── _constants.py       #   EPS 중앙 관리
│   ├── cognitive/              #   인지 레이어 (관측자 모드)
│   │   ├── ring_attractor.py   #   관성 기억 (Mexican-hat bump)
│   │   └── spin_ring_coupling.py#  물리↔인지 필드 연결
│   └── README.md               #   ★ 상세 문서 (물리 개념 + 검증)
│
├── trunk/                      # ── L1 Dynamics: 운동방정식 구성요소 ──
│   ├── Phase_A/                #   자전 (코리올리 회전)
│   ├── Phase_B/                #   공전 (가우시안 다중 우물)
│   └── Phase_C/                #   요동 (Langevin noise, FDT)
│
├── hippo/                      # ── L3 Memory: 장기기억 (v0.6.0) ──
│   ├── memory_store.py         #   우물 생애주기 (생성·강화·감쇠·소멸)
│   ├── energy_budgeter.py      #   I(x,v,t) 자동 제어 (탐색/정착/리콜)
│   └── hippo_memory_engine.py  #   통합 엔진 + HippoConfig
│
├── analysis/                   # ── L4 Analysis: 분석 도구 ──
│   ├── Layer_1~6/              #   통계역학 ~ 정보 기하학
│   ├── brain_analyzer.py       #   Layer 1+5+6 통합 분석
│   └── ocean_simulator.py      #   바다 시뮬레이터
│
├── examples/                   # 실행 가능한 검증 스크립트 (32개)
│   ├── let_there_be_light_demo.py  # ★ 빛이 있으라 — 태양 광도 (v1.3.0)
│   ├── full_solar_system_demo.py   # ★ 10-body 100년 N-body (v1.0.0)
│   ├── em_layer_demo.py            # ★ 전자기 통합 검증 (v1.2.0)
│   ├── magnetic_dipole_demo.py     # 자기쌍극자 단독 검증 (v1.1.0)
│   ├── spin_ring_coupling_demo.py  # Ring Attractor 커플링 (v0.9.0)
│   ├── planet_evolution_demo.py    # 탄생→세차운동 6Phase (v0.8.0)
│   ├── real_solar_system_verification.py  # 실제 태양계 비율 20/20
│   ├── lagrange_point_verification.py     # 라그랑주 L1~L5 20/20
│   ├── layer1~6_verification.py    # Layer 1~6 각 5항목
│   └── ...                    # hippo, tidal, fdt, phase_a/b 등
│
├── blockchain/                 # PHAM 블록체인 서명 (53개 체인)
│
└── docs/
    ├── COGNITIVE_SOLAR_SYSTEM.md    # ★ 인지 태양계 설계
    ├── VERSION_LOG.md              # ★ solar/ 버전 히스토리 (v0.8.0~v1.3.0)
    ├── LET_THERE_BE_LIGHT_LOG.txt  # 빛이 있으라 ALL PASS 출력
    ├── FULL_SOLAR_SYSTEM_LOG.txt   # 10-body 100년 검증 출력
    ├── EM_LAYER_LOG.txt            # 전자기 레이어 ALL PASS 출력
    ├── MAGNETIC_DIPOLE_LOG.txt     # 자기쌍극자 검증 출력
    ├── PRECESSION_VERIFICATION_LOG.txt  # 3체 세차 검증 출력
    ├── SPIN_RING_COUPLING_LOG.txt  # Ring Attractor 커플링 출력
    ├── FULL_CONCEPT_AND_STATUS.md  # 전체 개념 (한국어)
    ├── FULL_CONCEPT_AND_STATUS_EN.md  # Full concept (English)
    ├── HIPPO_MEMORY_CONCEPT.md     # HippoMemory 설계
    ├── TIDAL_DYNAMICS_CONCEPT.md   # 3계층 중력 설계
    └── WORK_LOG.md                 # 시간순 작업 기록
```

---

## PHAM 블록체인 서명

이 프로젝트의 코드 기여는 PHAM v4 블록체인으로 무결성을 기록합니다.

- **4-Signal 스코어링**: Byte(25%) + Text(35%) + AST(30%) + Exec(10%)
- **체인 구조**: `SHA256(index | prev_hash | timestamp | data_hash)`
- **라이선스**: 누구나 자유롭게 사용. 수익 발생 시 6% 후원 (신뢰 기반)

서명 도구: [pham_sign_v4.py](https://github.com/qquartsco-svg/PotentialField_Engine/blob/main/blockchain/pham_sign_v4.py)
라이선스 전문: PHAM-OPEN v2.0

---

## 현재 상태와 방향

| 단계 | 상태 | 버전 |
|------|------|------|
| 정적 퍼텐셜 (우물 생성 + 수렴) | 완료 | v0.1.0 |
| 자전 (코리올리 회전, 에너지 보존) | 완료 | v0.2.0 |
| 공전 (다중 우물 순환 궤도) | 완료 | v0.2.0 |
| WellFormation → Gaussian 브릿지 | 완료 | v0.2.0 |
| 에너지 주입/소산 (-γv + I) | 완료 | v0.3.0 |
| 요동 + FDT (σ²=2γT/m) | 완료 | v0.3.0 |
| Layer 1~3 (통계역학, 다체, 게이지) | 완료 | v0.3.0 |
| Layer 4~6 (비평형, 확률역학, 정보기하) | 완료 | v0.4.0 |
| BrainAnalyzer (Layer 1+5+6 통합) | 완료 | v0.5.0 |
| HippoMemoryEngine (태양/운영층) | 완료 | v0.6.0 |
| 3계층 중력 (태양+달+조석) | 완료 | v0.7.0 |
| 달 타원공전+자전+조석텐서+OceanSimulator | 완료 | v0.7.1 |
| hippo 힘 합성 + 달 동적 추적 + 아키텍처 정리 | 완료 | v0.7.2 |
| **3D EvolutionEngine — 점 객체→세차운동** | **완료** | **v0.8.0** |
| Ring Attractor 관성 기억 결합 | 완료 | v0.9.0 |
| **전체 태양계 10-body N-body + 기어 분리** | **완료** | **v1.0.0** |
| 자기쌍극자장 (B ∝ 1/r³, 세차 연동) | 완료 | v1.1.0 |
| **태양풍 + 자기권 (전자기 레이어 완비)** | **완료** | **v1.2.0** |
| EM 개념 문서화 + EPS 중앙 관리 | 완료 | v1.2.2 |
| **빛이 있으라 — 태양 광도·조도·온도** | **완료** | **v1.3.0** |

```
v0.1  정적 퍼텐셜
v0.2  자전 + 공전 + 브릿지
v0.3  에너지 + 요동 + FDT + Layer 1~3
v0.4  폴더 정리 + Layer 4~6
v0.5  BrainAnalyzer (통합 분석)
v0.6  HippoMemoryEngine (태양 = V(x)→V(x,t))
v0.7  3계층 중력 (태양·지구·달 = 장·끌림·리듬)
v0.8  3D EvolutionEngine — 세차운동 실증 (4.6% 오차)
v0.9  Ring Attractor — 관성 기억 (인지 기어 결합)
v1.0  ★ 전체 태양계 10-body — NASA 실측 데이터 (3.9% 오차)
v1.1  자기쌍극자장 — B ∝ 1/r³, 세차 연동
v1.2  ★ 태양풍 + 자기권 — 전자기 레이어 완비 (ALL PASS)
v1.3  ★ 빛이 있으라 — 태양 광도 L = M^α, 지구 254 K (ALL PASS)
```

> **점 하나에서 시작해, 중력 방정식만으로 자전·공전·세차·조석·해류가 자연 발생한다.**
> 그 위에 자기쌍극자·태양풍·자기권·태양 광도를 기어 분리 구조로 얹었다.
> 빛이 켜지고, 형태와 온도가 존재하기 시작한다.
> 10-body 태양계가 실제 우주와 3.9% 오차로 일치한다.

---

*GNJz (Qquarts) · Cookiie Brain v1.3.0*
*"Code is Free. Success is Shared."*
