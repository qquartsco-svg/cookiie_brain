# Planet Dynamics Engine — JOE Engine (파인만 물리 기반 독립 모듈)

**엔진 이름: J.O.E.**  
- **J**oe **O**bserver **E**ngine  
- 파인만 1권의 **조(Joe)** = 땅에 가만히 선 **정지 관측자(기준계)**.  
- 이 엔진은 행성 동역학(질량·회전·대칭성·붕괴)을 **그 기준계(Joe 시점)**에서 계산한다.  
- 즉 “행성이라는 무대가 어떻게 유지/붕괴되는가”를 **Joe의 눈**으로 보는 물리 엔진.

**목적**  
파인만 물리학 강의 1권의 로직(운동량·질량·대칭성·붕괴)을 **행성 동역학 전용 독립 엔진**으로 모듈화할 수 있는지 확인하고, EdenOS 전체 아키텍처에서의 위치를 한 장으로 정리한다.

**관련 문서**  
- [FEYNMAN_VOL1_AS_PLANET_MOTION.md](FEYNMAN_VOL1_AS_PLANET_MOTION.md) — 행성 운동으로 읽는 1권 로직, 조/모 = Macro–Micro  
- [PANGEA_ROTATION_AND_WATER_BUDGET.md](PANGEA_ROTATION_AND_WATER_BUDGET.md) — L0~L3 레이어, 물 예산, instability  
- [FOLDER_AND_LAYER_MAP.md](FOLDER_AND_LAYER_MAP.md) §8 — **JOE + EdenOS 레이어 스택** 파일·폴더·문서 위치 및 호출 흐름  
- [FOLDER_AND_LAYER_MAP.md](FOLDER_AND_LAYER_MAP.md) §9 — **의존 방향·역할 고정** 런타임 순서(루시퍼→JOE→궁창→MOE→UnderWorld/Siren), 하데스=Authoring

---

## 0.0 ENGINE_HUB 00_PLANET_LAYER 독립 배치 — 가능 여부

**ENGINE_HUB**는 **CookiieBrain 안이 아니라 00_BRAIN 바로 아래** (CookiieBrain과 형제) 에 두는 **기능별 완전 독립 엔진** 레이어다 (00_PLANET_LAYER, 10_AUTONOMIC_LAYER, … 60_APPLIED_LAYER).  
**가능하다.** JOE를 **00_BRAIN/ENGINE_HUB/00_PLANET_LAYER** 안에 완전히 독립 엔진으로 둘 수 있다.

**조건**  
- **00_PLANET_LAYER** 쪽 코드는 `solar.eden`(InitialConditions, EdenWorld 등)을 **import 하지 않는다**.  
- 대신 **입력 = 스냅샷(dict)** 로만 받고, **출력 = (planet_stress, instability)** 만 반환한다.

**배치**  
- **독립 엔진**: `00_BRAIN/ENGINE_HUB/00_PLANET_LAYER/Joe_Engine`. CookiieBrain 안에 복사본 없음.  
- CookiieBrain에서는 `solar/planet_dynamics` 가 동일 수식 로컬 구현 사용. ENGINE_HUB는 CookiieBrain 내부에 두지 않음.

---

### 0.1 공식 명칭

**JOE = Joe Observer Engine** (확정)

- 파인만 1권의 **조(Joe)** = 정지 관측자(기준계).  
- 엔진이 **“세계를 직접 만들기”** 가 아니라 **“행성 상태를 관찰 → 분석 → 이벤트 감지”** 하는 구조임을 이름에 반영.

### 0.2 Observer 철학

엔진은 **“신처럼 계산”** 하는 것이 아니라 **“관찰하고 판단한다”** 는 역할을 가진다.

```
물리 상태 (rotation, water_budget, plate_stress, …)
    ↓ observe
관찰
    ↓ analyze
분석 (planet_stress, instability)
    ↓ detect
이벤트 감지 (collapse condition)
    ↓
Event Trigger → Firmament / Flood
```

이 흐름은 소프트웨어의 **Observer pattern**(상태 변화 감지 → 이벤트 발생)과 같다.  
즉 JOE = **Planet State Observer** — 행성 상태를 관찰하고, 임계점을 발견하면 이벤트를 발생시킨다.

### 0.3 EdenOS 내 위치

```
Planet Dynamics (L0/L1 상태)
        ↓
JOE Observer Engine  — observe() / analyze() / detect()
        ↓
Event Trigger (instability ≥ θ_collapse)
        ↓
Firmament / Flood
        ↓
EdenOS, Cherubim 이 사용
```

