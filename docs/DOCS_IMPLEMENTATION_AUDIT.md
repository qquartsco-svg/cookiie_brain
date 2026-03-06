# 문서 ↔ 구현 감사 (전체 확인)

**목적**: 오늘 논의된 레이어·엔진 개념이 문서만 있는지, 실제 코드로 구현되어 있는지 전부 재확인.

**기준일**: 2026-02-27 기준 코드·문서 상태.

---

## 0. 조(JOE) 엔진 — 쿠키브레인 내 구현 위치 (천지창조 로직)

조 엔진은 **solar 폴더** 안에서 아래처럼 구현·호출된다.

| 구분 | 경로 | 내용 |
|------|------|------|
| **구현** | `solar/planet_dynamics/__init__.py` | 조 엔진 로직. `_compute_from_snapshot_local()`(PANGEA §4), `compute_planet_stress_and_instability_from_snapshot(snapshot)`, `compute_planet_stress_and_instability(ic, water_snapshot)`. L0/L1(ic) 또는 스냅샷 dict → (planet_stress, instability). |
| **호출** | `solar/eden/eden_os/eden_os_runner.py` | 천지창조 러너가 매 틱 `_compute_instability()`에서 `compute_planet_stress_and_instability(self._world.ic, water_snapshot=None)` 호출 → **instability**만 궁창에 전달. (104행 import, 243–254행 `_compute_instability`, 299–300행에서 사용.) |
| **사용** | `solar/eden/firmament.py` | `FirmamentLayer.step(dt_yr, instability=...)`. 전달받은 instability ≥ 0.85 이면 붕괴( collapse_triggered ). |

**흐름**: L0/L1(`initial_conditions`) → **L2 조 엔진**(`planet_dynamics`) → `EdenOSRunner._compute_instability()` → **L3 궁창** `firmament.step(instability)` → `get_layer0_snapshot()` → `scenario_overlay` → `make_eden_world()`.

**독립 엔진**: `00_BRAIN/ENGINE_HUB/00_PLANET_LAYER/Joe_Engine`. 쿠키브레인 런타임은 **solar/planet_dynamics** 로컬 구현만 사용.

---

## 1. FOLDER_AND_LAYER_MAP.md (§8, §9, §10)

| 문서 개념 | 구현 여부 | 코드 위치 | 비고 |
|-----------|-----------|-----------|------|
| **L0/L1 슬롯 (Macro)** | ✅ | `solar/eden/initial_conditions.py` | `InitialConditions`: omega_spin_rad_s, obliquity_deg, GEL_surface_eden_m, W_canopy_ref_km3 |
| **L2 JOE (거시 관측)** | ✅ | `solar/planet_dynamics/__init__.py` | PANGEA §4 로컬 구현. 독립 엔진: 00_BRAIN/ENGINE_HUB/00_PLANET_LAYER/Joe_Engine. |
| **L3 궁창 (Firmament)** | ✅ | `solar/eden/firmament.py` | `FirmamentLayer.step(dt_yr, instability=...)`, `get_layer0_snapshot()`, instability ≥ 0.85 → 붕괴 |
| **통합 Runner** | ✅ | `solar/eden/eden_os/eden_os_runner.py` | 매 틱: _compute_instability() → firmament.step(instability) → scenario_overlay → make_eden_world(scenario_overlay) → hades.listen(..., layer0_snapshot) |
| **MOE (Eden Finder/체루빔)** | ✅ | `solar/eden/search.py`, `solar/eden/eden_os/cherubim_guard.py` | search: EdenCriteria, EdenCandidate 랭킹. cherubim_guard: 접근 제어 (Step 4) |
| **루시퍼(내부 코어)** | ⚠️ 부분 | `solar/underworld/deep_monitor.py`, `solar/day4/core/` | deep_monitor: read_deep_snapshot(engine, layer0_snapshot). day4/core: EvolutionEngine 등. "루시퍼" 이름은 문서 전용. |
| **하데스 (룰 평가)** | ✅ | `solar/underworld/hades.py`, `solar/underworld/rules.py` | listen(tick, world_snapshot, deep_engine, layer0_snapshot) → evaluate_rules_all → ConsciousnessSignal |
| **UnderWorld / Siren** | ✅ | `solar/underworld/` (wave_bus, siren, consciousness) | hades → ConsciousnessSignal. (선택) wave_bus.propagate → siren.broadcast. Runner는 hades_signal만 직접 사용. |
| **ENGINE_HUB 00_PLANET_LAYER** | ✅ 독립 | **00_BRAIN/ENGINE_HUB/00_PLANET_LAYER/Joe_Engine**. ENGINE_HUB는 CookiieBrain 안에 두지 않음. |

