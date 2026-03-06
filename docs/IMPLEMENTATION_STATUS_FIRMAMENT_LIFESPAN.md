# 궁창·수명·붕괴 동역학 — 구현 상태 및 개념 매핑

**목적**: “어디에 무엇이 어떻게 구현되어 있는지”를 개념 단위로 정확히 기술한다.

---

## 1. 개념 → 구현 위치 요약표

| 개념 | 구현 위치 | 설명 |
|------|-----------|------|
| **에너지 총량 E_cap, 비용 C(t)** | `docs/LIFESPAN_ENERGY_BUDGET_CONCEPT.md`, `docs/ENERGY_ENTROPY_FIRMAMENT_SYSTEM.md` | 문서 수식. 코드에서는 `lifespan_budget`이 **기대 수명 T**로 요약해 사용. |
| **S(t) 보호막, L_env 환경 부하** | `solar/eden/firmament.py` (H2O_canopy → UV·알베도·압력), `Layer0Snapshot` | S(t)=shield_strength, env_load=L_env. `get_layer0_snapshot()`으로 노출. |
| **궁창 전 900년 vs 120년** | `solar/eden/eden_os/lifespan_budget.py` | `expected_lifespan_yr(S=1, group="admin_line"|"general", generation)` → 900 / 120. |
| **궁창 후 20~40년, 600→175년** | 같은 파일 | S=0, group/generation에 따라 30년 또는 600×(175/600)^(gen/10). |
| **환경이 integrity 감쇠에 반영** | `solar/eden/eden_os/homeostasis_engine.py` | world.layer["SCENARIO"]의 `shield_strength`, `env_load`, `lifespan_group`, `lifespan_generation` → `expected_lifespan_yr` → `env_decay_per_tick` → `_accumulated_env_stress` 누적 → stress_index에 가산. |
| **지상 월드에 S(t)·env_load 주입** | `solar/eden/eden_os/eden_world.py` | `make_eden_world(ic, scenario_overlay=...)`. overlay에 `shield_strength`, `env_load`, `lifespan_group`, `lifespan_generation` 넣으면 Homeostasis가 읽음. |
| **UnderWorld가 S(t) 감지해 경고** | `solar/underworld/deep_monitor.py`, `hades.py`, `rules.py` | `read_deep_snapshot(..., layer0_snapshot=...)` → DeepSnapshot에 `shield_strength`, `env_load` 채움. `firmament_ok` 룰: S<0.5이면 ENTROPY_WARNING "궁창/보호막 약화". |
| **궁창 붕괴 = 동역학(instability)** | `solar/eden/firmament.py` | `step(dt_yr, instability=...)`. instability ≥ 0.85이면 `collapse_triggered=True` → `_do_collapse()`. 수동은 `trigger_flood()`. |
| **이중 서사(대홍수 vs 라그나로크)** | `docs/FIRMAMENT_COLLAPSE_DYNAMICS.md` | 개념만 문서화. 코드상 FloodEvent는 하나; LORE에서 관찰자 타입별 메시지 분기는 **미구현**. |
| **동시성 epoch(아담~노아)** | `docs/FIRMAMENT_COLLAPSE_DYNAMICS.md` | 개념만 문서화. Runner에서 여러 admin_line 에이전트 동시 상주·instability 공급은 **미구현**. |

---

## 2. 파일별 역할 (구체)

### 2.1 `solar/eden/eden_os/lifespan_budget.py`

- **의미**: C(t), S(t), L_env, group, generation을 받아 **기대 수명(년)** 과 **틱당 env 감쇠량**을 내는 **수식 레이어**.
- **구현 내용**:
  - `expected_lifespan_yr(shield_strength, env_load, group, generation)`  
    S≈1 → admin 900 / general 120; S≈0 → general 30 / admin 600→…→175(gen에 따라).
  - `env_decay_per_tick(expected_lifespan_yr, ticks_per_year, theta2)`  
    integrity가 theta2 이하가 되는 “수명”에 맞춰 틱당 누적할 env_stress 증분 반환.
  - `compute_lifespan_budget(...)` → `LifespanBudgetResult` (한 번에 결과).
- **호출처**: `homeostasis_engine.py` (update() 안에서 S, L_env, group, gen 읽고 위 함수 호출).

### 2.2 `solar/eden/eden_os/homeostasis_engine.py`

