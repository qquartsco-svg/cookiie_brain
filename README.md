# Cookiie Brain

**상태 동역학 기반 뇌 모델링 통합 엔진**

```
Version : 0.3.0
License : PHAM-OPEN v2.0
Python  : 3.8+
Author  : GNJz (Qquarts)
```

---

## 이 프로젝트가 하는 일

공이 산과 골짜기가 있는 지형 위에서 굴러가는 장면을 떠올려 보세요.

- **골짜기(우물)** = 기억. 경험이 쌓이면 지형에 골짜기가 파인다.
  깊은 골짜기일수록 강한 기억. 공은 가까운 골짜기로 자연스럽게 끌려간다.
- **공의 움직임** = 상태. 공은 골짜기로 끌려가면서 기억을 떠올린다.
  여러 골짜기 사이에서 공이 어디로 향하느냐가 곧 "지금 무엇을 떠올리는가"이다.
- **자전** = 리듬. 공이 골짜기 바닥에 멈추지 않고 회전하면, 위상(타이밍)이 생긴다.
  수면 중에도 뇌는 멈추지 않는다. 리듬이 있어야 다음 상태로 넘어갈 수 있다.

이 엔진은 이 과정을 물리 수식으로 구현합니다.
정답을 주는 시스템이 아니라, 각자의 해답을 찾아갈 수 있는 **구조**를 만드는 것이 목적입니다.

**기술적으로는:**
Hopfield 에너지 지형 위에서 상태 벡터의 동역학을 시뮬레이션합니다.
경험(episodes)으로부터 에너지 우물(W, b)을 형성하고,
상태가 퍼텐셜 필드 위에서 수렴·회전·전이하는 과정을
수치 적분(symplectic Euler, Strang splitting)으로 추적합니다.
Phase A에서는 코리올리형 회전항(ωJv)을 도입하여,
에너지를 보존하면서 위상 구조(limit cycle)를 생성하는 것까지 구현되어 있습니다.

---

## What This Project Does

Imagine a ball rolling across a landscape of hills and valleys.

- **Valleys (wells)** = memories. As experiences accumulate, valleys form in the terrain.
  Deeper valleys represent stronger memories. The ball naturally rolls toward the nearest one.
- **The ball's motion** = state. As the ball is pulled into a valley, it "recalls" that memory.
  Which valley the ball moves toward is essentially "what is being recalled right now."
- **Spin** = rhythm. If the ball doesn't just stop at the bottom but keeps rotating, phase (timing) emerges.
  The brain never truly stops — even in sleep. Rhythm is what enables transitions between states.

This engine implements these dynamics with physics equations.
It is not a system that gives answers, but a **structure** that lets each user find their own.

**Technically:**
State-vector dynamics on a multi-well energy landscape.
The full equation of motion is a Langevin equation with Coriolis rotation:

```
m ẍ = -∇V(x) + ωJv - γv + I(x,v,t) + σξ(t)
```

- **Phase A (Spin):** Coriolis term ωJv — energy-conserving rotation
- **Phase B (Orbit):** Gaussian multi-well potential — circulation between memories
- **Phase C (Fluctuation):** Langevin noise σξ(t) — stochastic transitions
- **FDT:** σ² = 2γT/m — temperature-based noise, Boltzmann steady state guaranteed

Full concept (English): [docs/FULL_CONCEPT_AND_STATUS_EN.md](docs/FULL_CONCEPT_AND_STATUS_EN.md)

---

## 핵심 수식

```
골짜기의 깊이 (퍼텐셜):   V(x) = -(1/2)x'Wx - b'x   (지역 최솟값 최대 1개)
공을 끌어당기는 힘:        g(x) = -∇V(x)
전체 운동 방정식:          m ẍ = -∇V(x) + ωJv - γv + I(x,v,t) + σξ(t)
총 에너지:                 E = (1/2)||v||² + V(x)
```

