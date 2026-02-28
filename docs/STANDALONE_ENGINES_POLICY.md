# 독립 엔진 모듈 정책 (Standalone Engine Policy)

**목적**: Day 1~6에서 **“독립 엔진(Engine)으로 분리해서 돌릴 수 있는 것”**을 의존성(입력 포트) 기준으로 확정한다.  
이 문서가 **정해진 목록**이다. 분석·후보 논의는 `ENGINE_CANDIDATES_ANALYSIS.md` 참고.

---

## 1. 독립 엔진 판정 기준

- **입력 포트가 명확**: `env` dict / `params` / 생성자 인자로만 받음. 다른 레이어를 직접 import하지 않거나, 인터페이스(함수 시그니처·타입)로만 받음.
- **상태(state)가 캡슐화**: `State` dataclass 또는 클래스 내부 `self.*`로 보유.
- **step(dt)** 형태로 단독 적분 가능: 한 번에 한 스텝 진행, 외부에서 반복 호출로 시뮬레이션.
- **다른 레이어와의 연결**: 읽기/쓰기는 **포트(인자·반환값)**로만. 내부에서 `from solar.dayX` 로 타 레이어를 가져오지 않거나, 선택 의존만 허용(예: `InteractionGraph` 타입만 받기).

---

## 2. 확정 목록: 독립 엔진으로 구성할 것들

아래는 **독립 엔진 모듈**로 정한 것이다.  
- **A**: 단일 모듈/클래스가 그대로 독립 엔진 (입력 포트만 맞추면 단독 실행).  
- **B**: 결합/브리지 엔진 (여러 엔진을 결선하는 상위 엔진).

---

### Day 1 — 물리/입력 생성기 엔진

| # | 엔진 이름 | 현재 소스 | 입력 포트 | 출력 포트 | 비고 |
|---|-----------|------------|-----------|-----------|------|
| 1 | **SolarLuminosity** | day1/em/solar_luminosity | mass_solar, r(AU), A, emissivity, redistribution | F(r), T_eq, P_rad | 완전 독립 (step 없음, 계산기) |
| 2 | **MagneticDipole** | day1/em/magnetic_dipole | B_surface_equator, tilt, 위치/축 벡터 | B_field(r) | 완전 독립 |
| 3 | **SolarWind** | day1/em/solar_wind | P0, r | P_sw, flux, IMF | 완전 독립 |
| 4 | **Magnetosphere** | day1/em/magnetosphere | dipole, wind, R, 위치벡터 | r_mp, shielding | 결합 엔진(1+2+3만 있으면 단독 가능) |

→ Day1은 **엔진**이라기보다 **물리 계산 라이브러리**로 두고, 필요 시 `RadiativeEngine` 래퍼로 진입점 하나 추가 가능.

---

### Day 2 — 환경 상태 엔진

| # | 엔진 이름 | 현재 소스 | 입력 포트 | 출력 포트 | 비고 |
|---|-----------|------------|-----------|-----------|------|
| 5 | **AtmosphereEngine** | day2/atmosphere/column (AtmosphereColumn) | F_solar, A_eff, g/planet params, composition, dt | T_surface, P_surface, water_phase, habitable | 독립 엔진 (g/행성 파라미터 공급만 하면 됨) |
| 6 | **GreenhouseEngine** | day2/atmosphere/greenhouse | composition, T | optical_depth, effective_emissivity, T_eq | 서브엔진; Column 내부 기어이나 “온실효과 계산기”로 독립 가능 |

---

### Day 3 — 생태/항상성 엔진