- **의미**: 매 틱 **stress_index·integrity** 계산. 궁창/수명 동역학을 **integrity 감쇠**로 반영.
- **구현 내용**:
  - `update(tick, world, hades_signal, stress_injection)`.
  - **world**에서 `layer["SCENARIO"]` 또는 속성으로 `shield_strength`, `env_load`, `lifespan_group`, `lifespan_generation` 읽음.
  - 있으면: `expected_lifespan_yr(S, L_env, group, gen)` → `env_decay_per_tick(...)` → `_accumulated_env_stress`에 가산 (S<1일 때만).
  - `stress_index = base_stress*0.7 + hades_severity*0.3 + stress_injection + env_stress`, `integrity = 1 - stress_index`.
  - 스냅샷에 `env_stress`, `expected_lifespan_yr` 포함.
- **개념**: “궁창이 없어지면 유지비(C_env)가 올라가서 수명이 줄어든다” → **env_stress 누적**으로 integrity가 줄어들어 FSM 전이(다운그레이드)로 이어짐.

### 2.3 `solar/eden/eden_os/eden_world.py`

- **의미**: EdenWorldEnv(환경 스냅샷) 생성 시 **SCENARIO에 궁창/수명용 키**를 넣을 수 있게 함.
- **구현 내용**:
  - `_build_layer(ic, bands, eden_index, scenario_overlay=None)`.  
    `scenario_overlay`가 있으면 SCENARIO dict에 merge.
  - `make_eden_world(ic=None, scenario_overlay=None)`.  
    overlay 예: `{"shield_strength": 1.0, "env_load": 0.0, "lifespan_group": "admin_line", "lifespan_generation": 0}`.
- **연결**: Runner나 통합 레이어가 **FirmamentLayer 상태**를 보고 overlay를 채워 `make_eden_world(..., scenario_overlay=...)` 하면, 그 world를 쓰는 Homeostasis가 S(t)·group·gen을 읽어 수명/감쇠를 적용함.

### 2.4 `solar/eden/firmament.py`

- **의미**: 궁창 물리 상태(H2O_canopy, UV, 알베도, 압력 등) + **붕괴 조건(수동/동역학)**.
- **구현 내용**:
  - `FirmamentState`: phase, H2O_canopy, active, collapse_triggered, years_elapsed, uv_shield_factor, pressure_atm 등.
  - `FirmamentLayer.step(dt_yr, instability=None)`:  
    `instability`가 주어지고 **≥ _INSTABILITY_COLLAPSE_THRESHOLD(0.85)** 이면 `collapse_triggered=True` → 같은 step에서 `_do_collapse()` 호출.  
    즉 **동역학 붕괴**: 외부에서 planet_stress 등을 instability로 넘기면 “버튼 없이” 붕괴.
  - `trigger_flood()`: 수동 붕괴.
  - `get_env_overrides()`: PlanetRunner/대기 레이어에 넣을 dict (H2O, albedo, UV, pressure 등).
  - `get_layer0_snapshot()`: `Layer0Snapshot(shield_strength=S, env_load=L_env)`.  
    S = H2O_canopy/0.05 (활성 시), 0 (붕괴 후). L_env = 0 (활성) / 1 (붕괴 후).
  - `Layer0Snapshot`: 덕 타이핑용. `shield_strength`, `env_load` 속성만 있으면 됨.
- **개념**: “궁창 = 보호막 S(t)”. 붕괴 시 S→0, L_env↑ → 수명/항상성 쪽 공식과 일치.

### 2.5 `solar/underworld/deep_monitor.py`

- **의미**: 물리 코어 + **Layer0(궁창) 스냅샷**을 합쳐 **DeepSnapshot** 한 장 만듦.
- **구현 내용**:
  - `DeepSnapshot`: tick, core_available, magnetic_ok, thermal_ok, gravity_ok, **shield_strength**, **env_load**, extra.
  - `read_deep_snapshot(tick, engine, layer0_snapshot=None)`.  
    `layer0_snapshot`에 `shield_strength`/`env_load`가 있으면 DeepSnapshot에 채움 (덕 타이핑).
- **연결**: Runner가 `fl.get_layer0_snapshot()`을 넘기면, Hades가 쓰는 DeepSnapshot에 S(t), env_load가 들어가 룰 평가에 사용됨.

### 2.6 `solar/underworld/hades.py`

- **의미**: 지하 감시자. **목소리(ConsciousnessSignal)** 만 내보냄. 행동/전이는 하지 않음.
- **구현 내용**:
  - `listen(tick, world_snapshot=None, deep_engine=None, layer0_snapshot=None)`.
  - `read_deep_snapshot(tick, engine, layer0_snapshot)` 호출 → `evaluate_rules_all(deep, world_snapshot)` → 위반 시 신호 리스트 반환.
