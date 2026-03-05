# _05_noah_flood — 노아 대홍수 이벤트

**역할**: 조(JOE)에서 올라오는 `instability`와, 궁창(Firmament)·대홍수(Flood) 엔진을
한 타임라인 위에 올려,

> 궁창 시대(antediluvian) → 붕괴(flood) → postdiluvian 지구

로 이어지는 환경 전이를 **알고리즘 시나리오**로 따라가 보는 레이어다.

---

## 관련 구현 파일

- `solar/_03_eden_os_underworld/eden/firmament.py`  
  궁창 레이어(`FirmamentLayer`).
  - `FirmamentLayer.step(dt_yr, instability=...)`  
    - instability ≥ 0.85 이면 내부에서 자동으로 `collapse_triggered` → `_do_collapse()` → `FloodEvent` 생성.
  - `get_env_overrides()` 로 대기/수권/UV/압력/알베도/극도차를 PlanetRunner 쪽에 주입.

- `solar/_03_eden_os_underworld/eden/flood.py`  
  대홍수 진행 엔진(`FloodEngine`).
  - `step(dt_yr)` → `FloodSnapshot` (f_land, albedo, T, mutation, pole_eq_delta_K, sea_level_anomaly_m 등).
  - `get_env_overrides()` 로 postdiluvian 환경으로의 전이 곡선을 PlanetRunner 에 전달.

- `solar/_03_eden_os_underworld/eden/initial_conditions.py`  
  - `make_antediluvian()` / `make_postdiluvian()` — 에덴/현재 지구 기준 IC 프리셋.

- `solar/_01_beginnings/joe/*`  
  - PANGEA §4 Aggregator에서 나오는 `planet_stress`, `instability` 값이
    궁창 붕괴 트리거에 쓰일 수 있다.

이 폴더 파일:

- `engine.py`
  - `run_flood_step()` / `run_trigger_flood()` — 기존 단일 스텝/트리거 래퍼.
  - `compute_effective_instability()` — JOE instability + (선택) MOE 리스크 합성기.
  - `run_noah_cycle()` — 조→궁창→홍수→postdiluvian 한 사이클을 따라가는 시뮬레이션 헬퍼.
- `scenarios.py`
  - `run_scenario_macro_only()` / `run_scenario_macro_decay()` /
    `run_scenario_combined_ramp()` / `run_scenario_impulse_shock()`
    등 여러 트리거 패턴을 돌려보는 데모 러너.
- `SCENARIOS.md`
  - 위 시나리오들의 설정·실행법·해석을 정리한 문서.
- `__init__.py` — re-export

---

## Noah 시나리오 개념

조(JOE) → 모(MOE) → 체루빔 → EdenOS 위에, 다음 한 줄을 추가로 얹는다.

```text
JOE(instability) → FirmamentLayer → FloodEngine → postdiluvian InitialConditions
```

- **JOE(instability)**  
  - PANGEA §4 Aggregator 수식:
    - `instability_raw = b1·planet_stress + b2·(W_surface/W_total) + b3·dW_surface_dt_norm`
  - 여기서 나온 `instability` [0~1] 은
    궁창이 얼마나 버티기 힘든지에 대한 거시 지표로 쓴다.

- **FirmamentLayer**  
  - Instability가 낮으면 에덴 궁창 시대를 유지:
    - H2O_canopy ≈ 5%, pressure_atm ≈ 1.25, UV_shield ≈ 0.95, f_land ≈ 0.40.
  - Instability가 임계값(기본 0.85)을 넘는 방향으로 누적되면
    `collapse_triggered=True` → `FloodEvent`:
    - `sea_level_rise_m ≈ 80m + α·H2O_released`
    - `f_land: 0.40 → 0.10 → 0.29`
    - `albedo: 0.20 → 0.10 → 0.306`
    - `mutation_factor: 0.01 → 1.0`

- **FloodEngine**  
  - rising / peak / receding / stabilizing / complete 5단계 전이 곡선으로
    위 파라미터들을 시간에 따라 변화시킨다.

- **postdiluvian InitialConditions**  
  - FloodEngine 이 complete 상태에 도달하면,
    `make_postdiluvian()` 이 제공하는 현재 지구 근방 IC와 정합되는 상태:
    - `f_land ≈ 0.29`, `albedo ≈ 0.306`, `pressure_atm ≈ 1.0`,
    - `H2O_canopy ≈ 0`, `UV_shield ≈ 0`, `mutation_factor ≈ 1.0`.

---

## run_noah_cycle() — 설계 철학

`run_noah_cycle()` 은 **"실제 물리 엔진을 대체"하는 것이 아니라**,
이미 있는 조/모/궁창/홍수/IC 엔진들이 올바른 순서로 이어질 수 있는지를
검증하는 **시나리오 드라이버**다.

개략 흐름:

1. 시간 t마다 `joe_instability_fn(t)` 으로 JOE instability를 샘플링한다.
2. 선택적으로 `risk_fn(t)` 으로 water_cycle_risk, magnetosphere_risk, greenhouse_proxy 를 얻는다.
3. `compute_effective_instability(...)` 로 합성해서 FirmamentLayer.step(..., instability=...) 에 넣는다.
4. FirmamentLayer 가 붕괴되면 FloodEngine 을 생성해, 홍수 전이 곡선을 따라간다.
5. FloodEngine 이 complete 상태에 도달하면 `make_postdiluvian()` 으로
   postdiluvian InitialConditions 를 만들어 NoahSimulationResult.post_ic 에 담는다.

이 결과를 바탕으로:

- post-flood IC 가 실제 `make_postdiluvian()` 값과 어느 정도 일치하는지,
- EdenSearch/EdenOS 가 여전히 안정적인 에덴/아크 후보를 찾을 수 있는지,

등을 실험해 볼 수 있다.

