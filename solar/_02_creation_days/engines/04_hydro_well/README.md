# 04 Hydro Well — 순환 엔진 (OceanNutrients)

> *"물들이 한 곳으로 모이고" — 창세기 1:9*

## 역할
조석 혼합 → 영양염 용승 → 탄소 펌프.
**upwelling_uM**, **CO₂ 흡수량** 을 시간 적분.

## 독립성
- 의존: stdlib(`math`, `dataclasses`) 만
- 완전 독립 — 복사만 해도 즉시 실행

## 주요 클래스
| 클래스 | 역할 |
|--------|------|
| `OceanNutrients` | 해양 영양염 ODE — `step(dt, upwelling_uM, light_factor)` |
| `OceanState` | 해양 상태 dataclass |

## 빠른 시작
```python
import sys; sys.path.insert(0, '.')
from hydro_engine import OceanNutrients

ocean = OceanNutrients()
state = ocean.step(dt=1.0, upwelling_uM=10.0, light_factor=0.8)
print(f"upwelling={state.upwelling_uM:.2f} μM  CO2_sink={state.co2_sink_ppm:.3f} ppm")
```

## 시스템 위치
```
12 Well 시스템
└── 04_hydro_well  ← 순환층 (조석→혼합→탄소 펌프)
```
