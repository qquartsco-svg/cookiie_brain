# CookiieBrain — 전체 개념과 현재 상태

> 이 문서는 프로젝트의 물리적 개념, 구현 상태, 검증 결과, 다음 방향을
> 하나로 정리한 것이다. 새로 합류하는 사람이 이 문서 하나로 전체를 파악할 수 있어야 한다.

**마지막 업데이트: 2026-02-24 (Layer 2 다체/장론 구현 반영)**

---

## 0. 한 문장 요약

**공이 산과 골짜기가 있는 지형 위에서 굴러가는 시스템을 만들고 있다.**
골짜기 = 기억, 공 = 현재 상태, 공의 궤적 = 사고의 흐름.

---

## 1. 무엇을 만들고 있나 — 큰 그림

### 비유

| 물리 | 인지 비유 |
|---|---|
| 골짜기 (Gaussian well) | 기억 하나 |
| 골짜기의 깊이 (amplitude) | 기억의 강도 |
| 골짜기의 폭 (sigma) | 기억의 유인 범위 |
| 공 (state vector) | 현재 사고 상태 |
| 공의 속도 | 사고의 활성도 |
| 공이 골짜기 안에서 회전 (자전) | 한 기억 안에서 생각이 활성 상태로 유지됨 |
| 공이 골짜기 사이를 이동 (공전) | 기억 간 연상, 사고 전환 |
| 감쇠 (γ) | 피로, 망각, 활성 감소 |
| 외부 주입 (I) | 새 자극, 각성, 외부 입력 |
| 요동 (ξ) | 예측 불가능한 변동, 창의적 전환 |

### 전체 운동 방정식 (현재)

```
m ẍ = -∇V(x) + ωJv - γv + I(x,v,t) + σξ(t)
```

| 항 | 이름 | 역할 | 에너지 영향 |
|---|---|---|---|
| `-∇V(x)` | 퍼텐셜 gradient | 골짜기로 끌어당김 (보존력) | 보존 |
| `ωJv` | 코리올리 회전 | 속도 방향만 꺾음 (자전/공전 방향) | 보존 (v·Jv=0) |
| `-γv` | 감쇠 | 속도에 비례해 에너지를 빼앗음 | **소산** |
| `I(x,v,t)` | 외부 주입 | 외부에서 에너지를 넣어줌 | **주입** |
| `σξ(t)` | 확률적 요동 | 매 순간 랜덤 방향으로 밀어줌 | **확률적** |

**요동-소산 정리 (FDT):**
```
σ² = 2γT/m    (kB = 1 자연단위)
```
temperature(T) 설정 시 σ가 γ, T, m으로부터 자동 결정.
정상 분포 보장: P(x,v) ∝ exp(-E/T), 등분배 ⟨½mv²⟩ = T/2 (per DoF).

**에너지 밸런스:**

```
E = ½||v||² + V(x)
dE/dt = -γ||v||² + v·I(x,v,t) + (노이즈 기여)
```

- γ=0, I=0, σ=0 → 에너지 보존 (영원히 같은 궤도)
- γ>0, I=0, σ=0 → 에너지 감소 (결국 하나의 골짜기에 갇힘)
- γ=0, I≠0, σ=0 → 에너지 증가 가능 (갇힌 상태에서 탈출 가능)
- γ>0, I≠0, σ=0 → 감쇠와 주입의 균형 (현실적 동역학)
- γ>0, σ>0 → 감쇠+요동의 평형 (열적 정상 상태, Kramers 탈출 가능)

---

## 2. 각 단계의 개념과 수식

### 2-1. 정적 퍼텐셜 (기반)

**개념**: 경험(episodes)이 쌓이면 지형에 골짜기가 파인다.

**Hopfield 퍼텐셜** (WellFormationEngine 출력, 단일 우물):

```
V_hopfield(x) = -½ x'Wx - b'x
```

- W: 경험으로부터 Hebbian 학습으로 생성된 가중치 행렬
- b: 바이어스 벡터
- 연속 공간에서 지역 최솟값 최대 1개 → 단일 기억

**Gaussian 다중 우물 퍼텐셜** (Phase B, 다중 기억):

```
V(x) = -Σᵢ Aᵢ exp(-||x - cᵢ||² / (2σᵢ²))
```

- 각 Gaussian이 하나의 기억 (독립적인 골짜기)
- 여러 개 배치하면 → 기억 사이 장벽 형성 → 전이/순환 가능
- cᵢ: 기억 위치, Aᵢ: 기억 강도, σᵢ: 유인 범위

**왜 두 가지인가:**
Hopfield는 경험으로부터 자동 생성되지만 우물 1개만 만든다.
Gaussian은 여러 우물을 가질 수 있지만 좌표를 정해줘야 한다.
→ "브릿지"가 Hopfield 결과를 누적하여 Gaussian 다중 우물로 변환한다.

---

### 2-2. Phase A — 자전 (Spin)