### 0.4 인터페이스 요약 (역할)

| 단계 | 입력/출력 |
|------|------------|
| **observe()** | rotation, mass_distribution, water_budget, plate_stress |
| **analyze()** | → planet_stress, instability |
| **detect()** | → collapse_event (instability ≥ θ) |

현재 코드는 `compute_planet_stress_and_instability(ic, water_snapshot)` 한 함수로 observe+analyze를 수행하고, detect는 FirmamentLayer.step(instability=...) 내부에서 수행한다.

### 0.5 대안 확장명 (동의어)

문맥에 따라 아래 해석을 **보조적으로** 인용할 수 있다. 공식 명칭은 **Joe Observer Engine** 유지.

| 약자 | 의미 | 용도 |
|------|------|------|
| **Joint Observation Engine** | 여러 물리 모듈 → 하나의 관찰 시스템 | L0/L1/L2 통합 관찰 강조 시 |
| **Judicial Observer of Entropy** | 엔트로피(붕괴)를 엄격히 감시·판단 | 붕괴/엔트로피 분석 강조 시 |
| **Joint Orbital Evolution** | 공동 궤도 진화 | 궤도·항성-행성 상호작용 확장 시 |

### 0.6 M.O.E. (모) 예약

파인만의 **모(Moe)** = 운동 관측자(이동 관성계).  
추후 **M.O.E.** 는 서브 모듈 또는 **이동 관측자/출력 레이어**(예: “Moe-side output”, 다른 관성계에서 본 결과 내보내기) 용도로 예약해 둘 수 있다. 현재는 JOE만 구현.

---

**가능하다.**  
파인만 1권에서 다루는 **질량·에너지 보존, 각운동량, 대칭성, 붕괴**는 모두 **제1원리(First Principles)** 에 기반하므로, 수식과 입·출력만 정의하면 **다른 행성/시나리오에도 끼워 쓸 수 있는 물리 규칙 팩(Rule Pack)** 으로 독립 모듈화할 수 있다.

---

## 2. 계층 구조 — 전체 한 장

```
┌─────────────────────────────────────────────────────────────────────────┐
│  Level 1 — JOE Engine (Joe Observer Engine / Planet Dynamics)           │
│  ─────────────────────────────────────────────────────────────────────  │
│  역할: 행성 자체가 어떻게 형성·유지·붕괴되는지 계산. “무대 제작”.          │
│  입력: mass, radius, omega_spin, obliquity, water_budget(L1), …         │
│  출력: planet_stress, instability, (선택) axis_shift, rotation_change    │
│  모듈: L0(형상·회전) + L1(물 예산) + L2(스트레스·불안정도)               │
└─────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  Level 2 — Planet Environment Engine (EdenOS / Firmament / 수명)        │
│  ─────────────────────────────────────────────────────────────────────  │
│  역할: 주어진 행성 위의 환경(궁창, 대기, 수명 곡선). “무대 위 연출”.     │
│  입력: L2의 instability, L0/L1 파라미터, 초기조건(IC)                    │
│  출력: shield_strength S(t), env_load L_env(t), expected_lifespan, …    │
│  모듈: FirmamentLayer(L3), HomeostasisEngine, make_eden_world           │
└─────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  Level 3 — Eden Finder (체루빔 / Eden 탐색기)                            │
│  ─────────────────────────────────────────────────────────────────────  │
│  역할: 이미 형성된 행성 **내부**에서 생명 유지 최적 입지 탐색.           │
│  입력: 환경 엔진의 band_T, GPP, geography, …                              │
│  출력: 최적 정착지, 접근 제어, 선악과/생명나무 조건                      │
│  모듈: Cherubim, 4대강, tree_of_life, search (Eden 탐색)                 │
└─────────────────────────────────────────────────────────────────────────┘
```

**비유**  
- **JOE Engine** = “행성이 유지될 수 있는가?” (Joe 기준계에서 본 물리 뼈대)  
- **Planet Environment** = “그 위에서 궁창·대기·수명이 어떻게 변하는가?”  
- **Eden Finder** = “그 행성 어디가 제일 살기 좋은가?” (최적화/탐색)

---

## 3. 파인만 엔진의 4대 핵심 → 모듈 대응

| 파인만 로직 | 엔진 모듈 역할 | PANGEA 레이어 |
|-------------|----------------|----------------|
| **질량·에너지 보존** | 행성 “체급”·에너지 재분배 → 형상/회전 변화 | L0, L1 |
| **운동량·각운동량** | 자전 방향·세차·편평 타원체 유지 | L0 |
| **대칭성 (Noether)** | 보존량 ↔ 대칭; 궤도/회전 안정성 판별 | L0, L2 |
| **붕괴·엔트로피** | stress 누적 → instability → 궁창 붕괴 시나리오 | L2 → L3 |

