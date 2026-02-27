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

### 3. Creation Days와의 관계 / Relation to Day1–Day4

- **입력 레이어**
  - Day 1: `SolarLuminosity` (복사 조도, 평형 온도)  
  - Day 2: `AtmosphereColumn` (T, P, water_phase, habitable)  
  - Day 3: `SurfaceSchema`, `BiosphereColumn`, `FireEngine`  
  - Day 4: `EvolutionEngine`, `NitrogenCycle`, `MilankovitchCycle`, `gravity_tides` (간접적으로 사용)

- **출력 레이어**
  - BrainCore / CookiieBrain: `solar_environment` extension, NeuronEvent, CognitiveBrainSnapshot  
  - Gaia Layer: Loop A/B/C 가 닫힌 항상성 상태 (`LoopState`, PlanetStressIndex)

브리지들은 **엔진의 내부 물리를 수정하지 않고**,  
항상 **입력/출력 데이터 변환만 담당**하도록 설계되어 있습니다.

### 4. 버전 및 PHAM 서명 / Version & PHAM

- Gaia 루프 브리지 (`gaia_loop_connector.py`): Phase 8.5, Day 3–4 루프 통합.  
- CookiieBrain ↔ GaiaFire 브리지 (`gaia_bridge.py`): Phase 8.0.  
- BrainCore 환경 브리지 (`brain_core_bridge.py`): GEAR_CONNECTION_STRATEGY Phase 1.  
- 추적 체인: `blockchain/pham_chain_LAYER8_bridges.json` (추가 예정).

*v2.x · PHAM-ready · GNJz (Qquarts) + Claude 5.1*