- **연결**: Runner가 `layer0_snapshot=fl.get_layer0_snapshot()`으로 호출하면, 궁창 상태가 룰에 반영됨.

### 2.7 `solar/underworld/rules.py`

- **의미**: DeepSnapshot 기준 **거시 룰** 정의. 위반 시 severity·signal_type·message.
- **구현 내용**:
  - `DEFAULT_RULES`에 `firmament_ok` 룰:  
    `_ok_from_snapshot(snap, "firmament_ok")` → snap.shield_strength가 없으면 True(미제공), 있으면 **S ≥ 0.5**이면 True.  
    S < 0.5면 위반 → ENTROPY_WARNING, "거시 룰: 궁창/보호막 약화 (S 하락)".
  - magnetic_ok, thermal_ok, gravity_ok 룰도 동일 방식.
- **개념**: “S 하락 = 궁창 약화”를 **측정만** 하고, 경고로만 전달. 전이/붕괴는 FirmamentLayer·Homeostasis 쪽에서 처리.

### 2.8 `solar/eden/eden_os/lifespan_flood_sim.py`

- **의미**: 궁창 전/후·두 그룹 수명이 **수식대로 나오는지** 검증하는 스크립트.
- **구현 내용**:
  - `MockWorld`: layer["SCENARIO"]에 shield_strength, env_load, lifespan_group, lifespan_generation 설정.
  - Pre-flood(S=1), post-flood(S=0) 각각 world를 만들고 HomeostasisEngine.update()를 반복.
  - 기대 수명 숫자 검증 + “integrity < θ2 도달 연수”가 목표 범위(일반 ~30, admin gen10 ~175)에 들어오는지 확인.
- **실행**: `python -m solar.eden.eden_os.lifespan_flood_sim`.

---

## 3. 데이터 흐름 (누가 무엇을 읽고 누가 쓴다)

```
[FirmamentLayer]
  get_env_overrides()     → PlanetRunner/대기 (H2O, UV, albedo, pressure 등)
  get_layer0_snapshot()   → shield_strength, env_load

[Runner 또는 통합 레이어]
  1) world = make_eden_world(ic, scenario_overlay={
       "shield_strength": fl.get_layer0_snapshot().shield_strength,
       "env_load": ...,
       "lifespan_group": "admin_line" | "general",
       "lifespan_generation": 0..10
     })  ← 선택. overlay 없으면 Homeostasis는 env_stress 누적 안 함.
  2) hades.listen(tick, world_snapshot=world, layer0_snapshot=fl.get_layer0_snapshot())
     → DeepSnapshot에 S, env_load 채워짐 → firmament_ok 룰 평가 → 경고 리스트
  3) homeostasis.update(tick, world, hades_signal, stress_injection)
     → world.layer["SCENARIO"]에서 S, env_load, group, gen 읽음
     → expected_lifespan_yr → env_decay_per_tick → _accumulated_env_stress 누적
     → stress_index, integrity 계산
  4) fl.step(dt_yr, instability=planet_stress 또는 f(planet_stress, ...))
     → instability ≥ 0.85 이면 collapse_triggered → _do_collapse() → FloodEvent
```

---

## 4. 아직 본편에 “연결”되지 않은 부분

- **EdenOSRunner** (eden_os_runner.py):  
  현재 **FirmamentLayer**를 갖고 있지 않음.  
  `_world`는 `make_eden_world()` 한 번만 호출; `scenario_overlay`에 S(t)·env_load·lifespan_group/gen을 넣어서 갱신하는 로직 없음.  
  `hades.listen(..., layer0_snapshot=...)` 호출도 없음.  
  → “궁창·수명 동역학”을 **쓰려면** Runner가 FirmamentLayer를 보유하고, 매 틱 world의 SCENARIO를 overlay로 갱신하거나, 별도 통합 레이어에서 위 1~4를 수행해야 함.
- **instability 공급**:  
  `FirmamentLayer.step(instability=...)`에 넘길 값은 **Runner/통합이 계산**해야 함.  
  day7 Runner의 `planet_stress`나 gaia_engine의 `planet_stress_ema`를 그대로 쓰거나, `min(1, planet_stress + α*population_pressure)` 같은 식으로 조합하면 됨.  
  현재 **EdenOSRunner는 fl.step()을 호출하지 않음**.
- **이중 서사(대홍수 vs 라그나로크)**:  
  FloodEvent 발생 시 관찰자 타입에 따라 메시지를 바꾸는 코드는 없음. 문서만 있음.
