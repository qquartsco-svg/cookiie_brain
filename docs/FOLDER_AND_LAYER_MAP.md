# 작업 파일 위치 및 레이어 정리

---

## 0. 서사 vs 독립 엔진 — 두 개 따로 감 (폴더 구조 원칙)

| 구분 | 위치 | 내용 |
|------|------|------|
| **서사 + 레이어** | **CookiieBrain 안** | 지금까지 말한 모든 개념이 여기 레이어로 쌓임. `solar/` (eden, planet_dynamics, firmament, underworld …), `cookiie_brain/`, `docs/` |
| **독립 엔진 모듈** | **00_BRAIN/ENGINE_HUB/** | 엔지니어링적으로 독립 가능한 건 엔진으로 만들어서 **따로** 레이어 폴더에 저장. `00_PLANET_LAYER/`, `10_AUTONOMIC_LAYER/`, … `60_APPLIED_LAYER/` |

- **CookiieBrain 안에 ENGINE_HUB 두지 않음.** 독립 엔진은 00_BRAIN 직하 ENGINE_HUB 레이어에만 둠.
- 서사·레이어 = CookiieBrain. 독립 엔진 = ENGINE_HUB. 같이 따로 간다.

**00_BRAIN 직하 독립 엔진 레이어 폴더:**

```
00_BRAIN/
├── CookiieBrain/             ← 서사 + 레이어 (위 §2)
└── ENGINE_HUB/               ← 독립 엔진만. 레이어별 저장
    ├── 00_PLANET_LAYER/      ← Joe_Engine, Cherubim_Engine, GaiaFire_Engine 등
    ├── 10_AUTONOMIC_LAYER/
    ├── 20_LIMBIC_LAYER/
    ├── 30_CORTEX_LAYER/
    ├── 40_SPATIAL_LAYER/
    ├── 50_DIAGNOSTIC_LAYER/
    └── 60_APPLIED_LAYER/
```

---

## 1. 루트 경로

| 경로 | 의미 |
|------|------|
| `/Users/jazzin/Desktop/00_BRAIN/` | 00_BRAIN 생태계 루트 |
| `/Users/jazzin/Desktop/00_BRAIN/CookiieBrain/` | CookiieBrain 프로젝트 (환경 물리 + 인지) |

**상태공간이 표현되는 곳**: `CookiieBrain/solar/` + `CookiieBrain/cookiie_brain/`  
BrainCore와 연동 시: `BrainCore`의 `GlobalState` (extensions)

---

## 2. CookiieBrain 폴더 구조 (서사·레이어만. 독립 엔진 없음)

```
CookiieBrain/
├── solar/                    ← ★ 환경 물리·서사 레이어 (상태공간 핵심)
│   ├── core/                 ← 물리 코어 (EvolutionEngine, Body3D, SurfaceOcean)
│   ├── data/                 ← NASA 상수, build_solar_system()
│   ├── em/                   ← 전자기 (광도, 자기장, 태양풍, 자기권)
│   ├── surface/              ← 표면 (땅-바다, 알베도) [Phase 7]
│   ├── atmosphere/           ← 대기 (온실, 수순환) [Phase 6a/6b]
│   ├── cognitive/            ← 인지 (Ring Attractor)
│   ├── eden/                 ← EdenOS, Firmament, JOE 연동 (서사 레이어)
│   ├── planet_dynamics/      ← L2 스냅샷→stress/instability (로컬 구현)
│   ├── underworld/           ← Hades, Siren, rules (서사 레이어)
│   ├── brain_core_bridge.py  ← BrainCore extension 연동
│   └── __init__.py
│
├── cookiie_brain/            ← 퍼텐셜장·Hippo·분석 (기존)
│   ├── trunk/                ← Phase A/B/C (자전, 공전, 요동)
│   ├── hippo/                ← HippoMemoryEngine
│   ├── analysis/             ← Layer 1~6
│   └── cookiie_brain_engine.py
│
├── examples/                 ← 검증·데모 스크립트
├── docs/                     ← 문서 (전략, 설계, 점검)
│
└── standalone_build/        ← 독립 엔진 소스(복사용). 배포 위치는 00_BRAIN/ENGINE_HUB
    └── Joe_Engine/           → 00_BRAIN/ENGINE_HUB/00_PLANET_LAYER/Joe_Engine 에 복사
```

---

## 3. 레이어별 상태공간 표현

| 레이어 | 경로 | 상태 변수 |
|--------|------|-----------|
| **data** | `solar/data/` | PlanetData, NASA 상수 (frozen) |
| **core** | `solar/core/` | pos, vel, spin_axis, depths[], vorticity[] |
| **em** | `solar/em/` | F(r), B(x), P_sw, r_mp (관측 결과) |
| **surface** | `solar/surface/` | land_fraction, albedo_land, albedo_ocean |
| **atmosphere** | `solar/atmosphere/` | T_surface, P_surface, composition, water_phase |
| **cognitive** | `solar/cognitive/` | Ring 위상 φ |
| **bridge** | `solar/brain_core_bridge.py` | solar_environment extension (dict) |

---

## 4. 상태공간이 “살아 있는” 곳

### (A) solar/ 내부

- **EvolutionEngine** (`core/evolution_engine.py`): bodies[].pos, vel, spin_axis, oceans[].depths
- **AtmosphereColumn** (`atmosphere/column.py`): T_surface, composition, _tau, _eps_a
- **SurfaceOcean** (`core/evolution_engine.py`): depths[], current_vel[], vorticity[]

### (B) BrainCore 연동 시

- **GlobalState** (`BrainCore`): state_vector, extensions
- **solar_environment** extension: bodies[Earth].F_solar, T_surface, P_surface, habitable, water_phase

---

## 5. 00_BRAIN 루트 문서

| 경로 | 내용 |
|------|------|
| `00_BRAIN/docs/GEAR_CONNECTION_STRATEGY.md` | 기어 연결 전략, 00_BRAIN 생태계 |

---

## 6. 의존 방향 (import 규칙)

```
data/ → core/ ← em/
              ← surface/ (독립)
              ← atmosphere/ (em, surface 읽기)
              ← cognitive/
              ← brain_core_bridge (solar 내부만 사용)
```

- `core/`는 상위 레이어를 **import하지 않음**
- `surface/`는 의존 없음
- `atmosphere/`는 em/, surface/ **읽기 전용**

---

## 7. 요약

| 질문 | 답 |
|------|-----|
| **작업 파일 위치** | `CookiieBrain/solar/`, `CookiieBrain/docs/`, `CookiieBrain/examples/` |
| **상태공간 표현** | `solar/core/`, `solar/atmosphere/`, `solar/em/` + BrainCore `GlobalState.extensions` |
| **루트 폴더** | `/Users/jazzin/Desktop/00_BRAIN/CookiieBrain/` |
| **환경 물리 핵심** | `solar/` (core → em → surface → atmosphere → cognitive) |

---

## 8. JOE + EdenOS 레이어 스택 — 파일·폴더·문서 위치

(조/모 = Macro–Micro, docs/PLANET_DYNAMICS_ENGINE.md, PANGEA_ROTATION_AND_WATER_BUDGET.md 기준)  
**런타임 의존 방향**(루시퍼→JOE→궁창→MOE→UnderWorld/Siren) 및 **역할 고정·하데스 Authoring**은 **§9** 참조.

### 8.1 레이어가 쌓이는 순서

```
L0/L1 (Macro, 조)  →  L2 (JOE observe/analyze)  →  L3 (Firmament)  →  scenario_overlay  →  EdenOS World  →  Cherubim
     ↑                        ↑                          ↑                   ↑                    ↑
  IC 슬롯              planet_dynamics             firmament.py         eden_world.py        eden_os/
```

### 8.2 구현 위치 (파일·폴더)

| 레이어/역할 | 폴더/파일 | 설명 |
|-------------|-----------|------|
| **L0/L1 슬롯 (Macro)** | `solar/eden/initial_conditions.py` | `InitialConditions`: omega_spin_rad_s, obliquity_deg, GEL_surface_eden_m, W_canopy_ref_km3. make_antediluvian(), make_postdiluvian(). |
| **L2 (JOE Engine)** | `solar/planet_dynamics/__init__.py` | `compute_planet_stress_and_instability(ic, water_snapshot)` → (planet_stress, instability). PANGEA §4 로컬 구현. |
| **L3 (궁창·붕괴)** | `solar/eden/firmament.py` | `FirmamentLayer`, `step(dt_yr, instability=...)`, `get_layer0_snapshot()` → shield_strength, env_load. |
| **통합 Runner** | `solar/eden/eden_os/eden_os_runner.py` | 매 틱: JOE 호출 → instability → firmament.step(instability) → scenario_overlay → make_eden_world(scenario_overlay). |
| **환경 월드** | `solar/eden/eden_os/eden_world.py` | `make_eden_world(ic, scenario_overlay)` → EdenWorldEnv, layer["SCENARIO"] 에 S, env_load 반영. |
| **수명 엔진** | `solar/eden/eden_os/homeostasis_engine.py` | world.layer["SCENARIO"]["shield_strength"], env_load 읽어 수명·integrity 계산. |
| **통합 검증** | `solar/eden/eden_os/lifespan_flood_sim.py` | FirmamentLayer 루프 + scenario_overlay 로 "붕괴→수명" 체인 검증. `--integration` 옵션. |
| **Eden 탐색(체루빔)** | `solar/eden/eden_os/cherubim_guard.py`, `solar/eden/search.py` | 행성 내부 최적 입지·접근 제어. |

### 8.3 관련 문서 위치

| 문서 | 경로 | 내용 |
|------|------|------|
| JOE 명칭·Observer 철학·계층 | `docs/PLANET_DYNAMICS_ENGINE.md` | JOE = Joe Observer Engine 확정, observe→analyze→detect, Level 1/2/3 다이어그램. |
| 레이어 L0~L3·물예산·GEL | `docs/PANGEA_ROTATION_AND_WATER_BUDGET.md` | L0(자전)·L1(물)·L2(stress, instability)·L3(Firmament), 조/모=Macro–Micro. |
| 파인만·조/모·Macro–Micro | `docs/FEYNMAN_VOL1_AS_PLANET_MOTION.md` | 1권 로직, Joe/Moe 관측자, JOE/MOE 예약. |
| 수명·에너지 예산 | `docs/LIFESPAN_ENERGY_BUDGET_CONCEPT.md` | S(t), env_load, expected_lifespan. |
| 궁창 붕괴 동역학 | `docs/FIRMAMENT_COLLAPSE_DYNAMICS.md` | instability ≥ θ, FloodEvent. |

### 8.4 solar/ 내 트리 (JOE·Eden 관련만)

```
solar/
├── planet_dynamics/          ← JOE Engine (L2)
│   └── __init__.py           ← compute_planet_stress_and_instability()
├── eden/
│   ├── initial_conditions.py ← L0/L1 슬롯 (InitialConditions)
│   ├── firmament.py          ← L3 FirmamentLayer
│   ├── eden_os/
│   │   ├── eden_os_runner.py ← 통합: JOE → firmament → scenario_overlay → world
│   │   ├── eden_world.py     ← make_eden_world(ic, scenario_overlay)
│   │   ├── homeostasis_engine.py
│   │   ├── lifespan_flood_sim.py
│   │   ├── lifespan_budget.py
│   │   ├── cherubim_guard.py
│   │   └── ...
│   └── search.py             ← Eden 탐색
└── ...
```

### 8.5 호출 흐름 (한 틱)

1. `EdenOSRunner._execute_tick()`  
2. `instability = self._compute_instability()` → 내부에서 `compute_planet_stress_and_instability(self._world.ic)` 호출 (solar.planet_dynamics)  
3. `self._firmament.step(dt_yr=1.0, instability=instability)`  
4. `layer0 = self._firmament.get_layer0_snapshot()`  
5. `scenario_overlay = { "shield_strength": layer0.shield_strength, "env_load": layer0.env_load, ... }`  
6. `self._world = make_eden_world(ic=self._world.ic, scenario_overlay=scenario_overlay)`  
7. 이후 Step 1~7 (rivers, tree, guard, agents, lineage, log) 에서 `self._world` 사용.

---

## 9. 레이어 흐름 — 의존 방향·역할 고정 (권장)

전체 의도: **관측(조) → 내부탐색(모) → 환경전이(궁창) → 내부코어(지질/유체) → 규칙편집(룰) → 경고/모니터링**.  
역할 중복을 제거하고 **의존 방향** 기준으로 재정렬한 최종 정의다.

### 9.1 역할 충돌 정리 (레이어 책임 분리)

| 문제 지점 | 분리 원칙 | 고정 정의 |
|-----------|-----------|-----------|
| **MOE(내부 탐색) vs 루시퍼(내부 구조)** | 루시퍼 = 원인계(물리 생성/진화), MOE = 관찰자(탐사/맵핑) | **루시퍼** = 내부 물리 코어(맨틀·지각·수분·응력 적분). **MOE** = 궁창 이후 “어디가 깨지고 새는지/균열 경로/핫스팟” 탐색·추적(탐사선). |
| **궁창 = “탐색”?** | 궁창은 탐색이 아니라 전이/이벤트 | **궁창** = 이벤트·전이 엔진 — 붕괴/홍수/차폐 변화(S, env_load). L3 이벤트 레이어. |
| **하데스 = 런타임 엔진?** | 룰 편집은 Authoring/Config, 런타임과 분리 | **하데스** = 룰·파라미터 레지스트리(편집기). 런타임에는 **CONFIG로 주입·읽기 전용**. “편집”은 런타임 체인 바깥. |

### 9.2 런타임(한 틱) 의존 방향 — 권장 순서

**데이터가 흐르는 순서** (원인 → 관측 → 이벤트 → 탐사 → 경고):

```
(A) 루시퍼 (내부 코어)
    내부 유체/압력/응력/열/수분 저장소 상태를 시간 적분해서 생성.
    출력: Pw, σ_plate, W_ground, dW_ground/dt, (선택) 자기장 → 궁창 보호막 강도
    대응: deep_monitor + solar/core, day4/core

        ↓

(B) JOE (거시 관측자, 조)
    L0/L1 + 루시퍼 출력을 읽어 planet_stress, instability 산출.
    출력: instability
    대응: solar/planet_dynamics

        ↓

(C) 궁창 (Firmament / Flood — 이벤트 레이어)
    instability 읽고 collapse / flood transition 결정.
    출력: layer0_snapshot (S, env_load, H2O_canopy, phase...)
    대응: solar/eden/firmament.py

        ↓

(D) MOE (내부 탐사/맵핑, 모)
    궁창 이후 환경/지질이 바뀐 뒤, 내부 “경로·핫스팟·취약점” 탐색·추적.
    출력: 탐사 결과(지도/핫스팟/경로) = 시나리오 변수 후보
    대응: Eden Finder(체루빔, search.py)

        ↓

(E) UnderWorld + Siren (모니터링/경고)
    위 모든 신호를 관찰하고 로그/알람/서사 출력. (측정만, 편집 없음)
    출력: 경고/로그/서사(시스템 외부로). 조/모 목소리 빌려 사용자 경고.
    대응: solar/underworld (hades listen → wave_bus → siren)
```

**하데스 = 런타임 체인 바깥 (Rule Authoring / Policy / Param Registry)**

- 룰을 **편집/검증/버전 고정** → 런타임 시작 시 **CONFIG로 주입**.
- 런타임에서는 **읽기 전용**으로만 사용 → 하드코딩/혼입 방지.
- 대응: `solar/underworld/rules.py` (RuleSpec, DEFAULT_RULES), `hades.py`는 주입된 룰로 **평가만** 수행.

### 9.3 7단계 레이어 표 (의미·물리·폴더)

| L | 엔진 | 역할 (고정) | 물리적 로직 (Feynman) | CookiieBrain 폴더/파일 |
|---|------|-------------|------------------------|-------------------------|
| L1 | **JOE** | 거시 관측(조) — 요약 지표 | 자전·공전·질량·각운동량 등 거시 궤도 역학 | `solar/planet_dynamics` |
| L2 | **MOE** | 미시 탐사(모) — 경로·핫스팟·취약점 지도화 | 지표면 상태, 대기압, 복사 평형 + 궁창 이후 탐사 | `solar/eden/search.py`, 체루빔, `solar/surface/` |
| L3 | **궁창** | 이벤트/전이 — 붕괴·홍수·차폐 | 외부(태양풍 등) 차단막, 기권-수권 에너지 순환 | `solar/eden/firmament.py`, `solar/em/`, `solar/atmosphere/` |
| L4 | **루시퍼** | 내부 물리 코어 — 맨틀·지각·수분·응력 적분 | 내핵·외핵 대류, 맨틀 열전달, 자기장(Dynamo) → 궁창 보호막 강도 | `solar/underworld/deep_monitor`, `solar/core/` |
| L5 | **하데스** | 룰/파라미터 레지스트리(편집기) | 중력 G, 엔트로피 증가율 등 상수·정책 — 런타임에 주입 | `solar/underworld/rules.py` (편집), `solar/data/` (상수) |
| L6 | **UnderWorld** | 자원·저장소·로그·엔트로피 누적 | 지각 아래 매장 에너지, 탄소 순환, 데이터 히스토리 | `solar/underworld/` (hades listen, deep_monitor) |
| L7 | **Siren** | 시스템 경고·피드백 | instability 임계치 도달 시 조/모 목소리로 경고 | `solar/underworld/siren.py`, `solar/cognitive/` |

### 9.4 데이터 파이프라인 요약

```
HADES (Rule)     →  상수·룰 선언 (런타임 전 주입)
LUCIFER (Core)   →  내핵 열·자기장·지각 변동 생성
JOE (Macro)      →  질량·에너지 기반 궤도·자전·instability 확정
궁창 (Protection)→  instability로 붕괴/홍수 전이, S(t), env_load
MOE (Micro)      →  확정된 환경 내 지표·핫스팟·경로 탐사
UnderWorld/Siren →  마찰(Stress)·임계치 감지 → 경고/로그/서사
```

### 9.5 한 장 요약 (의존 방향 + 하데스 분리)

```
[ Authoring ]  Hades: 룰/상수 편집·검증·버전 → CONFIG 주입
                    ↓ (읽기 전용)
[ Runtime ]   루시퍼 → JOE → 궁창 → MOE → UnderWorld → Siren
              (원인)   (관측)  (전이)  (탐사)   (감시)    (경고)
```

### 9.6 레이어 ↔ 폴더 매핑 (정리)

| 레이어 | solar/ 경로 | 비고 |
|--------|-------------|------|
| **루시퍼** | `core/`, `underworld/deep_monitor.py`, `day4/` | 내부 물리 코어·스냅샷 |
| **JOE** | `planet_dynamics/` | 거시 관측, instability |
| **궁창** | `eden/firmament.py`, `em/`, `atmosphere/` | 이벤트·전이·보호막 |
| **MOE** | `eden/search.py`, `eden/eden_os/cherubim_guard.py`, `surface/` | 탐사·맵핑·Eden Finder |
| **하데스** | `underworld/rules.py`, `underworld/hades.py`, `data/` | 룰 편집/상수·런타임 평가 |
| **UnderWorld** | `underworld/` (wave_bus, consciousness 등) | 로그·엔트로피·저장소 |
| **Siren** | `underworld/siren.py`, `cognitive/` | 경고·피드백·인지 출력 |

---

## 10. ENGINE_HUB — 기능적 완전 독립 모듈 레이어 (서사 아님)

**ENGINE_HUB**는 **CookiieBrain 안에 두지 않는다.** **00_BRAIN 바로 아래** (CookiieBrain과 형제) 에 두는 **독립** 레이어 구조다.

### 10.1 구조 (기능적 독립 모듈)

| 레이어 폴더 | 성격 | 비고 |
|-------------|------|------|
| **00_PLANET_LAYER** | 행성 조건·궤도·거시 관측 | 조(JOE) 엔진 등 |
| 10_AUTONOMIC_LAYER | 자율/자동화 | |
| 20_LIMBIC_LAYER | 변연계 | |
| 30_CORTEX_LAYER | 피질 | |
| 40_SPATIAL_LAYER | 공간 | |
| 50_DIAGNOSTIC_LAYER | 거시 감시·진단 | 예: UnderWorld 독립 패키지 |
| 60_APPLIED_LAYER | 응용 | |

경로: **00_BRAIN/ENGINE_HUB/** (CookiieBrain과 형제. CookiieBrain/ENGINE_HUB 아님.)

각 레이어는 **한 기능만 담당하는 독립 모듈**을 두기 위한 것이며, 호출 순서나 “스토리”가 아니라 **입력/출력 계약**으로만 연동한다.

### 10.2 조(JOE) 엔진이 00_PLANET_LAYER에 들어갈 수 있는가?

**가능하다.** 조 엔진(JOE) 로직을 **상용화 가능한 다른 행성 탐색 독립 엔진**으로 만들어 **00_BRAIN/ENGINE_HUB/00_PLANET_LAYER/Joe_Engine/** 에 둔다.

| 항목 | 내용 |
|------|------|
| **위치** | **00_BRAIN/ENGINE_HUB/00_PLANET_LAYER/Joe_Engine/** (CookiieBrain 밖) |
| **소스(복사용)** | CookiieBrain 레포 안 **standalone_build/Joe_Engine/** — 상용화 가능한 다른 행성 탐색 독립 엔진(assess_planet, explore.py, __main__.py 등). 이 폴더 전체를 00_BRAIN/ENGINE_HUB/00_PLANET_LAYER/Joe_Engine 로 복사해 사용. |
| **입력** | 스냅샷만 (dict). solar.eden import 불필요. |
| **출력** | `(planet_stress, instability)` |
| **CookiieBrain** | `solar/planet_dynamics` 는 동일 수식 로컬 구현 사용. ENGINE_HUB 안에 두지 않음. |

정리: **ENGINE_HUB = 00_BRAIN 아래 독립.** 조 엔진 = **00_BRAIN/ENGINE_HUB/00_PLANET_LAYER/Joe_Engine** (폴더 생성됨. CookiieBrain/standalone_build/Joe_Engine 에서 복사).

---

## 11. 레이어 ↔ 실제 경로 검증표 (파일/문서 확인용)

**기준 루트**: `/Users/jazzin/Desktop/00_BRAIN/`  
아래 경로가 실제로 존재하는지 확인하면 로직·문서 검증 가능.

### 11.1 00_BRAIN 직하 (CookiieBrain 밖)

| 레이어/구분 | 절대 경로 | 확인 항목 |
|-------------|-----------|-----------|
| **ENGINE_HUB** | `/Users/jazzin/Desktop/00_BRAIN/ENGINE_HUB/` | 폴더 존재 |
| **00_PLANET_LAYER** | `/Users/jazzin/Desktop/00_BRAIN/ENGINE_HUB/00_PLANET_LAYER/` | 폴더 존재 |
| **Joe_Engine (조)** | `/Users/jazzin/Desktop/00_BRAIN/ENGINE_HUB/00_PLANET_LAYER/Joe_Engine/` | 상용화 가능한 다른 행성 탐색 독립 엔진. `__init__.py`, `explore.py`, `_core.py`, `__main__.py`, `README.md`, `requirements.txt` |
| **CookiieBrain** | `/Users/jazzin/Desktop/00_BRAIN/CookiieBrain/` | 프로젝트 루트 |

### 11.2 CookiieBrain 내 — 런타임 레이어 (실제 파일)

| 레이어 | 절대 경로 | 파일 |
|--------|-----------|------|
| L0/L1 | `/Users/jazzin/Desktop/00_BRAIN/CookiieBrain/solar/eden/initial_conditions.py` | InitialConditions |
| L2 JOE | `/Users/jazzin/Desktop/00_BRAIN/CookiieBrain/solar/planet_dynamics/__init__.py` | compute_planet_stress_and_instability |
| L3 궁창 | `/Users/jazzin/Desktop/00_BRAIN/CookiieBrain/solar/eden/firmament.py` | FirmamentLayer, step(instability) |
| 통합 Runner | `/Users/jazzin/Desktop/00_BRAIN/CookiieBrain/solar/eden/eden_os/eden_os_runner.py` | EdenOSRunner |
| 환경 월드 | `/Users/jazzin/Desktop/00_BRAIN/CookiieBrain/solar/eden/eden_os/eden_world.py` | make_eden_world |
| 수명 | `/Users/jazzin/Desktop/00_BRAIN/CookiieBrain/solar/eden/eden_os/lifespan_budget.py`, `homeostasis_engine.py` | expected_lifespan_yr, update() |
| MOE/체루빔 | `/Users/jazzin/Desktop/00_BRAIN/CookiieBrain/solar/eden/search.py`, `eden_os/cherubim_guard.py` | EdenCriteria, CherubimGuard |
| 하데스 | `/Users/jazzin/Desktop/00_BRAIN/CookiieBrain/solar/underworld/hades.py`, `rules.py` | listen(), evaluate_rules_all |
| deep_monitor | `/Users/jazzin/Desktop/00_BRAIN/CookiieBrain/solar/underworld/deep_monitor.py` | read_deep_snapshot |
| Siren | `/Users/jazzin/Desktop/00_BRAIN/CookiieBrain/solar/underworld/siren.py` | broadcast() |

### 11.3 문서 (레이어·로직 확인용)

| 문서 | 절대 경로 | 내용 |
|------|-----------|------|
| 레이어·폴더 맵 | `/Users/jazzin/Desktop/00_BRAIN/CookiieBrain/docs/FOLDER_AND_LAYER_MAP.md` | §8·§9·§10·§11 (본 문서) |
| JOE·엔진 | `/Users/jazzin/Desktop/00_BRAIN/CookiieBrain/docs/PLANET_DYNAMICS_ENGINE.md` | JOE 정의, 스냅샷 계약 |
| L0~L3·물예산 | `/Users/jazzin/Desktop/00_BRAIN/CookiieBrain/docs/PANGEA_ROTATION_AND_WATER_BUDGET.md` | planet_stress, instability 수식 |
| 조/모 | `/Users/jazzin/Desktop/00_BRAIN/CookiieBrain/docs/FEYNMAN_VOL1_AS_PLANET_MOTION.md` | Joe/Moe 관측자 |
| 구현 감사 | `/Users/jazzin/Desktop/00_BRAIN/CookiieBrain/docs/DOCS_IMPLEMENTATION_AUDIT.md` | 문서↔구현 대조 |

---