**개념**: 공이 골짜기 바닥에서 멈추지 않고 회전한다.
멈추면 "고정된 기억"일 뿐이다. 회전하면 "활성화된 기억"이 된다.

**수식**: 속도에 수직인 힘을 가한다.

```
R(v) = ωJv     여기서 J = [[0, -1], [1, 0]]
```

- J는 90° 회전 행렬 (반대칭)
- v·Jv = 0 → 에너지가 변하지 않는다 (구조적 보장)
- ω: 회전 속도 (파라미터 하나로 제어)
- 물리적 비유: 자기장 속 하전 입자의 Lorentz force와 동일 구조

**적분**: Strang splitting (Boris 방식)

```
1. half drift:     x_half = x + (dt/2)·v
2. half kick:      v⁻ = v + (dt/2)·g(x_half)
3. exact rotation: v_rot = R(ωdt)·v⁻        ← |v| 정확 보존
4. half kick:      v_new = v_rot + (dt/2)·g(x_half)
5. half drift:     x_new = x_half + (dt/2)·v_new
```

회전을 exp(ωJdt) (회전행렬)로 정확히 적용 → 속력 완벽 보존 → 장기 drift 없음.

**검증 결과:**
- 에너지 보존: < 0.01% drift
- 궤도 유계: 공이 무한히 멀어지지 않음
- v·R = 0 직교: 매 스텝 확인

---

### 2-3. Phase B — 공전 (Orbit)

**개념**: 공이 하나의 골짜기에 머무르지 않고 여러 골짜기를 순환한다.
"기억 A를 떠올리다가 기억 B로, 다시 C로, 그리고 다시 A로 돌아오는" 연상 과정.

**왜 Hopfield로는 안 되는가:**
Hopfield 이차 퍼텐셜은 연속 공간에서 지역 최솟값이 최대 1개다.
공전하려면 분리된 여러 최솟값이 필요하다 → Gaussian 다중 우물.

**공전의 조건 (실험으로 발견):**

| 조건 | 역할 |
|---|---|
| 우물 3개 이상, 비직선 배치 (삼각형) | 순환 경로가 존재 |
| E > V_saddle (에너지가 장벽보다 높음) | 장벽 통과 가능 |
| ωJv (코리올리) | 궤도를 한 방향으로 꺾어 순환 방향 생성 |
| ω가 적절한 크기 | 너무 크면 우물 내부에서만 회전, 너무 작으면 방향성 없음 |

**왜 우물 2개로는 안 되는가:**
직선 배치 2개 → ωJv가 순환 방향을 만들지 못함 → 왕복만 가능, 공전 아님.
3개 삼각형 → ωJv가 한쪽으로 꺾어줌 → A→B→C→A 한 방향 순환.

**삼각형 중앙의 물리:**
- 중앙은 극댓값 (언덕 꼭대기), 안장점이 아님 (Hessian이 음정부호)
- 안장점은 삼각형의 변 위 (우물 사이)에 존재
- ωJv에 의한 궤적 편향은 공간 전체에서 균일하게 작용, 중앙이 특별하지 않음

**검증 결과 (3-우물, 삼각형, ω=0.3):**
- 순환 횟수: 8 (A→B→C→A)
- 주 순환 방향: 88% (한 방향 우세)
- 에너지 보존: 0.0006%
- E < V_saddle → 전이 0 (갇힘 확인)

---

### 2-4. WellFormation → Gaussian 브릿지

**개념**: "경험이 쌓이면 자동으로 골짜기가 생기고, 골짜기가 3개 이상 모이면 공전이 시작된다."

**문제**: WellFormation은 Hopfield (W, b)를 출력한다. 이건 단일 우물이다.
공전에는 Gaussian 다중 우물이 필요하다. 변환이 필요.

**변환 수식:**

| 파라미터 | 추출 방법 | 의미 |
|---|---|---|
| center | mean(post_activity) | 경험 패턴의 중심 위치 |
| amplitude | spectral_radius(W) × scale | 가중치 행렬의 최대 고유값 → 기억 강도 |
| sigma | scale / √(mean\|λ_neg\|) | W의 음 고유값 역수 → 유인 범위 |

**WellRegistry (누적 저장소):**
- WellFormation 결과를 반복 수신 → GaussianWell로 변환 → 누적
- 거리 기반 중복 제거 (가까운 우물은 가중 평균으로 병합)
- wells ≥ 3 → Gaussian 모드 자동 전환 (cookiie_brain_engine에서)

**파이프라인:**

```
경험 1 → WellFormation → W₁, b₁ → GaussianWell #0 → Registry
경험 2 → WellFormation → W₂, b₂ → GaussianWell #1 → Registry
경험 3 → WellFormation → W₃, b₃ → GaussianWell #2 → Registry
                                                      ↓ (count ≥ 3)
                                             MultiWellPotential
                                                      ↓
                                             PotentialFieldEngine
                                                      ↓
                                             자전 + 공전 자동 시작
```

