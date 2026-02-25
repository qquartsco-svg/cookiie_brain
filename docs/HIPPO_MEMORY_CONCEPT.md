# HippoMemoryEngine — 태양의 탄생

> **한 문장**: 물리 엔진(Phase A~C)이 "행성이 굴러가는 지형"이라면,
> HippoMemoryEngine은 그 지형을 **스스로 만들고, 깎고, 키우는 태양**이다.

---

## 0. 왜 필요한가

현재 CookiieBrain은 이렇게 작동한다:

```
[누군가가 우물을 수동 배치] → PFE가 궤적 생성 → Layer 1~6이 분석
```

문제: **우물을 누가 만드는가?** 지금은 사람이 직접 좌표를 지정하거나,
WellFormation이 단발성으로 생성할 뿐이다. 우물이 강화되거나 사라지지 않는다.

이건 태양 없는 태양계다. 행성은 있는데 궤도를 유지시키는 에너지원이 없다.

---

## 1. 세 관점에서 본 HippoMemoryEngine

### 솔라시스템 관점

| 구성 | 역할 | 수식 |
|------|------|------|
| **태양** | 중심 에너지원. 행성 생성/소멸 제어 | `I(x,v,t)` 주입 정책 |
| 행성 | 안정 상태 덩어리 | `GaussianWell` (center, A, σ) |
| 궤도 | 행성 간 순환 | Phase B 공전 + Kramers 탈출 |
| 태양풍 | 확률적 교란 | Phase C 요동 `σξ(t)` |
| 중력 | 행성을 궤도에 묶는 힘 | `-∇V(x)` gradient |

**태양이 하는 일:**
- 행성(우물)을 **생성**한다 — 외부 입력이 특정 영역에 집중되면 우물 탄생
- 행성을 **강화**한다 — 반복 방문하면 amplitude 증가 (핵반응 ≈ 강화학습)
- 행성을 **소멸**시킨다 — 오래 방문하지 않으면 amplitude 감소 → 사라짐
- **에너지를 배분**한다 — 탐색/정착 모드로 `I(x,v,t)` 제어

### 인지과학 관점

| 구성 | 역할 |
|------|------|
| **해마(Hippocampus)** | 장기기억 형성·인출의 중추 |
| 우물 | 개별 기억 |
| 우물 깊이 A(t) | 기억 강도 (시간에 따라 변화) |
| 우물 폭 σ(t) | 기억의 유인 범위 (일반화 정도) |
| 강화 | 반복 경험 → 기억 고착 (LTP) |
| 망각 | 비사용 시 약화 (자연 감쇠) |
| 리콜 | 부분 단서 → 해당 우물로 수렴 |
| 간섭 | 유사 기억 간 경쟁 (근접 우물 병합/분리) |

**에너지 주입 정책 = 주의(Attention):**
- 탐색 모드 = 주의 분산: 새 자극 탐색, 에너지 넓게 분배
- 정착 모드 = 주의 집중: 특정 기억에 몰입, 에너지 국소 집중
- 리콜 모드 = 방향성 주의: 특정 위치로 끌어당기는 외부력

### 물리/공학 관점

| 구성 | 수식 | 설명 |
|------|------|------|
| 운동 방정식 | `m ẍ = -∇V(x,t) + ωJv - γv + I(x,v,t) + σξ(t)` | V가 이제 시간 의존 |
| 우물 생애주기 | `dA_i/dt = η·δ(visit_i) - λ·A_i` | 방문 시 강화, 자연 감쇠 |
| 에너지 주입 | `I = I_explore + I_exploit + I_recall` | 세 모드의 합성 |
| 정상 상태 조건 | `⟨dA/dt⟩ = 0` → `A_eq = η·f_visit / λ` | 방문 빈도와 감쇠의 균형 |

핵심 물리:
- **V(x, t)**: 이제 퍼텐셜이 시간에 따라 변한다 (비정적 지형)
- Layer 4 비평형 일 정리가 여기서 진가를 발휘한다: `dV/dt ≠ 0`이면 일(work)이 발생
- Layer 1 엔트로피 생산이 "기억 갱신 비용"을 측정한다

---

## 2. 설계: 두 개의 핵심 모듈

### (A) MemoryStore — 우물 구조 갱신

