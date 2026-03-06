# _05_noah_flood — 노아 대홍수 이벤트

**역할**: 조(JOE)에서 올라오는 `instability`와, 궁창(Firmament)·대홍수(Flood) 엔진을
한 타임라인 위에 올려,

> 궁창 시대(antediluvian) → 붕괴(flood) → postdiluvian 지구

로 이어지는 환경 전이를 **알고리즘 시나리오**로 따라가 보는 레이어다.

---

## 1. 서사 관점 — 조→모→체루빔→EdenOS→궁창→노아

이 레이어는 단독 엔진이 아니라, 본편 테라포밍/에덴 서사 위에 얹힌
**“마지막 상전이 단계”**다.

- 1단계: `_01_beginnings/joe` — 조(JOE) 거시 탐사  
  - PANGEA §4 Aggregator 로 행성 거시 조건(`planet_stress`, `instability`)을 평가한다.
  - 붕괴하지 않을 행성만 다음 레이어로 넘긴다.
- 2단계: `_02_creation_days` — 모(MOE) 환경 구축  
  - day1~7, `fields/`, `physics/`, `engines/`, `day7/runner` 가
    6도메인(대기·수권·지질·자기권·궤도·생물권) 스냅샷을 만든다.
- 3단계: `_03_eden_os_underworld/eden` — 체루빔 + EdenOS  
  - `eden/search.py` 가 EdenCandidate / SearchResult 를 찾고,
  - `eden/eden_os/*.py` 가 CherubimGuard + EdenOSRunner 로 에덴 Basin 을 운영한다.
- 4단계: `_04_firmament_era` — 궁창 환경시대  
  - `eden/firmament.py` 의 `FirmamentLayer` 가
    에덴 궁창(고압·고습·저엔트로피) 상태를 유지한다.
- 5단계: `_05_noah_flood` — 궁창 붕괴·대홍수·postdiluvian 상전이 (현재 레이어)  
  - 위 레이어들에서 만들어진 `instability` / 환경 스냅샷을 받아,
  - 궁창 시대 → 붕괴 → 홍수 → 현재 지구(Postdiluvian) 로 넘어가는
    **시간 축 시나리오**를 담당한다.

요약하면,

> 조(JOE) → (_02_creation_days 전체) → EdenSearch/EdenOS → FirmamentEra → NoahFlood

라는 서사 흐름의 **마지막 물리 상전이 레이어**가 `_05_noah_flood`다.

---

## 2. 엔지니어링 관점 — 어떤 모듈이 어떻게 연결되는가

- `L0_solar/_03_eden_os_underworld/eden/firmament.py`  
  궁창 레이어(`FirmamentLayer`).
  - `FirmamentLayer.step(dt_yr, instability=...)`  
    - instability ≥ 0.85 이면 내부에서 자동으로 `collapse_triggered` → `_do_collapse()` → `FloodEvent` 생성.
  - `get_env_overrides()` 로 대기/수권/UV/압력/알베도/극도차를 PlanetRunner 쪽에 주입.

- `L0_solar/_03_eden_os_underworld/eden/flood.py`  
  대홍수 진행 엔진(`FloodEngine`).
  - `step(dt_yr)` → `FloodSnapshot` (f_land, albedo, T, mutation, pole_eq_delta_K, sea_level_anomaly_m 등).
  - `get_env_overrides()` 로 postdiluvian 환경으로의 전이 곡선을 PlanetRunner 에 전달.

- `L0_solar/_03_eden_os_underworld/eden/initial_conditions.py`  
  - `make_antediluvian()` / `make_postdiluvian()` — 에덴/현재 지구 기준 IC 프리셋.

- `L0_solar/_01_beginnings/joe/*`  
  - PANGEA §4 Aggregator에서 나오는 `planet_stress`, `instability` 값이
    궁창 붕괴 트리거에 쓰일 수 있다.

이 폴더 파일:

- `engine.py`
  - `run_flood_step()` / `run_trigger_flood()` — 기존 단일 스텝/트리거 래퍼.
  - `compute_effective_instability()` — JOE instability + (선택) MOE 리스크 합성기.
  - `run_noah_cycle()` — 조→궁창→홍수→postdiluvian 한 사이클을 따라가는 시뮬레이션 헬퍼.
  - `evaluate_postdiluvian()` — post-flood IC 가 지구형(postdiluvian) 타깃과
    얼마나 일치하는지 평가.
- `scenarios.py`
  - `run_scenario_macro_only()` / `run_scenario_macro_decay()` /
    `run_scenario_combined_ramp()` / `run_scenario_impulse_shock()`
    등 여러 트리거 패턴을 돌려보는 데모 러너.
- `SCENARIOS.md`
  - 위 시나리오들의 설정·실행법·해석을 정리한 문서.
- `__init__.py`
  - 위 함수들(`run_flood_step`, `run_noah_cycle`, `evaluate_postdiluvian`,
    `compute_effective_instability` 등)과 Flood/Firmament/IC 타입들을
    외부에서 한 번에 import 할 수 있도록 re-export 한다.

---

## 3. Noah 시나리오 개념 — 조·모·궁창·대홍수 상전이

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

## 4. run_noah_cycle() — 설계 철학 (시나리오 드라이버)

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

---

## 5. 시나리오·환경 셋팅 요약

구체적인 시나리오 정의와 실행 방법은 `SCENARIOS.md` 를 참고하되,
핵심 개념만 요약하면 다음과 같다.

- **입력 축**
  - `joe_instability_fn(t)` : 조(JOE)가 보는 거시 불안정도 (0~1).
  - `risk_fn(t)` : 필요 시 `{"water_cycle_risk", "magnetosphere_risk", "greenhouse_proxy"}` 를
    시간 함수로 제공 (없으면 0으로 간주).
  - `mode` : `"macro"`, `"decay"`, `"combined"` 중 하나로 합성 방식 선택.

- **대표 시나리오 네 가지**
  - A. `macro_only` — 거시 물리만 서서히 올림 (조 신호만으로 붕괴가 가능한지).
  - B. `macro_decay` — 낮은 instability + decay 모드(장기 안정/붕괴 여부 체크).
  - C. `combined_ramp` — 조 + 수순환 + 온실 + 자기권 리스크를 함께 램프업.
  - D. `impulse_shock` — 평소 안정 상태에서 짧은 강한 외부 임펄스로 임계선 돌파.

- **실행 예**

  ```bash
  python -m solar._05_noah_flood.scenarios
  ```

이렇게 해서 본편 서사에서 축적된 상태가 정말로 “노아급 대홍수 상전이”를 통해
지금의 지구형 환경으로 이어질 수 있는지를 여러 입력 시나리오로 실험·비교할 수 있다.

