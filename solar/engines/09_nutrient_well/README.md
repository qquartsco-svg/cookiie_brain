# 09 Nutrient Well — 자원 엔진 (NitrogenCycle)

> *"씨 맺는 채소와 씨 가진 열매 맺는 나무" — 창세기 1:11*

## 역할
질소 고정·탈질·N_soil 순환 ODE.
온도·수분·GPP를 입력받아 **N_soil** (식물이 쓸 수 있는 질소량) 을 시간 적분.
12우물 시스템의 "자원 분배" 엔진.

## 독립성
- 의존: stdlib(`math`, `dataclasses`) 만
- 내부 파일: `fixation.py`

## 주요 클래스
| 클래스 | 역할 |
|--------|------|
| `NitrogenCycle` | 질소 순환 ODE — `step(dt, B_pioneer, GPP_rate, O2_frac, T_K, W_moisture)` |
| `NitrogenState` | 질소 상태 dataclass |

## 빠른 시작
```python
import sys; sys.path.insert(0, '.')
from nutrient_engine import NitrogenCycle

nc    = NitrogenCycle()
state = nc.step(dt=1.0, B_pioneer=0.5, GPP_rate=1.0,
                O2_frac=0.21, T_K=288.0, W_moisture=0.6)
print(f"N_soil={state.N_soil:.4f}")
```

## 시스템 위치
```
12 Well 시스템
└── 09_nutrient_well  ← 자원 (질소·영양 순환)
```