WellRegistry를 확장하여 **시간 의존 우물 관리**를 추가한다.

```
기존 WellRegistry:
  add() → 우물 추가 (한 번 추가되면 영원불변)

HippoMemoryEngine MemoryStore:
  encode()    → 새 입력 패턴으로 우물 생성/강화
  decay()     → 전체 우물 amplitude 자연 감쇠
  prune()     → threshold 이하 우물 제거
  recall()    → 부분 단서 → 가장 가까운 우물 활성화
```

**강화 규칙:**
```
A_i(t + dt) = A_i(t) + η · proximity(x, c_i)    (방문 시)
A_i(t + dt) = A_i(t) · exp(-λ · dt)              (매 스텝)
```
- `η`: 강화율 (learning rate)
- `λ`: 망각률 (decay rate)
- `proximity(x, c)`: `exp(-||x - c||² / (2σ²))` — 우물 근처에 있을수록 강하게 강화
- `A < A_threshold` → 우물 삭제 (기억 소멸)

**생성 규칙:**
```
if min_dist(x, all_centers) > creation_threshold:
    new_well = GaussianWell(center=x, amplitude=A_init, sigma=σ_init)
```
- 기존 우물에서 먼 곳에서 반복 활동하면 새 기억 형성

### (B) EnergyBudgeter — I(x,v,t) 자동 제어

세 가지 주입 모드를 합성한다:

```
I(x,v,t) = α_explore · I_explore + α_exploit · I_exploit + α_recall · I_recall
```

| 모드 | I 정의 | 발동 조건 |
|------|--------|----------|
| **탐색** (explore) | 랜덤 방향, 에너지 증가 | 전이 정체 (entropy ≈ 0) |
| **정착** (exploit) | 현재 우물 방향으로 약한 끌림 | 안정 상태 유지 |
| **리콜** (recall) | 특정 우물 c_target 방향으로 강한 끌림 | 외부 리콜 요청 시 |

**탐색-정착 전환 (자동):**
```
if entropy_production < ε_low:
    α_explore ↑, α_exploit ↓    (정체 → 탐색)
elif transition_rate > r_high:
    α_explore ↓, α_exploit ↑    (과잉 방황 → 정착)
```

이것이 피드백 2에서 말한 **"에너지 배분 정책"**이다.

---

## 3. 전체 통합 흐름 (HippoMemory 추가 후)

```
외부 입력 (자극/경험)
    ↓
┌── HippoMemoryEngine ──────────────────────┐
│                                            │
│  [MemoryStore]        [EnergyBudgeter]     │
│   encode() ──→ 우물 생성/강화               │
│   decay()  ──→ 우물 자연 감쇠               │
│   prune()  ──→ 소멸된 기억 제거             │
│   recall() ──→ 리콜 타깃 설정               │
│                   │                        │
│                   ↓                        │
│              I(x,v,t) 정책 결정              │
│                                            │
└────────────────┬───────────────────────────┘
                 ↓
┌── PotentialFieldEngine (trunk) ────────────┐
│                                            │
│  m ẍ = -∇V(x,t) + ωJv - γv + I + σξ      │
│                                            │
│  Phase A: 자전 (ωJv)                       │
│  Phase B: 궤도 (-∇V, 동적 우물)             │
│  Phase C: 요동 (σξ, FDT)                   │
│                                            │
└────────────────┬───────────────────────────┘
                 ↓
              궤적 (x, v, t)
                 ↓
┌── BrainAnalyzer (analysis) ────────────────┐
│                                            │
│  Layer 1: 전이 확률, 엔트로피               │
│  Layer 5: 확률 밀도, Nelson 분해             │
│  Layer 6: Fisher 계량, 곡률                 │
│                                            │
│  → 리포트 → EnergyBudgeter 피드백           │
│                                            │
└────────────────────────────────────────────┘
```

**핵심 변화:**
- V(x)가 V(x, t)로 변한다 — 지형이 살아 움직인다
- I(x,v,t)가 자동 제어된다 — 정체/방황에 반응
- BrainAnalyzer의 출력이 EnergyBudgeter로 피드백된다 — 폐루프

---

## 4. 극한 일관성

