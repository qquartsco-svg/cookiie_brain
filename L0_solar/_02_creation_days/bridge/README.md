## bridge/ — Gaia · BrainCore 연결 브리지 레이어

### 1. 이 폴더가 하는 일 / What this folder is for

- **역할 (Role)**  
  `bridge/` 는 **Creation Days 엔진(solar.day1~day4)** 을  
  - **BrainCore / 뉴런 레이어**,  
  - **Gaia 항상성 루프(Loop A/B/C)**  
  와 연결해 주는 **브리지 모듈**을 모아둔 곳입니다.  
  물리 엔진(`day4/core`, `day1~3`)의 코드를 직접 바꾸지 않고,  
  “읽기/변환/패치” 만 수행하는 **관측자·어댑터 레이어**입니다.

### 2. 파일별 역할 / Files

- `gaia_loop_connector.py`  
  - **Gaia 항상성 루프를 닫는 연결기 (Loop A/B/C)**  
  - 입력:
    - `AtmosphereColumn` (from `day2/atmosphere`)
    - `FireEngine`, `FireEnvSnapshot` (from `day3/fire`)
    - (옵션) biosphere 결과 dict (`delta_CO2`, `delta_O2`, `delta_albedo_land` 등)  
  - 루프:
    - **Loop A**: 산불 CO₂ → 대기 CO₂ (fire_engine → atmosphere)  
    - **Loop B**: 식생 알베도 → 온도 (biosphere → atmosphere)  
    - **Loop C**: 세차 obliquity → 건기 계절성 (core/day4 + cycles → fire_risk)  
  - 출력: `GaiaLoopConnector`, `LoopState`, `make_connector`, `make_fire_env` 등.  
    → 셋째날/넷째날 모듈들이 **같은 Gaia attractor 위에서** 돌도록 묶어 줍니다.

- `gaia_loop_demo.py`  
  - V1~V4 시나리오로 Loop A/B/C 및 통합 루프가 **정상적으로 닫히는지**를 보여주는 데모입니다.

- `gaia_bridge.py`  
  - **CookiieBrain ↔ GaiaFire 브리지 (뉴런 → 산불/행성 스트레스)**  
  - 입력:
    - BrainCore / CookiieBrain의 `GlobalState` (에너지, 속도 등)  
  - 변환:
    - `GlobalState.energy` → `atp_consumed` (정규화)  
    - 상태 벡터 속도 → `heat_mw`  
    - 시뮬레이션 시간 → `time_ms`  
  - 출력:
    - `NeuronEvent` 스트림 → `StressAccumulator`  
    - `FireEnvSnapshot` patch → `FireEngine` 에 주입  
    - `PlanetStressIndex`, `CognitiveBrainSnapshot` (있을 경우)  
  - 요약: **“뉴런이 스트레스 받으면, 어느 위도에서 불이 날지”** 를 행성 스케일로 번역하는 레이어입니다.

- `gaia_bridge_demo.py`  
  - 간단한 시나리오로 `GaiaBridge` 의 파이프라인(push → update → patch)을 보여주는 데모입니다.

- `brain_core_bridge.py`  
  - **solar → BrainCore 방향 환경 export 브리지**  
  - 입력:
    - `EvolutionEngine` (`day4/core`) + `SolarLuminosity` (`day1/em`)  
    - 행성별 `AtmosphereColumn` (`day2/atmosphere`)  
    - (옵션) `SurfaceSchema` (`day3/surface`), `BiosphereColumn` (`day3/biosphere`)  
  - 동작:
    - 각 행성에 대해 F_solar, T_surface, P_surface, CO₂/O₂/H₂O, water_phase, habitable 여부를 모읍니다.  
    - biosphere가 있을 경우, `biosphere_feedback_to_atmosphere` 를 통해  
      대기 조성/잠열/알베도에 피드백을 반영합니다.
  - 출력:
    - BrainCore `GlobalState` 의 extension 으로 넣을 수 있는 dict:
      ```python
      {
        "time_yr": float,
        "bodies": { "Earth": {...}, ... },
        "global": {"any_habitable": bool, "body_count": int},
      }
      ```  
    - 예시:  
      ```python
      data = get_solar_environment_extension(engine, sun, atmospheres, dt_yr=0.01, ...)
      state.set_extension("solar_environment", data)
      ```

### 3. Creation Days와의 관계 / Relation to Day1–Day5

- **입력 레이어**
  - Day 1: `SolarLuminosity` (복사 조도, 평형 온도)
  - Day 2: `AtmosphereColumn` (T, P, water_phase, habitable)
  - Day 3: `SurfaceSchema`, `BiosphereColumn`, `FireEngine`
  - Day 4: `EvolutionEngine`, `NitrogenCycle`, `MilankovitchCycle`, `gravity_tides` (간접적으로 사용)
  - Day 5: `BirdAgent`, `FishAgent`, `SeedTransport`, `FoodWeb` (생물 이동 → Loop F/G/H)

- **출력 레이어**
  - BrainCore / CookiieBrain: `solar_environment` extension, NeuronEvent, CognitiveBrainSnapshot
  - Gaia Layer: Loop A/B/C/F/G/H 가 닫힌 항상성 상태 (`LoopState`, PlanetStressIndex)

브리지들은 **엔진의 내부 물리를 수정하지 않고**,
항상 **입력/출력 데이터 변환만 담당**하도록 설계되어 있습니다.

### 4. Loop A/B/C 표준 정의 / Standard Loop Definition (Day 3–4)

