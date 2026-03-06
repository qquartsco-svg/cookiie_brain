# CookiieBrain — 레이어 아키텍처

> 모든 레이어는 **하나의 상태공간(State Space)** 위에서 맞물린다.
> 서사가 위에서 흐르고, 물리 엔진이 아래에서 받쳐주고, 기억이 각인되고, 분석이 관찰한다.

---

## 전체 레이어 흐름

```
┌────────────────────────────────────────────────────────────┐
│  L0_solar/  — 서사 레이어 (Layer 0)                        │
│                                                            │
│  _01_beginnings                                           │
│       ↓  행성 거시 조건 (instability, planet_stress)        │
│  _02_creation_days  (Day 1 ~ Day 7)                       │
│       ↓  6도메인 스냅샷 (대기·수권·지질·자기권·궤도·생물권)    │
│  _03_eden_os_underworld                                    │
│       ↓  에덴 Basin 운영. 체루빔 가드. 하데스 심층 모니터    │
│  _04_firmament_era                                         │
│       ↓  instability ≥ 0.85 → 창공 붕괴 트리거             │
│  _05_noah_flood                                            │
│       ↓  impulse_shock → E_eff_MT, delta_T_pole            │
│  _06_lucifer_impact                                        │
│       ↓  AOD, solar_block, H2O_canopy                     │
│  _07_polar_ice           (단기 0~50yr)                     │
│       ↓  T_pole_final, h_ice                              │
│  _08_ice_age             (장기 ~100,000yr)                 │
│       → 빙하선 60°N, 해수면 −125m, LGM                     │
└─────────────────────┬──────────────────────────────────────┘
                      │ cookiie_brain_engine.py
                      │ (레이어 간 오케스트레이터)
          ┌───────────┼───────────┐
          ↓           ↓           ↓
┌──────────────┐ ┌──────────┐ ┌──────────────┐
│ L1_dynamics/ │ │L3_memory/│ │ L4_analysis/ │
│              │ │          │ │              │
│ Phase_A      │ │ Hippo    │ │ Layer_1~6    │
│ 자전·조석·   │ │ 우물 생성 │ │ 측정·분석    │
│ 코리올리     │ │ 강화·감쇠 │ │ (읽기 전용)  │
│              │ │ 소멸     │ │              │
│ Phase_B      │ │          │ │ Layer_1: 통계│
│ 에너지 우물  │ │ Energy   │ │ Layer_2: N체│
│ → 가우시안   │ │ Budgeter │ │ Layer_3: 게이│
│              │ │          │ │ Layer_4: 요동│
│ Phase_C      │ │ Memory   │ │ Layer_5: 확률│
│ 열적 요동    │ │ Store    │ │ Layer_6: 기하│
│ FDT          │ │          │ │ 위상         │
└──────────────┘ └──────────┘ └──────────────┘
```

---

## 각 레이어 상세

### Layer 0 — 서사 (`L0_solar/`)

**하는 일**: 창조부터 빙하시대까지 서사 시나리오 실행.
각 단계는 상태 벡터를 읽고 갱신해 다음 단계로 넘긴다.

| 모듈 | 입력 | 출력 |
|---|---|---|
| `_01_beginnings/joe` | 행성 파라미터 | instability, planet_stress |
| `_02_creation_days` | IC | 6도메인 스냅샷 |
| `_03_eden_os_underworld` | 스냅샷 | 에덴 Basin 상태 |
| `_04_firmament_era` | 에덴 상태 | H2O_canopy, collapse_triggered |
| `_05_noah_flood` | instability + impulse | FloodSnapshot, impulse_shock |
| `_06_lucifer_impact` | D_km, v_kms | E_eff_MT, AOD, delta_T_pole |
| `_07_polar_ice` | E_eff_MT, delta_T | T_pole_K, h_ice_m |
| `_08_ice_age` | T_pole_K, V_ice | 빙하선, 해수면, T_global |

---

### Layer 1~2 — 동역학 (`L1_dynamics/`)

**하는 일**: L0의 서사가 돌아갈 **물리 장(field)** 을 만든다.

| 파즈 | 역할 | 핵심 출력 |
|---|---|---|
| Phase_A | 자전·조석·코리올리 | 회전 에너지 장 |
| Phase_B | 우물→가우시안 변환 | 에너지 지형 |
| Phase_C | 열적 요동·FDT | 확률적 진동 |

---

### Layer 3 — 기억 (`L3_memory/`)

**하는 일**: L0의 서사 이벤트를 **Hippo 우물**로 각인한다.

```
노아 홍수 impulse  → well 생성 (깊이 ∝ 충격 강도)
루시퍼 충돌       → well 강화
빙하 형성         → well 확장 (시간 스케일 확장)
```

| 파일 | 역할 |
|---|---|
| `hippo_memory_engine.py` | 우물 생성·강화·감쇠 |
| `energy_budgeter.py` | 탐색/정착/리콜 에너지 관리 |
| `memory_store.py` | 우물 저장소 |

---

### Layer 4 — 분석 (`L4_analysis/`)

**하는 일**: 시스템을 **변경하지 않고** 궤적과 물리량을 측정한다.

| 레이어 | 측정 대상 |
|---|---|
| Layer_1 | 통계역학 (엔트로피·분포) |
| Layer_2 | N체 역학 (궤도·중력) |
| Layer_3 | 게이지 이론 (대칭·보존) |
| Layer_4 | 요동 정리 (FDT 검증) |
| Layer_5 | 확률적 역학 (Fokker-Planck) |
| Layer_6 | 기하 위상 (Berry phase) |

---

## 통합 오케스트레이터 (`cookiie_brain_engine.py`)

```python
# 전체 레이어 연결
from cookiie_brain_engine import CookiieBrainEngine
engine = CookiieBrainEngine()
engine.run_full_pipeline()
```

내부 구성:
1. `WellFormationEngine` → W, b 행렬 생성
2. `PotentialFieldEngine` → 에너지 지형 변환
3. `TidalField` → 3계층 중력 (태양·달·조석)
4. `HippoMemoryEngine` → 장기 기억
5. `CerebellumEngine` → 운동 조율

---

## 블록체인 서명 (`blockchain/`)

모든 핵심 모듈은 PHAM Chain으로 서명 추적된다.

```bash
# 서명
cd blockchain
python3 pham_sign_v4.py ../L0_solar/_07_polar_ice/simulation.py \
    --author "GNJz" --desc "극지 결빙 시뮬레이션"

# 검증
python3 pham_verify_chain.py pham_chain_simulation.json
```

각 블록: `{ sha256, author, timestamp, description, prev_hash }`
→ 재현 가능성·변조 추적·서사 완결성 보장

---

## 독립 엔진 (`ENGINE_HUB/`)

```
ENGINE_HUB/ → 00_BRAIN/ENGINE_HUB (심볼릭 링크)
└── 00_PLANET_LAYER/
    └── Lucifer_Engine/    혜성 궤도·충돌 완전 독립 패키지
```

`_06_lucifer_impact`는 `Lucifer_Engine` 설치 여부에 따라
자동으로 3단계 폴백(full_pipeline → effects_only → impact_only)으로 동작한다.

---

## 레이어가 아닌 것

| 폴더 | 종류 | 설명 |
|---|---|---|
| `examples/` | 검증·데모 | 레이어 실행 스크립트 |
| `docs/` | 설계 문서 | 개념·아키텍처 문서 |
| `blockchain/` | 서명 기록 | PHAM 체인 |
| `ENGINE_HUB` | 심볼릭 링크 | 독립 엔진 허브 |
