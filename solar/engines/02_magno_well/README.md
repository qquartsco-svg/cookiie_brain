# 02 Magno Well — 보호막 엔진 (Magnetosphere)

> *"궁창이 있어 물 가운데 있으라" — 창세기 1:6*

## 역할
행성 자기쌍극자장 + 태양풍을 계산하여 **자기권 경계(r_magnetopause)** 와 **차폐 효율** 을 반환.
생명이 존재하기 위한 방어막.

## 독립성
- 의존: `numpy` 만
- `solar/` 패키지 없이 이 폴더만 복사해도 동작

## 주요 클래스
| 클래스 | 역할 |
|--------|------|
| `Magnetosphere` | 자기권 경계·차폐 계산 |
| `MagneticDipole` | 쌍극자 자기장 B(r) |
| `SolarWind` | 태양풍 동압·플럭스 |

## 빠른 시작
```python
import sys; sys.path.insert(0, '.')
import numpy as np
from magno_engine import Magnetosphere
from magnetic_dipole import MagneticDipole
from solar_wind import SolarWind

dipole = MagneticDipole()
wind   = SolarWind()
mag    = Magnetosphere(dipole=dipole, wind=wind)
r_mp   = mag.magnetopause_radius(r_AU=1.0)
print(f"자기권 경계: {r_mp:.2f} R_planet")
```

## 시스템 위치
```
12 Well 시스템
└── 02_magno_well  ← 보호막 (01 에너지 → 02 차폐 → 03 대기)
```
