# 01 Solar Well — 에너지 엔진 (SolarLuminosity)

> *"빛이 있으라" — 창세기 1:3*

## 역할
태양 광도와 행성 표면 복사를 계산한다.
거리·알베도·온실 파라미터를 받아 **평형 온도(T_eq)** 와 **복사 플럭스(F)** 를 반환.

## 독립성
- 의존: `numpy` 만
- `solar/` 패키지 없이 이 폴더만 복사해도 동작

## 주요 클래스
| 클래스 | 역할 |
|--------|------|
| `SolarLuminosity` | L☉ → F(r), T_eq 계산기 |
| `IrradianceState` | 계산 결과 상태 dataclass |

## 빠른 시작
```python
import sys; sys.path.insert(0, '.')
from solar_engine import SolarLuminosity

sun = SolarLuminosity()
F   = sun.flux_at_distance(r_AU=1.0)      # W/m²
T   = sun.equilibrium_temp(A=0.3, f=0.25) # K
print(f"F={F:.1f} W/m²  T_eq={T:.1f} K")
```

## 시스템 위치
```
12 Well 시스템
└── 01_solar_well  ← 에너지 원천 (모든 엔진의 출발점)
```