---

## 2. PLANET_DYNAMICS_ENGINE.md

| 문서 개념 | 구현 여부 | 코드 위치 |
|-----------|-----------|-----------|
| JOE = Joe Observer Engine | ✅ | `solar/planet_dynamics/`, 독립 엔진: `00_BRAIN/ENGINE_HUB/00_PLANET_LAYER/Joe_Engine/` |
| observe → analyze → detect | ✅ | compute_planet_stress_and_instability_from_snapshot → normalize/saturate. detect는 firmament.step(instability≥θ). |
| 스냅샷 계약 (L0/L1 키) | ✅ | planet_dynamics에서 ic → snapshot 변환. 독립 엔진은 dict만 입력. |
| 독립 엔진 배치 | ✅ | 00_BRAIN/ENGINE_HUB/00_PLANET_LAYER/Joe_Engine. CookiieBrain 안에 ENGINE_HUB 두지 않음. |
| 7단계 레이어 스택 (L1~L7) | ⚠️ 문서 정리 | 런타임 순서·폴더 매핑은 문서. 코드는 JOE/궁창/하데스/UnderWorld 등 개별 구현됨. |

---

## 3. PANGEA_ROTATION_AND_WATER_BUDGET.md

| 문서 개념 | 구현 여부 | 코드 위치 |
|-----------|-----------|-----------|
| L0 Geometry & Rotation | ✅ | `initial_conditions.py`: omega_spin_rad_s, obliquity_deg |
| L1 Water Budget | ✅ | InitialConditions: GEL_surface_eden_m, W_canopy_ref_km3. 스냅샷에 W_surface, W_total 등 확장 가능. |
| L2 planet_stress, instability | ✅ | PANGEA §4: `solar/planet_dynamics/__init__.py` 로컬 구현. 독립 엔진: 00_BRAIN/ENGINE_HUB/00_PLANET_LAYER/Joe_Engine. |
| L3 Firmament & Flood | ✅ | `solar/eden/firmament.py`: step(instability), trigger_flood(), FloodEvent |
| H2O_canopy_frac 매핑 | ✅ | firmament: H2O_canopy, get_layer0_snapshot(). L1→L3 규약은 initial_conditions·firmament 주석/문서. |

---

## 4. FIRMAMENT_COLLAPSE_DYNAMICS.md

| 문서 개념 | 구현 여부 | 코드 위치 |
|-----------|-----------|-----------|
| instability ≥ θ → 붕괴 | ✅ | `firmament.py`: _INSTABILITY_COLLAPSE_THRESHOLD=0.85, step(instability=...) |
| planet_stress → instability | ✅ | planet_dynamics / 00_BRAIN/ENGINE_HUB/00_PLANET_LAYER/Joe_Engine 에서 PANGEA §4. |
| 이중 서사 (대홍수 vs 라그나로크) | ❌ | 문서만. FloodEvent는 하나; 관찰자 타입별 메시지 분기 미구현. |
| 동시성 epoch (N명 관리자) | ❌ | 문서만. Lineage는 1명 관리자; N명·population_pressure 미구현. |

---

## 5. LIFESPAN_ENERGY_BUDGET_CONCEPT.md

| 문서 개념 | 구현 여부 | 코드 위치 |
|-----------|-----------|-----------|
| S(t), L_env, 기대 수명 | ✅ | `solar/eden/eden_os/lifespan_budget.py`: expected_lifespan_yr(S, env_load, group, generation) |
| env_stress → integrity 감쇠 | ✅ | `solar/eden/eden_os/homeostasis_engine.py`: SCENARIO에서 S, env_load 읽고 env_decay_per_tick 누적 |
| 궁창 전 900/120년, 후 30/600→175년 | ✅ | lifespan_budget.py 상수 및 수식 |

---

## 6. IMPLEMENTATION_STATUS_FIRMAMENT_LIFESPAN.md

