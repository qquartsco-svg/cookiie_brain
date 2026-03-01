# solar/ 폴더 전체 확인 (에덴 탐색기 완성 기준)

**확인일**: 2026-02-27  
**기준**: Creation Days (day1~7) + Eden(창세기 2장) + bridge/cognitive, 에덴 탐색기(Grid 연동·탐사 확장) 완성 반영.

---

## 1. 최상위 구조

| 폴더/파일 | 역할 |
|-----------|------|
| `README.md` | solar 전체 개념·아키텍처·검증·Eden 탐색기 섹션 |
| `LAYERS.md` | 개념 레이어 순서 (0~4, 폴더 매핑) |
| `__init__.py` | 공개 API: core, data, em, surface, atmosphere, cognitive, gaia_bridge, gaia_loop_connector, cycles, nitrogen, gravity_tides (eden은 `solar.eden` 서브패키지로 진입) |
| `day1/` | 첫째날 — 빛이 있으라 (em: SolarLuminosity, MagneticDipole, SolarWind, Magnetosphere) |
| `day2/` | 둘째날 — 궁창 (atmosphere: greenhouse, column, water_cycle) |
| `day3/` | 셋째날 — 땅·바다·식생·산불 (surface, biosphere, fire) |
| `day4/` | 넷째날 — 중력·질소·Milankovitch·조석 (core, data, nitrogen, cycles, gravity_tides) |
| `day5/` | 다섯째날 — 생물 이동·정보 네트워크 (BirdAgent, FishAgent, SeedTransport, FoodWeb) |
| `day6/` | 여섯째날 — 진화·상호작용 (species_engine, mutation_engine, niche_model, integration) |
| `day7/` | 일곱째날 — 완성·안식 (runner, sabbath, completion_engine) |
| **`eden/`** | **창세기 2장 — 에덴·대홍수·탐색기** |
| `bridge/` | BrainCore·Gaia·Grid Engine 브리지 |
| `cognitive/` | 인지 레이어 (RingAttractorEngine, SpinRingCoupling) |
| `engines/` | 우물별 엔진 (01_solar ~ 12_evos) |
| `legacy/` | 구 버전 호환 shim |
| `concept/` | 개념용 README (00_system ~ 04_onward) |

---

## 2. Eden (에덴 탐색기) — 완성 상태

| 모듈 | 내용 |
|------|------|
| `firmament.py` | 궁창: H2O_canopy, UV_shield, albedo, pressure_atm, pole_eq_delta 등 env override |
| `flood.py` | 대홍수 전이: rising → peak → receding → stabilizing → complete |
| `initial_conditions.py` | **EDEN_IC_CONFIG** 기반 τ, ε_a, T_surface, pole_eq_delta, band_T, GPP, mutation_factor |
| `geography.py` | EdenGeography, 자기장 프레임, make_eden_geography |
| `search.py` | **EdenSearchEngine**, SearchSpace, EdenCriteria, EdenCandidate, SearchResult; **exploration 그리드 연동**, **grid_agent** |
| **`exploration.py`** | **EdenExplorationGrid**, **trim_candidates_by_exploration** (12밴드 탐사 + Grid 포커스) |
| `biology.py` | 물리 → 수명/체형/거대동물·안정 생태계 |
| `eden_search_demo.py` | 전체 데모; Grid 연동 시 `[Grid Engine 연동]` 블록 출력 |

**진입점**: `from solar.eden import make_eden_search, make_antediluvian_space, ...`  
**실행**: `python -m solar.eden.eden_search_demo`

---

## 3. bridge/ — Grid·Gaia·BrainCore

| 파일 | 내용 |
|------|------|
| `grid_engine_bridge.py` | Grid Engine 2D~7D 로드, **get_max_grid_dimension()**, **create_grid_engine_nd()**, **create_latitude_grid_agent()**, LatitudeGridAdapter |
| `ring_attractor_shim/` | hippo_memory.ring_engine → solar 경량 Ring Attractor (Grid 2D~7D 의존성 대체) |
| `gaia_bridge.py` | GaiaBridge, BrainGaiaState |
| `gaia_loop_connector.py` | GaiaLoopConnector, Loop A/B/C |
| `brain_core_bridge.py` | BrainCore 환경 확장 |

---

## 4. 의존 방향 (요약)

```
day4/data → day4/core ← day1/em, day2/atmosphere, day3/surface, cognitive/, bridge/
eden/     → initial_conditions 기반으로 독립 탐색 (선택적으로 Day7 runner 연동)
bridge/   → Grid Engine 패키지(00_BRAIN) + Ring Attractor shim
```

---

## 5. 검증·문서

| 항목 | 위치 |
|------|------|
| 에덴 탐색기 점검 | `docs/EDEN_ENGINEERING_FINAL.md` (패키지 인덱스, τ/ΔT 더블카운트, Config 화) |
| 에덴×Grid 확장 체크리스트 | `docs/EDEN_GRID_EXTENSION_CHECKLIST.md` |
| PHAM 체인 | `blockchain/pham_chain_exploration.json`, `pham_chain_search.json`, `pham_chain_grid_engine_bridge.json`, `pham_chain_initial_conditions.json`, `pham_chain_EDEN_ENGINEERING_FINAL.json` 등 |

---

## 6. 결론

- **Creation Days (day1~7)** + **Eden(창세기 2장)** + **bridge/cognitive** 구조가 solar/ 안에 일관되게 들어 있음.
- **에덴 탐색기**는 **search.py** + **exploration.py** + **grid_engine_bridge** 로 완성되어 있으며, 12밴드 탐사·Grid 포커스·트림·결과 grid_agent까지 반영됨.
- **initial_conditions**는 EDEN_IC_CONFIG 규약 준수, **문서**는 τ/알베도/ΔT 더블카운트 방지 규칙 정리됨.

이 상태를 **에덴 탐색기 완성** 기준으로 solar 폴더 전체 확인이 완료된 상태로 본다.
