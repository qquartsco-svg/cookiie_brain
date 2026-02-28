# Day 1~6 모듈 중 독립 엔진 후보 분석

**확정 목록**: 독립 엔진으로 **정해진** 목록은 → **`docs/STANDALONE_ENGINES_POLICY.md`** 참고.

**목적**: 현재 1~6 레이어에서 "독립 모듈"로 **엔진** 호칭을 줄 만한 대상을 정리한다.  
기준: (1) 상태 보유 + `step()` 또는 명확한 진입점, (2) 다른 Day에 대한 의존이 적거나 인터페이스로 차단 가능, (3) 한 가지 물리/생물 역할에 대한 단일 진입점.

---

## 1. 엔진 vs 비엔진 정리

### 1.1 이미 "Engine" 명칭을 쓰는 것

| Day | 클래스/모듈 | 역할 | 독립성 |
|-----|-------------|------|--------|
| 3 | **FireEngine** | 산불 확산·O₂ attractor, 밴드별 step | Day2 Atmosphere, Day3 surface 알베도 등 연동 가능하나 진입점 단일 |
| 4 | **EvolutionEngine** | N-body·세차·조석·해양, `step(dt)` | core+data 내부 의존, 외부는 PlanetData 등 입력만 |
| 4 | **SeasonEngine** | 계절 위상·진폭, `step(dt)`, `state(lat_deg)` | Milankovitch/obliquity 입력만 받으면 독립 |
| 5 | **mobility_engine** (모듈명) | BirdAgent / FishAgent (이동률·플럭스) | Day5 내부 상수만, Day3 biomass/land_fraction은 인자로 받으면 독립 |
| 6 | **ContactEngine** | P_contact(i,j), `compute(rho)` | 완전 독립 (인자만) |
| 6 | **MutationEngine** | μ_eff, 변이 이벤트 `step(...)` | env dict 등 인자만 |
| 6 | **ReproductionEngine** | 재조합·변이 `produce`/`step` | genome_state만 내부, 독립 |
| 6 | **SelectionEngine** | Exploitation/Exploration 선택 | 독립 |
| 6 | **SpeciesEngine** | 개체군 ODE, `step(state, env, graph?)` | Optional graph로 확장 가능, 독립 |
| 6 | **GaiaFeedbackEngine** | Genome→환경 수정 | 독립 (env, genomes, densities 인자) |

→ **이미 엔진으로 쓰는 것들은 그대로 두고**, "독립 모듈로 엔진 호칭 할 만한" 추가 후보만 아래에서 구분한다.

---

## 2. Day별: 엔진 호칭 후보 (현재 비엔진)

### Day 1 (EM)

| 구성요소 | 현재 명칭 | step() | 비고 |
|----------|-----------|--------|------|
| 광도·조도 | SolarLuminosity, IrradianceState | 없음 (순수 함수) | "RadiativeEngine"으로 묶으면 state + step( t_yr ) 형태로 진입점 하나 가능. 선택 사항. |
| 자기권·태양풍 | Magnetosphere, SolarWind, MagneticDipole | 없음 | 계산기 집합. 엔진이라기보다 **라이브러리**에 가깝다. |

**결론**: Day1은 **독립 모듈**이지만 "엔진"보다는 **물리 계산 라이브러리**로 두는 편이 자연스럽다.  
원하면 `RadiativeEngine( t_yr ) → F, T_eq` 같은 얇은 래퍼만 추가해 엔진 호칭 가능.

---

### Day 2 (대기)

| 구성요소 | 현재 명칭 | step() | 비고 |
|----------|-----------|--------|------|
| 단일 기둥 대기 | AtmosphereColumn | 있음 `step(F_solar_si, dt_yr, ...)` | 상태(T, composition) 보유, ODE 적분. **AtmosphereEngine**으로 호칭해도 무방. |

**의존**: day2 내부 `greenhouse`, `water_cycle`, `_constants`만. Day1/3는 **호출자가** F_solar, albedo 등을 넘기면 되므로 엔진 자체는 독립.

**결론**: **AtmosphereColumn → AtmosphereEngine** 별칭 또는 래퍼를 두면 "독립 모듈 + 엔진"으로 정리하기 좋다.  
(기존 이름 유지 시에는 "대기 엔진 = AtmosphereColumn"으로 문서만 통일해도 됨.)

---

### Day 3 (땅·생명·불)

