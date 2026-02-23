# Cookiie Brain

**상태 동역학 기반 뇌 모델링 통합 엔진**

에너지 지형 위에서 상태가 흐르고, 회전하고, 수렴하는 과정을 물리학으로 표현합니다.
정답을 제시하기보다, 각자의 해답을 찾아갈 수 있는 구조를 만드는 것이 목적입니다.

```
Version : 0.2.0
License : PHAM-OPEN v2.0
Python  : 3.8+
Author  : GNJz (Qquarts)
```

---

## 핵심 수식

```
state_{t+1} = engine.update(state_t)

V(x) = E_hopfield(x) = -(1/2)x'Wx - b'x       # 퍼텐셜 (기억 우물)
g(x) = -∇V(x) = Wx + b                          # 필드 (가속도)
a    = g(x) + ωJv                                # 자전 포함 시 (코리올리형)
E    = (1/2)||v||² + V(x)                        # 총 에너지 (보존량)
```

수학적 기초 · 구현 상세: [PotentialFieldEngine CONCEPT](../Brain_Disorder_Simulation_Engine/Unsolved_Problems_Engines/PotentialFieldEngine/docs/CONCEPT.md)

---

## 엔진 파이프라인

```
WellFormationEngine        episodes → W, b (Hopfield 가중치)
       ↓
PotentialFieldEngine       V(x), g(x) → 상태 업데이트 (적분)
       ↓                   ├ 기본: symplectic Euler
       ↓                   └ 자전: Strang splitting + exact rotation
Phase_A (선택)             ωJv 코리올리 회전 → 에너지 보존 자전
       ↓
CerebellumEngine (선택)    운동 보정
       ↓
HippoMemoryEngine (예정)   장기 기억
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

퍼텐셜 우물 안에서 에너지를 보존하면서 회전하는 상태를 구현합니다.

```
R(x, v) = ωJv                   # 코리올리형: 힘이 속도에 수직
v · R = v · (ωJv) = 0           # J 반대칭 → 항상 0 → 에너지 보존
```

**적분**: Drift-Kick/Rotate-Kick-Drift (Boris 방식)
- exact rotation `exp(ωJdt)` 으로 `|v|` 정확 보존
- secular drift 없음 (검증: rel_drift < 1e-6)

검증 실행:
```bash
python examples/phase_a_minimal_verification.py
```

수학적 기초 · 단계 로드맵: [Phase_A/](Phase_A/)

---

## 설계 원칙

- **state 불변**: `new_state = state.copy()` 후 반환. 원본 안 건드림
- **하드코딩 금지**: 물리 상수, 경로 전부 파라미터화
- **엔진은 상태를 perturb할 뿐, 지배하지 않음**
- **GlobalState 하나로 모든 엔진 연결**: extensions 규약으로 데이터 교환

상세: [docs/](docs/)

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
├── Phase_A/                    # 자전 모듈
│   ├── rotational_field.py     #   코리올리형 + pole형 회전 생성
│   ├── moon.py                 #   위성 중력장
│   └── docs/                   #   작업 기록 · 수학 문서
├── examples/                   # 실행 가능한 예제
│   ├── phase_a_minimal_verification.py  # 자전 검증 (ALL PASS)
│   ├── phase_a_integration_test.py      # 우물 + 자전 통합
│   └── integration_test_demo.py         # 기본 통합 테스트
└── docs/                       # 참고 문서 (설계 분석 · 리뷰 · 로드맵)
```

---

## PHAM 블록체인 서명

이 프로젝트의 코드 기여는 PHAM v4 블록체인으로 무결성을 기록합니다.

- **4-Signal 스코어링**: Byte(25%) + Text(35%) + AST(30%) + Exec(10%)
- **체인 구조**: `SHA256(index | prev_hash | timestamp | data_hash)`
- **라이선스**: 누구나 자유롭게 사용. 수익 발생 시 6% 후원 (신뢰 기반)

서명 도구: [pham_sign_v4.py](../Brain_Disorder_Simulation_Engine/Unsolved_Problems_Engines/PotentialFieldEngine/blockchain/pham_sign_v4.py)
라이선스 전문: PHAM-OPEN v2.0

---

## 현재 상태와 방향

| 단계 | 상태 |
|------|------|
| 정적 퍼텐셜 (우물 생성 + 수렴) | 완료 |
| 자전 (코리올리 회전, 에너지 보존) | 완료 |
| 공전 (다중 중심 상호작용) | 미착수 |
| 요동 (확률적 요동, 불확정성) | 미착수 |

> 고전 구조가 먼저, 확률은 마지막에 얹는다.
> 구조가 있어야 요동의 의미가 생긴다.

단계 설명: [Phase_A/STAGES_SPIN_ORBIT_FLUCTUATION.md](Phase_A/STAGES_SPIN_ORBIT_FLUCTUATION.md)

---

*GNJz (Qquarts) · Cookiie Brain v0.2.0*
*"Code is Free. Success is Shared."*