**검증 결과:**
- 변환 정확성: center error 0.024 (PASS)
- 중복 제거: 근접 우물 → 1개로 병합 (PASS)
- 장벽 양수: barrier ≈ 1.96 (PASS)
- 공전 재현: 5순환, 18전이 (PASS)

---

### 2-5. 에너지 주입/소산

**개념**: 보존계에서 비보존계로 전환. 에너지가 줄고 늘어난다.

**왜 필요한가:**
- 보존계: 공전하면 영원히 공전. 갇히면 영원히 갇힘. 변화 없음.
- 비보존계: 감쇠로 공전→갇힘 전이, 주입으로 갇힘→공전 전이 가능.
- 현실 인지: "피로해서 한 생각에 고착" → "새 자극 받아 다른 기억 연상"

**추가된 항:**

```
이전:  ẍ = -∇V(x) + ωJv                     (에너지 보존)
이후:  ẍ = -∇V(x) + ωJv - γv + I(x,v,t)    (에너지 변동)
```

| 항 | 물리 | 인지 비유 |
|---|---|---|
| `-γv` | 마찰 (속도에 비례한 감쇠) | 피로, 망각, 활성 감소 |
| `I(x,v,t)` | 외부 힘 (시간/위치 의존) | 새 자극, 각성, 외부 입력 |

**적분 (Modified Strang splitting):**

```
D(dt/2) → S(dt/2) → K(dt/2) → R(dt) → K(dt/2) → S(dt/2) → D(dt/2)
```

- D: v *= exp(-γ·dt/2) — 감쇠 정확해, 대칭 래핑 (무조건 안정)
- S: drift (위치 업데이트)
- K: kick (gradient + injection)
- R: exact rotation (코리올리)
- γ=0, I=None이면 기존 Strang splitting과 100% 동일 (하위 호환)

**검증 결과:**
- 하위 호환 (γ=0): PASS (E drift 9.25e-06, 14전이)
- 감쇠→갇힘 (γ=0.02): PASS (E: 0.699→-1.900, 후반 전이 0)
- 주입→전이 (pulse): PASS (E<V_saddle→3우물 방문)
- 에너지 밸런스: PASS (상관 0.999995, 비율 1.0001)

---

## 3. 현재 시스템 — 전체 파이프라인

```
경험(episodes)
    ↓
WellFormationEngine          Hebbian 학습 → W, b
    ↓
WellRegistry                 W, b → GaussianWell 변환, 누적
    ↓ (wells ≥ 3)
MultiWellPotential           V(x) = -Σ A exp(-||x-c||²/2σ²)
    ↓
PotentialFieldEngine
    ├── -∇V(x)               퍼텐셜 gradient (골짜기 인력)
    ├── ωJv                   코리올리 회전 (자전/공전 방향)
    ├── -γv                   감쇠 (에너지 소산)
    ├── I(x,v,t)              외부 주입 (에너지 공급)
    └── σξ(t)                 확률적 요동 (Langevin noise)
    ↓
상태 벡터 (x, v) 업데이트
    ↓
Extensions에 기록
    ├── potential_field: V, E, g, time, gamma, noise_sigma, noise_mode, temperature, mass, ...
    ├── well_formation: W, b
    └── well_registry: n_wells, ready_for_orbit, wells info
```

---

## 4. 구현 상태 요약

| 단계 | 상태 | 핵심 수식 | 검증 |
|---|---|---|---|
| 정적 퍼텐셜 | ✔ | V = -½x'Wx - b'x | — |
| 자전 (Phase A) | ✔ | ẍ = g(x) + ωJv | ALL PASS (에너지 <0.01%) |
| 공전 (Phase B) | ✔ | V = -ΣA exp(...) + ωJv | ALL PASS (8순환, 88%) |
| WellFormation 브릿지 | ✔ | W,b → center/A/σ | ALL PASS (5항목) |
| 에너지 주입/소산 | ✔ | -γv + I(x,v,t) | ALL PASS (상관 0.999995) |
| 요동 (Phase C) | ✔ | +σξ(t), σ²=2γT/m (FDT) | ALL PASS (v1: 4항목, v2: 5항목) |
| **Layer 1: 통계역학** | ✔ | Kramers rate, 전이행렬, dS/dt | ALL PASS (5항목) |

---

## 5. 파일 구조 (현재)

