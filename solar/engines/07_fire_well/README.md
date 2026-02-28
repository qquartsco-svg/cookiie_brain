# 07 Fire Well — 정화 엔진 (FireEngine)

> *"불과 유황" — 창세기 19:24 / "연단하는 불" — 말라기 3:2*

## 역할
산불 확산·O₂ 어트랙터·CO₂ 방출.
O₂ 농도가 너무 높으면 산불 확률이 높아지고 O₂를 소모 → **O₂ 자기 조절** 메커니즘.

## 독립성
- 의존: stdlib(`math`, `dataclasses`) 만
- 내부 파일: `fire_risk.py`
- 완전 독립

## 주요 클래스
| 클래스 | 역할 |
|--------|------|
| `FireEngine` | 산불 ODE — `step(env, dt_yr)` |

## 빠른 시작
```python
import sys; sys.path.insert(0, '.')
from fire_engine import FireEngine

fire = FireEngine()
env  = {"O2_frac": 0.25, "CO2_ppm": 400.0, "dryness": 0.5, "season": 0.0}
result = fire.step(env=env, dt_yr=1.0)
print(f"fire_index={result.get('fire_index',0):.3f}")
```

## 시스템 위치
```
12 Well 시스템
└── 07_fire_well  ← 정화 (O₂ 자기 조절·CO₂ 순환)
```
