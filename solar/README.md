# solar/ — 전체 태양계 N-body + 자기권 + 광도 + 대기권 + 관성 기억 (v1.5.0)

**코드·서사·문서 어디 있는지 한눈에** → **[INDEX_CODE_AND_DOCS.md](INDEX_CODE_AND_DOCS.md)** (지금까지 쌓아온 것 전체 위치).

NASA/JPL 실측 데이터 기반 10-body 심플렉틱 엔진.
자기쌍극자 + 태양풍 + 자기권 + 태양 광도 전자기 레이어 완비.
빛이 있으라 — 중력장 위에 빛이 켜지고, 형태와 온도가 존재하기 시작한다.

> *10-body symplectic engine with magnetic dipole, solar wind,
> magnetosphere, and solar luminosity. Gear-separated: core/ ← data/ ← em/ ← cognitive/*

---

## 폴더·레이어 확인 (먼저 보기)

| 확인 목적 | 보는 곳 |
|-----------|---------|
| **행성 탐사 → 행성 구성 → 모듈 구성 → 천지창조 → 에덴 → 언더월드** | **[`LAYER_FLOW.md`](LAYER_FLOW.md)** · **[`FOLDER_MAP.md`](FOLDER_MAP.md)** |
| 코드·서사·문서 전체 위치 | **[`INDEX_CODE_AND_DOCS.md`](INDEX_CODE_AND_DOCS.md)** |

**폴더**: _01_beginnings(행성 탐사) → _02_creation_days(천지창조 day1~7) → _03_eden_os_underworld(에덴·OS·언더월드) → _04_firmament_era(궁창 환경시대) → _05_noah_flood(노아 대홍수).

---

## 폴더 구조 (정리)

**solar 최상위** = **시간 흐름 레이어** 하나. 상세: [`FOLDER_MAP.md`](FOLDER_MAP.md).

| 구분 | 폴더 | 설명 |
|------|------|------|
| **코드(시간축)** | _00_precreation, _01_physics_core, _02_firmament_fields, _03_land_surface, _04_biosphere_eden, _05_cognitive_moe, _06_governance_hades, _07_monitoring_siren, _09_bridge | 조→물리→필드→지표→생태→인지→규칙→경고→브리지. import는 `solar.day1`, `solar.eden` 등 별칭. |
| **문서·개념·폐기** | _meta/ (10_CODE, 20_CONCEPT, 90_LEGACY, concept) | 레이어 매핑·개념 문서. [_meta/20_CONCEPT/maps/LAYERS.md](_meta/20_CONCEPT/maps/LAYERS.md). |

레이어 순서·경로 표: [`20_CONCEPT/maps/LAYERS.md`](20_CONCEPT/maps/LAYERS.md)

---

## 개념 레이어 (Creation Days · 폴더 구조)

환경 설정이 **우주필드 → 태양계 중력장 → 빛 → 궁창 → 땅/바다/생명 → 넷째날 장주기 순환** 순서로 쌓인다고 보면 된다.

| 순서 | 개념 | 구현 폴더 (현재 구조) |
|------|------|------------------------|
| 0 | 우주필드·태양·태양계·달·지구 | `day4/core/`, `day4/data/` |
| 1 | 빛이 있으라 (EM 레이어) | `day1/` (`day1/em/*`) |
| 2 | 궁창 (대기/수순환) | `day2/` (`day2/atmosphere/*`) |
| 3 | 땅·바다·토양·식생·산불 Gaia | `day3/` (`day3/surface/*`, `day3/biosphere/*`, `day3/fire/*`, `bridge/gaia_loop_connector.py`) |
| 4 | 해·달·별·질소·Milankovitch·조석 | `day4/` (`day4/nitrogen/*`, `day4/cycles/*`, `day4/gravity_tides/*`) |
| 5 | 생물 이동·정보 네트워크 (새·물고기 transport) | `day5/` (`day5/mobility_engine`, `seed_transport`, `food_web`) |
| 6 | 진화 상호작용 (경쟁·변이·종 다양성) | `day6/` (`day6/species_engine`, `mutation_engine`, `interaction_graph`, `niche_model`) |
| 7~ | 인지·BrainCore 브리지 | `cognitive/`, `bridge/` |
| 지하 | 거시 룰 감시·의식 경고 (하데스 목소리) | `underworld/` |

**지하 → 지상 (서사 이어짐)**  
지하(underworld)는 **측정만** 하고, **의식 경고(ConsciousnessSignal)** 만 올린다. 그 신호를 받는 쪽은 **지상** — 에덴(EdenOS)·아담·항상성(Homeostasis)·무결성(IntegrityFSM)이다. Runner가 매 틱 하데스 목소리를 observe / homeostasis / integrity_fsm에 넣어 주기 때문에, **물리·항상성 한계선**을 넘으면 아담 OS가 자연스럽게 상태 전이(예: IMMORTAL → MORTAL_NPC)를 한다. 즉, “지하가 심판하는” 구조가 아니라 **지하가 재는 값 → 지상이 읽고 동역학이 전이**하는 흐름으로 본편 서사가 이어진다. 상세는 [underworld/README.md](underworld/README.md)와 [eden/](eden/) 쪽 문서를 이어서 보면 된다.

**직관용**: `concept/` 아래에 00_system → 01_light → … → 04_onward, **creation_days**, **pipeline_phases**, **maps** (레이어↔경로 표).  
**정의**: [`concept/maps/LAYERS.md`](concept/maps/LAYERS.md) 와 각 `dayN/README.md` 참고.

---: 작동 원리 / From Point Mass to Precession

```
① 점 질량 탄생
   빈 공간에 태양(대질량)과 지구(소질량) 두 점을 놓는다.
   지구에 초기 속도를 주면, 중력 F = GMm/r² 하나만으로
   안정된 타원 궤도가 형성된다. (케플러 궤도)

        태양 ●─────────────── ○ 지구
             ← F = GMm/r² →     v↑ (접선 속도)

② 바다 형성
   지구 표면에 12개 우물(well)을 배치한다.
   아직 외부 힘이 없으므로 우물은 원형 대칭.

③ 거대 충돌 (Giant Impact)
   외부 천체가 비스듬히 충돌 → 두 가지 결과:
   (a) 파편이 궤도에 진입 → 달 생성
   (b) 충돌 각운동량 전달 → 자전축이 23.44° 기울어짐
   이제 지구는 "기울어진 채 회전하는 편평 구(oblate spheroid)"가 된다.

                 자전축 ↗ (23.44° 기울어짐)
                  ╱
        지구 ── ○ ── 적도 팽대부 (J2)
                  ╲
                   달 ◦ (궤도 진입)

④ 조석 변형
   달의 중력은 지구에 균일하지 않다.
   가까운 쪽은 더 강하게, 먼 쪽은 더 약하게 당긴다.
   이 중력 구배(gradient)가 원형 우물을 타원으로 늘린다.

        달 ◦ ──→ 지구 우물: ○ → ⬮ (타원 변형)

⑤ 세차운동 발생 (핵심)
   지구는 편평하다 (적도가 볼록 = J2).
   자전축은 궤도면에서 23.44° 기울어져 있다.

   태양과 달이 이 볼록한 적도 부분을 당기면,
   자전축을 궤도면으로 "눕히려는" 토크가 발생한다.

   그런데 지구는 회전하고 있다 (각운동량 보유).
   회전하는 물체에 토크를 가하면 — 토크 방향이 아니라
   토크에 수직인 방향으로 축이 움직인다.
   (팽이가 쓰러지지 않고 원을 그리며 흔들리는 것과 같은 원리)

        토크 τ = (3GM/2r³) · J2 · R² · sin(2ε)
                  ↓
        자전축이 원뿔을 그리며 회전 (세차)
        주기 ≈ 25,000년, 방향 = 역행(retrograde)

             ↗ 자전축 (시간 t₁)
        ── ○ ──
             ↗  ↖ 자전축 (시간 t₂)  ← 축이 서서히 이동
        25,000년 후 한 바퀴 완성

⑥ 해류 패턴
   기울어진 자전 + 조석 변형 → 우물 간 수심 차이 발생
   수심 차이 → 압력 차이 → 유동 (해류)
   자전하는 계에서 유동 → 코리올리 편향
   결과: 위도별로 다른 와도(vorticity)와 해류 패턴이 자연 발생

        고위도: 강한 코리올리 → 서풍 편향
        적도:   약한 코리올리 → 직선 흐름
```

**정확한 의미 구분 (과장 방지):**

1. **세차 운동 자체는 하드코딩이 아니다.**
   세차 각도·주기·방향을 "정답으로 넣어둔" 것이 아니라,
   중력(F = GMm/r²)과 토크(τ = r × F)의 수치 적분 결과로
   자전축이 실제로 움직여서 역행 세차와 ~25,000년 주기가 나온다.

2. **다만, 세차가 가능한 상태(초기조건)는 이벤트로 구성한다.**
   달 생성, 자전 부여, J2 편평도 설정은 `giant_impact()` 데모 시나리오가
   사건으로 주는 구조(Phase 2)이다. "완전한 자연발생"이 아니라,
   **조건 설정 → 물리적 진행**의 2단계 구조.

3. **Ring Attractor는 세차의 원인이 아니다.**
   세차를 만드는 것은 태양·달의 중력 토크(EvolutionEngine).
   Ring Attractor는 세차로 생기는 방향 변화를
   인지 상태공간(관성 기억)으로 **매핑하는 레이어**다.

---

## 이 엔진이 증명하는 것 / What This Engine Demonstrates

1. **전체 태양계 N-body 중력장** — 10개 천체(태양+8행성+달)가
   실측 질량/거리로 100년간 안정 운행. 궤도 편차 < 1%.
2. **경사 세차(obliquity precession)는 중력 토크에서 자연 발생한다**
   — 편평(J2) 천체에 작용하는 토크로부터. 세차 전용 코드 없음.
3. **다행성 환경에서도 세차 정밀도 유지** — 24,763년 주기
   (NASA 25,772년 대비 3.9% 오차). 목성 섭동 포함.
4. **결합 궤도-스핀 역학**을 심플렉틱 립프로그 적분기로
   실제 질량비·거리비 하에서 재현할 수 있다.
5. **장기 수치 안정성** — 500,000 스텝에서 dE/E = 3.20×10⁻¹⁰.
6. **조석 변형 및 표면 해류**가 중력 구배와 코리올리 편향으로부터
   유체 솔버 없이 발생한다.

---

## 이 엔진이 주장하지 않는 것 / What This Engine Does NOT Claim

- 지구의 지구물리학적 진화를 완전히 재현한다.
- 일반상대론 보정을 포함한다 (수성 근일점 이동 등).
- 물리적 유사성으로 인지적 동치를 직접 증명한다.
- 실제 유체 난류, 기후 피드백, 대기 역학을 모델링한다.
- 고정밀 천체력 코드를 대체한다 (JPL DE 시리즈, REBOUND 등).

---

## 검증 결과 / Verification Results

### v1.0.0 — 전체 태양계 (10-body, 100년)

| 항목 | 시뮬레이션 | 관측값 (NASA) | 오차 |
|------|-----------|--------------|------|
| 세차 주기 | 24,763년 | 25,772년 | 3.9% |
| 세차 방향 | 역행(retrograde) | 역행(retrograde) | 일치 |
| 자전축 기울기 | 23.4403° | 23.44° | 일치 |
| 에너지 보존 | dE/E = 3.20×10⁻¹⁰ | — | PASS |
| 각운동량 보존 | dL/L = 3.04×10⁻¹⁴ | — | PASS |
| 궤도 안정성 | 전 행성 < 1% 편차 | — | PASS |

### 개별 행성 궤도 정밀도

| 행성 | 평균 거리(AU) | NASA a(AU) | 편차 |
|------|:---:|:---:|:---:|
| Mercury | 0.3872 | 0.3871 | 0.02% |
| Venus | 0.7233 | 0.7233 | 0.00% |
| Earth | 1.0009 | 1.0000 | 0.09% |
| Mars | 1.5236 | 1.5237 | 0.01% |
| Jupiter | 5.1963 | 5.2026 | 0.12% |
| Saturn | 9.5147 | 9.5549 | 0.42% |
| Uranus | 19.1065 | 19.2184 | 0.58% |
| Neptune | 29.8597 | 30.1104 | 0.83% |

### v1.3.0 — 빛이 있으라 / Let There Be Light

| 항목 | 결과 |
|------|------|
| 질량-광도 L(1.0 M☉) | 1.0000 L☉ (오차 0.00) |
| 역제곱 법칙 F ∝ 1/r² | 8행성 0.000% |
| 지구 평형 온도 (A=0.306) | 254 K (NASA 255 K, 0.4%) |
| 복사압-태양풍 비율 | 1.0000 (5행성) |
| core 에너지 보존 | dE/E = 4.49×10⁻¹⁰ |

전체 시뮬레이션 출력:
- [LET_THERE_BE_LIGHT_LOG.txt](../docs/LET_THERE_BE_LIGHT_LOG.txt) (v1.3.0, 빛이 있으라)
- [FULL_SOLAR_SYSTEM_LOG.txt](../docs/FULL_SOLAR_SYSTEM_LOG.txt) (v1.0.0, 10-body)
- [PRECESSION_VERIFICATION_LOG.txt](../docs/PRECESSION_VERIFICATION_LOG.txt) (v0.8.0, 3-body)

---

## 설치 및 실행 / Installation & Run

```bash
git clone https://github.com/qquartsco-svg/cookiie_brain.git
cd cookiie_brain

# 전체 태양계 10-body (100년, ~8분)
python examples/full_solar_system_demo.py

# 3체 세차운동 (50년, ~13초)
python examples/planet_evolution_demo.py
```

NumPy만 필요.

---

## 아키텍처 / Architecture

### 파일 구조 (v2.x — Creation Days 기준)

```text
solar/
├── __init__.py          ← 공개 API (Creation Days 인덱스 + legacy shim)
├── README.md            ← 지금 보고 있는 파일
├── LAYERS.md            ← 개념 레이어 정의
│
├── day1/                ← 첫째날: 빛이 있으라 (EM 레이어)
│   ├── __init__.py      ← `solar/em/*` 재export
│   └── em/              ← SolarLuminosity, MagneticDipole, SolarWind, Magnetosphere
│
├── day2/                ← 둘째날: 궁창 / Atmosphere
│   ├── __init__.py      ← AtmosphereColumn, AtmosphereComposition …
│   └── atmosphere/      ← greenhouse, column, water_cycle, _constants
│
├── day3/                ← 셋째날: 땅·바다·토양·식생·산불 Gaia
│   ├── __init__.py      ← SurfaceSchema, BiosphereColumn, FireEngine, GaiaLoopConnector …
│   ├── surface/         ← land_fraction, effective_albedo
│   ├── biosphere/       ← 토양 ODE, 생애주기, planet_bridge
│   └── fire/            ← FireEngine, FireEnvSnapshot, StressAccumulator
│
├── day4/                ← 넷째날: 중력장 + 질소 + Milankovitch + 조석
│   ├── __init__.py      ← EvolutionEngine, PlanetData, NitrogenCycle, MilankovitchCycle …
│   ├── core/            ← 3D N-body + 스핀·세차·조석 (중력 필드)
│   ├── data/            ← 태양계 상수 세트 (PLANETS, SUN_DATA)
│   ├── nitrogen/        ← NitrogenFixation, NitrogenCycle
│   ├── cycles/          ← Milankovitch 3-cycle + insolation driver
│   └── gravity_tides/   ← tidal mixing + ocean nutrients (탄소 펌프)
│
├── bridge/              ← BrainCore·Gaia 브리지 및 legacy 루프
│   ├── gaia_bridge.py           ← 뉴런 ↔ Gaia 환경 브리지
│   ├── gaia_loop_connector.py   ← Loop A/B/C (CO2, albedo, obliquity)
│   └── brain_core_bridge.py     ← BrainCore 환경 extension
│
├── cognitive/           ← 인지 레이어 (ring attractor, spin–ring coupling)
│   └── spin_ring_coupling.py
│
├── underworld/          ← 지하: 거시 감시·의식 경고 (Hades measure-only)
│   ├── __init__.py      ← ConsciousnessSignal, HadesObserver, make_hades_observer
│   ├── consciousness.py ← 신호 DTO (ConsciousnessSignal, SignalType)
│   ├── deep_monitor.py  ← DeepSnapshot, read_deep_snapshot (물리 코어 어댑터)
│   ├── hades.py         ← HadesObserver.listen(tick, world_snapshot?, deep_engine?)
│   └── rules.py         ← RuleSpec, DEFAULT_RULES, evaluate_rules() — 룰 데이터 분리
│
├── legacy/              ← 옛 파일 (central_body, tidal_field, orbital_moon …)
└── concept/, docs/, blockchain/ …
```

**의존 방향 규칙 (현재 구조)**:

```text
day4/data → day4/core ← cognitive/
                      ← day1/em
                      ← day2/atmosphere
                      ← day3/surface, day3/biosphere, day3/fire
                      ← bridge/* (Gaia, BrainCore)
```
- `day4/core` 는 상위 레이어를 **직접 import 하지 않음** (데이터/파라미터만 입력으로 받음).  
- `day1~day3` 레이어는 서로의 출력(env dict, driver output)만 읽고, 구현 세부는 숨김.  
- `bridge/` 는 Creation Days를 잇는 **관찰자/브리지 계층**으로, 물리 엔진을 수정하지 않고 상태만 읽어간다.  
- `underworld/` 는 **물리 코어(day4)를 직접 import 하지 않음**; `deep_monitor` 가 엔진을 선택 인자로 받아 스냅샷만 읽음. `solar.eden` 을 import 하지 않아, 추후 독립 패키지로 분리 시 의존성 단순.

### 주요 클래스

| 클래스 | 층 | 역할 |
|--------|------|------|
| `Body3D` | 물리 | 위치, 속도, 스핀 벡터, J2, 반지름, 관성모멘트 비 |
| `SurfaceOcean` | 물리 | 파라메트릭 표면 우물: 조석 변형, 압력 해류, 와도 |
| `EvolutionEngine` | 물리 | 심플렉틱 적분기 + 토크 결합 + 해양 업데이트 루프 |
| `PlanetData` | 데이터 | 행성 물리 상수 (불변, frozen dataclass) |
| `build_solar_system()` | 데이터 | NASA 데이터 → Body3D 변환 팩토리 |
| `MagneticDipole` | 전자기 | 자기쌍극자장: spin_axis 연동, B ∝ 1/r³ |
| `DipoleFieldPoint` | 전자기 | 관측 지점의 B 벡터 + 자기 위도 + L-shell |
| `SolarLuminosity` | 전자기 | 태양 광도: L=M^α, 조도, 온도, 복사압 |
| `IrradianceState` | 전자기 | 관측 지점의 복사 상태 (조도, 온도, 복사압) |
| `SolarWind` | 전자기 | 태양풍 플라즈마: 동압·플럭스·IMF, P ∝ 1/r² |
| `SolarWindState` | 전자기 | 관측 지점의 태양풍 상태 (압력, 플럭스, 방향) |
| `Magnetosphere` | 전자기 | 자기권: dipole vs P_sw 균형, 마그네토포즈, 차폐 |
| `MagnetosphereState` | 전자기 | 자기권 경계·차폐·쿠스프·에너지 유입 |
| `AtmosphereColumn` | 대기 | 0D 컬럼: 온실·열적 관성·대기압·물 상태 [Phase 6a] |
| `AtmosphereComposition` | 대기 | CO₂, H₂O, CH₄ 등 동적 조성 (outgassing 갱신 가능) |
| `RingAttractorEngine` | 인지 | 관성 기억: Mexican-hat bump attractor, 위상 보존 |
| `SpinRingCoupling` | 커플링 | 물리↔인지 필드 연결, 자전축 방위각 → Ring 위상 투영 |

### 시뮬레이션 단계

```
Phase 0 — 탄생:  태양 중력장에 점 질량 배치
Phase 1 — 바다:  표면 우물 형성 (12개 파라메트릭 우물)
Phase 2 — 충돌:  거대 충돌 → 달 방출, 자전축 23.44° 기울어짐
Phase 3 — 조석:  달 중력이 원형 우물을 타원으로 변형
Phase 4 — 세차:  태양+달 토크 → 자전축 역행 회전 (~25,000년 주기)
Phase 5 — 해류:  코리올리 + 조석 압력 → 표면 유동 패턴
Phase 6a— 궁창:  온실 τ→ε_a, 열적 관성, T_eq 254K → T_s 288K
Phase 6b— 수순환: 증발·응결·잠열, surface_heat_flux → SurfaceOcean
```

### 전자기 레이어 / EM Layer

core/(중력/세차) 위에 얹는 환경 필드 레이어.
궤도에 힘을 되먹이지 않는 **관측자 모드**로 동작한다.

| 모듈 | 물리 | 핵심 출력 |
|------|------|----------|
| `solar_luminosity.py` | 태양 광도, 복사 조도 | L, F(r), T_eq, P_rad |
| `magnetic_dipole.py` | 자기쌍극자장 B ∝ 1/r³ | B(x,t), 자기 위도 |
| `solar_wind.py` | 태양풍 플라즈마 P_sw ∝ 1/r² | 동압, 플럭스, IMF |
| `magnetosphere.py` | 자기권 경계 (B² vs P_sw) | r_mp, 차폐율 |

상세 물리 해설, 수식, 코드 상태공간, 파라미터:
**→ [solar/em/README.md](em/README.md)**

"빛이 있으라" 기록:
**→ [solar/em/light/](em/light/)** — 폴더를 열면 읽을 수 있다

---

### 언더월드(지하·하데스 목소리) / Underworld

물리 코어(day4)와 지상(EdenOS) 사이에서 **거시 룰 위반만 감시**하고, **의식 경고(ConsciousnessSignal)** 만 내보내는 레이어.  
서사상 “지하의 목소리”는 행위자가 아니라 **측정값**이다. 결정·처벌·전이는 모두 지상 동역학(IntegrityFSM, HomeostasisEngine)에서만 이루어진다.

**흐름 (서사 ↔ 로직)**  
1. **물리 코어** (day4/core, 선택) → `deep_monitor.read_deep_snapshot()` 로 자기장/열/중력 등 정상 여부 스냅샷 생성.  
2. **지하** `HadesObserver.listen(tick, world_snapshot=None, deep_engine=None)` → `evaluate_rules_all(deep)` 로 룰 평가 → **List[ConsciousnessSignal]** (위반 없으면 [QUIET], 복합 위반 시 여러 신호).  
3. **지상** EdenOS Runner가 매 틱 `hades.listen()` 호출 후, 반환 **리스트**를 `adam.observe(..., hades_signal)`, `homeostasis.update(..., hades_signal, ...)`, `integrity_fsm.step(tick, integrity)` 에 **강제 주입** (에이전트가 무시해도 동역학은 작동).  
4. 경고 severity가 stress/integrity에 반영되고, N 틱 연속으로 integrity가 θ 이하이면 자연 전이(MORTAL_NPC) 또는 선악과 시 즉시 강등.

**설계 규칙 (불가침)**  
- **Hades ONLY measures. Hades NEVER acts.**  
- 언더월드는 관측·신호 생성만 담당. 추방·권한 박탈·상태 전이는 Dynamics/IntegrityFSM 쪽 전용.  
- 이 경계가 유지될 때만 “해킹/스토리 진행형”이 아니라 “동역학적 한계선 → 자연스러운 전이” 구조가 유지된다.

**엔지니어링 (추후 독립 모듈화)**  
- **의존성**: `underworld` 는 `solar.eden` 을 import 하지 않음. `consciousness`, `deep_monitor`, `rules` 만 참조.  
- **진입점**: `listen(tick, world_snapshot=None, deep_engine=None) -> List[ConsciousnessSignal]` 하나. Runner가 리스트를 observe/homeostasis/integrity_fsm에 강제 주입.  
- **룰 정책**: `rules.py` 의 `RuleSpec`, `DEFAULT_RULES`, `evaluate_rules()` 로 분리됨. hades.py 는 오케스트레이션만 담당.  
- **스텁**: 물리 코어 없으면 `core_available=False` → QUIET 반환.  
상세 확장성·확장 포인트(world_snapshot 민감도 보정, 다중 신호): **→ [docs/UNDERWORLD_EXTENSIBILITY.md](../docs/UNDERWORLD_EXTENSIBILITY.md)**  
모듈 전용 개념·로직·API: **→ [solar/underworld/README.md](underworld/README.md)**

---

### 설정된 것 vs 창발된 것 / Prescribed vs. Emergent

| 요소 | 설정(Prescribed) | 창발(Emergent) |
|------|:---:|:---:|
| 중력 법칙 (F = GMm/r²) | O | — |
| 토크 법칙 (τ = r × F, J2 천체) | O | — |
| 초기 위치 & 속도 | O | — |
| 거대 충돌 이벤트 트리거 | O | — |
| 해양 우물 개수 (12) | O | — |
| 경사 세차운동 | — | **O** |
| 세차 주기 & 방향 | — | **O** |
| 조석 변형 패턴 | — | **O** |
| 표면 해류 방향 | — | **O** |
| 위도별 와도 분포 | — | **O** |

지배 방정식과 초기/경계 조건은 설정된다.
"창발"로 표시된 동역학 현상들은 명시적으로 코딩된 것이 아니라,
해당 방정식의 수치 적분으로부터 발생한다.

---

## 레이어 구조 / Layer Architecture (v1.6.0)

```
┌──────────────────────────────────────────────┐
│  인지 층 — RingAttractorEngine               │
│  Mexican-hat bump attractor                  │
│  위상 기억 + 안정화 + 관성 보존              │
│  φ(t) ∈ S¹                                   │
└──────────────┬───────────────────────────────┘
               │ 필드 결합 (coupling_strength)
               │ 물리 → 인지: 자전축 방위각 투영
               │ 인지 → 물리: 없음 (관측자 모드)
┌──────────────┴───────────────────────────────┐
│  대기 층 — atmosphere/ [Phase 6a/6b]        │
│  greenhouse: τ → ε_a, T_s = [F(1-A)/(fσ(1-ε/2))]^¼
│  column: C·dT/dt = F_in - F_out - Q_latent  │
│  water_cycle: e_sat(T), E, L_v×E            │
│  A from surface/, F from em/, core/ 읽기    │
└──────────────┬───────────────────────────────┘
               │ A = surface.effective_albedo()
┌──────────────┴───────────────────────────────┐
│  표면 층 — surface/ [Phase 7 / 셋째날]      │
│  SurfaceSchema: f_land, A_land, A_ocean      │
│  A_eff = f_land×A_land + (1-f_land)×A_ocean  │
└──────────────┬───────────────────────────────┘
               │ 독립 (em과 병렬)
┌──────────────┴───────────────────────────────┐
│  전자기 층 — em/                             │
│  solar_luminosity: L = M^α, F(r), T_eq      │
│  magnetic_dipole: B ∝ 1/r³                  │
│  solar_wind: P_sw ∝ 1/r²                     │
│  magnetosphere: dipole vs P_sw, r_mp         │
└──────────────┬───────────────────────────────┘
               │ spin_axis, pos 읽기 (관측자 모드)
┌──────────────┴───────────────────────────────┐
│  물리 층 — EvolutionEngine                   │
│  10-body 중력 + 스핀-궤도 토크 + 해양 역학   │
│  ŝ(t) ∈ S²                                   │
└──────────────┬───────────────────────────────┘
               │ build_solar_system()
┌──────────────┴───────────────────────────────┐
│  데이터 층 — solar/data/                     │
│  NASA/JPL 실측 상수 (PlanetData, frozen)     │
│  8행성 + 태양 + 달 질량/궤도/스핀            │
└──────────────────────────────────────────────┘
```

**의존 방향 규칙 (상호 참조 금지)**:
```
data/ → core/ ← cognitive/
              ← em/
              ← atmosphere/
```
- core는 상위 레이어를 **절대** import하지 않음
- em과 cognitive는 **서로** 참조하지 않음
- atmosphere는 em/, core/ 읽기 전용
- 각 레이어는 독립 기어

검증 결과 (v1.0.0):

| 항목 | 결과 |
|------|------|
| 물리 보존 (dE/E) | 3.20×10⁻¹⁰ — PASS (10-body, 100yr) |
| 각운동량 보존 (dL/L) | 3.04×10⁻¹⁴ — PASS |
| 세차 주기 | 24,763 yr (NASA 25,772 yr, 3.9%) — PASS |
| 전 행성 궤도 편차 | < 1% — PASS |
| Ring 위상 추적 오차 | 평균 0.12° — PASS (v0.9.0) |
| Ring 안정성 | 0.908 — PASS (v0.9.0) |
| 표면 자기장 정확도 | 적도/극/중위도 오차 0.00% — PASS (v1.1.0) |
| 1/r³ 감쇠 법칙 | 오차 0.00% — PASS (v1.1.0) |
| 세차-자기장 연동 | 자기축 기울기 11.50° 보존 — PASS (v1.1.0) |
| 태양풍 1/r² 법칙 | 5행성 오차 0.00% — PASS (v1.2.0) |
| 마그네토포즈 | 7.58 R_E (5-20 범위) — PASS (v1.2.0) |
| BS/MP 비율 | 1.30 — PASS (v1.2.0) |
| 차폐 지표 | 0.78 (>0.7) — PASS (v1.2.0) |
| 세차-자기권 연동 | 동기 확인 — PASS (v1.2.0) |
| 온실 T_eq→T_s | 254K → 288K (+34K) — PASS (v1.4.0) |
| 열적 관성 τ_th | ~2 yr — PASS (v1.4.0) |
| 기어 분리 (6a) | dE/E = 4.06×10⁻¹² — PASS |
| 수순환 H₂O/잠열 | ocean_extras 연동 — PASS (v1.5.0) |
| 기어 분리 (6b) | dE/E < 1e-5 — PASS |

검증: `examples/atmosphere_demo.py`, `examples/water_cycle_demo.py`

**EM / atmosphere / cognitive 레이어는 관측자(observer) 모드로 동작한다:**
- core/의 `Body3D.spin_axis`, `.pos` 등을 **읽기 전용**으로 참조
- 궤도·자전에 힘·토크를 되먹이지 않음 (로렌츠 힘, 자기 토크 없음)
- 물리 엔진(core/)의 에너지·각운동량 보존에 영향을 주지 않음

이 분리는 의도적이다: EM/cognitive는 "환경 필드"이지 "역학 피드백"이 아니다.
향후 로렌츠 힘이나 자기 감속 토크를 도입할 경우,
별도의 **피드백 커플링 레이어**를 추가해야 하며, core/ 내부를 직접 수정하지 않는다.

---

## 단위 체계 / Unit System

이 엔진은 **전 레이어 무차원(dimensionless) 단위**를 사용한다.
SI 변환이 필요하면, 각 기준값에 실제 물리 상수를 곱한다.

| 물리량 | 기준(= 1.0) | 실제 환산 | 레이어 |
|--------|-------------|-----------|--------|
| 거리 | 1 AU | 1.496 × 10¹¹ m | 전체 |
| 시간 | 1 yr | 3.156 × 10⁷ s | 전체 |
| 질량 | 1 M☉ | 1.989 × 10³⁰ kg | 전체 |
| 중력 상수 | G = 4π² AU³/(M☉·yr²) | 6.674 × 10⁻¹¹ SI | core/ |
| 자기장 | B₀ = 표면 적도 자기장 | 지구: 31 μT | em/ |
| 태양풍 동압 | P₀ = 1 AU 동압 | ~2.0 nPa | em/ |
| 태양풍 속도 | v₀ = 1 AU 속도 | ~400 km/s | em/ |
| IMF 세기 | B_sw₀ = 1 AU IMF | ~5 nT | em/ |

**왜 무차원인가:**
- core/(중력/세차)와 em/(자기장/태양풍) 사이에 단위 변환 레이어가 불필요
- 각 모듈의 출력은 기준값 대비 비율이므로, 레이어 간 결합 시 스케일 충돌 없음
- SI가 필요한 경우: `B_real = B * 31e-6` (지구), `P_real = P * 2e-9` (Pa)

---

## 파라미터 정책 / Parameter Policy

**이 엔진의 물리 법칙(방정식)은 하드코딩되지 않는다.**
세차 각도·주기·방향은 "정답으로 넣어둔" 것이 아니라,
중력과 토크의 수치 적분 결과로 발생한다.

**다만, 지구 물리 상수(시나리오 파라미터)는 외부에서 주어진다:**

| 파라미터 | 기본값 | 출처 | 의미 |
|----------|--------|------|------|
| J2 (편평도) | 1.0826×10⁻³ | NASA | 적도 팽대의 크기 |
| C/(MR²) (관성모멘트 비) | 0.3307 | NASA | 세차 토크 응답 스케일 |
| tilt_deg (자기축 기울기) | 11.5° | 관측값 | 자전축 대비 자기축 오프셋 |
| magnetic_pressure_ratio | 1.9×10⁵ | 유도값 | B₀²/(2μ₀P₀) 무차원 비율 |
| bow_shock_ratio | 1.3 | 관측 근사 | 보우쇼크/마그네토포즈 비 |
이것들은 `__init__` 파라미터로 외부에서 변경 가능하다.
**알고리즘이 답을 강제하지 않는다. 방정식이 답을 만든다.**
단, 방정식에 들어가는 물리 상수는 파라미터로 주어진다.

---

## 한계 / Limitations

| 한계 | 영향 |
|------|------|
| 뉴턴 중력만 사용 | GR 보정 없음 (수성 근일점, 관성계 끌림) |
| 단순화된 J2 모델 | 고차항 (J4, J6) 생략 |
| 조석 소산 없음 | 달이 후퇴하지 않음; 지구 자전이 느려지지 않음 |
| 달 궤도면 고정 | 완전한 장동 (18.6년 주기) 미재현 |
| 파라메트릭 해양 모델 | 유체 솔버가 아님; 우물은 기하학적, 유체역학적이 아님 |
| 강체 가정 | 맨틀 대류, 탄성 변형, 핵-맨틀 결합 없음 |
| 대기 결합 없음 | 기후, 알베도, 온실 피드백 부재 |
| ~~2체 토크~~ | ~~다행성 세차 섭동 미포함~~ → **v1.0.0에서 해결** |

이 엔진은 **핵심 스핀-궤도 결합 역학**을 정확히 재현한다.
완전한 지구물리 시뮬레이터는 아니다.

---

## 확장 가능성 / Extension Possibilities

### 루트 A — 물리 정밀화

| 확장 | 효과 | 상태 |
|------|------|------|
| ~~다행성 (수성~해왕성)~~ | ~~완전 태양계 N-body~~ | **v1.0.0 완료** |
| ~~자기쌍극자장~~ | ~~자전축 연동 자기장 표현~~ | **v1.1.0 완료** |
| ~~태양풍 / 복사압~~ | ~~1/r² 입자·광자 흐름~~ | **v1.2.0 완료** |
| ~~자기권~~ | ~~dipole vs P_sw 균형~~ | **v1.2.0 완료** |
| J4, J6 중력 고조파 | 세차 정밀도 향상 | 미정 |
| 장동 (달 교점 퇴행) | 세차 위 18.6년 진동 | 미정 |
| 조석 소산 | Gyr 스케일 달 후퇴 + 지구 자전 감속 | 미정 |

→ 지구물리학적으로 현실적인 지구-달 진화 시뮬레이터 방향.

### 루트 B — 인지 동역학 (CookiieBrain 통합)

| 확장 | 효과 |
|------|------|
| CookiieBrainEngine 결합 | 2D 메인 엔진 ↔ 3D 진화 엔진 |
| 해류 위 정보 입자 | 표면 흐름을 따라 데이터 유동 |
| 다체 인지 공명 | 다중 기억 질량의 궤도 공명 |
| 가치축 추적 | 인지 기준 프레임의 장기 드리프트 |

→ 동역학 기반 AI 아키텍처 방향.
유비 프레임워크는 [부록: 인지 매핑](#부록-인지-매핑-구조적-유비--appendix-cognitive-mapping) 참조.

### 루트 C — 분산 엣지 AI

| 확장 | 효과 |
|------|------|
| 행성 → 물리 디바이스 | 각 엣지 노드가 자율 실행 (자전 = 로컬 처리) |
| 중력장 → 네트워크 프로토콜 | 결합 강도가 1/r²로 감쇠 (거리 가중 영향) |
| 은하 스케일 | 다중 태양계 = 다중 인지 클러스터 |

→ 필드 기반 분산 엣지 AI 네트워크 방향.

상세 로드맵: [docs/COGNITIVE_SOLAR_SYSTEM.md](../docs/COGNITIVE_SOLAR_SYSTEM.md)

---

## 최소 사용 예 / Minimal Usage

### 전체 태양계 (v1.0.0)

```python
from solar import EvolutionEngine, Body3D, build_solar_system

engine = EvolutionEngine()
for d in build_solar_system():
    if "_moon_config" in d:
        cfg = d["_moon_config"]
        engine.giant_impact(cfg["target"], **{k: v for k, v in cfg.items() if k != "target"})
    else:
        engine.add_body(Body3D(**d))

for _ in range(500_000):
    engine.step(0.0002, ocean=False)

print(f"dE/E = {abs((engine.total_energy() - E0) / E0):.2e}")
```

### 3체 세차 (v0.8.0 호환)

```python
from solar import EvolutionEngine, Body3D
import numpy as np

engine = EvolutionEngine()
engine.add_body(Body3D("Sun",   mass=1.0,  pos=[0,0,0], vel=[0,0,0]))
engine.add_body(Body3D("Earth", mass=3e-6, pos=[1,0,0], vel=[0, 2*np.pi, 0],
               radius=4.26e-5))
engine.giant_impact("Earth", obliquity_deg=23.44, spin_period_days=1.0)

for _ in range(250_000):
    engine.step(0.0002)
```

---

## 관련 파일 / Related Files

| 파일 | 경로 | 설명 |
|------|------|------|
| 물리 엔진 | [`solar/core/evolution_engine.py`](core/evolution_engine.py) | Body3D, SurfaceOcean, EvolutionEngine |
| 중력 우물 | [`solar/core/central_body.py`](core/central_body.py) | CentralBody (태양 1/r) |
| 달 궤도 | [`solar/core/orbital_moon.py`](core/orbital_moon.py) | OrbitalMoon (타원 공전 + 조석) |
| NASA 데이터 | [`solar/data/solar_system_data.py`](data/solar_system_data.py) | 8행성+태양+달 실측 상수 + 빌더 |
| 태양 광도 | [`solar/em/solar_luminosity.py`](em/solar_luminosity.py) | SolarLuminosity (L=M^α, 조도, 온도, 복사압) |
| 자기쌍극자 | [`solar/em/magnetic_dipole.py`](em/magnetic_dipole.py) | MagneticDipole (B ∝ 1/r³, 11.5° 기울기) |
| 태양풍 | [`solar/em/solar_wind.py`](em/solar_wind.py) | SolarWind (P ∝ 1/r², 동압+플럭스+IMF) |
| 자기권 | [`solar/em/magnetosphere.py`](em/magnetosphere.py) | Magnetosphere (Chapman-Ferraro, 차폐, 쿠스프) |
| EM 문서 | [`solar/em/README.md`](em/README.md) | EM 물리+엔지니어링 전체 참조 |
| 빛이 있으라 | [`solar/em/light/`](em/light/) | Phase 5 기록 (폴더 열면 README) |
| 관성 기억 엔진 | [`solar/cognitive/ring_attractor.py`](cognitive/ring_attractor.py) | RingAttractorEngine (Mexican-hat bump) |
| 커플링 레이어 | [`solar/cognitive/spin_ring_coupling.py`](cognitive/spin_ring_coupling.py) | SpinRingCoupling (물리↔인지 필드 연결) |
| 태양계 데모 | [`examples/full_solar_system_demo.py`](../examples/full_solar_system_demo.py) | 10-body 전체 태양계 검증 |
| 세차 데모 | [`examples/planet_evolution_demo.py`](../examples/planet_evolution_demo.py) | 6단계 전과정 실행 |
| 커플링 데모 | [`examples/spin_ring_coupling_demo.py`](../examples/spin_ring_coupling_demo.py) | 물리↔인지 통합 검증 |
| 자기쌍극자 데모 | [`examples/magnetic_dipole_demo.py`](../examples/magnetic_dipole_demo.py) | Phase 2 단독 검증 |
| EM 통합 데모 | [`examples/em_layer_demo.py`](../examples/em_layer_demo.py) | Phase 2+3+4 통합 검증 |
| EM 통합 로그 | [`docs/EM_LAYER_LOG.txt`](../docs/EM_LAYER_LOG.txt) | Phase 2+3+4 ALL PASS 출력 |
| 대기권 데모 | [`examples/atmosphere_demo.py`](../examples/atmosphere_demo.py) | Phase 6a 궁창 8항목 ALL PASS |
| 수순환 데모 | [`examples/water_cycle_demo.py`](../examples/water_cycle_demo.py) | Phase 6b 수순환 5항목 ALL PASS |
| 대기 README | [`solar/atmosphere/README.md`](atmosphere/README.md) | 궁창·수순환 물리 개념 |
| 표면 데모 | [`examples/surface_day3_demo.py`](../examples/surface_day3_demo.py) | Phase 7 셋째날 4항목 ALL PASS |
| 자기장 로그 | [`docs/MAGNETIC_DIPOLE_LOG.txt`](../docs/MAGNETIC_DIPOLE_LOG.txt) | Phase 2 검증 출력 |
| 태양계 로그 | [`docs/FULL_SOLAR_SYSTEM_LOG.txt`](../docs/FULL_SOLAR_SYSTEM_LOG.txt) | 10-body 100년 검증 출력 |
| 세차 로그 | [`docs/PRECESSION_VERIFICATION_LOG.txt`](../docs/PRECESSION_VERIFICATION_LOG.txt) | 3-body 세차 출력 |
| 개념 문서 | [`docs/COGNITIVE_SOLAR_SYSTEM.md`](../docs/COGNITIVE_SOLAR_SYSTEM.md) | 인지 매핑 & 로드맵 |
| 확장 가능성 | [`docs/CREATION_ENGINE_SCALE_UP.md`](../docs/CREATION_ENGINE_SCALE_UP.md) | ESM/GCM 코어 병렬, 스케일 업·마이크로 스텝 개념도 |
| **언더월드** | [`solar/underworld/README.md`](underworld/README.md) | 지하 거시 감시·의식 경고 — 개념·로직·API (엔지니어링) |
| 언더월드 확장성 | [`docs/UNDERWORLD_EXTENSIBILITY.md`](../docs/UNDERWORLD_EXTENSIBILITY.md) | 룰 분리, world_snapshot·다중 신호 확장 포인트 |
| 블록체인 서명 | [`blockchain/pham_chain_evolution_engine.json`](../blockchain/pham_chain_evolution_engine.json) | PHAM A_HIGH (0.9999) |

---

## 부록: 인지 매핑 (구조적 유비) / Appendix: Cognitive Mapping

> **범위 주의:** 아래 매핑은 *구조적 유비(structural analogy)*이며,
> 증명된 기능적 동치가 아니다. 유사한 미분방정식이 지배하는 두 시스템은
> 구조적으로 유사한 끌개(attractor)와 위상 공간 거동을 보일 수 있다.
> 이것이 물리 현상과 인지 현상 사이의 **의미적 또는 기능적 동치를
> 함의하지는 않는다.**
>
> *The mappings below are structural analogies — not proven functional
> equivalences. Similar differential equations may yield structurally
> similar attractors and phase-space behaviors. This does not imply
> semantic or functional equivalence between physical and cognitive phenomena.*

### 유비 테이블 / Analogy Table

| 물리 현상 | 수학 구조 | 인지 해석 |
|-----------|-----------|-----------|
| 중력 F = GMm/r² | 보존적 인력 장 | 기억 간 끌림 (장기기억이 당김) |
| 공전 (궤도 운동) | 해밀턴 흐름 | 인지 상태 전이 |
| 자전 (회전) | 자율 각운동량 | 독립 내부 처리 (엣지 노드) |
| 세차운동 | 장주기 축 회전 | 가치관/관점 기준 프레임의 점진적 이동 |
| 조석 변형 | 외부 구배에 의한 재형성 | 무의식이 의식 지형을 변형 |
| 해류 | 코리올리 하 구속 유동 | 인지 회전 하의 사고 흐름 패턴 |

### 상태 벡터 재해석 / State Vector Reinterpretation

```
물리:  State = (positions, velocities, spin_vectors)
인지:  State = (memory_positions, activation_levels, value_axes)
```

지배 방정식은 이 재해석 하에서 동일하게 유지된다.
이 구조적 대응이 의미 있는 인지 예측을 생성하는지는
**열린 연구 질문이며, 확정된 주장이 아니다.**

### 구체적 메커니즘 (가설) / Concrete Mechanisms (Hypothetical)

- 기억 A → B 최적 전이 = 호만 전이 궤도
- 외부 충격 흡수 = 목성형 대질량에 의한 섭동 포획
- 창의적 연상 = 조석력이 우물 장벽을 낮춤 → 상태 터널링
- 세계관 변화 = 가치축의 장기 세차운동

**위 메커니즘은 향후 조사를 위한 가설적 유비이며, 검증된 모델이 아니다.**

---

---

## Eden 독립 탐색 엔진 / Eden Search Engine (v2.0)

> **"에덴은 좌표가 아니라 파라미터 상태(state basin)이다"**

Day1~7 물리 행성 위에 올라오는 **행성 거주 가능성 탐색 레이어**.
지구뿐 아니라 외계 행성(Exoplanet) 탐사에도 즉시 투입 가능한 독립 엔진.

### 구조

```
solar/eden/
├── firmament.py          — 궁창(수증기 캐노피) 물리 모델
├── flood.py              — 대홍수 전이 곡선 (4단계)
├── initial_conditions.py — 6개 파라미터 → 전 지구 상태 동역학 (EDEN_IC_CONFIG)
├── geography.py          — 자기장 좌표계 + 시대별 지형
├── search.py             — EdenSearchEngine (파라미터 공간 탐색)
├── exploration.py        — EdenExplorationGrid: 12밴드 탐사 + Grid Engine 포커스 연동
├── eden_search_demo.py   — 에덴 탐색 전체 데모 (Grid 연동 출력)
└── biology.py            — 물리 환경 → 수명/체형/생태계 안정성
```

**Grid Engine 연동** (선택): `solar/bridge/grid_engine_bridge.py` — 2D~7D 확장, `create_latitude_grid_agent()`, `get_max_grid_dimension()`. 탐색 시 포커스 밴드 반영 트림 + 결과 `grid_agent`.

### 탐색 결과 (antediluvian 기준)

| 항목 | 에덴 | 현재 지구 |
|------|------|-----------|
| Eden Score | **1.000** | 0.000 |
| 추정 수명 | **196~212yr** | 80yr |
| 추정 신장 | **188~190cm** | 170cm |
| 거대동물 | ✅ 가능 | ❌ |
| 안정 생태계 | ✅ | ❌ |
| 빙하 밴드 | 0/12 | 4/12 |

### 탐색 공간 프리셋

| 프리셋 | 용도 |
|--------|------|
| `make_antediluvian_space()` | 창세기 에덴 환경 |
| `make_postdiluvian_space()` | 현재 지구 기준 |
| `make_exoplanet_space()` | 외계 행성 거주 가능성 스크리닝 |

### 빠른 실행

```bash
# 에덴 탐색 전체 데모 (5단계)
python -m solar.eden.eden_search_demo

# 에덴 환경 시뮬레이션 (궁창→대홍수→이후)
python -m solar.eden.eden_demo
```

### 블록체인 서명 (PHAM)

| 파일 | 블록 | 점수 |
|------|------|------|
| `initial_conditions.py` | A_HIGH | 1.0000 |
| `search.py` | A_HIGH | 0.9999 |
| `exploration.py` | A_HIGH | 0.9993 |
| `biology.py` | A_HIGH | 1.0000 |
| `geography.py` | A_HIGH | 1.0000 |
| `firmament.py` | A_HIGH | 1.0000 |
| `flood.py` | A_HIGH | 1.0000 |
| `bridge/grid_engine_bridge.py` | A_HIGH | 0.9996 |

---

*v2.0.0 · PHAM Signed · GNJz (Qquarts)*
