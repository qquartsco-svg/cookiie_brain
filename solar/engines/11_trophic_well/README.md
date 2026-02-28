# 11 Trophic Well — 에너지 흐름 엔진 (FoodWeb)

> *"바다의 물고기와 하늘의 새와 땅에 움직이는 모든 생물" — 창세기 1:28*

## 역할
Lotka-Volterra 트로픽 ODE.
식물성플랑크톤 → 초식동물 → 육식동물 에너지 흐름을 시간 적분.
CO₂ 호흡량 계산 포함.

## 독립성
- 의존: stdlib(`dataclasses`, `math`) 만
- 내부 파일: `_constants.py`

## 주요 클래스
| 클래스 | 역할 |
|--------|------|
| `FoodWeb` | 트로픽 ODE — `step(state, env, dt_yr)` |
| `TrophicState` | 트로픽 상태 dataclass |

## 빠른 시작
```python
import sys; sys.path.insert(0, '.')
from trophic_engine import FoodWeb, TrophicState

fw    = FoodWeb()
state = TrophicState(phyto=1.0, herbivore=0.5, carnivore=0.2, co2_resp_yr=0.0)
env   = {"GPP": 0.5, "fish_predation": 0.01}
new   = fw.step(state, env=env, dt_yr=1.0)
print(f"phyto={new.phyto:.3f}  herbivore={new.herbivore:.3f}  carnivore={new.carnivore:.3f}")
```

## 시스템 위치
```
12 Well 시스템
└── 11_trophic_well  ← 에너지 흐름 (먹이사슬 ODE)
```
