# Layer 5 — 확률역학 (Stochastic Mechanics)

> **궤적에서 밀도로** — Layer 1–4의 Langevin 궤적 관점을 확률 밀도 ρ(x,t) 진화 관점으로 전환한다.

---

## 관점 전환: Langevin ↔ Fokker-Planck

```
Langevin (궤적):       γ dx = −∇V dt + σ dW
Fokker-Planck (밀도):   ∂ρ/∂t = ∇·(∇V·ρ/(mγ)) + D∇²ρ
```

| | Langevin (Layer 1–4) | **Fokker-Planck (Layer 5)** |
|---|---|---|
| 대상 | 단일 궤적 x(t) | 확률 밀도 ρ(x,t) |
| 방정식 | SDE (확률 미분방정식) | PDE (편미분방정식) |
| 정보 | 한 번의 실현 | 모든 실현의 통계 |
| 평형 | 궤적의 시간 평균 | ρ_eq ∝ exp(−V/T) |

두 관점은 **수학적으로 동치**이다. 밀도 관점에서만 보이는 것이 있다:
- 확률류 J(x,t)의 공간 패턴
- 삼투 속도 v_osmotic (Nelson 확률역학)
- 비평형 정상 상태(NESS)의 순환 구조

---

## 핵심 방정식

### Fokker-Planck (overdamped 한정)

```
∂ρ/∂t = ∂/∂x [V'(x)·ρ/(mγ)] + D·∂²ρ/∂x²
       = −∂J/∂x
```

- **D = T/(mγ)**: 확산 계수 — FDT로부터 유도
- **J = b·ρ − D·∇ρ**: 확률류
- **b = −V'/(mγ)**: overdamped drift

**현재 구현은 overdamped (위치 공간) FP에 한정된다.**
underdamped Kramers FP (위상 공간):

```
∂ρ/∂t = −v·∂ₓρ + ∂ᵥ(γvρ + V'ρ/m) + (γT/m)·∂²ᵥρ
```

는 향후 확장 사항이다.

### 정상 분포

```
ρ_eq ∝ exp(−V/T)    (볼츠만)
J_eq = 0             (detailed balance)
```

### Nelson 속도 분해

```
v_+ = b + D·∇ln ρ    (forward drift)
v_- = b − D·∇ln ρ    (backward drift)
v_current = b          (표류 속도)
v_osmotic = D·∇ln ρ    (삼투 속도)
```

| 속도 | 의미 | 평형에서 |
|------|------|---------|
| v_current | 외력에 의한 체계적 이동 | −V'/(mγ) |
| v_osmotic | 밀도 기울기에 의한 확산 유도 속도 | D·∇ln ρ_eq = −V'/(mγ) |
| v_+ | forward = current + osmotic | 0 (상쇄!) |
| v_- | backward = current − osmotic | −2V'/(mγ) |

**평형에서 v_+ = 0**: forward drift가 사라진다. 이것이 detailed balance의 속도 수준 표현이다.

---

## 구성 요소

### FokkerPlanckSolver1D

1D 격자 위에서 ρ(x,t)를 시간 진화시킨다.

```python
from analysis.Layer_5 import FokkerPlanckSolver1D

fp = FokkerPlanckSolver1D(
    x_min=-4, x_max=4, nx=201,
    V_func=lambda x: 0.5 * 2.0 * x**2,
    T=1.0, gamma=2.0,
)

rho0 = gaussian_initial(fp.x, center=2.0, sigma=0.5)
rho_final = fp.evolve(rho0, dt=0.0005, n_steps=40000)
```

### NelsonDecomposition

확산 과정의 drift를 current + osmotic으로 분해.

| 메서드 | 수식 |
|--------|------|
| `current_velocity(x, dVdx, m, γ)` | v_c = −V'/(mγ) |
| `osmotic_velocity(ρ, dx, D)` | v_o = D·∇ln ρ |
| `forward_velocity(v_c, v_o)` | v_+ = v_c + v_o |
| `backward_velocity(v_c, v_o)` | v_- = v_c − v_o |

수치 안정성: `∇(ln ρ)` 직접 계산 (`∇ρ/ρ` 대신).

### ProbabilityCurrent

확률류 J = bρ − D∇ρ 분석.

---

## Layer 1 의존성

```
D = T/(mγ) = σ²/(2γ)    ← FDT: σ² = 2γT/m
```

Layer 5의 모든 확산 계수 D는 Layer 1의 FDT에서 유도된다.
FDT가 깨지면 Fokker-Planck의 정상 분포가 볼츠만이 되지 않는다.

---

## 극한 일관성

| 극한 | 결과 | 보장 타입 |
|------|------|-----------|
| t→∞ | ρ → ρ_eq ∝ exp(−V/T) | 구조적 |
| ∫ρ dx = 1 | 모든 t에서 | 구조적 (no-flux BC) |
| J_eq = 0 | boltzmann에서 | 구조적 (detailed balance) |
| v_osmotic + v_current = 0 | 평형에서 | 구조적 (Nelson) |
| FP ↔ Langevin | 히스토그램 일치 | 수치적 (dt, N 의존) |

---

## Parisi-Wu 확률적 양자화 (향후)

```
허시간 τ의 Langevin:  ∂φ/∂τ = −δS/δφ + η(τ)
τ→∞ 정상 분포:        P[φ] ∝ exp(−S[φ])  (양자 분배함수)
```

현재 구현은 **고전 Fokker-Planck에 한정**한다.
Parisi-Wu 확장은 장론(field theory)과 결합하여 Layer 2+5의 교차점에서 구현 예정.

---

## 검증 결과 (layer5_verification.py)

| 테스트 | 결과 | 핵심 수치 |
|--------|------|-----------|
| 정상 분포 = 볼츠만 | PASS | L1 = 0.023, L∞ = 0.010 |
| 확률 보존 ∫ρ=1 | PASS | 최대 편차 2.2e-16 (기계 정밀도) |
| 평형 확률류 J=0 | PASS | J_max = 2.9e-04 (수치 미분 오차) |
| Nelson 삼투 속도 | PASS | 오차 = 0.000000 (∇ln ρ 직접 계산) |
| Langevin ↔ FP 일치 | PASS | L1 = 0.023 (이중 우물) |

---

## 인지적 해석

| 물리 | 인지 해석 |
|------|----------|
| ρ(x,t) | 사고 상태의 확률 분포 (어디에 있을 가능성이 높은가) |
| ρ_eq | 장기 기억의 안정 패턴 |
| v_osmotic | 밀도 기울기에 의한 "은밀한" 이동 — 무의식적 편향 |
| v_current | 외력(자극)에 의한 의식적 이동 |
| J = 0 (평형) | 사고가 순환하지 않는 균형 상태 |
| J ≠ 0 (비평형) | 사고의 반복적 순환 (강박, 루미네이션) |

---

## 향후 확장 방향

1. **2D Fokker-Planck**: 다차원 밀도 진화
2. **Parisi-Wu 확률적 양자화**: 허시간 Langevin → 양자 분배함수
3. **NESS 분석**: J ≠ 0 정상 상태의 순환 패턴
4. **정보 기하학**: Fisher 정보, KL 발산과 확률류의 관계
5. **Kramers-Moyal 확장**: 고차 항의 효과