| 구성요소 | 현재 명칭 | step() | 비고 |
|----------|-----------|--------|------|
| 산불 | FireEngine | 있음 | 이미 엔진. |
| 단일 밴드 생물권 | BiosphereColumn | 있음 `step(env, dt_yr)` | GPP·호흡·CO₂/O₂. **BiosphereEngine** 후보. |
| 위도 밴드 집합 | LatitudeBands | 있음 `step(dt_yr)` | 내부에 BiosphereColumn 리스트. "BandAggregator" 또는 **BiosphereBandsEngine** 같은 통칭 가능. |
| 표면 | SurfaceSchema | 없음 | 스키마·알베도 계산. 엔진 후보 아님. |

**의존**: BiosphereColumn은 day3 내부(pioneer, photo, _constants). LatitudeBands는 BiosphereColumn + obliquity 등 입력.  
bridge(gaia_loop_connector)가 Day2·Day3를 조합하므로, **BiosphereColumn / LatitudeBands는 각각 독립 모듈**로 쓸 수 있고, 호칭만 "엔진"으로 올릴지 선택 가능.

**결론**:  
- **BiosphereColumn** → "단일 밴드 생물권 엔진"으로 문서/별칭 정리 가능.  
- **LatitudeBands** → 여러 밴드 진입점이 필요하면 "BiosphereBandsEngine" 등으로 부를 만함.

---

### Day 4 (순환·중력)

| 구성요소 | 현재 명칭 | step() | 비고 |
|----------|-----------|--------|------|
| N-body·세차·조석 | EvolutionEngine | 있음 | 이미 엔진. |
| 계절 | SeasonEngine | 있음 | 이미 엔진. |
| 질소 순환 | NitrogenCycle | 있음 `step(...)` | N 고정·탈질·N_soil. **NitrogenEngine** 호칭 가능. |
| 장주기 | MilankovitchCycle, MilankovitchDriver | Driver가 `step(t_yr)` | 일사·이심률·경사. **MilankovitchEngine** 또는 Driver를 엔진으로 통칭 가능. |
| 조석 | TidalField | 상태 보유, 계산 | step 형태는 OceanNutrients 쪽. TidalField는 "필드 계산기". |
| 해양 영양염 | OceanNutrients | 있음 `step(...)` | 조석→혼합→탄소. **OceanNutrientsEngine** 또는 TidesEngine 일부로. |

**의존**:  
- NitrogenCycle → day4/nitrogen 내부.  
- Milankovitch → day4/cycles 내부.  
- OceanNutrients → TidalField 등 day4 내부.  

전부 **Day4 내부**에서만 의존하므로, Day4를 "독립 패키지"로 둔 채 각각을 서브엔진으로 부르기 좋다.

**결론**:  
- **NitrogenCycle** → **NitrogenEngine** (또는 기존 Cycle 유지하고 "질소 엔진 = NitrogenCycle" 문서화).  
- **MilankovitchDriver** → **MilankovitchEngine** 통칭 가능.  
- **OceanNutrients** → **OceanNutrientsEngine** 또는 **TidalMixingEngine** 등으로 호칭할 만함.

---

### Day 5 (이동·네트워크)

| 구성요소 | 현재 명칭 | step() | 비고 |
|----------|-----------|--------|------|
| 이동 에이전트 | BirdAgent, FishAgent (mobility_engine) | 플럭스·이동률 계산 | step이 아니라 "rate/flux 반환". 모듈명이 이미 mobility_engine. **MobilityEngine** 클래스로 Bird+Fish를 한 진입점으로 묶으면 독립 엔진. |
| 씨드 수송 | SeedTransport | 있음 `step(B, dt_yr)` | 보존형 커널. **TransportEngine** 호칭 가능. |
| 먹이사슬 | FoodWeb | 있음 `step(...)` | 트로픽 ODE. **FoodWebEngine** 호칭 가능. |

**의존**: Day5 내부 _constants, mobility_engine ↔ seed_transport는 인자로 연결. Day3 biomass/land_fraction은 호출자가 넘김.

**결론**:  
- **SeedTransport** → 독립 모듈이며 **TransportEngine** 또는 **SeedTransportEngine**으로 부를 만함.  
- **FoodWeb** → **FoodWebEngine**으로 호칭해도 됨.  
- **MobilityEngine**: 현재는 모듈명만 있고 클래스 없음. 원하면 `MobilityEngine( n_bands, ... ).fluxes( ... )` 같은 단일 진입점 클래스를 두어 "독립 엔진"으로 정리 가능.

