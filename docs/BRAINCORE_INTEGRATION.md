# CookiieBrain ↔ BrainCore 연동

**GEAR_CONNECTION_STRATEGY Phase 1**

환경 물리(F, T, P, habitable)를 BrainCore GlobalState extension으로 노출.

---

## Extension 형식

```python
state.set_extension("solar_environment", data)
```

`data` 구조:
```python
{
    "time_yr": float,
    "bodies": {
        "Earth": {
            "F_solar": float,    # [W/m²]
            "T_surface": float,  # [K]
            "P_surface": float,  # [Pa]
            "habitable": bool,
            "water_phase": str,  # "solid"|"liquid"|"gas"
            "r_au": float,
            "T_eq": float,
            "greenhouse_dT": float,
        },
        ...
    },
    "global": {
        "any_habitable": bool,
        "body_count": int,
    },
}
```

---

## 사용법

### 1. Bridge만 사용 (BrainCore 없이)

```python
from solar.brain_core_bridge import (
    get_solar_environment_extension,
    create_default_environment,
)

engine, sun, atmospheres = create_default_environment()
data = get_solar_environment_extension(engine, sun, atmospheres, dt_yr=0.01)
# data를 원하는 형태로 사용
```

### 2. BrainCore와 연동

```python
from brain_core import GlobalState
from solar.brain_core_bridge import (
    get_solar_environment_extension,
    create_default_environment,
)

state = GlobalState(state_vector=..., energy=0.0, risk=0.0)
engine, sun, atmospheres = create_default_environment()
data = get_solar_environment_extension(engine, sun, atmospheres, dt_yr=0.01)
state.set_extension("solar_environment", data)

# 다른 엔진이 읽기
env = state.get_extension("solar_environment")
earth_T = env["bodies"]["Earth"]["T_surface"]
```

---

## 데모

```bash
python examples/brain_core_environment_demo.py
```

BrainCore 설치 시 `state.set_extension` 예시가 동작. 미설치 시 extension 형식만 출력.

---

## 의존

- CookiieBrain `solar/` (core, em, atmosphere, surface)
- BrainCore: 선택 (extension 형식만 사용 시 불필요)
