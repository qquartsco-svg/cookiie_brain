# Eden System — 최종 구조 재확인 결과 (엔지니어링 검증)

**기준**: 업로드된 Eden 시스템 파일 전체  
(README + firmament / flood / geography / initial_conditions / search + demo들)  
**관점**: 재확인 결과의 **실제 코드와의 일치 여부**만 정리. 개념 평가 X.

---

## 결론 요약

| 재확인 항목 | 코드와 일치 | 비고 |
|-------------|-------------|------|
| Eden = Day1–7 위 환경 레이어, IC 제어기 | ✅ | initial_conditions → to_runner_kwargs() → PlanetRunner |
| Eden = x₀ (initial state generator) | ✅ | InitialConditions._build() 가 동역학으로 상태 생성 |
| firmament = boundary_condition modifier | ✅ | get_env_overrides() 로 H2O, albedo, τ, UV, pole_eq_delta 등 주입 |
| flood = discontinuity / phase transition | ✅ | FloodEngine.step() → FloodSnapshot, 구간별 전이 곡선 |
| geography = surface/topology·land·basin | ✅ | band_land_fraction, ArcticBasinState, ExposedRegion (elevation proxy 없음) |
| search = parameter sweep + attractor 탐색 | ✅ | SearchSpace.grid() → criteria.check() → compute_eden_score |
| 에덴 = “조건 찾기” (좌표 아님) | ✅ | EdenCriteria는 T, GPP, ice, mutation, hab_bands |
| Day1–7와 연결·계층 위반 없음 | ✅ | IC → runner; deep_validate에서 runner 사용 |
| **Eden Score 명시화** | ⚠️ **이미 구현됨** | 아래 수정 반영 |
| **Flood → Day7 Stress 연결** | ❌ **미구현** | 아래 유지 |
| **Firmament ↔ Radiation 입력** | ❌ **미구현** | 아래 유지 |

---

## 1. Eden 레이어 위치 — 코드와 일치 ✅

- **Day1–7 위에 Eden**  
  - `PlanetRunner.__init__(initial_conditions=...)` 가 `InitialConditions.to_runner_kwargs()` 결과를 받음.  
  - `solar.eden.search` 의 `deep_validate()` 에서 `c.ic.to_runner_kwargs()` → `make_planet_runner(initial_conditions=kwargs)` 호출.  
  - Eden은 “새 물리 엔진”이 아니라 **초기 조건 공급자**로만 쓰임. ✅

- **Eden = x₀ (initial state generator)**  
  - `initial_conditions.py`: 독립 파라미터 6개 + `_build()` 에서 τ, T_surface, band(T_K, soil_W, GPP, ice_mask, habitable), mutation_factor 계산.  
  - dynamics F(x,t) 는 Day1–7, x₀ 생성은 Eden. ✅

---

## 2. 파일별 역할 — 코드와 일치 ✅

| 파일 | 재확인 문서 역할 | 코드 확인 |
|------|------------------|-----------|
| **initial_conditions.py** | 행성 초기 상태 생성기, phase-space 선택기 | `InitialConditions`, `EarthBandState`, `_optical_depth`, `_T_surface`, `_band_temperatures`, `_gpp_per_band` 등으로 atmosphere·hydrology·band(생산성·빙하·거주) 생성. geography는 별도 `geography.py`. ✅ |
| **firmament.py** | 대기 경계 조건 modifier | `get_env_overrides()` → `H2O_override`, `albedo_override`, `delta_tau`, `uv_shield_factor`, `mutation_rate_factor`, `pressure_atm`, `pole_eq_delta_K`, `precip_mode`, `firmament_active`. ✅ |
| **flood.py** | discontinuity / phase transition | `FloodEngine.step(dt_yr)` → `FloodSnapshot(flood_phase, f_land, albedo, T_surface_K, ...)`. `FLOOD_PHASES` 로 rising/peak/receding/stabilizing/complete 구간 정의. ✅ |
| **geography.py** | surface topology, land, basin | `EdenGeography`: `band_land_fraction`, `ArcticBasinState`, `ExposedRegion`, `MagneticFrameGeography`, `band_protection()`. **elevation proxy 는 코드에 없음.** ✅ (역할만) |
| **search.py** | parameter sweep, attractor 탐색 | `SearchSpace.grid()` → `InitialConditions(**params)` → `criteria.check(ic)` → `compute_eden_score()` → `EdenCandidate` 수집·랭킹. ✅ |
| **eden_demo.py** | integration smoke test | 궁창 → 대홍수 발동 → FloodEngine 12단계, greenhouse로 T 추정, 밴드별 빙하 비교. ✅ |
| **eden_search_demo.py** | integration smoke test | compare_phases, antediluvian/postdiluvian 탐색, biology 비교. ✅ |

---

## 3. Eden Score — “명시화 필요”에 대한 수정 ⚠️