입력은 **초기조건(IC) + (선택) 물 예산 스냅샷**, 연산은 **보존 법칙 + 정규화(saturate)** 로 고정하면, 다른 행성/시나리오에 그대로 끼워 쓸 수 있다.

---

## 4. 독립 엔진 인터페이스 (코드 계약)

**모듈 경계**: `solar/planet_dynamics` — **JOE Engine (Joe Observer Engine)** 구현부.

**입력**  
- `ic`: `InitialConditions` — L0/L1 슬롯(omega_spin_rad_s, obliquity_deg, GEL_surface_eden_m, W_canopy_ref_km3) 포함.  
- `water_snapshot`: (선택) L1 물 예산 스냅샷(W_surface, W_canopy, dW/dt 등). 없으면 ic만으로 근사.

**출력**  
- `planet_stress`: `float` [0~1] — 정규화된 행성 스트레스.  
- `instability`: `float` [0~1] — L3 FirmamentLayer.step(instability=...) 에 넣을 값.  
- (추후) `axis_shift`, `rotation_change` 등 확장 가능.

**동작**  
- 현재는 **스텁**: `(0.0, 0.0)` 반환 → 붕괴 미발동.  
- 추후: PANGEA §4 수식 `planet_stress_raw`, `instability_raw` → `normalize`, `saturate` 적용 후 반환.

이렇게 하면 **EdenOS Runner**는 “Planet Dynamics 엔진 한 번 호출 → instability 받아서 FirmamentLayer.step(instability=...)” 만 하면 되고, 엔진 내부는 독립적으로 확장 가능하다.

---

## 5. 범위 선택 — A vs B

| 옵션 | 내용 | EdenOS와의 맞음 |
|------|------|------------------|
| **A** | 행성 **형성**까지 포함 (dust disk → planet formation → impact → rotation) | 대형 시뮬; 현재 EdenOS는 “이미 지구가 있음” 전제 |
| **B** | **이미 형성된 행성**만 (rotation, mass 재분배, tectonics, collapse) | ✅ **현재 EdenOS와 가장 잘 맞음** |

**채택**: **B**. 완성된 행성의 동역학만 담당하는 **JOE Engine (Joe Observer Engine)** 으로 한정. 형성 시뮬은 필요 시 별도 레포/모듈로 확장.

---

## 6. 현재 코드 상태와 다음 단계

| 항목 | 상태 |
|------|------|
| L0/L1 슬롯 (IC) | ✅ `InitialConditions`에 omega_spin_rad_s, obliquity_deg, GEL_surface_eden_m, W_canopy_ref_km3 존재 |
| L2 계산 (planet_stress, instability) | ❌ 미구현. Runner의 `_compute_instability()` 는 0.0 반환. |
| L3 (FirmamentLayer) | ✅ `step(dt_yr, instability=...)` 구현됨, instability ≥ θ 시 붕괴 |
| 독립 모듈 경계 | ✅ `solar/planet_dynamics` 스텁 추가 시, Runner가 여기서 instability 를 받아 fl.step() 에 주입 |

**다음 단계**  
1. **PlanetDynamicsEngine** 스텁 모듈 추가: `compute_planet_stress_and_instability(ic, water_snapshot=None) -> (planet_stress, instability)`.  
2. EdenOSRunner에서 `_compute_instability()` 대신 위 함수 호출하도록 연결.  
3. PANGEA §4 수식대로 `planet_stress_raw`, `instability_raw` 구현 후 normalize/saturate 적용.

---

## 7. 정리

- **파인만 책의 로직**을 “운동량·질량·대칭성·붕괴”를 추적하는 **독립 엔진(JOE Engine)**으로 모듈화하는 것은 **가능**하며, EdenOS는 **Level 2(환경) + Level 3(Eden 탐색)** 이고, 그 아래에 **Level 1(JOE = Joe Observer Engine)** 를 하나 더 두는 구조가 된다.  
- **에덴 탐색기(체루빔)** = 행성 **내부** 최적 입지 탐색.  
- **파인만 모델(JOE Engine)** = 행성 **자체**가 어떻게 형성·유지·붕괴되는지를 계산하는 물리 엔진 (Joe = 기준 관측자 시점).  
- 범위는 **B(이미 형성된 행성만)** 로 두고, 인터페이스(입력 IC + 물 스냅샷, 출력 planet_stress, instability)를 고정하면 다른 프로젝트에서도 “물리 규칙 팩”으로 재사용할 수 있다.

