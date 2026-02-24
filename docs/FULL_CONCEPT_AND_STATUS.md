# CookiieBrain — 전체 개념과 현재 상태

> 이 문서는 프로젝트의 물리적 개념, 구현 상태, 검증 결과, 다음 방향을
> 하나로 정리한 것이다. 새로 합류하는 사람이 이 문서 하나로 전체를 파악할 수 있어야 한다.

**마지막 업데이트: 2026-02-24**

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
| 요동 (ξ) | 예측 불가능한 변동, 창의적 전환 (미구현) |

### 전체 운동 방정식 (현재)

```
ẍ = -∇V(x) + ωJv - γv + I(x,v,t) + σξ(t)
```

| 항 | 이름 | 역할 | 에너지 영향 |
|---|---|---|---|
| `-∇V(x)` | 퍼텐셜 gradient | 골짜기로 끌어당김 (보존력) | 보존 |
| `ωJv` | 코리올리 회전 | 속도 방향만 꺾음 (자전/공전 방향) | 보존 (v·Jv=0) |
| `-γv` | 감쇠 | 속도에 비례해 에너지를 빼앗음 | **소산** |
| `I(x,v,t)` | 외부 주입 | 외부에서 에너지를 넣어줌 | **주입** |
| `σξ(t)` | 확률적 요동 | 매 순간 랜덤 방향으로 밀어줌 | **확률적** |

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
    ├── potential_field: V, E, g, time, gamma, noise_sigma, dissipation_power, injection_power
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
| 요동 (Phase C) | ✔ | +σξ(t) | ALL PASS (4항목) |

---

## 5. 파일 구조 (현재)

```
CookiieBrain/
├── cookiie_brain_engine.py          # 통합 엔진 (오케스트레이션)
│                                      WellFormation → Registry → PFE 자동 연결
│                                      gamma, injection_func config 전달
├── README.md                        # 프로젝트 소개
├── Phase_A/
│   ├── __init__.py                  # 모듈 export
│   ├── rotational_field.py          # 코리올리형 ωJv + pole형 ωJ(x-x_pole)
│   ├── moon.py                      # 위성 중력장
│   ├── verify_math.py               # 수학 검증
│   ├── README.md                    # Phase A 개념 문서
│   ├── STAGES_SPIN_ORBIT_FLUCTUATION.md  # 단계 정리 (자전→공전→요동)
│   └── docs/                        # 상세 작업 기록
├── Phase_B/
│   ├── __init__.py                  # 모듈 export
│   ├── multi_well_potential.py      # Gaussian 다중 우물 퍼텐셜
│   │                                  V, field, saddle, barrier, landscape_info
│   ├── well_to_gaussian.py          # WellFormation → Gaussian 브릿지
│   │                                  WellToGaussianConfig, WellRegistry
│   └── README.md                    # Phase B 개념 + 공전 조건 + 브릿지
├── examples/
│   ├── phase_a_minimal_verification.py       # 자전 검증
│   ├── phase_b_orbit_verification.py         # 공전 검증 (3-우물)
│   ├── bridge_verification.py                # 브릿지 검증
│   ├── dissipation_injection_verification.py # 에너지 주입/소산 검증
│   └── fluctuation_verification.py           # 요동 검증
└── docs/
    ├── FULL_CONCEPT_AND_STATUS.md   # ← 이 문서
    └── WORK_LOG.md                  # 시간순 작업 기록

(별도 레포)
PotentialFieldEngine/
└── potential_field_engine.py        # 물리 적분 엔진
                                       Strang splitting, symplectic Euler
                                       omega_coriolis, gamma, injection_func,
                                       noise_sigma (Langevin)
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
- σ: 노이즈 세기 (온도와 비슷한 역할)
- 이것은 **Langevin 방정식** (확률 미분 방정식)

### 요동이 들어가면 뭐가 달라지나

| 현상 | 결정론 (이전) | 확률적 (현재) |
|---|---|---|
| 우물에 갇힘 | 영원히 갇힘 | 확률적으로 탈출 가능 (Kramers escape) |
| 공전 궤도 | 항상 같은 경로 | 매번 약간 다른 경로 |
| 같은 초기 조건 | 같은 결과 | 다른 결과 가능 |
| 기억 전환 | 감쇠/주입으로만 | 자발적 전환 가능 |

### 적분

Strang splitting의 감쇠 반스텝을 O-U (Ornstein-Uhlenbeck) 반스텝으로 확장:

```
O-S-K-R-K-S-O  (기존 D-S-K-R-K-S-D에서 D→O)

O(dt/2):  v *= exp(-γ·dt/2)        ← 감쇠 (기존과 동일)
          v += σ·√(dt/2)·N(0,1)    ← 노이즈 (Wiener increment)
```

- σ=0이면 기존 D 스텝과 100% 동일 (하위 호환)
- √dt 스케일링 = Euler-Maruyama 이산화
- 대칭 래핑: 시작과 끝에 각각 독립 노이즈 → 총 분산 σ²dt (표준 Wiener)

### 검증 결과

| # | 검증 | 결과 |
|---|------|------|
| 1 | 하위 호환 (σ=0 결정론) | PASS (시드 무관 동일 궤적, E drift 2.58e-06) |
| 2 | Kramers 탈출 (σ=0.25, γ=0.01) | PASS (탈출 10/10, 100%) |
| 3 | 통계적 비편향 (free particle) | PASS (bias ratio 0.066) |
| 4 | 감쇠+노이즈 정상 상태 | PASS (E bounded, std=0.25) |

### 다음: 은하 구조 실험

요동이 완성되어, "바깥 우물 → 확률적 전이 → 안쪽 우물 → 중앙 수렴" 같은
**나선형 탐사 구조**가 가능해졌다.

이것이 "은하 모양 지형 위를 공이 여행하는 시스템"의 물리적 기반이다.
새 물리가 필요한 것이 아니라, 우물 배치 설정만 바꾸면 된다.

실험 방향:
1. 은하 배치 — 우물을 동심원/나선 형태로 배치
2. 감쇠(γ) + 약한 중앙 바이어스 → 바깥→안쪽 수렴
3. 노이즈(σ) → 확률적 전이로 다양한 경로 탐사

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
