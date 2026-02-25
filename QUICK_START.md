# 빠른 시작 가이드

**버전**: 0.6.0

> **v0.4.0 경로 변경**: `Phase_X/` → `trunk/Phase_X/`, `Layer_N/` → `analysis/Layer_N/`
> **v0.6.0 신규**: `hippo/` — HippoMemoryEngine (태양/운영층)

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
from analysis.Layer_1 import kramers_rate, entropy_production_rate
from analysis.Layer_5 import FokkerPlanckSolver1D, NelsonDecomposition
from analysis.Layer_6 import FisherMetricCalculator, ParameterSpace
```

---

## 검증 실행

```bash
# trunk 검증 (Phase A~C)
python examples/phase_a_minimal_verification.py
python examples/phase_b_orbit_verification.py
python examples/fluctuation_verification.py
python examples/fdt_verification.py

# analysis 검증 (Layer 1~6)
python examples/layer1_verification.py
python examples/layer2_verification.py
python examples/layer3_verification.py
python examples/layer4_verification.py
python examples/layer5_verification.py
python examples/layer6_verification.py

# hippo + 통합 검증 (v0.6.0)
python examples/hippo_memory_verification.py
python examples/integrated_pipeline_verification.py
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

## HippoMemoryEngine 사용 (v0.6.0)

```python
from cookiie_brain_engine import CookiieBrainEngine
import numpy as np

brain = CookiieBrainEngine(
    enable_well_formation=True,
    enable_potential_field=True,
    enable_hippo_memory=True,   # 태양 활성화
)

# 기억 인코딩 → 우물 자동 생성
brain.hippo_memory_engine.encode(np.array([3.0]))
brain.hippo_memory_engine.encode(np.array([-2.0]))

# 시뮬레이션 → 우물이 자동으로 강화/감쇠/소멸
for _ in range(1000):
    state = brain.update(state)

# 리콜
brain.hippo_memory_engine.recall(np.array([2.8]))
```

hippo 독립 사용:
```python
from hippo import HippoMemoryEngine, HippoConfig

config = HippoConfig(eta=0.1, decay_rate=0.001)
engine = HippoMemoryEngine(config, dim=1)
injection, changed = engine.step(x, v, dt)
```

상세: [hippo/README.md](hippo/README.md)

---

## 주요 문서

| 문서 | 내용 |
|------|------|
| [README.md](README.md) | 전체 구조, 수식, 파이프라인 |
| [hippo/README.md](hippo/README.md) | HippoMemoryEngine 상세 (태양/운영층) |
| [docs/HIPPO_MEMORY_CONCEPT.md](docs/HIPPO_MEMORY_CONCEPT.md) | HippoMemory 설계 (솔라시스템 비유) |
| [docs/FULL_CONCEPT_AND_STATUS.md](docs/FULL_CONCEPT_AND_STATUS.md) | 전체 개념 · 현재 상태 (한국어) |
| [docs/FULL_CONCEPT_AND_STATUS_EN.md](docs/FULL_CONCEPT_AND_STATUS_EN.md) | Full concept (English) |
| [analysis/Layer_1/](analysis/Layer_1/) ~ [analysis/Layer_6/](analysis/Layer_6/) | 각 레이어 README |

---

## 현재 상태

| 모듈 | 상태 | 버전 |
|------|------|------|
| Phase A (자전) | 완료 | v0.2.0 |
| Phase B (공전) | 완료 | v0.2.0 |
| Phase C (요동/FDT) | 완료 | v0.3.0 |
| Layer 1 (통계역학) | 완료 | v0.3.0 |
| Layer 2 (다체/장론) | 완료 | v0.3.0 |
| Layer 3 (게이지/기하학) | 완료 | v0.3.0 |
| Layer 4 (비평형 일 정리) | 완료 | v0.4.0 |
| Layer 5 (확률역학) | 완료 | v0.4.0 |
| Layer 6 (정보 기하학) | 완료 | v0.4.0 |
| BrainAnalyzer (통합 분석) | 완료 | v0.5.0 |
| **HippoMemoryEngine (태양)** | **완료** | **v0.6.0** |

---

*GNJz (Qquarts) · v0.6.0*
