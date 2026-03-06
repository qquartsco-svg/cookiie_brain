# 12 Evos Well — 지능 엔진 (MutationEngine)

> *"하나님이 자기 형상 곧 하나님의 형상대로 사람을 창조하시되" — 창세기 1:27*

## 역할
베르누이 변이 + 재조합 이진 수렴 압력.
환경 신호(T, CO₂)를 받아 **변이 이벤트(MutationEvent)** 를 생성.
Day6 진화 OS의 핵심 — 혼돈에서 질서로 수렴하는 메커니즘.

## 독립성
- 의존: stdlib(`random`, `dataclasses`) 만
- 완전 독립 — 복사만 해도 즉시 실행

## 주요 클래스
| 클래스 | 역할 |
|--------|------|
| `MutationEngine` | 베르누이 변이 — `step(p_contact, env, dt_yr, ...)` |
| `MutationEvent` | 변이 이벤트 dataclass |
| `make_mutation_engine` | 팩토리 함수 |

## 빠른 시작
```python
import sys, random; sys.path.insert(0, '.')
from evos_engine import MutationEngine

me     = MutationEngine(base_mutation_rate=0.01)
rng    = random.Random(42)
env    = {"T_surface": 288.0, "CO2_ppm": 400.0}
events = me.step(p_contact=0.3, env=env, dt_yr=1.0,
                 band_idx=0, n_traits=4, rng=rng)
print(f"변이 이벤트: {len(events)}개")
for e in events:
    print(f"  {e.parent_trait} → {e.new_trait}  (via_recomb={e.via_recombination})")
```

## 시스템 위치
```
12 Well 시스템
└── 12_evos_well  ← 지능 (진화 OS — 혼돈→수렴)
```
