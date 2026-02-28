# 05 Litho Well — 기초 엔진 (BiosphereColumn)

> *"땅이 드러나라" — 창세기 1:9*

## 역할
단일 위도 밴드의 생물권 ODE.
온도·CO₂·수분 → **GPP**, **호흡**, **Δ CO₂**, **Δ O₂** 시간 적분.

## 독립성
- 의존: stdlib(`math`, `dataclasses`) 만
- 내부 파일: `state.py`, `pioneer.py`, `photo.py`, `_constants.py`

## 주요 클래스
| 클래스 | 역할 |
|--------|------|
| `BiosphereColumn` | 생물권 ODE — `step(env, dt_yr)` |
| `BiosphereState` | 생물권 상태 dataclass |

## 빠른 시작
```python
import sys; sys.path.insert(0, '.')
from litho_engine import BiosphereColumn

bio = BiosphereColumn()
env = {"T_surface": 288.0, "CO2_ppm": 400.0, "O2_frac": 0.21,
       "water_phase": "liquid", "land_fraction": 0.29}
result = bio.step(env=env, dt_yr=1.0)
print(f"GPP={result.get('GPP',0):.4f}  ΔCO2={result.get('delta_CO2',0):.4f}")
```

## 시스템 위치
```
12 Well 시스템
└── 05_litho_well  ← 기초층 (땅·광합성·호흡)
```