```
CookiieBrain/
├── cookiie_brain_engine.py          # 통합 엔진 (오케스트레이션)
│                                      WellFormation → Registry → PFE 자동 연결
│                                      gamma, injection_func config 전달
├── README.md                        # 프로젝트 소개
├── trunk/                           # ── 줄기 (운동방정식 구성요소) ──
│   ├── Phase_A/                     #   자전 (ωJv 코리올리 회전)
│   │   ├── rotational_field.py
│   │   ├── moon.py
│   │   └── docs/
│   ├── Phase_B/                     #   공전 (가우시안 다중 우물)
│   │   ├── multi_well_potential.py
│   │   └── well_to_gaussian.py
│   └── Phase_C/                     #   요동 (Langevin noise, FDT)
│       ├── README.md / README_EN.md
│       └── (구현은 PFE에 내장)
├── analysis/                        # ── 분석 도구 (trunk 위에 쌓임) ──
│   ├── Layer_1/                     #   통계역학 (Kramers, 전이, 엔트로피)
│   ├── Layer_2/                     #   다체/장론 (N-body 상호작용)
│   ├── Layer_3/                     #   게이지/기하학 (위치 의존 B(x))
│   ├── Layer_4/                     #   비평형 일 정리 (Jarzynski, Crooks)
│   ├── Layer_5/                     #   확률역학 (Fokker-Planck, Nelson)
│   └── Layer_6/                     #   정보 기하학 (Fisher 계량, 곡률)
├── examples/
│   ├── phase_a_minimal_verification.py       # 자전 검증
│   ├── phase_b_orbit_verification.py         # 공전 검증 (3-우물)
│   ├── bridge_verification.py                # 브릿지 검증
│   ├── dissipation_injection_verification.py # 에너지 주입/소산 검증
│   ├── fluctuation_verification.py           # 요동 검증
│   ├── fdt_verification.py                  # FDT 검증
│   └── layer1_verification.py               # Layer 1 통계역학 검증
└── docs/
    ├── FULL_CONCEPT_AND_STATUS.md    # ← 이 문서 (한국어)
    ├── FULL_CONCEPT_AND_STATUS_EN.md # Full concept (English)
    └── WORK_LOG.md                   # 시간순 작업 기록

(별도 레포)
PotentialFieldEngine/
└── potential_field_engine.py        # 물리 적분 엔진
                                       Strang splitting, symplectic Euler
                                       omega_coriolis, gamma, injection_func,
                                       noise_sigma, temperature, mass (FDT)
```

---

## 6. Phase C — 요동 (Fluctuation) [완료]

### 왜 필요한가

결정론적 시스템에서는 같은 초기 조건 → 항상 같은 결과. 감쇠가 있어도 경로는 하나.

현실 인지에서는 같은 자극에도 매번 다른 결과가 나올 수 있다.
감쇠로 우물에 갇힌 상태에서, **우연히** 장벽을 넘어 다른 기억으로 전이하는 것 — 이건 결정론으로 불가능하다.

### 수식

```
ẍ = -∇V(x) + ωJv - γv + I(x,v,t) + σξ(t)
```

- ξ(t): 백색 노이즈 (매 순간 랜덤 방향으로 밀어줌)
- σ: 노이즈 세기
- FDT (v2): σ² = 2γT/m — 온도 T를 설정하면 σ가 자동 결정
- 이것은 **Langevin 방정식** (확률 미분 방정식)

### 요동이 들어가면 뭐가 달라지나

| 현상 | 결정론 (이전) | 확률적 (현재) |
|---|---|---|
| 우물에 갇힘 | 영원히 갇힘 | 확률적으로 탈출 가능 (Kramers escape) |
| 공전 궤도 | 항상 같은 경로 | 매번 약간 다른 경로 |
| 같은 초기 조건 | 같은 결과 | 다른 결과 가능 |
| 기억 전환 | 감쇠/주입으로만 | 자발적 전환 가능 |

### 적분

Strang splitting의 감쇠 반스텝을 O-U exact 반스텝으로 확장:

```
O-S-K-R-K-S-O  (기존 D-S-K-R-K-S-D에서 D→O)

O(h):  dv = -γv dt + σ dW 의 정확해
       v → e^{-γh} · v + σ√((1-e^{-2γh})/(2γ)) · ξ
       γ→0 limit: v → v + σ√h · ξ
```

- O-U exact: 감쇠와 노이즈의 정확한 결합 (분리 적용이 아님)
- γ>0일 때 노이즈 분산 자동 보정: `(1-e^{-2γh})/(2γ)`
- σ=0이면 기존 D 스텝과 100% 동일 (하위 호환)
- 대칭 래핑: h=dt/2, 시작과 끝에 독립 O-U 반스텝

### 검증 결과

| # | 검증 | 결과 |
|---|------|------|
| 1 | 하위 호환 (σ=0 결정론) | PASS (시드 무관 동일 궤적, E drift 2.58e-06) |
| 2 | Kramers 탈출 (σ=0.25, γ=0.01) | PASS (탈출 10/10, 100%) |
| 3 | 통계적 비편향 (free particle) | PASS (bias ratio 0.066) |
| 4 | 감쇠+노이즈 정상 상태 | PASS (E bounded, std=0.25) |

### Phase C v2: FDT (요동-소산 정리)

**왜 필요한가:**
Phase C v1에서는 σ와 γ가 독립 파라미터였다. 임의 조합이 가능해 비물리적 상태를 만들 수 있었다.
FDT를 도입하면 σ가 γ, T, m에 종속되어, 열역학적으로 올바른 정상 분포가 보장된다.

