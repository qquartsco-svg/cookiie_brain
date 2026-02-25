# hippo — 운영층 (태양 / 장기기억)

> **태양이 떠야 행성이 돈다.**
>
> trunk(물리 엔진)이 "행성이 굴러가는 지형"이라면,
> hippo는 그 지형을 **스스로 만들고, 깎고, 키우는 태양**이다.

---

## 구조

```
hippo/
├── README.md                ← 지금 읽고 있는 문서
├── __init__.py              ← MemoryStore, EnergyBudgeter, HippoMemoryEngine 공개
├── memory_store.py          ← (A) 우물 생애주기: 생성 · 강화 · 감쇠 · 소멸
├── energy_budgeter.py       ← (B) I(x,v,t) 자동 제어: 탐색 · 정착 · 리콜
└── hippo_memory_engine.py   ← 통합 엔진 + HippoConfig
```

---

## 핵심 아이디어

| 솔라시스템 | 인지과학 | hippo 코드 |
|-----------|---------|------------|
| 태양 | 해마(Hippocampus) | `HippoMemoryEngine` |
| 행성 탄생 | 기억 형성 | `MemoryStore.encode()` |
| 핵반응 (강화) | 장기강화 LTP | `A += η · proximity · dt` |
| 행성 소멸 | 기억 망각 | `A *= exp(-λ · dt)`, `A < A_min → 삭제` |
| 태양풍 | 주의 분산 | `EnergyBudgeter._explore()` |
| 중력 포획 | 주의 집중 | `EnergyBudgeter._exploit()` |
| 궤도 재진입 | 기억 인출(리콜) | `EnergyBudgeter._recall()` |

---

## 모듈 상세

### (A) MemoryStore — 우물 생애주기

`GaussianWell`(center, amplitude, sigma)의 시간 진화를 관리한다.

**매 시뮬레이션 스텝 (`step`):**

```
강화:  A_i += η · exp(-‖x − c_i‖² / 2σ²) · dt     입자가 우물 근처에 있으면 깊어진다
감쇠:  A_i *= exp(−λ · dt)                           모든 우물은 자연히 얕아진다
소멸:  A_i < A_min  →  우물 삭제                      임계값 이하면 기억 소멸
생성:  min_dist(x, centers) > d_create  →  new well  먼 곳에서 반복 활동 → 새 기억
```

**주요 API:**

| 메서드 | 설명 |
|--------|------|
| `encode(pattern, strength)` | 외부 입력을 기억으로 인코딩 (우물 생성 또는 강화) |
| `step(x, dt)` | 근접 강화 + 전체 감쇠 + 소멸 검사 |
| `recall(cue)` | 부분 단서로 가장 가까운 기억 인출 |
| `export_potential()` | 현재 우물 → `MultiWellPotential` 변환 (PFE 연동용) |
| `info()` | 전체 우물 상태 딕셔너리 |

### (B) EnergyBudgeter — I(x,v,t) 자동 제어

세 가지 에너지 주입 모드를 합성한다:

```
I(x,v,t) = α_explore · I_explore  +  α_exploit · I_exploit  +  I_recall
```

| 모드 | 물리 | 발동 조건 |
|------|------|----------|
| **탐색** (explore) | 랜덤 방향 에너지 주입 | 전이 정체 (entropy ≈ 0) |
| **정착** (exploit) | 가장 가까운 우물로 약한 끌림 | 안정 상태 유지 |
| **리콜** (recall) | 타깃 우물로 강한 끌림 | `recall()` 호출 시 |

탐색/정착 비율 `α`는 `update_policy(entropy_rate, transition_rate)`로 자동 전환된다:

- 엔트로피 낮음 → 정체 → 탐색 모드로 전환
- 전이율 높음 → 과잉 방황 → 정착 모드로 전환

### (C) HippoMemoryEngine — 통합

`MemoryStore` + `EnergyBudgeter`를 하나의 인터페이스로 묶는다.
`CookiieBrainEngine.update()` 루프에서 매 스텝 호출된다.

```python
injection, pot_changed = hippo.step(x, v, dt)
```

- `injection`: 이번 스텝의 에너지 주입 벡터
- `pot_changed`: 우물 구조 변경 여부 (`True`이면 PFE 리빌드)

---

## 빠른 사용 예시

