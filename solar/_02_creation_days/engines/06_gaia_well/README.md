# 06 Gaia Well — 항상성 엔진 (StressAccumulator)

> *"각기 종류대로" — 창세기 1:11*

## 역할
행성 스케일 스트레스 누적·방전·리셋.
뉴런 이벤트(NeuronEvent) → 세포→기관→행성 3단계 EMA 필터링.
**HomeostasisOS**의 핵심 — 스트레스가 임계를 넘으면 방전(discharge)하고 리셋.

## 독립성
- 의존: stdlib(`math`, `dataclasses`, `collections`) 만
- 완전 독립 — 복사만 해도 즉시 실행

## 주요 클래스
| 클래스 | 역할 |
|--------|------|
| `StressAccumulator` | 3단계 스트레스 EMA 누적기 |
| `NeuronEvent` | 이벤트 입력 dataclass |
| `CellStressState` | 세포 스트레스 상태 |
| `PlanetStressIndex` | 행성 스트레스 요약 |

## 빠른 시작
```python
import sys; sys.path.insert(0, '.')
from gaia_engine import StressAccumulator, NeuronEvent

sa = StressAccumulator()
sa.push_neuron_event(NeuronEvent(neuron_id="co2_spike", intensity=0.8, source="atmosphere"))
summary = sa.summary()
print(f"planet_stress={summary['planet_stress_ema']:.3f}")
```

## 시스템 위치
```
12 Well 시스템
└── 06_gaia_well  ← 항상성 (스트레스 누적→임계→방전→리셋)
```
