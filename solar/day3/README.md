# day3/ — 셋째날: 땅·바다 + 식생 + 산불 Gaia Attractor

**창세기 구절**  
> *“물이 한 곳으로 모이고 마른 땅이 드러나니”*  
> *“땅은 풀과 씨 맺는 채소와 씨 가진 열매 맺는 나무를 내라”*

**엔진 해석**  
셋째날은

1. **땅과 바다의 분리 (`surface/`)**  
2. 그 위에서 **토양 형성·식생·대기 피드백 (`biosphere/`)**  
3. 산불에 의한 **O₂ attractor / CO₂ 피드백 (`fire/`)**  
4. 이 모든 것을 닫힌 루프로 묶는 **Gaia 루프 (`gaia_loop_connector.py`)**

가 연속으로 작동하는 단계다.

`day3/` 폴더는 이 네 레이어의 핵심 기어를 **셋째날 관점에서 한 눈에 보여주는 집합 패키지**다.

---

## 1. 포함되는 모듈 / 기어

`day3/__init__.py` 에서 재export 되는 이름:

- `SurfaceSchema`, `effective_albedo` (`surface/`)  
- `BiosphereColumn`, `BiosphereState`, `LatitudeBands`, `BAND_CENTERS_DEG`, `BAND_WEIGHTS` (`biosphere/`)  
- `FireEngine`, `FireEnvSnapshot` (`fire/`)  
- `GaiaLoopConnector`, `LoopState`, `make_connector` (`gaia_loop_connector.py`)

실제 구현 위치 (현재 구조):

- `solar/day3/surface/*`
- `solar/day3/biosphere/*`
- `solar/day3/fire/*`
- `solar/bridge/gaia_loop_connector.py`

---

## 2. 셋째날 전체 흐름

```text
[surface/]    — land_fraction, A_land, A_ocean
      │
      ▼
[atmosphere/] — F_solar, A_eff → T_surface, CO2/O2/H2O, water_phase
      │
      ▼
[biosphere/]  — pioneer 토양 형성 + 광합성 + 대기 피드백
      │
      ▼
[fire/]       — 전지구 산불 엔진 (O2 attractor)
      │
      ▼
[GaiaLoopConnector] — Loop A/B/C 로 CO2, albedo, obliquity 루프 닫힘
```

- `surface/` 가 **땅/바다 분리 + 유효 알베도**를 만든다.  
- `biosphere/` 가 **척박→선구→광합성→대기 변화→호흡 식생** 흐름을 모델링한다.  
- `fire/` 가 **O₂ 과잉일 때 산불이 자동으로 발생하는 attractor**를 만든다.  
- `GaiaLoopConnector` 가 **산불 CO₂, 식생 알베도, 세차 obliquity** 를 묶어  
  **자율 조절 Gaia 항상성 루프(Loop A/B/C)** 를 완성한다.

---

## 3. 사용 예시 (요약)

### 3.1 Surface + Atmosphere + Biosphere 1D 컬럼

```python
from solar.day1 import SolarLuminosity
from solar.day2 import AtmosphereColumn
from solar.day3 import SurfaceSchema, BiosphereColumn

sun = SolarLuminosity(mass_solar=1.0)
surf = SurfaceSchema(land_fraction=0.29, albedo_land=0.28, albedo_ocean=0.06)
atm = AtmosphereColumn(T_surface_init=288.0, albedo=surf.effective_albedo())
bio = BiosphereColumn(body_name="Earth", land_fraction=0.29)

dt_yr = 0.02
for _ in range(50):
    F = sun.irradiance_si(1.0)
    atm.step(F, dt_yr)
    st = atm.state(F)
    env = {
        "F_solar_si": F,
        "T_surface": st.T_surface,
        "P_surface": st.P_surface,
        "CO2": st.composition.CO2,
        "H2O": st.composition.H2O,
        "O2": st.composition.O2,
        "water_phase": st.water_phase,
        "land_fraction": surf.land_fraction,
    }
    fb = bio.step(env, dt_yr)
    # fb["delta_CO2"], fb["delta_O2"], fb["delta_albedo_land"] 등을
    # AtmosphereColumn/SurfaceSchema 쪽에 반영하는 것이 셋째날 피드백 루프.
```

### 3.2 FireEngine + GaiaLoopConnector

```python
from solar.day3 import FireEngine, FireEnvSnapshot, GaiaLoopConnector, make_connector

atm, connector = make_connector(T_init=288.0, CO2_ppm=400.0, O2_frac=0.21)
engine = FireEngine()

env = FireEnvSnapshot(O2_frac=0.21, CO2_ppm=400.0, time_yr=0.5)
results = engine.predict(env)

# Loop A: 산불 CO2 → 대기 CO2
delta_CO2 = connector.apply_fire_co2_loop(results, dt_yr=1.0)

# Loop B: biosphere delta_albedo_land → atmosphere.albedo
# (biosphere step 결과 dict를 전달)

# Loop C: obliquity_deg는 day2/3/4에서 공급 (Milankovitch 연동시)
```

---

## 4. 참고 문서 및 블록체인 서명

- `solar/biosphere/README.md` — 셋째날 biosphere 레이어 전체 사양.  
- `docs/BIOSPHERE_LAYER_SPEC.md` — 토양·생애주기·Gaia 루프 상세 설계.  
- `docs/VERSION_LOG.md` — v1.6.0~v2.4.0 (surface, biosphere, fire, Gaia 루프) 기록.
- 블록체인 체인:
  - `blockchain/pham_chain_surface_schema.json`
  - `blockchain/pham_chain_LAYER4_verification.json`
  - `blockchain/pham_chain_DAY3_PROGRESS_CHECK.json`

```text
PHAM_CHAIN:
  - 셋째날(surface/biosphere/fire) 관련 체인들 — 토양·식생·산불 Gaia Attractor 검증 (A_HIGH)
```

*v2.4.x · PHAM Signed · GNJz (Qquarts) + Claude 5.1*