**수식:**
```
σ² = 2γT/m    (kB = 1)
정상 분포: P(x,v) ∝ exp(-E/T)
등분배:    ⟨½mv²⟩ = T/2  (per DoF)
```

**모드 우선순위:**
- `noise_sigma > 0` → manual (직접 지정, FDT 무시)
- `temperature > 0` + `γ > 0` → fdt (σ 자동 계산)
- 그 외 → off (결정론적)

**변경 파일:**
- `potential_field_engine.py`: temperature, mass 파라미터, noise_sigma property (FDT 자동 계산), noise_mode property
- `cookiie_brain_engine.py`: temperature, mass config 전달 경로 추가

**검증 결과:**
```
python examples/fdt_verification.py → ALL PASS (5/5)
```
| # | 검증 | 결과 |
|---|------|------|
| 1 | 하위 호환 (temperature=None) | PASS — 기존 결정론적 동작 동일 |
| 2 | FDT σ 계산 | PASS — σ = √(2γT/m), 오차 0 |
| 3 | Manual override | PASS — noise_sigma 우선, temperature 무시 |
| 4 | Boltzmann 등분배 | PASS — ⟨|v|²⟩ = 2.01 (이론 2.00), 오차 0.6% |
| 5 | γ=0 안전장치 | PASS — temperature>0이어도 σ=0 |

### 다음: Layer 1 (통계역학 정식화)

Phase C가 완성되어 trunk(줄기)가 닫혔다.
이 위에 첫 번째 토양(Layer 1)을 쌓는다.

---

## 6-1. Layer 1 — 통계역학 정식화 [완료]

### 왜 필요한가

Phase C까지 완성하면 시뮬레이션에서 궤적이 나온다.
그 궤적을 **확률·열역학 언어로 번역**하려면 Layer 1이 필요하다.

- 우물 사이 전이는 얼마나 자주 일어나는가? → **Kramers 탈출률**
- 전이 패턴에 방향성이 있는가? → **전이 행렬, 순환 흐름**
- 시스템이 에너지를 얼마나 비가역적으로 소산하는가? → **엔트로피 생산률**

이것 없이는 Layer 2(다체), Layer 3(게이지), Layer 4(비평형 열역학)가
뿌리를 내릴 수 없다.

### 구성

#### ① Kramers 탈출률

```
k(i→j) = (λ₊ / ω_b) · (ω_a / 2π) · exp(−ΔV / T)

λ₊ = −γ/(2m) + √((γ/(2m))² + ω_b²)    (Kramers-Grote-Hynes)
```

- ω_a: 우물 바닥 고유 진동수 √(λ_max/m) (합성 퍼텐셜 수치 Hessian)
- ω_b: 안장점 불안정 진동수 (수치 Hessian)
- `kramers_rate_matrix(mwp, T, γ, m)` → 연속시간 Markov chain 생성 행렬

#### ② 전이 행렬 분석기 (TransitionAnalyzer)

기본 성질:
- `transition_matrix()`: P[i,j] = N(i→j) / Σ_k N(i→k) (확률 행렬, 행 합 = 1)
- `mean_residence_times()`: 우물별 평균 체류 시간
- `occupation_fractions()`: 시간 기준 우물 점유 비율

비평형 진단:
- `net_circulation()`: J[i,j] = N(i→j) − N(j→i) (순환 흐름)
- `detailed_balance_violation()`: Σ_{i<j}|J[i,j]| / (2·Σ_{i,j}N[i,j]) (0=평형, 1에 가까울수록 비평형)

#### ③ 엔트로피 생산률

```
Ṡ = (γ/T)(⟨|v|²⟩ − dT/m) − (1/T)⟨v·I⟩
```

극한 일관성:
- 평형 (I=0, FDT): ⟨|v|²⟩ = dT/m → **Ṡ = 0** (열역학 제2법칙 정합)
- 비평형 (I≠0): Ṡ > 0

### 검증 결과

```
python examples/layer1_verification.py → ALL PASS (5/5)
```

| # | 검증 | 결과 |
|---|------|------|
| 1 | Kramers rate 공식 정합성 | PASS |
| 2 | Kramers rate vs 시뮬레이션 전이 | PASS |
| 3 | 전이 행렬 성질 + 상세 균형 | PASS |
| 4 | 엔트로피 생산률: 평형 Ṡ ≈ 0 (극한 일관성) | PASS |
| 5 | Arrhenius 법칙 | PASS |

### 확장 방향

Layer 1은 나머지 모든 Layer의 토양이다:

```
Layer 1 (Kramers, P[i,j], dS/dt)
  ├→ Layer 2: N-입자, 상호작용, 연속 장  ← 완료
  ├→ Layer 3: 위치 의존 J(x), 비가환 게이지  ← 완료
  ├→ Layer 4: Jarzynski, Crooks, Landauer  ← 완료
  ├→ Layer 5: Nelson 확률역학, Fokker-Planck  ← 완료
  └→ Layer 6: Fisher 정보 기하학  ← 완료
```