| Loop | 물리 의미 | 읽는 포트 (from) | 쓰는 포트 (to) | 주요 함수 (gaia_loop_connector) |
|------|-----------|------------------|----------------|----------------------------------|
| A | 산불 CO₂ → 대기 CO₂ | `FireEngine.predict` 결과 (`CO2_source_kgC`, 밴드별 결과) | `AtmosphereComposition.CO2` (mol/mol) | `apply_fire_co2_loop(fire_results, dt_yr)` |
| B | 식생 알베도 → 온도 | `BiosphereColumn.step` 결과 (`delta_albedo_land`, `delta_CO2`, `delta_O2`, `delta_H2O`) | `atmosphere.albedo`, `AtmosphereComposition.(CO2,O2,H2O)` | `apply_biosphere_feedback` (`biosphere_feedback_to_atmosphere` 내부 호출) |
| C | 세차 obliquity → 계절성 (건기) | `MilankovitchCycle` / `MilankovitchDriver` (`obliquity_deg`, `insolation_scale`) | `FireEnvSnapshot` 의 건기 진폭(dry_season_modifier 계열) | `make_fire_env` / `make_fire_env_milank` |

Loop A/B/C 는 위 표를 기준으로 다른 문서들(day3/day4 README, docs/PORTS_AND_UNITS.md)과 의미를 맞춘다.

### 4-bis. Loop F/G/H 표준 정의 / Standard Loop Definition (Day 5)

Day 5 생물 이동 레이어가 추가하는 3개 피드백 루프.
**구현 모듈**: `solar/day5/mobility_engine.py`, `seed_transport.py`, `food_web.py`

| Loop | 물리 의미 | 읽는 포트 (from) | 쓰는 포트 (to) | 연결 방법 |
|------|-----------|------------------|----------------|-----------|
| **F** | 씨드 분산 → pioneer 원거리 확산 | `BirdAgent.seed_flux(B_pioneer)` → `SeedTransport.step(B, dt_yr)` | 각 위도 밴드 `pioneer += Δ` (Day3 `BiosphereColumn` 외부 주입) | `B_new = transport.step(B_pioneer, dt_yr)` 후 각 밴드 pioneer 갱신 |
| **G** | 구아노 N → 토양 질소 보강 | `BirdAgent.guano_flux()` → `[g N/m²/yr]` per band | Day4 `NitrogenCycle` 입력 또는 `N_soil[i] += guano[i] * dt_yr` | `nitro.step(..., external_N_source=guano[i])` 또는 직접 가산 |
| **H** | 포식 → phyto 감소 → CO₂ 호흡 | `FishAgent.predation_flux(phyto_by_band)` → `env["fish_predation"]` | `FoodWeb.step(state, env, dt_yr)` → `co2_resp_yr` → Day2 대기 CO₂ | `fw.step(state, env={"GPP": gpp, "fish_predation": fish_pred[i]}, dt_yr)` |

#### Loop F/G/H 연결 개요

```text
[BirdAgent]
  migration_rates(o2_by_band) ──► [SeedTransport.step(B_pioneer)]
                                        │
                                        ▼  (보존형 transport)
                                  각 밴드 pioneer += Δ  ─► Loop F 닫힘

  guano_flux() ─────────────────► N_soil[i] += guano[i] * dt_yr
                                        │
                                        ▼
                              [NitrogenCycle.N_limitation] ─► Loop G 닫힘

[FishAgent]
  predation_flux(phyto_by_band) ─► env["fish_predation"]
                                        │
                                        ▼
                               [FoodWeb.step(state, env)]
                                        │
                                  co2_resp_yr [kgC/m²/yr]
                                        │
                                        ▼
                          atmosphere.CO₂ += net_co2_flux(state, gpp) ─► Loop H 닫힘
```

#### 단위 요약 (Loop F/G/H)

| 포트 | 단위 | 비고 |
|------|------|------|
| `migration_rates()` | 1/yr | O₂ 반응형 이동률 |
| `seed_flux(B_pioneer)` | 1/yr (rate) | pioneer biomass와 같은 단위 스케일 |
| `guano_flux()` | g N/m²/yr | Day4 `NitrogenCycle` N_soil 입력과 동일 단위 |
| `predation_flux(phyto)` | 1/yr (rate) | phyto biomass 기준 포식률 |
| `co2_resp_yr` | kgC/m²/yr | 연간 환산 플럭스 (누적값 아님) |
| `net_co2_flux(state, gpp)` | kgC/m²/yr | GPP 흡수 − 호흡 합산 |

> **통합 시 주의사항**
> - Loop F: `SeedTransport.step(B)` 은 보존형. 결과를 외부에서 pioneer 에 더함. `BiosphereColumn` 내부 수정 불필요.
> - Loop G: `guano_flux()` 결과는 `NitrogenCycle.step` 의 `external_N_source` 파라미터로 주입하거나, `N_soil[i]` 에 직접 가산.
> - Loop H: `FoodWeb.step` 에 `env["fish_predation"]` 키로 주입. 없으면 0.0 으로 처리 (기본값 보장).
> - 모든 상수는 `solar/day5/_constants.py` 단일 소스. `M_CARNIVORE`, `R_PREDATION` 등 참고.

### 5. 버전 및 PHAM 서명 / Version & PHAM

- Gaia 루프 브리지 (`gaia_loop_connector.py`): Phase 8.5, Day 3–4 루프 통합.
- CookiieBrain ↔ GaiaFire 브리지 (`gaia_bridge.py`): Phase 8.0.
- BrainCore 환경 브리지 (`brain_core_bridge.py`): GEAR_CONNECTION_STRATEGY Phase 1.
- **Day 5 Loop F/G/H 연결 정의 추가**: `solar` v2.8.0 (생물 이동 레이어 통합).
- 추적 체인: `blockchain/pham_chain_LAYER8_bridges.json` (추가 예정).

*v2.8.0 · PHAM-ready · GNJz (Qquarts) + Claude*