| # | 엔진 이름 | 현재 소스 | 입력 포트 | 출력 포트 | 비고 |
|---|-----------|------------|-----------|-----------|------|
| 7 | **SurfaceEngine** | day3/surface/surface_schema | land_fraction, albedo_land, albedo_ocean | effective_albedo() | 정적/유틸 엔진 |
| 8 | **BiosphereEngine** | day3/biosphere/column (BiosphereColumn) | env (T, CO2, O2, water_phase, land_fraction…), dt | delta_CO2, delta_O2, GPP, 내부 상태 | 독립 (env 포트만 맞추면 됨) |
| 9 | **BiosphereBandsEngine** | day3/biosphere/latitude_bands (LatitudeBands) | obliquity, F0, T_eq_by_band, dt | 밴드별 생물권 상태 | 독립 (위도 집계 진입점) |
| 10 | **FireEngine** | day3/fire/fire_engine | O2, CO2, dryness/season, time | fire index, CO2 injection 등 | 이미 엔진, 유지 |
| 11 | **StressAccumulatorEngine** | day3/fire/stress_accumulator | 뉴런/기관/행성 스케일 입력 이벤트, dt | Level 1/2/3 스트레스, excess, 방전 | **stdlib만 의존 → 즉시 독립 후보** (Day7 HomeostasisEngine 기반) |
| 12 | **GaiaLoopConnector** | bridge/gaia_loop_connector | biosphere/fire/cycles에서 올라오는 Δ들 | CO2, albedo, obliquity scaling | **B** 결합 엔진 (다른 엔진 결선) |

---

### Day 4 — 장주기 리듬·순환 엔진

| # | 엔진 이름 | 현재 소스 | 입력 포트 | 출력 포트 | 비고 |
|---|-----------|------------|-----------|-----------|------|
| 13 | **EvolutionEngine** | day4/core/evolution_engine | PlanetData, dt | N-body, 세차, 조석, 해양 | 이미 엔진, 유지 |
| 14 | **SeasonEngine** | day4/season_engine | obliquity, lat, dt | phase, ΔT, dry_modifier | 완전 독립 helper |
| 15 | **NitrogenEngine** | day4/nitrogen/cycle (NitrogenCycle) | B_pioneer, GPP, O2, T, W, dt | N_soil, N_limitation | 독립 엔진 |
| 16 | **MilankovitchEngine** | day4/cycles (MilankovitchCycle/Driver) | t_yr, latitude | obliquity, ecc, precession, insolation_scale, glacial flag | **stdlib만 의존 → 즉시 독립** (리듬 엔진) |
| 17 | **TidalFieldEngine** | day4/gravity_tides/tidal_field | t, moon/sun params | 조석 변형 필드 | 필드 계산기 |
| 18 | **OceanNutrientsEngine** | day4/gravity_tides/ocean_nutrients | TidalField 결과, dt | upwelling, CO2_sink_ppm | 독립 (TidalField는 인자로 주입 가능) |

---

### Day 5 — 연결/전달 엔진

| # | 엔진 이름 | 현재 소스 | 입력 포트 | 출력 포트 | 비고 |
|---|-----------|------------|-----------|-----------|------|
| 19 | **TransportEngine** | day5/seed_transport (SeedTransport) | B_by_band, rates, neighbors/kernel, dt | B_new (보존형) | 완전 독립 (수치 안정성만 유지) |
| 20 | **MobilityEngine** | day5/mobility_engine (BirdAgent + FishAgent) | O2_by_band, phyto_by_band, land_fraction_by_band | migration_rates, seed_flux, guano_flux, predation_flux | 독립 (환경 포트만 설계) |
| 21 | **FoodWebEngine** | day5/food_web (FoodWeb) | env (GPP, fish_predation), state, dt | trophic state, CO2 resp | 독립 엔진 |

---

### Day 6 — 진화 OS 엔진