---

## 6-2. Layer 2 — 다체/장론 [완료]

### 왜 필요한가

단일 입자에서 "통일장"은 없다. 장(field)은 입자가 여러 개일 때 비로소 의미를 갖는다.
Layer 2는 N 입자 간의 상호작용을 도입하여, 집단 동역학(collective dynamics)의 토양을 만든다.

### 핵심 설계

trunk은 state_vector의 내부 구조를 모른다.
`[x₁...xₙ, v₁...vₙ]`를 그냥 큰 (x, v) 벡터로 적분한다.
Layer 2 ForceLayer가 내부에서 (N, d) reshape를 처리한다.

### 구성 요소

| 클래스 | 역할 |
|--------|------|
| `NBodyState` | flat ↔ (N,d) reshape 유틸리티 |
| `InteractionForce` | 쌍체 상호작용 Σ_{i<j} φ(r_ij) |
| `ExternalForce` | 입자별 외부 퍼텐셜 Σᵢ V(xᵢ) |
| `NBodyGauge` | 입자별 코리올리 회전 |

편의 함수: `gravitational_interaction()`, `spring_interaction()`, `coulomb_interaction()`

### 수식

```
m ẍᵢ = -∇ᵢ V(xᵢ) + Σ_{j≠i} F_ij(xᵢ, xⱼ) + G(vᵢ, dt) - γvᵢ + σξᵢ(t)
```

Newton 제3법칙: `F_ij = -F_ji` (구조적 보장) → 총 운동량 보존

### 극한 일관성

| 극한 | 기대 | 보장 타입 | 검증 |
|------|------|----------|------|
| N=1 | 단일 입자와 동일 | 구조적 | 차이 0.0 |
| F_ij = -F_ji | 운동량 보존 | 구조적 | 변화 3.2e-14 |
| 중심력 | 각운동량 보존 | 구조적 | 변화 5.3e-15 |
| γ=0, σ=0 | 에너지 보존 | 적분기 의존 | drift < 0.23% |
| FDT + N입자 | 등분배 | 적분기 의존 | 오차 2.0% |

> N→∞ 극한은 밀도 고정, 상호작용 스케일링(1/N), coarse-graining 등 추가 정의가 필요하며, 현재 범위 밖이다.

### 검증

```
python examples/layer2_verification.py → ALL PASS (5/5)
```

| # | 검증 | 결과 |
|---|------|------|
| 1 | Newton 제3법칙 — 운동량 보존 | PASS |
| 2 | 에너지 보존 — 보존계 | PASS |
| 3 | N=1 극한 — 단일 입자와 동일 | PASS |
| 4 | 등분배 정리 — 열평형 | PASS |
| 5 | 2체 순환 — 각운동량 보존 | PASS |

---

## 6-3. Layer 3 — 게이지/기하학 [완료]

### 목적

trunk의 전역 Coriolis 회전(ω = const)을 **위치 의존 자기장 B(x)** 로 확장한다.
"공간의 각 위치마다 회전이 다르다" — 이것이 게이지 기하학의 핵심이다.

### 수식

2D 자기장형 힘:
```
F = B(x) · J · v = B(x) · (-v_y, v_x)

에너지 보존: F · v = B(x)·(-v_y·v_x + v_x·v_y) = 0  (구조적)
```

E×B drift (일정 기울기 + 균일 B):
```
v_drift = (∂V/∂y, −∂V/∂x) / B
```

자기 선속 기반 위상 축적 (Abelian, Stokes 정리):
```
Φ = ∫∫ B dA   (= ∮A·dl, 단 A(x) 미정의 — 면적분으로 계산)
```

### 구성 요소

| 클래스 | 역할 |
|--------|------|
| `MagneticForce` | 단일 입자 위치 의존 자기장형 힘 |
| `NBodyMagneticForce` | N 입자 각각에 B(x) 적용 |
| `GeometryAnalyzer` | 선속 기반 위상 축적(Abelian), 곡률, drift 계산 |

편의 함수:
| 함수 | B(x) | 용도 |
|------|------|------|
| `uniform_field(B₀)` | B₀ | 균일 자기장 |
| `gaussian_field(B₀, c, σ)` | B₀·exp(−\|x−c\|²/2σ²) | 국소 집중 |
| `dipole_field(μ, c, ε)` | μ/(\|x−c\|²+ε²) | 쌍극자형 |
| `multi_well_field(…)` | Σ Bᵢ·gauss | 다중 우물별 |

### 극한 일관성

| 극한 | 기대 | 보장 타입 |
|------|------|----------|
| B(x) = ω (const) | CoriolisGauge와 동일 | 구조적 |
| B(x) = 0 | 자유 입자 (힘 없음) | 구조적 |
| F·v = 0 | 에너지 보존 | 구조적 (J^T = −J) |
| N=1 | 단일 입자와 동일 | 구조적 |
| 사이클로트론 | ω_c = B/m, 원 궤도 | 적분기 의존 |
| E×B drift | v = (∂V/∂y, −∂V/∂x)/B | 적분기 의존 |
| 선속 기반 위상 축적 | Φ = ∫∫B dA (Abelian) | 수치 적분 정밀도 |

