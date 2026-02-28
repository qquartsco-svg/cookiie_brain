# 03 Atmos Well — 호흡 엔진 (AtmosphereColumn)

> *"궁창 아래의 물" — 창세기 1:7*

## 역할
단일 기둥 대기 ODE 적분기.
태양 복사 + 알베도 + 대기 조성 → **표면 온도(T_surface)**, **CO₂**, **수분 상태** 를 시간 적분.

## 독립성
- 의존: `numpy` 만
- 내부 파일: `greenhouse.py`, `water_cycle.py`, `_constants.py`

## 주요 클래스
| 클래스 | 역할 |
|--------|------|
| `AtmosphereColumn` | 대기 ODE — `step(F_solar, dt_yr)` |
| `AtmosphereState` | 대기 상태 dataclass |

## 빠른 시작
```python
import sys; sys.path.insert(0, '.')
from atmos_engine import AtmosphereColumn

atm = AtmosphereColumn()
atm.step(F_solar_si=1361.0, dt_yr=1.0)
print(f"T_surface={atm.T_surface:.1f}K  CO2={atm.composition.get('CO2_ppm',400):.1f}ppm")
```

## 시스템 위치
```
12 Well 시스템
└── 03_atmos_well  ← 호흡층 (온도·CO₂·물 순환)
```
