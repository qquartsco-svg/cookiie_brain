# Layer 4 — 비평형 일 정리 (Non-equilibrium Work Theorems)

> **임의의 비평형 과정에서 자유 에너지를 추출한다** — Layer 1의 평형 열역학을 정확한 비평형 등식으로 확장.

---

## Layer 1 → Layer 4: 무엇이 달라지는가

| | Layer 1 (통계역학) | **Layer 4 (비평형 일 정리)** |
|---|---|---|
| 영역 | 평형/근평형 | **임의의 비평형** |
| 핵심 도구 | Kramers 탈출률, 전이행렬 | **Jarzynski 등식, Crooks 정리** |
| 자유 에너지 | 평형 분포에서 직접 계산 | **비평형 일(W) 측정으로 추출** |
| 제2법칙 | 엔트로피 생산률 Ṡ ≥ 0 | **⟨W⟩ ≥ ΔF** |
| 정확도 | 근사 (Kramers, 선형 응답) | **정확한 등식** (근사 아님) |

---

## 핵심 정리

### Jarzynski 등식

```
⟨e^{-W/T}⟩ = e^{-ΔF/T}
```

- **정확한 등식**이다 (근사가 아님)
- **초기 평형 분포에서 시작한** 임의의 프로토콜 구동 과정에서 성립한다
- ΔF: 초기/최종 평형 상태의 자유 에너지 차이
- W: 프로토콜이 시스템에 한 일

### 제2법칙 (따름정리)

```
⟨W⟩ ≥ ΔF       (Jensen 부등식: ⟨e^X⟩ ≥ e^{⟨X⟩})
⟨W_diss⟩ = ⟨W⟩ − ΔF ≥ 0
```

### Crooks 요동 정리

```
P_F(W) / P_R(−W) = e^{(W − ΔF)/T}
```

정방향(λ: a→b)의 일 분포와 역방향(λ: b→a)의 일 분포가 위 관계를 만족한다.
Jarzynski 등식은 Crooks의 따름정리이다.

---

## 일(Work)의 정의 — inclusive work

시간 의존 프로토콜 λ(t)가 퍼텐셜 V(x, λ)를 변화시킬 때:

```
W = Σ_n [V(x_n, λ_{n+1}) − V(x_n, λ_n)]
```

고정된 배치(x_n)에서 λ 변화에 의한 퍼텐셜 차이.
이것이 열역학적 '일'이다 — 시스템에 주입된 에너지.

### inclusive work vs 경로 확률

| 방식 | 정의 | 적용 범위 |
|------|------|-----------|
| **inclusive work** (현재) | W = Σ[V(x_n,λ_{n+1})−V(x_n,λ_n)] | 프로토콜 구동 과정 |
| 경로 확률 (미구현) | ΔS = ln P[path] / P[reverse path] | NESS + 프로토콜 모두 |

현재 구현은 **inclusive work** 방식이다:
- 외부 프로토콜 λ(t)에 의한 구동만 다룬다
- 프로토콜이 없는 비평형 정상 상태(NESS)는 범위 밖
- 프로토콜 구동 과정에서는 **정확**하다

경로 확률 방식(path action ratio)은 더 일반적이지만,
벡터 퍼텐셜 A(x) 또는 경로 적분의 이산화가 필요하다.
향후 확장으로 분류한다.

---

## 구성 요소

### Protocol

시간 의존 퍼텐셜 V(x, λ(t)) 정의.

```python
from Layer_4 import Protocol

protocol = Protocol(
    V_func=lambda x, lam: 0.5 * lam * np.dot(x, x),
    g_func=lambda x, lam: -lam * x,
    lambda_schedule=lambda t: 1.0 + t / 10.0,
)
```

### ProtocolForce

ForceLayer 프로토콜 준수 — trunk에 직접 연결.

```python
from Layer_4 import ProtocolForce

pf = ProtocolForce(protocol)
engine = PotentialFieldEngine(force_layers=[pf], ...)
```

### WorkAccumulator

궤적을 따라 일 W를 축적.

```python
from Layer_4 import WorkAccumulator

wa = WorkAccumulator(protocol, dt)
for n in range(n_steps):
    wa.step(state.state_vector[:dim])
    state = engine.update(state)
print(f"W = {wa.W}")
```