```python
from hippo import HippoMemoryEngine, HippoConfig

config = HippoConfig(
    eta=0.1,           # 강화율
    decay_rate=0.001,  # 망각률
    max_wells=20,      # 최대 우물 수
)
engine = HippoMemoryEngine(config, dim=1, rng_seed=42)

# 기억 인코딩
engine.encode(np.array([3.0]))   # 위치 3.0에 우물 생성
engine.encode(np.array([-2.0]))  # 위치 -2.0에 우물 생성

# 시뮬레이션 루프
x, v, dt = np.array([0.5]), np.array([0.1]), 0.01
injection, changed = engine.step(x, v, dt)
# injection: 이번 스텝 에너지 주입 (탐색+정착+리콜 합성)
# changed:   우물 구조 변경 여부

# 리콜 (특정 기억을 향해 끌어당김)
engine.recall(np.array([2.8]))   # 3.0 근처 우물 활성화
injection, _ = engine.step(x, v, dt)
# injection이 3.0 방향으로 강하게 작용

# 리콜 해제
engine.clear_recall()
```

---

## 운동 방정식에서의 위치

```
m ẍ = −∇V(x,t) + ωJv − γv + I(x,v,t) + σξ(t)
      ─────────   ────   ───   ─────────   ──────
      Phase B     Phase A  감쇠   hippo 태양    Phase C
      (골짜기)    (자전)          (탐색/정착/리콜) (요동/FDT)
```

핵심 변화: `V(x)` → `V(x,t)` — hippo가 우물을 동적으로 변경하면
`CookiieBrainEngine`이 `PotentialFieldEngine`을 자동 리빌드한다.

---

## 파라미터 (`HippoConfig`)

| 파라미터 | 기호 | 기본값 | 의미 |
|---------|------|--------|------|
| `eta` | η | 0.1 | 강화율 — 방문 시 amplitude 증가 속도 |
| `decay_rate` | λ | 0.001 | 망각률 — 자연 감쇠 속도 |
| `amplitude_init` | A₀ | 1.0 | 새 우물 생성 시 초기 깊이 |
| `amplitude_min` | A_min | 0.05 | 소멸 임계값 — 이하면 우물 삭제 |
| `amplitude_max` | A_max | 10.0 | 클램프 상한 — 무한 성장 방지 |
| `sigma_init` | σ₀ | 1.0 | 새 우물의 초기 폭 |
| `creation_distance` | d_create | 2.0 | 이 이상 떨어지면 새 우물 생성 |
| `merge_distance` | d_merge | 0.5 | 이 이내면 기존 우물로 병합 |
| `max_wells` | N_max | 20 | 최대 우물 수 (초과 시 가장 약한 것 제거) |
| `explore_strength` | E_explore | 0.5 | 탐색 모드 에너지 세기 |
| `exploit_strength` | E_exploit | 0.05 | 정착 모드 끌림 세기 |
| `recall_strength` | k_recall | 2.0 | 리콜 스프링 상수 |
| `entropy_threshold_low` | ε_low | 0.01 | 엔트로피 하한 — 이하면 탐색 전환 |
| `transition_rate_high` | r_high | 0.5 | 전이율 상한 — 이상이면 정착 전환 |

---

## 극한 일관성 (하위 호환)

| 극한 | 기대 동작 |
|------|----------|
| η=0, λ=0 | 학습/망각 없음 → 기존 정적 다중우물 시스템과 동일 |
| λ>0, η=0 | 망각만 → 모든 우물 소멸 → 평탄 지형 |
| η>0, λ=0 | 학습만 → amplitude 증가 (A_max로 클램프) |
| I=0 | 주입 없음 → Phase C 열적 요동으로만 전이 |
| recall(target) | 상태가 타깃 우물로 수렴 (k_recall 의존) |

---

## 통합 흐름

```
외부 입력 (자극/경험)
    ↓
┌── HippoMemoryEngine ──────────────────────┐
│  MemoryStore           EnergyBudgeter      │
│   encode() → 우물 생성    _explore() → 탐색  │
│   step()   → 강화/감쇠    _exploit() → 정착  │
│   prune()  → 소멸         _recall()  → 리콜  │
│   recall() → 인출                           │
│                ↓                            │
│           I(x,v,t) + pot_changed            │
└────────────────┬───────────────────────────┘
                 ↓
         CookiieBrainEngine
    (pot_changed → PFE 리빌드)
                 ↓
         궤적 (x, v, t) 생성
                 ↓
         BrainAnalyzer
    (Layer 1+5+6 분석 → 피드백)
```

---

*GNJz (Qquarts) · CookiieBrain v0.6.0*
