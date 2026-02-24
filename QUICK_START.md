# 빠른 시작 가이드

**버전**: 0.3.0

---

## 실행 전 준비

```bash
pip install numpy
```

---

## 독립 모듈 사용 (Layer 1~6)

Layer 1~6은 외부 의존 없이 독립 실행 가능합니다:

```python
import numpy as np
from Layer_1 import kramers_rate, entropy_production_rate
from Layer_5 import FokkerPlanckSolver1D, NelsonDecomposition
from Layer_6 import FisherMetricCalculator, ParameterSpace
```

---

## 검증 실행

```bash
# 전체 검증 (Phase A + Layer 1~6)
python examples/phase_a_minimal_verification.py
python examples/phase_b_orbit_verification.py
python examples/fluctuation_verification.py
python examples/fdt_verification.py
python examples/layer1_verification.py
python examples/layer2_verification.py
python examples/layer3_verification.py
python examples/layer4_verification.py
python examples/layer5_verification.py
python examples/layer6_verification.py
```

---

## 통합 엔진 사용 (BrainCore 필요)

```python
from cookiie_brain_engine import CookiieBrainEngine
from brain_core.global_state import GlobalState
import numpy as np

brain = CookiieBrainEngine(
    enable_well_formation=True,
    enable_potential_field=True,
    potential_field_config={
        "enable_phase_a": True,
        "phase_a_mode": "minimal",
        "phase_a_omega": 1.0,
    },
)

state = GlobalState(
    state_vector=np.array([1.0, 0.0, 0.0, 0.0]),
    energy=0.0,
)
state.set_extension("episodes", [...])
result = brain.update(state)
```

BrainCore, WellFormationEngine, PotentialFieldEngine이 같은 프로젝트 내에 있어야 합니다.

---

## 주요 문서

| 문서 | 내용 |
|------|------|
| [README.md](README.md) | 전체 구조, 수식, 파이프라인 |
| [docs/FULL_CONCEPT_AND_STATUS.md](docs/FULL_CONCEPT_AND_STATUS.md) | 전체 개념 · 현재 상태 (한국어) |
| [docs/FULL_CONCEPT_AND_STATUS_EN.md](docs/FULL_CONCEPT_AND_STATUS_EN.md) | Full concept (English) |
| [Layer_1/](Layer_1/) ~ [Layer_6/](Layer_6/) | 각 레이어 README (한국어 + 영어) |

---

## 현재 상태

| 모듈 | 상태 |
|------|------|
| Phase A (자전) | 완료 |
| Phase B (공전) | 완료 |
| Phase C (요동/FDT) | 완료 |
| Layer 1 (통계역학) | 완료 |
| Layer 2 (다체/장론) | 완료 |
| Layer 3 (게이지/기하학) | 완료 |
| Layer 4 (비평형 일 정리) | 완료 |
| Layer 5 (확률역학) | 완료 |
| Layer 6 (정보 기하학) | 완료 |

---

*GNJz (Qquarts) · v0.3.0*
