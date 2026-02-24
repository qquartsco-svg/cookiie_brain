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
It simulates state-vector dynamics on a Hopfield energy landscape.
Experiences (episodes) shape energy wells (W, b),
and the state's convergence, rotation, and transitions across the potential field
are tracked via numerical integration (symplectic Euler, Strang splitting).
In Phase A, a Coriolis-type rotational term (ωJv) is introduced
to generate phase structure (limit cycles) while strictly conserving energy.

---

## 핵심 수식

```
골짜기의 깊이 (퍼텐셜):   V(x) = -(1/2)x'Wx - b'x   (지역 최솟값 최대 1개)
공을 끌어당기는 힘:        g(x) = -∇V(x) = Wx + b
전체 운동 방정식:          ẍ = g(x) + ωJv - γv + I(x,v,t) + σξ(t)
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
ẍ = -∇V(x) + ωJv - γv + I(x,v,t) + σξ(t)

σ : 노이즈 세기 (온도와 비슷한 역할)
ξ : 백색 노이즈 (매 순간 랜덤 방향)
```

**적분**: Strang splitting의 감쇠 반스텝에 Wiener increment 추가
- `v += σ·√(dt/2)·N(0,1)` (Euler-Maruyama)
- σ=0이면 기존 결정론적 동작과 100% 동일

검증 실행:
```bash
python examples/fluctuation_verification.py
```

---

## 설계 원칙

- **state 불변**: `new_state = state.copy()` 후 반환. 원본 안 건드림
- **하드코딩 금지**: 물리 상수, 경로 전부 파라미터화
- **엔진은 상태를 perturb할 뿐, 지배하지 않음**
- **GlobalState 하나로 모든 엔진 연결**: extensions 규약으로 데이터 교환

상세: [docs/](docs/)
전체 개념 · 현재 상태: [docs/FULL_CONCEPT_AND_STATUS.md](docs/FULL_CONCEPT_AND_STATUS.md)

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
│   └── README.md               #   개념 · 구현 위치 · 사용법
├── examples/                   # 실행 가능한 예제
│   ├── phase_a_minimal_verification.py  # 자전 검증 (ALL PASS)
│   ├── phase_b_orbit_verification.py    # 공전 검증 (ALL PASS)
│   ├── bridge_verification.py           # 브릿지 검증 (ALL PASS)
│   ├── dissipation_injection_verification.py  # 에너지 주입/소산 검증 (ALL PASS)
│   ├── fluctuation_verification.py            # 요동 검증 (ALL PASS)
│   ├── phase_a_integration_test.py      # 우물 + 자전 통합
│   └── integration_test_demo.py         # 기본 통합 테스트
└── docs/                       # 참고 문서
    ├── FULL_CONCEPT_AND_STATUS.md  # 전체 개념 · 현재 상태 (핵심 문서)
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

| 단계 | 상태 |
|------|------|
| 정적 퍼텐셜 (우물 생성 + 수렴) | 완료 |
| 자전 (코리올리 회전, 에너지 보존) | 완료 |
| 공전 (다중 우물 순환 궤도, 3-우물 검증) | 완료 |
| WellFormation → Gaussian 브릿지 | 완료 |
| 에너지 주입/소산 (-γv + I) | 완료 |
| 요동 (Langevin noise, σξ(t)) | 완료 |

> 고전 구조가 먼저, 확률은 마지막에 얹는다.
> 구조가 있어야 요동의 의미가 생긴다.

단계 설명: [Phase_A/STAGES_SPIN_ORBIT_FLUCTUATION.md](Phase_A/STAGES_SPIN_ORBIT_FLUCTUATION.md)

---

*GNJz (Qquarts) · Cookiie Brain v0.3.0*
*"Code is Free. Success is Shared."*
