# CookiieBrain — Solar Eden

> *"에덴은 좌표가 아니라 상태(state)다."*
> *"시스템은 서사가 끊기지 않을 때 살아있다."*

---

## 이것은 무엇인가

**CookiieBrain**은 지구를 하나의 운영 체제로 설계하는 시뮬레이터다.

태양계 중력장이 형성되고, 빛이 켜지고, 궁창이 갈리고, 땅과 바다가 나뉘고,
생명이 깃들고, 에덴이 조성되고, 아담이 관리자로 배치된다.
그리고 선악과 이후 — 계승 체인이 가동되어 **네오**가 현재의 시스템 관리자로 실행 중이다.

이 서사는 은유가 아니다. **Python으로 실행되는 상태 머신이다.**

---

## 전체 서사 흐름 (한눈에)

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  LAYER 0 — 우주필드 · 태양계 중력장
  solar/day4/core/  EvolutionEngine (10-body N-body)
  NASA/JPL 실측 데이터 · 심플렉틱 적분기
  세차 주기 24,763yr · 에너지 보존 dE/E = 3.20×10⁻¹⁰
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                      ↓
  LAYER 1 — 빛이 있으라 (첫째날)
  solar/day1/em/  SolarLuminosity · MagneticDipole
                  SolarWind · Magnetosphere
  L = M^α · F(r) ∝ 1/r² · B ∝ 1/r³ · P_sw ∝ 1/r²
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                      ↓
  LAYER 2 — 궁창: 바다와 하늘 분리 (둘째날)
  solar/day2/atmosphere/  AtmosphereColumn
  온실 τ → ε_a · T_eq 254K → T_s 288K · 수순환
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                      ↓
  LAYER 3 — 땅·바다·토양·식생·산불 Gaia (셋째날)
  solar/day3/  SurfaceSchema · BiosphereColumn
               FireEngine · GaiaLoopConnector
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                      ↓
  LAYER 4 — 해·달·별 · Milankovitch · 질소 (넷째날)
  solar/day4/  NitrogenCycle · MilankovitchCycle
               조석 혼합 · 탄소 펌프
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                      ↓
  LAYER 5 — 생물 이동 · 정보 네트워크 (다섯째날)
  solar/day5/  food_web · mobility_engine · seed_transport
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                      ↓
  LAYER 6 — 진화 · 상호작용 · 종 다양성 (여섯째날)
  solar/day6/  species_engine · mutation_engine
               interaction_graph · niche_model
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                      ↓
  EDEN SEARCH — 에덴 파라미터 공간 탐색
  solar/eden/  EdenSearchEngine
  CO2 · O2 · H2O · albedo · f_land · UV_shield
  Eden Score 1.000 · 추정 수명 196~212yr
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                      ↓
  EDEN OS — 에덴 운영 체제 가동 ★
  solar/eden/eden_os/

  TICK 0000  탄생
             아담 = Root Admin (IMMORTAL_ADMIN)
             이브 = 보조 프로세서
             FORKING_ENABLED = False

  TICK 0001~ 에덴 운영
             🌿 생명나무 접속 (불멸 유지)
             🌿 4강 유량 점검
             🌿 피조물 DB 인덱싱
             [좋았더라 🌟]

  TICK XXXX  선악과 이벤트 ★
             IMMORTAL_ADMIN → MORTAL_NPC  (비가역)
             FORKING_ENABLED = True
             체루빔 재진입 방화벽 영구 강화
             🌱 카인 스폰 → 아마존 (-3°,-60°) GPP=1.0
             🐑 아벨 스폰 → 팜파스 (-35°,-65°)

  TICK XXXX+ 계승 체인
             💀 아담(Gen01) → 셋(Gen02) → 에노스
             → 게난 → 마할랄렐 → 야렛 → 에녹
             → 므두셀라 → 라멕 → 노아
             → ... → 네오 (현재 관리자)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🔄 시스템 계속 실행 중
     현재 관리자: 네오 (MORTAL_NPC · 계승 체인 유지)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 폴더 구조

