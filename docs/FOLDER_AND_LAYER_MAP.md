# 작업 파일 위치 및 레이어 정리

---

## 1. 루트 경로

| 경로 | 의미 |
|------|------|
| `/Users/jazzin/Desktop/00_BRAIN/` | 00_BRAIN 생태계 루트 |
| `/Users/jazzin/Desktop/00_BRAIN/CookiieBrain/` | CookiieBrain 프로젝트 (환경 물리 + 인지) |

**상태공간이 표현되는 곳**: `CookiieBrain/solar/` + `CookiieBrain/cookiie_brain/`  
BrainCore와 연동 시: `BrainCore`의 `GlobalState` (extensions)

---

## 2. CookiieBrain 폴더 구조

```
CookiieBrain/
├── solar/                    ← ★ 환경 물리 (상태공간 핵심)
│   ├── core/                 ← 물리 코어 (EvolutionEngine, Body3D, SurfaceOcean)
│   ├── data/                 ← NASA 상수, build_solar_system()
│   ├── em/                   ← 전자기 (광도, 자기장, 태양풍, 자기권)
│   ├── surface/              ← 표면 (땅-바다, 알베도) [Phase 7]
│   ├── atmosphere/           ← 대기 (온실, 수순환) [Phase 6a/6b]
│   ├── cognitive/            ← 인지 (Ring Attractor)
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
│   ├── atmosphere_demo.py
│   ├── water_cycle_demo.py
│   ├── surface_day3_demo.py
│   ├── brain_core_environment_demo.py
│   └── ...
│
└── docs/                     ← 문서 (전략, 설계, 점검)
    ├── EMERGENCE_TRAJECTORY.md
    ├── AUTONOMOUS_CYCLE_PHYSICS.md
    ├── REACTION_DYNAMICS_LAYER_SPEC.md
    ├── BRAINCORE_INTEGRATION.md
    └── ...
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