---

### Day 6 (진화·재생산)

| 구성요소 | 현재 명칭 | step() | 비고 |
|----------|-----------|--------|------|
| Contact / Mutation / Reproduction / Selection / Species / GaiaFeedback | 모두 *Engine* | 있음 | 이미 엔진. |
| 니치·자원 경쟁 | NicheModel | 있음 `step(state, env_by_band, dt_yr)` | 밴드별 점유·비례 배분. **NicheEngine**으로 호칭할 만함. |
| interaction_graph, genome_state | 데이터/함수 | 없음 | 엔진 후보 아님. |
| integration | evolution_step | 함수 1개 | "한 세대" 통합. **EvolutionStepEngine** 같은 이름은 선택. |

**결론**: **NicheModel → NicheEngine** 별칭 또는 클래스명 변경이면, Day6도 전부 엔진 호칭으로 통일 가능.

---

## 3. 요약 표: 독립 모듈 & 엔진 호칭 적합성

| Day | 현재 이름 | 독립 모듈? | 엔진 호칭 제안 | 비고 |
|-----|------------|------------|----------------|------|
| 1 | SolarLuminosity 등 | ✅ (라이브러리) | 선택: RadiativeEngine 래퍼 | step 없음, 계산기 집합 |
| 2 | AtmosphereColumn | ✅ | **AtmosphereEngine** | state+step 있음, day2만 의존 |
| 3 | BiosphereColumn | ✅ | **BiosphereEngine** | 단일 밴드 생물권 |
| 3 | LatitudeBands | ✅ | **BiosphereBandsEngine** (선택) | 밴드 집합 진입점 |
| 3 | FireEngine | ✅ | 유지 | 이미 엔진 |
| 4 | EvolutionEngine, SeasonEngine | ✅ | 유지 | 이미 엔진 |
| 4 | NitrogenCycle | ✅ | **NitrogenEngine** | Cycle→Engine 통칭 |
| 4 | MilankovitchDriver | ✅ | **MilankovitchEngine** | Driver→Engine 통칭 |
| 4 | OceanNutrients | ✅ | **OceanNutrientsEngine** | 조석·탄소 펌프 |
| 5 | BirdAgent/FishAgent (mobility_engine) | ✅ | **MobilityEngine** 클래스 (선택) | 모듈만 엔진명, 단일 진입점 없음 |
| 5 | SeedTransport | ✅ | **TransportEngine** / SeedTransportEngine | 보존형 transport |
| 5 | FoodWeb | ✅ | **FoodWebEngine** | 트로픽 ODE |
| 6 | Contact/Mutation/Reproduction/Selection/Species/GaiaFeedback | ✅ | 유지 | 이미 *Engine* |
| 6 | NicheModel | ✅ | **NicheEngine** | step 있음, 자원 경쟁 |

---

## 4. 권장 우선순위 (엔진 호칭 정리 시)

- **바로 호칭만 정리해도 되는 것** (코드 변경 최소: 문서·별칭)  
  - AtmosphereColumn → "대기 엔진(AtmosphereEngine = AtmosphereColumn)".  
  - NitrogenCycle → "질소 엔진(NitrogenEngine = NitrogenCycle)".  
  - MilankovitchDriver → "Milankovitch 엔진".  
  - OceanNutrients → "해양영양염 엔진(OceanNutrientsEngine)".  
  - NicheModel → "니치 엔진(NicheEngine = NicheModel)".  
  - SeedTransport / FoodWeb → "Transport 엔진", "FoodWeb 엔진" 문서 통일.

- **클래스/모듈명까지 바꾸고 싶을 때**  
  - AtmosphereColumn → AtmosphereEngine (이름 변경 또는 래퍼).  
  - NicheModel → NicheEngine.  
  - (선택) MobilityEngine 클래스 추가해 BirdAgent+FishAgent 진입점 통합.

- **독립성 유지**  
  - 위 후보들은 모두 "다른 Day를 직접 import"하지 않고, **인자/인터페이스**로 입력받으면 독립 모듈로 사용 가능.  
  - bridge/gaia_loop_connector처럼 "여러 Day를 조합하는 통합 레이어"는 "통합 엔진"으로 두고, 개별 Day 1~6 구성요소를 위 표대로 **독립 엔진** 후보로 정리하면 된다.

이 문서는 **분석만** 담당한다. 실제 리네이밍·래퍼 추가는 별도 태스크로 진행하면 된다.