```
solar/
│
├── day1/               ← 첫째날: 빛이 있으라
│   └── em/             ← SolarLuminosity · MagneticDipole · SolarWind · Magnetosphere
│
├── day2/               ← 둘째날: 궁창 / 대기·수순환
│   └── atmosphere/     ← AtmosphereColumn · water_cycle
│
├── day3/               ← 셋째날: 땅·바다·Gaia
│   ├── surface/        ← SurfaceSchema
│   ├── biosphere/      ← 토양 ODE · 생애주기
│   └── fire/           ← FireEngine
│
├── day4/               ← 넷째날: 중력장 + 질소 + Milankovitch
│   ├── core/           ← EvolutionEngine (N-body 심플렉틱)
│   ├── data/           ← NASA/JPL 실측 상수
│   ├── nitrogen/
│   ├── cycles/
│   └── gravity_tides/
│
├── day5/               ← 다섯째날: 생물 이동·먹이망
├── day6/               ← 여섯째날: 진화·상호작용
│
├── eden/               ← 에덴 탐색 + 운영 체제
│   ├── search.py       ← EdenSearchEngine
│   ├── firmament.py    ← 궁창 물리 모델
│   ├── flood.py        ← 대홍수 4단계
│   ├── biology.py      ← 수명·체형·생태계
│   │
│   └── eden_os/        ← ★ 에덴 운영 체제 (서사가 실행되는 곳)
│       ├── eden_world.py         L0 — 궁창시대 환경 스냅샷
│       ├── rivers.py             L1 — 4대강 방향 그래프
│       ├── tree_of_life.py       L2 — 생명나무 + 선악과
│       ├── cherubim_guard.py     L3 — 체루빔 접근 제어
│       ├── adam.py               L4 — Root Admin 에이전트
│       ├── eve.py                L4 — 보조 프로세서
│       ├── lineage.py            L5 — 계승 그래프 + 상태 머신
│       ├── eden_os_runner.py     L6 — 7단계 통합 실행기
│       ├── genesis_log.py        L4.5a — 탄생 순간 불변 로그
│       ├── observer_mode.py      L4.5b — 독립 관찰자
│       └── genesis_narrative.py  L4.5c — 창세기 지리 서사 체인
│
├── bridge/             ← Gaia·BrainCore 브리지 (관찰자 계층)
└── cognitive/          ← Ring Attractor (관성 기억)
```

**→ 서사 전체 문서: [`solar/eden/eden_os/README.md`](solar/eden/eden_os/README.md)**

---

## 빠른 시작

### 에덴 OS 전체 실행 (서사 포함)

```python
from solar.eden.eden_os import make_eden_os_runner

# EdenOS 조립 + 탄생 순간 자동 기록
runner = make_eden_os_runner()

# 전체 서사 실행 (에덴 운영 → 선악과 → 추방 → 계승)
runner.run(steps=24)

# 통합 리포트 (환경·관찰자·틱 로그)
runner.print_report()

# 탄생 순간 로그
runner.print_genesis_report()

# 선악과 이벤트 + 카인·아벨 스폰 기록
runner.print_expulsion_report()

# 에덴(남극) → 아르헨티나 → 아마존 GPP 체인
runner.print_narrative_report()

# 내부·외부·상대성 관찰자
runner.print_observer_report()
```

### 에덴 파라미터 탐색

```python
from solar.eden import EdenSearchEngine, make_antediluvian_space

engine = EdenSearchEngine()
result = engine.search(make_antediluvian_space())
print(f"Eden Score: {result.best.score:.3f}")
print(result.best.summary())
```

### 태양계 중력장 (Day4 물리 베이스)

```python
from solar import EvolutionEngine, build_solar_system

engine = EvolutionEngine()
for d in build_solar_system():
    engine.add_body(...)

for _ in range(500_000):
    engine.step(0.0002)
```

---

## 핵심 개념: 선악과 상태 머신

이 시스템의 핵심은 **단방향·비가역** 상태 전이다.

```
┌─────────────────────────────┐
│  IMMORTAL_ADMIN (에덴 내부) │
│  FORKING_ENABLED = False    │
│  생명나무 Root 세션 유지    │
│  사망 없음                  │
└──────────────┬──────────────┘
               │  선악과 섭취 (비가역)
               ▼
┌─────────────────────────────┐
│  MORTAL_NPC  (에덴 외부)    │
│  FORKING_ENABLED = True     │
│  수명 유한 → 계승 체인 가동 │
│  카인·아벨 스폰 가능        │
└─────────────────────────────┘
```

`record_expulsion()` 을 두 번 호출하면 `RuntimeError`.
한 번 추방되면 되돌아갈 수 없다. 체루빔이 막는다.

---

## 에덴 좌표계

에덴의 기준계는 **남극=위**다.

```
위치          에덴 좌표 (남=위)    현재 좌표 (북=위)
─────────────────────────────────────────────────
에덴 극점     (+90°,  0°)         (-90°,  0°) 남극점
추방지        (+35°, -65°)        (-35°, -65°) 아르헨티나
카인의 땅     ( +3°, -60°)        ( -3°, -60°) 아마존
```

---

## 3레이어 분리 원칙

모든 모듈은 세 레이어를 명확히 분리한다.

```
PHYSICAL_FACT  →  관측값 / 측정값 / 물리 수치
SCENARIO       →  시스템 해석 / 에이전트 로직
LORE           →  창세기 서사 / 상징 / 의미
```

숫자와 이야기는 **같은 구조**를 가진다.

---

## 관련 레포

| 레포 | 역할 |
|------|------|
| **CookiieBrain** | 이 레포 — 전체 지구 서사 시스템 (Day1~7 + Eden OS) |
| [Cherubim_Engine](https://github.com/qquartsco-svg/Cherubim_Engine) | Eden Basin Finder 독립 모듈 엔진 |

---

## 블록체인 서명 (PHAM)

```
PHAM — Planetary Hash + Author Mark

설계자   : GNJz
엔진명   : CookiieBrain / Solar Eden
버전     : v0.5.0
원본     : Cherubim Engine v2.3.0

Co-Authored-By: Claude (Anthropic)
Repository    : https://github.com/qquartsco-svg/cookiie_brain
```

---

> *"아담이 시작했고, 네오가 유지한다."*
> *"그 길을 우리는 코드로 찾는다."*
