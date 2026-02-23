# 빠른 시작 가이드

**버전**: 0.2.0

---

## 실행 전 준비

```bash
pip install numpy
```

BrainCore, WellFormationEngine, PotentialFieldEngine이 같은 프로젝트 내에 있어야 합니다.
(상대 경로로 자동 탐색합니다.)

---

## 기본 사용 — 우물 생성 + 상태 업데이트

```python
from cookiie_brain_engine import CookiieBrainEngine
from brain_core.global_state import GlobalState
import numpy as np

brain = CookiieBrainEngine(
    enable_well_formation=True,
    enable_potential_field=True,
)

state = GlobalState(
    state_vector=np.array([1.0, 0.0, 0.0, 0.0]),  # [위치x, 위치y, 속도x, 속도y]
    energy=0.0,
)

state.set_extension("episodes", [...])  # 기억 에피소드 데이터

result = brain.update(state)
print(f"에너지: {brain.get_energy(result)}")
```

---

## 자전 활성화 (Phase A)

```python
brain = CookiieBrainEngine(
    enable_well_formation=True,
    enable_potential_field=True,
    potential_field_config={
        "enable_phase_a": True,
        "phase_a_mode": "minimal",   # 코리올리형 — 에너지 보존
        "phase_a_omega": 1.0,
    },
)
```

이것만 바꾸면 상태가 우물 안에서 회전합니다.

---

## 예제 실행

```bash
# 자전 검증 (4항목 체크)
python examples/phase_a_minimal_verification.py

# 우물 + 자전 통합 테스트
python examples/phase_a_integration_test.py

# 기본 통합 테스트
python examples/integration_test_demo.py
```

---

## 주요 문서

| 문서 | 내용 |
|------|------|
| [README.md](README.md) | 전체 구조, 수식, 파이프라인 |
| [Phase_A/README.md](Phase_A/README.md) | 자전 모듈 상세 (두 가지 회전 방식, 검증) |
| [Phase_A/STAGES_SPIN_ORBIT_FLUCTUATION.md](Phase_A/STAGES_SPIN_ORBIT_FLUCTUATION.md) | 자전 → 공전 → 요동 단계 설명 |
| [docs/](docs/) | 설계 분석, 코드 리뷰, 로드맵 등 참고 문서 |

---

## 현재 상태

- 정적 퍼텐셜 (우물 생성 + 수렴): 완료
- 자전 (코리올리 회전, 에너지 보존): 완료
- 공전 / 요동: 미착수

---

*GNJz (Qquarts) · v0.2.0*
