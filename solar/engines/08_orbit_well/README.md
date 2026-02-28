# 08 Orbit Well — 리듬 엔진 (MilankovitchCycle)

> *"해와 달과 별들로 징조와 계절과 날과 해를 이루라" — 창세기 1:14*

## 역할
지구 궤도 장주기 리듬 (Milankovitch 사이클).
이심률·경사각·세차를 시간 함수로 계산 → **일사량 스케일**, **빙하기 판정**.

## 독립성
- 의존: stdlib(`math`, `dataclasses`) 만
- 완전 독립 — 복사만 해도 즉시 실행

## 주요 클래스
| 클래스 | 역할 |
|--------|------|
| `MilankovitchCycle` | 궤도 요소 계산기 |
| `MilankovitchState` | 궤도 상태 dataclass |

## 빠른 시작
```python
import sys; sys.path.insert(0, '.')
from orbit_engine import MilankovitchCycle

mc  = MilankovitchCycle()
obl = mc.obliquity(t_yr=0.0)
ins = mc.insolation_scale(t_yr=0.0, phi_deg=45.0)
print(f"경사각={obl:.2f}°  일사 스케일={ins:.4f}")
```

## 시스템 위치
```
12 Well 시스템
└── 08_orbit_well  ← 리듬 (장주기 천문 사이클)
```