> **적분기 주의**: MagneticForce는 속도 의존 힘이므로, Strang splitting에서 에너지 error가 bounded O(dt²). Euler fallback에서는 drift 심각. `CoriolisGauge(0.0)` 또는 실제 gauge를 사용하여 Strang 활성화 권장.

### 검증

```
python examples/layer3_verification.py → ALL PASS (5/5)
```

| # | 검증 | 결과 |
|---|------|------|
| 1 | 에너지 보존 (가우시안 B, Strang) | PASS — drift < 5% |
| 2 | 사이클로트론 (균일 B) | PASS — r_c 오차 < 2% |
| 3 | B=0 극한 | PASS — 궤적 차이 = 0 |
| 4 | E×B drift (collisionless) | PASS — v_drift 오차 < 0.1% |
| 5 | 선속 기반 위상 축적 (가우시안 B, Abelian) | PASS — 면적분 오차 < 2% |

---

## 6-4. Layer 4 — 비평형 일 정리 [완료]

Layer 1(평형/근평형 열역학)을 **임의의 비평형 과정**으로 확장한다.

### 핵심 정리

- **Jarzynski**: `⟨e^{-W/T}⟩ = e^{-ΔF/T}` — 정확한 등식
- **제2법칙**: `⟨W⟩ ≥ ΔF` — Jensen 부등식
- **Crooks**: `P_F(W)/P_R(−W) = e^{(W−ΔF)/T}`

### 일(Work)의 정의

프로토콜 λ(t)가 퍼텐셜 V(x, λ)를 변화시킬 때:

```
W = Σ_n [V(x_n, λ_{n+1}) − V(x_n, λ_n)]
```

### 구성 요소

| 클래스 | 역할 |
|--------|------|
| `Protocol` | 시간 의존 퍼텐셜 V(x, λ(t)) |
| `ProtocolForce` | ForceLayer 프로토콜 준수 |
| `WorkAccumulator` | 궤적 따라 일 W 축적 |
| `JarzynskiEstimator` | ΔF 추출, 제2법칙 검증 |
| `CrooksAnalyzer` | 정방향/역방향 대칭 분석 |

### 극한 일관성

| 극한 | 결과 | 보장 타입 |
|------|------|-----------|
| τ→∞ (준정적) | ⟨W⟩ → ΔF | 구조적 |
| ΔF=0 (이동 트랩) | ⟨e^{-W/T}⟩ → 1 | 구조적 |
| 정방향/역방향 대칭 | ΔF_f = −ΔF_r | 구조적 (Crooks) |
| 수렴 속도 | rare event 의존 | 통계적 (표본 수) |

### Layer 1과의 관계

```
Layer 1: 평형  → Kramers 탈출률, 전이행렬, 엔트로피 생산률
Layer 4: 비평형 → Jarzynski 등식, Crooks 정리, ΔF 추출
```

Layer 1이 평형 근처에서 유효한 근사를 제공했다면,
Layer 4는 평형에서 임의로 먼 과정에서도 정확한 등식을 제공한다.

### 검증 결과 (layer4_verification.py)

| # | 테스트 | 결과 |
|---|------|------|
| 1 | Jarzynski 등식 (이동 트랩, ΔF=0) | PASS — ⟨e^{-W/T}⟩ = 1.008 |
| 2 | 제2법칙 (⟨W⟩ ≥ ΔF) | PASS — ⟨W_diss⟩ = 4.76 ≥ 0 |
| 3 | Jarzynski (강성 변화, 알려진 ΔF) | PASS — 오차 0.03% |
| 4 | 준정적 극한 (τ↑ → ⟨W⟩↓) | PASS — 단조 감소 |
| 5 | Crooks 대칭 (ΔF_f ≈ −ΔF_r) | PASS — |차이| = 0.016 |

---

## 6-5. Layer 5 — 확률역학 [완료]

Layer 1–4의 궤적(trajectory) 관점을 확률 밀도 ρ(x,t) 진화 관점으로 전환한다.

### 핵심 방정식

- **Fokker-Planck**: `∂ρ/∂t = ∂/∂x [V'ρ/(mγ)] + D∂²ρ/∂x²`, D = T/(mγ)
- **정상 분포**: ρ_eq ∝ exp(−V/T) (볼츠만)
- **확률류**: J = bρ − D∇ρ, 평형에서 J = 0

### Nelson 속도 분해

```
v_current = −V'/(mγ)     (표류, 외력)
v_osmotic = D·∇ln ρ      (삼투, 확산 유도)
v_+ = v_c + v_o           (forward, 평형에서 0)
v_- = v_c − v_o           (backward)
```

### 구성 요소