### JarzynskiEstimator

| 메서드 | 설명 | 수식 |
|--------|------|------|
| `free_energy(works, T)` | 자유 에너지 추출 | ΔF = −T·ln⟨e^{-W/T}⟩ |
| `jarzynski_average(works, T)` | Jarzynski 평균 | ⟨e^{-W/T}⟩ |
| `dissipated_work(works, ΔF)` | 소산된 일 | ⟨W⟩ − ΔF |
| `second_law_satisfied(works, ΔF)` | 제2법칙 검증 | ⟨W⟩ ≥ ΔF ? |

수치 안정성: log-sum-exp 트릭 사용.

### CrooksAnalyzer

정방향/역방향 프로토콜의 대칭 검증.

현재 구현: **양방향 Jarzynski** 수준 — `ΔF_f ≈ −ΔF_r` 검증.
이것은 Crooks 정리의 따름정리이다.
완전한 Crooks 검증(히스토그램 `P_F(W)/P_R(−W) = e^{(W−ΔF)/T}`)은 향후 확장.

### EntropyBridge

Layer 1 (엔트로피 생산률)과 Layer 4 (비평형 일)의 연결.

| 메서드 | 설명 | 수식 |
|--------|------|------|
| `total_entropy_production(works, ΔF, T)` | 총 엔트로피 생산 | ΔS_tot = (⟨W⟩−ΔF)/T |
| `entropy_per_trajectory(works, ΔF, T)` | 궤적별 엔트로피 | ΔS_i = (W_i−ΔF)/T |

### 편의 함수

| 함수 | 프로토콜 | ΔF |
|------|----------|-----|
| `moving_trap(k, L, τ)` | V = ½k\|x−λê₁\|² | 0 |
| `stiffness_change(k₁, k₂, τ)` | V = ½λ\|x\|² | (d/2)·T·ln(k₂/k₁) |
| `equilibrium_sample(k, T, m, d)` | 초기 평형 샘플 | — |

---

## Layer 1 의존성 (필수 조건)

Layer 4가 성립하려면 3가지가 반드시 유지되어야 한다:

### 1. FDT: σ² = 2γT/m

```
LangevinThermo(gamma=γ, temperature=T, mass=m)
→ sigma = sqrt(2γT/m)  (자동 계산, check_fdt()로 검증)
```

이 조건이 깨지면 Jarzynski/Crooks 등식이 **성립하지 않는다**.
trunk의 `TrunkChecker.check_fdt(thermo_layer)`로 확인 가능
(구현 위치: PotentialFieldEngine의 `layers.py`).

### 2. 평형 초기 조건

Jarzynski 등식은 **초기 평형 분포**에서 출발해야 한다:
- x ~ exp(−V(x,λ₀)/T) — 볼츠만 분포
- v ~ exp(−½m|v|²/T) — Maxwell 분포
- `equilibrium_sample(k, T, m, d)` 이 이를 보장

### 3. 시간 이산화와 Onsager 대칭

trunk의 O-U exact step (`ou_step`)은 **선형 과정에서 FDT를 정확히 보존**한다:
```
decay = exp(−γh)
amp = σ · sqrt((1 − exp(−2γh)) / (2γ))
```
이것은 연속 Langevin의 정확한 이산화이므로 Onsager 대칭을 깨지 않는다.
dt가 커도 FDT 자체는 보존된다 (힘 적분의 정확도만 dt에 의존).

---

## 극한 일관성

| 극한 | 결과 | 보장 타입 | 설명 |
|------|------|-----------|------|
| τ→∞ | ⟨W⟩ → ΔF | 구조적 | 가역 과정, W_diss → 0 |
| ΔF=0 | ⟨e^{-W/T}⟩ → 1 | 구조적 | 같은 모양 퍼텐셜 이동 |
| γ→0, σ→0 | W 결정론적 | 구조적 | Jarzynski 성립하나 통계적 의미 소실 |
| dt→0 | 이산화 오차 → 0 | 수치적 | O-U exact step은 FDT 보존 |
| N_traj→∞ | Jarzynski 수렴 | 통계적 | rare event sampling 필요 |
| 정방향/역방향 | ΔF_f ≈ −ΔF_r | 구조적 (Crooks) | 양방향 Jarzynski |