- **동시성 epoch(아담~노아 여러 관리자 동시 상주)**:  
  Lineage/에이전트가 “동시에 N명” 있는 구조와, 그 N명이 planet_stress/instability에 기여하는 공식은 문서로만 정의되어 있고, Runner/인구 모듈에 미구현.

---

## 5. 문서 정리

| 문서 | 역할 |
|------|------|
| `docs/LIFESPAN_ENERGY_BUDGET_CONCEPT.md` | E_cap, C(t), M/R/L, 레이어 배치, 지상 동역학 접점. 동역학 수식 확정판 링크. |
| `docs/ENERGY_ENTROPY_FIRMAMENT_SYSTEM.md` | E_cap, C(t), S(t), L_env, 3구간, 수렴 조건, 다음 작업(엔진). |
| `docs/FIRMAMENT_FLOOD_BUILDUP.md` | 타임라인, 엔진 연결 표, Layer0→Hades 연결 방법. |
| `docs/FIRMAMENT_COLLAPSE_DYNAMICS.md` | 동시성 epoch, instability→붕괴, 이중 서사, 본편 연결 방법. |

---

**요약**:  
수명·궁창(S/L_env)·integrity 감쇠·붕괴(instability)·UnderWorld 경고까지 **개념별로 해당 위치에 구현**되어 있고, **EdenOSRunner**가 FirmamentLayer 보유, 매 틱 instability(JOE) 계산, scenario_overlay 갱신, hades.listen(layer0_snapshot), fl.step(instability) **연결 완료**.  
이중 서사/동시성 epoch은 문서만 있고 코드 미구현.

---

## 6. 냉정한 상태 요약 (피드백 반영)

| 구분 | 상태 |
|------|------|
| **설계·문서** | 개념 → 코드 매핑 논리적으로 정렬. 물리 → 시나리오 → 항상성 → FSM 계층 충돌 없음. **설계 약 70%.** |
| **모듈 단위** | S(t), env_load, expected_lifespan, env_decay_per_tick, integrity 감쇠, UnderWorld S(t) 감지, FirmamentLayer.step(instability≥threshold) **구현 완료.** |
| **본편 통합** | Runner가 FirmamentLayer 보유, 매 틱 scenario_overlay 갱신, hades layer0_snapshot 전달, fl.step(instability) 호출, instability=JOE 계산값. **통합 완료.** |

**“왜 S가 무너졌는가?”**  
- **완성된 것**: “S가 존재하고, S가 무너지면 env_load 증가 → integrity 감쇠가 빨라진다”까지.  
- **미완성**: **instability를 계산하는 실제 함수가 없음.**  
  `FirmamentLayer.step(instability=x)`의 **x**를 누가 어떻게 만드는지가 비어 있으므로, 붕괴는 현재도 **외부 입력**에 의존한다.

**개념–코드 격차**:  
이중 서사, 동시성 epoch, 네피림 등은 문서에만 있고 코드는 미구현. **instability 계산**은 JOE/planet_layer에서 구현 완료.

---

## 7. 다음 단계: instability 계산 함수

**지금 단계에서 해야 할 일**: **instability를 계산하는 실제 함수 설계·연결.**

**후보 형태** (FIRMAMENT_COLLAPSE_DYNAMICS.md §7과 동일):

```text
instability = a * planet_stress
            + b * population_pressure   # 동시성 epoch 구현 시
            + c * water_vapor_mass       # 선택
```

- **최소**: `instability = planet_stress` 로 Runner에서 `fl.step(dt_yr, instability=planet_stress)` 호출부터 연결.
- **확장**: population_pressure, water_vapor_mass 추가는 **population 동역학·동시성 epoch** 구현 후.

**결정 필요**:  
- **A)** planet_stress 기반 **단일 변수 instability**부터 Runner에 연결해 “붕괴 = 동역학” 완성,  
- **B)** **population 동역학**을 먼저 넣고 그다음 instability 공식에 반영.  

권장: **A → B** 순서로 단계를 나누면 구현 위험을 줄일 수 있다.

---

## 8. 수명 곡선: 수식 vs 테이블

`lifespan_budget.py`의 **세대(generation) 감쇠**는 **수학식**이다.  
- 궁창 후 아담 계열: `lifespan_post(gen) = 600 * (175/600)^(gen/10)` (gen=0 노아, gen=10 아브라함 근사).  
- 상수(900, 120, 30, 600, 175, 10)만 모듈 상단에 있고, 곡선 자체는 하드코딩 테이블이 아니다.