| 클래스 | 역할 |
|--------|------|
| `FokkerPlanckSolver1D` | 1D 격자 위 ρ(x,t) 시간 진화 |
| `NelsonDecomposition` | v = v_current + v_osmotic |
| `ProbabilityCurrent` | J = bρ − D∇ρ 분석 |

### 검증 결과

| # | 테스트 | 결과 |
|---|------|------|
| 1 | 정상 분포 = 볼츠만 | PASS — L1 = 0.023 |
| 2 | 확률 보존 ∫ρ=1 | PASS — 편차 2.2e-16 |
| 3 | 평형 확률류 J=0 | PASS — J_max = 2.9e-04 |
| 4 | Nelson 삼투 속도 | PASS — 오차 = 0.000000 |
| 5 | Langevin ↔ FP 일치 | PASS — L1 = 0.023 |

---

### 6-6. Layer 6 — 정보 기하학 [완료]

**목적**: 매개변수 공간의 기하학적 구조를 Fisher 정보 계량으로 분석한다.

**Layer 3과의 관계**:
- Layer 3: 물리 공간의 게이지 — Ω(x)v, B-field
- Layer 6: 매개변수 공간의 기하 — g_μν, K (Fisher 계량)

**왜 naive Berry phase = 0인가 (1D 고전)**:

```
A_μ = ∂⟨x⟩/∂λ_μ  →  A = ∇_λ f  (gradient of scalar)
F = curl(∇f) = 0              (항상, Schwarz 정리)
```

1D overdamped 고전계에서 스칼라 기대값의 Berry connection은 trivial.
이것은 수학적 사실이지 구현 오류가 아니다.

**Fisher 계량은 비자명**:

```
g_μν(λ) = (1/T²) · Cov_λ(∂_μV, ∂_νV)
```

- 양정치 (positive definite)
- 가우스 곡률 K ≠ 0 (비평탄 매개변수 공간)
- 양자 Fubini-Study 계량의 고전 극한

| 구성 요소 | 역할 |
|-----------|------|
| `FisherMetricCalculator` | Fisher 계량, 곡률, 측지선 거리 |
| `ParameterSpace` | 2D 매개변수 격자 |

### 검증 결과

| # | 테스트 | 결과 |
|---|------|------|
| 1 | Fisher 계량 양정치 | PASS — 5점 모두 pd=True |
| 2 | 해석적 대조 (가우시안) | PASS — 오차 < 1e-12 |
| 3 | 가우스 곡률 비자명 K≠0 | PASS — |K|_max = 0.24 |
| 4 | Fisher ≠ 유클리드 (비자명) | PASS — 비율 ≠ 1 |
| 5 | 대칭점 g₁₂ = 0 | PASS — |g₁₂| < 1e-6 |

---

## 7. 설계 원칙

| 원칙 | 설명 |
|---|---|
| 하드코딩 금지 | 물리 상수, 경로, 스케일 전부 CONFIG/파라미터 |
| state 불변 | `state.copy()` 후 새 객체 반환. 원본 안 건드림 |
| 하위 호환 | 새 기능 추가 시 기존 동작이 깨지지 않아야 함 (γ=0 → 보존계) |
| 검증 필수 | 모든 물리 변경에 대해 수치 검증 스크립트 작성 |
| 구조 먼저, 확률 나중 | "고전 구조 확장 → 그 위에 확률적 층 추가" |
| 엔진은 상태를 perturb할 뿐 | 정답을 주는 시스템이 아닌, 구조를 제공하는 시스템 |

---

## 8. 핵심 용어 정리

| 용어 | 정의 |
|---|---|
| 퍼텐셜 V(x) | 위치 x에서의 에너지 지형. 낮을수록 안정 |
| gradient g(x) | -∇V(x). 퍼텐셜이 내려가는 방향. 공을 끌어당기는 힘 |
| 우물 (well) | 퍼텐셜의 지역 최솟값. 기억 하나에 대응 |
| 안장점 (saddle) | 두 우물 사이 장벽의 꼭대기. 이걸 넘어야 전이 가능 |
| 자전 (spin) | 우물 안에서 공이 회전하는 것. ωJv로 구현 |
| 공전 (orbit) | 우물 사이를 순환하는 것. 다중 우물 + ωJv |
| 감쇠 (dissipation) | -γv. 에너지를 빼앗아 공을 느리게 함 |
| 주입 (injection) | I(x,v,t). 외부에서 에너지를 넣어줌 |
| 요동 (fluctuation) | σξ(t). 확률적 노이즈. 비결정론적 전이의 원인 |
| Strang splitting | 적분 방법. 각 물리 연산자를 대칭적으로 분할 적용 |
| WellRegistry | 우물 누적 저장소. WellFormation 결과를 Gaussian으로 변환·축적 |

---

*GNJz (Qquarts) · CookiieBrain*
*"정답을 제시하기보다, 각자의 해답을 찾아갈 수 있는 방향 제시가 더 큰 목적이다."*