| 극한 | 기대 동작 | 보장 |
|------|----------|------|
| η=0, λ=0 (학습/망각 없음) | 기존 정적 시스템과 동일 | 하위 호환 |
| λ>0, η=0 (망각만) | 모든 우물 소멸 → 평탄 지형 | 구조적 |
| η>0, λ=0 (학습만) | 우물 무한 성장 → amplitude 발산 | A_max 클램프 |
| I=0 (주입 없음) | Phase C 요동으로만 전이 | 기존 동작 |
| recall(target) | 상태가 target 우물로 수렴 | I_recall 세기 의존 |
| 입력 시퀀스 반복 | 해당 우물 강화, 비방문 우물 약화 | η·f > λ 조건 |

---

## 5. MVP 검증 시나리오

### 테스트: "기억 3개 형성 → 망각 → 리콜"

```
1. 위치 A, B, C에 순서대로 입력 자극 → 우물 3개 자동 형성
2. 시뮬레이션 진행 → 공전 시작 (wells ≥ 3)
3. A만 반복 자극 → A 강화, B·C 망각 시작
4. 시간 경과 → C 소멸 (amplitude < threshold)
5. recall(B 근처 단서) → 상태가 B로 수렴 (아직 살아있으면)
6. 전체 Layer 1~6 분석 → 리포트
```

**검증 항목:**
1. 우물 자동 생성 (3개)
2. 반복 자극 → amplitude 증가
3. 비방문 → amplitude 감소
4. threshold 이하 → 우물 삭제
5. recall → 상태 수렴
6. Layer 1 전이 패턴 변화 관측
7. 하위 호환 (η=0, λ=0 → 기존 동작)

---

## 6. 핵심 파라미터 정리

| 파라미터 | 기호 | 기본값 | 의미 |
|---------|------|--------|------|
| 강화율 | η (eta) | 0.1 | 방문 시 amplitude 증가 속도 |
| 망각률 | λ (lambda) | 0.001 | 자연 감쇠 속도 |
| 초기 amplitude | A_init | 1.0 | 새 우물 생성 시 깊이 |
| 소멸 threshold | A_min | 0.05 | 이 이하면 우물 삭제 |
| 최대 amplitude | A_max | 10.0 | 클램프 상한 |
| 생성 거리 | d_create | 2.0 | 기존 우물에서 이 이상 떨어지면 새 우물 |
| 탐색 에너지 | E_explore | 0.5 | 탐색 모드 주입 세기 |
| 정착 에너지 | E_exploit | 0.05 | 정착 모드 주입 세기 |
| 리콜 세기 | k_recall | 2.0 | 리콜 시 끌림 스프링 상수 |
| 엔트로피 하한 | ε_low | 0.01 | 이 이하면 탐색 모드 전환 |
| 전이율 상한 | r_high | 0.5 | 이 이상이면 정착 모드 전환 |

---

## 7. 솔라시스템 ↔ 인지 ↔ 물리 대응표

| 솔라시스템 | 인지과학 | CookiieBrain 구현 | 수식 |
|-----------|---------|-------------------|------|
| 태양 | 해마(Hippocampus) | HippoMemoryEngine | MemoryStore + EnergyBudgeter |
| 태양의 핵반응 | 장기강화(LTP) | encode() + η | `A += η·proximity` |
| 태양풍 | 주의 분산 | I_explore | 랜덤 방향 에너지 주입 |
| 중력 포획 | 기억 고착 | I_exploit | 우물 방향 끌림 |
| 행성 형성 | 기억 생성 | add_well() | `d > d_create → new well` |
| 행성 소멸 | 기억 망각 | decay() + prune() | `A *= e^{-λt}, A < A_min → 삭제` |
| 궤도 안정화 | 연상 패턴 | Phase B + Kramers | 다중 우물 순환 |
| 태양계 리듬 | 인지 리듬 | Phase A 자전 + 공전 | ωJv + 다중 우물 |
| 소행성 충돌 | 새 자극 | 외부 입력 | encode(new_pattern) |
| 행성 간 중력 | 기억 간 간섭 | Layer 2 N-body | `F_ij = -∇φ(r_ij)` |

---

*GNJz (Qquarts) · CookiieBrain v0.6.0*
*"태양이 떠야 행성이 돈다."*