| # | 엔진 이름 | 현재 소스 | 입력 포트 | 출력 포트 | 비고 |
|---|-----------|------------|-----------|-----------|------|
| 22 | **ContactEngine** | day6/contact_engine | rho_i, k_encounter, V_cell | P_contact | **완전 독립** |
| 23 | **SpeciesEngine** | day6/species_engine | env (GPP_scale 등), state, dt, graph? | N_species 업데이트 | 독립 |
| 24 | **MutationEngine** | day6/mutation_engine | p_contact, env (T, CO2…), dt | mutation/speciation events | **완전 독립** |
| 25 | **ReproductionEngine** | day6/reproduction_engine + genome_state | parent genomes, rng | child genome (recombine+mutate) | **완전 독립** |
| 26 | **SelectionEngine** | day6/selection_engine | population, fitness_fn, rng | selected indices | **완전 독립** |
| 27 | **GaiaFeedbackEngine** | day6/gaia_feedback | env, genomes, densities, dt | env_new (env 수정량) | **완전 독립** (trait→env 매핑) |
| 28 | **NicheEngine** | day6/niche_model (NicheModel) | state, env_by_band, dt | 밴드별 점유(자원 비례 배분) | 독립 (단위/해석만 고정) |
| 29 | **InteractionGraph** | day6/interaction_graph | n_species, predation/competition 행렬 | 그래프(행렬) 기반 상호작용 | 데이터 구조 + from_contact_result; “그래프 엔진”으로 독립 가능 |

---

## 3. 즉시 solar 없이 독립 실행 가능 (우선순위)

아래는 **외부 의존이 stdlib(+numpy 등 최소)** 수준이라, 다른 프로젝트로 복사만 해도 단독 실행 가능한 엔진이다.

| 엔진 | 소스 | 의존 |
|------|------|------|
| StressAccumulatorEngine | day3/fire/stress_accumulator | stdlib만 |
| MilankovitchEngine | day4/cycles/milankovitch | stdlib만 |
| ContactEngine | day6/contact_engine | stdlib만 |
| MutationEngine | day6/mutation_engine | stdlib+random |
| SelectionEngine | day6/selection_engine | stdlib+random |
| GaiaFeedbackEngine | day6/gaia_feedback | stdlib만 |

→ **Day7 설계 시**: `stress_accumulator` + `milankovitch` → homeostasis_engine / rhythm_engine 기반으로 바로 활용 가능.

---

## 4. 결합/브리지 엔진 (B)

여러 독립 엔진을 “결선”하는 상위 엔진. 독립 엔진 목록에 포함하되, 역할은 **브리지**로 구분.

| 엔진 | 역할 |
|------|------|
| **GaiaLoopConnector** | Loop A/B/C — biosphere/fire/cycles → CO2, albedo, obliquity scaling |
| (확장) **통합 러너** | Day1~6 step 순서 호출, 포트만 연결 (Day7 완성/안식 레이어 후보) |

---

## 5. 정리: “독립 엔진으로 구성되어야 할 것” 핵심 묶음

- **물리/입력 생성기**: SolarLuminosity, MagneticDipole, SolarWind, Magnetosphere, MilankovitchEngine, SeasonEngine, TidalFieldEngine  
- **환경 상태**: AtmosphereEngine, OceanNutrientsEngine  
- **생태/항상성**: BiosphereEngine, BiosphereBandsEngine, FireEngine, NitrogenEngine, StressAccumulatorEngine  
- **연결/전달**: TransportEngine, MobilityEngine, FoodWebEngine  
- **진화 OS**: ContactEngine, SpeciesEngine, MutationEngine, ReproductionEngine, SelectionEngine, GaiaFeedbackEngine, NicheEngine, InteractionGraph  
- **브리지/결선**: GaiaLoopConnector  

이렇게 보면 **1~6은 이미 “엔진화” 가능한 모듈이 많고**, 독립성이 가장 강한 것은 **Day1, Day4(리듬), Day6** 이다.  
실제 코드에서 **이름 변경(Column→Engine, Model→Engine)** 이나 **engines/ 추출**은 별도 작업으로 진행하면 되며, 이 문서는 **무엇을 독립 엔진으로 볼지**에 대한 확정 목록이다.