**재확인 문서**: “Eden Score 함수 명시화 필요”, implicit 하다고 기술.

**실제 코드** (`search.compute_eden_score`):

```python
score = (
    gpp_score  * 0.30 +   # GPP 생산성
    t_score    * 0.25 +   # 온도 최적성 (가우시안)
    mut_score  * 0.20 +   # mutation 낮음
    hab_score  * 0.15 +   # 거주 밴드 수
    ice_score  * 0.10 +   # 빙하 없음
    mag_bonus             # geo 있으면 자기장 보너스 최대 10%
)
return min(1.0, score)
```

- **가중치와 항목이 이미 코드에 명시됨.**  
- 다만 항목 이름이 “stability”, “biodiversity”가 아니라 GPP/temperature/mutation/habitable/ice/magnetic 이므로, **문서/API에서 “stability·biodiversity·climate_variance·resource_balance”와 매핑만 해주면** 재확인 문서에서 요구한 “명시화”는 충족됨.  
- **정리**: “Eden Score 명시화 필요”는 **이미 구현되어 있음** → 부족한 3개에서 제외하고, 필요 시 용어 매핑만 추가하면 됨.

---

## 4. 부족한 부분 3개 — 코드 기준 정리

### (1) Eden Score 명시화 — ✅ 이미 구현됨 (위 3절)

- 코드상 명시적 가중치 존재. 재확인 문서의 “부족” 항목에서 제거.

### (2) Flood → Day7 Stress 연결 — ❌ 미구현 유지

- **현재**:  
  - `FloodEngine.get_env_overrides()` 에 `flood_phase`, `f_land`, `albedo`, `T_surface_K`, `mutation_rate_factor` 등 포함.  
  - `PlanetRunner` 는 **`initial_conditions` dict 만** 받음 (`runner.py`).  
  - `FloodEngine.get_env_overrides()` 를 runner에 넘기는 코드 경로 없음.  
  - `SabbathJudge` 는 `snap.planet_stress` 만 사용; `flood_phase` 또는 Flood 구간을 받지 않음.

- **재확인 문서 요구**: “Flood → StressEngine spike”, “SabbathJudge가 역사적 이벤트 인식”.

- **정리**: **미구현.** Flood 전이 중인 환경을 runner/stress에 주입하는 경로와, Sabbath 판정에 “홍수 이벤트”를 반영하는 설계가 필요.

### (3) Firmament ↔ Radiation 연결 — ❌ 미구현 유지

- **현재**:  
  - `firmament.py`: `uv_shield_factor`, `delta_tau` 등이 **H2O_canopy** 만으로 계산됨.  
  - 항성 광도(SolarLuminosity) 또는 UV flux 를 인자로 받지 않음.

- **재확인 문서 요구**: “SolarLuminosity → UV flux”, “Firmament → attenuation”.

- **정리**: **미구현.** 외부 UV flux/항성 광도 입력 → Firmament attenuation 파이프라인 없음.

---

## 5. Day1–7 연결 상태 — 코드와 일치 ✅

- **Eden → Runner**: `InitialConditions.to_runner_kwargs()` → `make_planet_runner(initial_conditions=...)`.  
- **Runner 내부**: Day4 rhythm, Day2 atmosphere, Day3 stress 등 사용 (`runner.py`).  
- **Search → Day7**: `deep_validate()` 에서 `make_planet_runner(initial_conditions=c.ic.to_runner_kwargs())` 로 n_steps 진행 후 CO2/T/stress 안정성 확인.  
- 논리 단절·순환 닫힘·계층 위반 없음. ✅

---

## 6. 시스템 성숙도 — 수정 반영

| 레이어 | 재확인 문서 | 검증 후 |
|--------|--------------|----------|
| Day1–4 물리 | ✅ 안정 | ✅ 유지 |
| Day5 네트워크 | ✅ 안정 | ✅ 유지 |
| Day6 진화 OS | ✅ 동작 | ✅ 유지 |
| Day7 메타 | ✅ 완성 | ✅ 유지 |
| Eden | 🟡 80% (score 정의만 부족) | **🟡 85%** — Score는 이미 명시적; 부족한 것은 (2) Flood→Stress, (3) Firmament↔Radiation 2개. |

---

## 7. 핵심 결론 (검증 반영)

- Eden 시스템은 **“초기 조건 탐색 시뮬레이터”** 로 코드에 구현되어 있음. ✅  
- **Creation Engine (1–6) → Stability Judge (7) → Eden = Stable Attractor Finder** 구조가 코드에서도 유지됨. ✅  
- **수정 사항**:  
  - Eden Score는 **이미 명시적**이므로 “부족 3개”에서 제외.  
  - **실제 부족 2개**: (2) Flood → Day7 Stress 연결, (3) Firmament ↔ Radiation 입력.  
- 다음 단계(Adam/Eve = control interface)로 넘어가는 지점이라는 재확인 문서의 정리와도 일치. ✅