수학적 기초 · 구현 상세: [PotentialFieldEngine CONCEPT](https://github.com/qquartsco-svg/PotentialField_Engine/blob/main/docs/CONCEPT.md)

---

## 엔진 파이프라인

```
WellFormationEngine           episodes → W, b (Hopfield 가중치)
       ↓
PotentialFieldEngine          V(x), g(x) → 상태 업데이트 (적분)
       │  ├ 기본: symplectic Euler
       │  └ 자전 모드 (Phase_A): Strang splitting + exact rotation
       │                         omega_coriolis → ωJv 내부 처리
       ↓
CerebellumEngine (선택)       운동 보정
       ↓
HippoMemoryEngine (예정)      장기 기억
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

수학적 기초 · 단계 로드맵: [Phase_A/](Phase_A/)

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
from Layer_1 import kramers_rate, TransitionAnalyzer, entropy_production_rate
```

검증 실행:
```bash
python examples/layer1_verification.py   # 5항목 ALL PASS
```

상세: [Layer_1/README.md](Layer_1/README.md) · [Layer_1/README_EN.md](Layer_1/README_EN.md)

## Layer 2 — 다체/장론

Layer 1 위에 N-body 다체 동역학을 쌓습니다.
단일 입자에서 "장(field)"은 의미가 없습니다. 입자가 여러 개여야 비로소 장이 됩니다.

- **InteractionForce**: 쌍체 상호작용 (중력, 스프링, 쿨롱 등)
- **ExternalForce**: 입자별 외부 퍼텐셜
- **NBodyGauge**: 입자별 코리올리 회전
- **Newton 제3법칙**: F_ij = -F_ji 구조적 보장 → 운동량 보존

```python
from Layer_2 import InteractionForce, NBodyState, spring_interaction
```

검증 실행:
```bash
python examples/layer2_verification.py   # 5항목 ALL PASS
```

상세: [Layer_2/README.md](Layer_2/README.md)

## Layer 3 — 게이지/기하학

Layer 2 위에 위치 의존 게이지(자기장형 힘)와 기하학적 분석을 쌓습니다.
trunk의 전역 Coriolis 회전 ω가, 공간의 각 위치마다 다른 회전 B(x)로 확장됩니다.

- **MagneticForce**: F = B(x)·J·v — 속도에 수직 (F·v = 0, 에너지 보존 구조적 보장)
- **NBodyMagneticForce**: N 입자 각각에 위치 의존 B(x) 적용
- **GeometryAnalyzer**: 자기 선속, 선속 기반 위상 축적(Abelian), E×B drift, 국소 곡률
- **극한 일관성**: B(x) = const → CoriolisGauge, B(x) = 0 → 자유 입자

```python
from Layer_3 import MagneticForce, GeometryAnalyzer
```

검증 실행:
```bash
python examples/layer3_verification.py   # 5항목 ALL PASS
```

상세: [Layer_3/README.md](Layer_3/README.md)

## Layer 4 — 비평형 일 정리

Layer 1(평형 열역학) 위에 임의의 비평형 과정을 위한 정확한 등식을 쌓습니다.
시간 의존 프로토콜 λ(t)로 퍼텐셜을 변화시키고, 일(W) 측정에서 자유 에너지를 추출합니다.

- **Jarzynski 등식**: `⟨e^{-W/T}⟩ = e^{-ΔF/T}` — 정확한 등식 (근사 아님)
- **제2법칙**: `⟨W⟩ ≥ ΔF` — Jensen 부등식
- **Crooks 정리**: 정방향/역방향 일 분포의 대칭 관계

```python
from Layer_4 import JarzynskiEstimator, moving_trap, stiffness_change
```

검증 실행:
```bash
python examples/layer4_verification.py   # 5항목 ALL PASS
```

상세: [Layer_4/README.md](Layer_4/README.md)

## Layer 5 — 확률역학

궤적(Langevin) 관점에서 확률 밀도(Fokker-Planck) 관점으로 전환합니다.
Nelson 확률역학의 forward/backward 속도 분해를 포함합니다.

- **Fokker-Planck**: `∂ρ/∂t = ∇·(∇V·ρ/(mγ)) + D∇²ρ`, 정상 분포 `ρ_eq ∝ exp(−V/T)`
- **Nelson 분해**: `v = v_current + v_osmotic`, 평형에서 `v_+ = 0`
- **확률류**: `J = bρ − D∇ρ`, 평형에서 `J = 0` (detailed balance)

```python
from Layer_5 import FokkerPlanckSolver1D, NelsonDecomposition
```

검증 실행:
```bash
python examples/layer5_verification.py   # 5항목 ALL PASS
```

상세: [Layer_5/README.md](Layer_5/README.md)

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
├── cookiie_brain_engine.py     # 통합 엔진 (오케스트레이션)
├── README.md
├── QUICK_START.md
├── Phase_A/                    # 자전 모듈 (완료)
│   ├── rotational_field.py     #   코리올리형 + pole형 회전 생성
│   ├── moon.py                 #   위성 중력장
│   └── docs/                   #   작업 기록 · 수학 문서
├── Phase_B/                    # 공전 모듈 (다중 우물 순환)
│   ├── multi_well_potential.py #   가우시안 다중 우물 퍼텐셜
│   └── README.md               #   개념 · 수식 · 사용법
├── Phase_C/                    # 요동 (Langevin noise)
│   ├── README.md               #   개념 · 구현 위치 · 사용법 (한국어)
│   └── README_EN.md            #   Phase C concept (English)
├── Layer_1/                    # 통계역학 정식화
│   ├── statistical_mechanics.py #  Kramers rate, TransitionAnalyzer, entropy
│   ├── README.md               #   Layer 1 개념 (한국어)
│   └── README_EN.md            #   Layer 1 concept (English)
├── Layer_2/                    # 다체/장론
│   ├── nbody.py               #   NBodyState, InteractionForce, ExternalForce
│   └── README.md              #   Layer 2 개념 (한국어)
├── Layer_3/                    # 게이지/기하학
│   ├── gauge.py               #   GaugeForce, GeometryAnalyzer
│   └── README.md              #   Layer 3 개념 (한국어)
├── Layer_4/                    # 비평형 일 정리
│   ├── fluctuation_theorems.py #  Jarzynski, Crooks, Protocol
│   └── README.md              #   Layer 4 개념 (한국어)
├── Layer_5/                    # 확률역학
│   ├── stochastic_mechanics.py #  Fokker-Planck, Nelson, ProbabilityCurrent
│   └── README.md              #   Layer 5 개념 (한국어)
├── examples/                   # 실행 가능한 예제
│   ├── phase_a_minimal_verification.py  # 자전 검증 (ALL PASS)
│   ├── phase_b_orbit_verification.py    # 공전 검증 (ALL PASS)
│   ├── bridge_verification.py           # 브릿지 검증 (ALL PASS)
│   ├── dissipation_injection_verification.py  # 에너지 주입/소산 검증 (ALL PASS)
│   ├── fluctuation_verification.py            # 요동 검증 (ALL PASS)
│   ├── fdt_verification.py                   # FDT 등분배 검증 (ALL PASS)
│   ├── layer1_verification.py                # Layer 1 통계역학 검증 (ALL PASS)
│   ├── layer2_verification.py                # Layer 2 다체/장론 검증 (ALL PASS)
│   ├── layer3_verification.py                # Layer 3 게이지/기하학 검증 (ALL PASS)
│   ├── layer4_verification.py                # Layer 4 비평형 일 정리 검증 (ALL PASS)
│   ├── layer5_verification.py                # Layer 5 확률역학 검증 (ALL PASS)
│   ├── phase_a_integration_test.py      # 우물 + 자전 통합
│   └── integration_test_demo.py         # 기본 통합 테스트
└── docs/                       # 참고 문서
    ├── FULL_CONCEPT_AND_STATUS.md   # 전체 개념 · 현재 상태 (한국어)
    ├── FULL_CONCEPT_AND_STATUS_EN.md # Full concept (English)
    └── WORK_LOG.md                  # 시간순 작업 기록
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

| 단계 | 상태 |
|------|------|
| 정적 퍼텐셜 (우물 생성 + 수렴) | 완료 |
| 자전 (코리올리 회전, 에너지 보존) | 완료 |
| 공전 (다중 우물 순환 궤도, 3-우물 검증) | 완료 |
| WellFormation → Gaussian 브릿지 | 완료 |
| 에너지 주입/소산 (-γv + I) | 완료 |
| 요동 (Langevin noise, σξ(t)) | 완료 |
| FDT (σ²=2γT/m, Boltzmann 등분배) | 완료 |
| **Layer 1: 통계역학 정식화** | 완료 |
| **Layer 2: 다체/장론** | 완료 |
| **Layer 3: 게이지/기하학** | 완료 |
| **Layer 4: 비평형 일 정리** | 완료 |
| **Layer 5: 확률역학** | 완료 |

> 고전 구조가 먼저, 확률은 마지막에 얹는다.
> 구조가 있어야 요동의 의미가 생긴다.
> 줄기가 닫힌 뒤, 토양(Layer 1)부터 쌓는다.
> Layer 2에서 장(field)이 태어난다.
> Layer 3에서 공간이 구부러진다.
> Layer 4에서 비평형이 정확해진다.
> Layer 5에서 궤적이 밀도가 된다.

단계 설명: [Phase_A/STAGES_SPIN_ORBIT_FLUCTUATION.md](Phase_A/STAGES_SPIN_ORBIT_FLUCTUATION.md)

---

*GNJz (Qquarts) · Cookiie Brain v0.3.0*
*"Code is Free. Success is Shared."*