### γ→0 극한의 의미

```
γ=0, σ=0 → 해밀토니안계 → W는 궤적마다 동일
⟨e^{-W/T}⟩ = e^{-W/T}  (단일 값, 통계 불필요)
```

Jarzynski 등식은 여전히 **수학적으로 성립**하지만,
fluctuation theorem의 핵심인 "요동으로부터 정보 추출"이 불가능해진다.
비평형 열역학은 **γ > 0인 dissipative 시스템**에서만 물리적으로 의미 있다.

---

## 수렴 주의사항

Jarzynski 지수 평균 `⟨e^{-W/T}⟩`은 **rare event에 민감**하다.

- 빠른 프로토콜 → 일 분포가 넓음 → 수렴 느림
- 느린 프로토콜 → 일 분포가 좁음 → 수렴 빠름
- 궤적 수가 충분해야 rare low-W 이벤트를 포착
- dt가 크면 Jarzynski 지수 평균이 발산할 수 있음

이것은 Jarzynski 등식의 알려진 수치적 한계이며, 물리적 문제가 아니다.

**실무 권장**: dt ≤ 0.01, N_traj ≥ 200, 느린 프로토콜(τ ≫ m/γ)에서 시작.

---

## 검증 결과 (layer4_verification.py)

| 테스트 | 결과 | 핵심 수치 |
|--------|------|-----------|
| Jarzynski (이동 트랩, ΔF=0) | PASS | ⟨e^{-W/T}⟩ = 1.008 |
| 제2법칙 (⟨W⟩ ≥ ΔF) | PASS | ⟨W_diss⟩ = 4.76 ≥ 0 |
| Jarzynski (강성 변화) | PASS | ΔF 오차 0.03% |
| 준정적 극한 | PASS | τ↑ → ⟨W⟩↓ (단조 감소) |
| Crooks 대칭 | PASS | \|ΔF_f + ΔF_r\| = 0.016 |

---

## Layer 1 ↔ Layer 4: 엔트로피 생산 연결

```
Layer 1: Ṡ = (γ/T)(⟨|v|²⟩ − dT/m)     (순간, 미시적)
Layer 4: ΔS_tot = (⟨W⟩ − ΔF) / T       (적분, 거시적)
```

| | Layer 1 | Layer 4 |
|---|---------|---------|
| 관점 | 순간 엔트로피 생산률 | 프로토콜 총 엔트로피 |
| 정의 | Ṡ = (γ/T)(⟨\|v\|²⟩ − dT/m) | ΔS = W_diss/T |
| 평형 | Ṡ = 0 | ΔS = 0 (준정적) |
| 비평형 | Ṡ > 0 | ΔS > 0 (제2법칙) |
| 관계 | ∫Ṡ dt ≈ ΔS_tot (프로토콜 구동이 유일한 비평형 원인일 때) |

---

## 인지적 해석

| 물리 | 인지 해석 |
|------|----------|
| 프로토콜 λ(t) | 외부 환경 변화 (학습 과정, 자극 변화) |
| 일 W | 환경 변화에 적응하기 위해 소비된 인지 자원 |
| ΔF (자유 에너지) | 새로운 상태에 도달하기 위한 최소 비용 |
| ⟨W⟩ − ΔF (소산) | 비효율적 적응으로 낭비된 자원 |
| 준정적 극한 | 천천히 배우면 최소 비용으로 적응 가능 |

---

## 향후 확장 방향

1. **Crooks 히스토그램 분석**: P_F(W)와 P_R(−W)의 교차점에서 ΔF 추출 (현재는 양방향 Jarzynski 수준)
2. **경로 확률 기반 엔트로피**: ΔS = ln P[path]/P[reverse] — NESS 분석 가능
3. **최적 프로토콜**: 주어진 시간 내 소산 최소화하는 λ(t) 탐색
4. **Landauer 원리**: 정보 삭제의 최소 비용 kT·ln2 검증
5. **비평형 자유 에너지 지형**: 다중 우물 전이의 ΔF 프로파일
6. **rare event sampling**: importance sampling 또는 weighted ensemble