---

## 8. 7단계 레이어 스택 — 런타임 의존 방향·폴더 매칭

(FOLDER_AND_LAYER_MAP.md §9와 동일 정의. 여기서는 파인만 물리·데이터 파이프라인 관점으로 요약.)

### 8.1 런타임(한 틱) 의존 방향

**원인 → 관측 → 이벤트 → 탐사 → 경고** 순서로 데이터가 흐른다.

| 순서 | 엔진 | 역할 | 출력 |
|------|------|------|------|
| A | **루시퍼** | 내부 물리 코어(맨틀·지각·수분·응력 적분) | Pw, σ_plate, W_ground, (선택) 자기장 → 궁창 보호막 |
| B | **JOE** | 거시 관측(조) — 요약 지표 | planet_stress, instability |
| C | **궁창** | 이벤트/전이 — 붕괴·홍수·차폐 | layer0_snapshot (S, env_load, phase...) |
| D | **MOE** | 미시 탐사(모) — 경로·핫스팟·취약점 맵핑 | 탐사 결과(지도/핫스팟/경로) |
| E | **UnderWorld + Siren** | 감시·경고·로그(측정만) | 경고/로그/서사(조·모 목소리) |

**하데스**는 런타임 체인 **밖**: 룰·상수 편집/검증/버전 → CONFIG 주입 후, 런타임에서는 **읽기 전용**.

### 8.2 7단계(L1–L7) 표 — 역할·물리·폴더

| L | 엔진 | 역할 (고정) | 물리적 로직 (Feynman) | solar/ 폴더 |
|---|------|-------------|------------------------|--------------|
| L1 | JOE | 거시 관측(조) | 자전·공전·질량·각운동량 | `planet_dynamics/` |
| L2 | MOE | 미시 탐사(모) | 지표·대기압·궁창 이후 탐사 | `eden/search.py`, `surface/` |
| L3 | 궁창 | 이벤트/전이 | 차단막·기권-수권 순환·붕괴/홍수 | `eden/firmament.py`, `em/`, `atmosphere/` |
| L4 | 루시퍼 | 내부 물리 코어 | 내핵·외핵·맨틀·자기장(Dynamo) → 보호막 | `core/`, `underworld/deep_monitor.py` |
| L5 | 하데스 | 룰/상수 레지스트리(편집) | G, 엔트로피율 등 — 런타임 주입 | `underworld/rules.py`, `data/` |
| L6 | UnderWorld | 로그·엔트로피·저장소 | 지각 아래 에너지·데이터 히스토리 | `underworld/` |
| L7 | Siren | 시스템 경고 | instability 임계치 → 조/모 목소리 | `underworld/siren.py`, `cognitive/` |

### 8.3 데이터 파이프라인 (알고리즘 흐름)

```
HADES (Rule)      →  중력 G·물리 법칙 선언 (런타임 전)
LUCIFER (Core)    →  내핵 열·자기장·지각 변동 생성
JOE (Macro)       →  질량·에너지 기반 궤도·자전·instability 확정
궁창 (Protection) →  instability로 붕괴/홍수 전이, S(t), env_load
MOE (Micro)       →  확정된 환경 내 지표·핫스팟·경로 탐사
UnderWorld/Siren  →  Stress·임계치 감지 → 경고/로그/서사
```

### 8.4 CookiieBrain 구조와의 매칭

| 구분 | solar/ 경로 | 대응 레이어 |
|------|-------------|-------------|
| 물리 코어·내부 | `core/`, `day4/` | LUCIFER + (JOE 입력 소스) |
| 거시 관측 | `planet_dynamics/` | JOE |
| 전자기·대기·보호 | `em/`, `atmosphere/`, `eden/firmament.py` | 궁창 (FIRMAMENT) |
| 표면·탐사 | `surface/`, `eden/search.py`, `eden/eden_os/cherubim_guard.py` | MOE |
| 룰·상수 | `data/`, `underworld/rules.py`, `underworld/hades.py` | HADES (Authoring + 런타임 평가) |
| 인지·경고 | `cognitive/`, `underworld/siren.py` | SIREN |

이 레이어 스택은 **질량(원인계)** → **관측** → **법칙(룰)** → **경고(인지)** 로 이어지며, **루시퍼(핵) → 궁창(자기권/보호막) → 사이렌(경고)** 흐름으로 행성 생존성 시뮬레이션에 맞춰져 있다.