| 문서 기술 (§4·§6) | 실제 코드 상태 | 수정 필요 |
|-------------------|----------------|-----------|
| "EdenOSRunner가 FirmamentLayer 미보유" | ❌ **거짓** | Runner는 _firmament 보유, make_eden_os_runner()에서 생성·주입. |
| "scenario_overlay 갱신 없음" | ❌ **거짓** | 매 틱 layer0 = fl.get_layer0_snapshot(), scenario_overlay 갱신 후 make_eden_world(ic, scenario_overlay). |
| "hades.listen(..., layer0_snapshot=...) 호출 없음" | ❌ **거짓** | _execute_tick()에서 hades.listen(self._tick, self._world, layer0_snapshot=layer0) 호출함. |
| "fl.step(instability) 미호출" | ❌ **거짓** | 매 틱 _compute_instability() → self._firmament.step(dt_yr=1.0, instability=instability). |
| "instability 계산 함수 없음" | ❌ **거짓** | solar/planet_dynamics 로컬 PANGEA §4. 독립 엔진: 00_BRAIN/ENGINE_HUB/00_PLANET_LAYER/Joe_Engine. |

→ **IMPLEMENTATION_STATUS_FIRMAMENT_LIFESPAN.md §4·§6·§7은 최신 코드 기준으로 수정 필요.**

---

## 7. UNDERWORLD_EXTENSIBILITY.md / UNDERWORLD 레이어

| 문서 개념 | 구현 여부 | 코드 위치 |
|-----------|-----------|-----------|
| Hades ONLY measures | ✅ | hades.py: listen() → ConsciousnessSignal만 반환. 행동/전이 없음. |
| rules.py 룰 정의 | ✅ | RuleSpec, DEFAULT_RULES, evaluate_rules_all, firmament_ok (S≥0.5) |
| deep_monitor + layer0 | ✅ | read_deep_snapshot(..., layer0_snapshot) → DeepSnapshot에 shield_strength, env_load 채움 |
| WaveBus / Siren | ✅ | wave_bus.propagate(), siren.broadcast(). Runner에서는 선택 경로로 미연결(직접 hades_signal 사용). |

---

## 8. 기타 핵심 문서 (요약)

| 문서 | 구현 요약 |
|------|-----------|
| FEYNMAN_VOL1_AS_PLANET_MOTION.md | 조/모 = Macro/Micro → L0/L1 vs L2/L3, JOE/MOE 예약. 코드는 planet_dynamics(JOE), search+cherubim(MOE)로 대응. |
| NOAH_ARC_SCALING.md | 규빗·방주 스케일. 수식·개념. 코드에서 직접 사용하는 모듈은 없음(시나리오/콘텐츠 레벨). |
| EDEN_SEARCH_STANDALONE_ENGINE.md | 에덴 탐색 독립 엔진화 가능성. search.py + IC + magnetic_protection_factor로 독립 가능하다고 문서화. 구현은 search.py 존재. |

---

## 9. 결론 요약

| 구분 | 상태 |
|------|------|
| **레이어 L0~L3 (조/모, JOE, 궁창)** | ✅ 구현됨. Runner에서 매 틱 연결됨. |
| **instability 계산** | ✅ planet_dynamics 로컬 PANGEA §4. Runner가 사용. |
| **UnderWorld (Hades, rules, deep_monitor)** | ✅ 구현됨. Runner가 hades.listen(layer0_snapshot) 호출. |
| **수명/항상성 (S, env_load, integrity)** | ✅ lifespan_budget, homeostasis_engine, eden_world scenario_overlay 연결됨. |
| **독립 엔진 (조/JOE)** | ✅ 00_BRAIN/ENGINE_HUB/00_PLANET_LAYER/Joe_Engine. ENGINE_HUB는 CookiieBrain 밖. |
| **이중 서사 / 동시성 epoch** | ❌ 문서만. 코드 미구현. |
| **문서와 불일치** | IMPLEMENTATION_STATUS_FIRMAMENT_LIFESPAN.md §4 — "아직 본편에 연결되지 않은 부분"은 **과거 기술**임. 실제로는 Runner 연결 완료. 본 감사 §6 및 해당 문서 §5 요약·§6 표 참고. |

전체적으로 **오늘 다룬 레이어·엔진 개념은 대부분 코드로 구현되어 있음.** 문서만 있는 부분은 이중 서사, 동시성 epoch 두 가지이며, IMPLEMENTATION_STATUS 문서는 Runner/instability 관련 내용을 최신 코드에 맞게 고쳐야 함.
