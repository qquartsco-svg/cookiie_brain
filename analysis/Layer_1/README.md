# Layer 1 — 통계역학 정식화

> trunk (Langevin + FDT) 위에 쌓이는 첫 번째 토양.
> 궤적을 확률·열역학 언어로 번역한다.

**위치**: Phase C (요동·FDT) → **Layer 1** → Layer 2 (다체/장론)

---

## 아키텍처 — 줄기와 가지

```
              ┌─ Layer 6: 위상 구조 ─┐
              │  Layer 5: 양자 연결   │
              │  Layer 4: 비평형 열역학 │
              │  Layer 3: 게이지/기하  │
              │  Layer 2: 다체/장론   │
             ┌┴────────────────────────┴┐
             │ ★ Layer 1: 통계역학 정식화 │  ← 이 모듈
             └┬────────────────────────┬┘
              │                        │
    ┌─────────┴────────────────────────┴─────────┐
    │  Trunk: m ẍ = -∇V + ωJv - γv + I + σξ(t)  │
    │         σ² = 2γT/m  (FDT)                  │
    └────────────────────────────────────────────┘
```

Layer 1은 나머지 모든 확장(Layer 2~6)의 **토양**이다.
여기서 나온 Kramers rate, 전이 행렬, 엔트로피가 없으면
위의 가지들이 뿌리를 내릴 수 없다.

---

## 구성 요소

**단위 규약**: 본 모듈은 자연 단위계에서 k_B = 1 로 두며, T는 에너지 단위로 해석한다.

### ① Kramers 탈출률

**물리**: 온도 T에서 장벽 ΔV를 넘는 확률적 전이 빈도.

```
k(i→j) = (λ₊ / ω_b) · (ω_a / 2π) · exp(−ΔV / T)
```

| 기호 | 의미 |
|------|------|
| ω_a | 우물 바닥 고유 진동수 √(λ_max / m) (합성 퍼텐셜 수치 Hessian) |
| ω_b | 안장점 불안정 진동수 (수치 Hessian, eps 튜닝 가능) |
| λ₊ | Kramers-Grote-Hynes 보정: −γ/(2m) + √((γ/(2m))² + ω_b²) |
| ΔV | 장벽 높이 V_saddle − V_well |
| T | 온도 (kB=1) |

`kramers_rate_matrix(mwp, T, γ, m)` → 전체 우물 간 rate 행렬 K.
K는 연속시간 Markov chain 생성 행렬: dp/dt = K^T p.

> **참고**: `well_frequency()`와 `saddle_frequency()`의 수치 Hessian은 중심 차분 `eps=1e-5` 를 기본값으로 사용한다. 퍼텐셜이 매우 좁거나(σ < 0.1) 매우 넓은(σ > 10) 경우, `eps` 인자를 조정하면 수치 정확도가 개선될 수 있다.

### ② 전이 행렬 분석기 (`TransitionAnalyzer`)

시뮬레이션 궤적에서 실측 통계를 추출한다.

| 메서드 | 반환 |
|--------|------|
| `observe(x, mwp, dt)` | 한 스텝 관측 (전이 카운트, 체류 시간 업데이트) |
| `transition_matrix()` | P[i,j] = N(i→j) / Σ_k N(i→k) (확률 행렬) |
| `mean_residence_times()` | τᵢ = (well i 체류 시간) / (well i 출발 횟수) |
| `occupation_fractions()` | 각 우물 시간 점유 비율 |
| `net_circulation()` | J[i,j] = N(i→j) − N(j→i) (비평형 순환 흐름) |
| `detailed_balance_violation()` | Σ|J| / (2Σ|N|) (0=평형, 1=비평형) |

### ③ 엔트로피 생산률

```
Ṡ = (γ/T)(⟨|v|²⟩ − dT/m) − (1/T)⟨v·I⟩
```

| 항 | 물리 |
|----|------|
| (γ/T)⟨\|v\|²⟩ | 마찰에 의한 소산 파워 / T |
| (γ/T)(dT/m) | 열욕조가 되돌려주는 평형 유지 비용 (baseline) |
| (1/T)⟨v·I⟩ | 외부 구동이 하는 일 |

극한 일관성:
- **평형 (I=0, FDT)**: ⟨|v|²⟩ = dT/m → **Ṡ = 0** (열역학 제2법칙 정합)
- **비평형 (I≠0)**: Ṡ > 0 (비가역 엔트로피 생산)

> **소산 파워와의 구분**: 마찰 소산 파워 γ⟨|v|²⟩ = γdT/m 자체는 평형에서도 양수이다.
> 그러나 노이즈 주입이 이를 정확히 상쇄하므로, 매질의 엔트로피 생산률 Ṡ = 0 이 된다.
> 즉 Ṡ는 "소산과 주입의 불균형"만 측정한다.

---

## 사용법

```python
from trunk.Phase_B.multi_well_potential import create_symmetric_wells
from analysis.Layer_1 import (
    kramers_rate,
    kramers_rate_matrix,
    TransitionAnalyzer,
    entropy_production_rate,
)
import numpy as np

# 우물 구성
centers = [np.array([-2, 0]), np.array([2, 0]), np.array([0, 2])]
mwp = create_symmetric_wells(centers, amplitude=2.0, sigma=1.0)

# Kramers rate 행렬
T, gamma, mass = 0.5, 0.5, 1.0
K = kramers_rate_matrix(mwp, T, gamma, mass)
print("Rate matrix:\n", K)

# 시뮬레이션 궤적에서 전이 통계
analyzer = TransitionAnalyzer(n_wells=3)
for x, dt in trajectory:
    analyzer.observe(x, mwp, dt)

P = analyzer.transition_matrix()          # 전이 확률
tau = analyzer.mean_residence_times()     # 체류 시간
db = analyzer.detailed_balance_violation() # 비평형 지표

# 엔트로피 생산
dS = entropy_production_rate(velocities, gamma, T, mass)
```

---

## 검증 결과 (2026-02-24)

```
python examples/layer1_verification.py → ALL PASS (5/5)
```

| # | 검증 | 결과 |
|---|------|------|
| 1 | Kramers rate 공식 정합성 (대칭, T↑→rate↑, γ↑→rate↓) | PASS |
| 2 | Kramers rate vs 시뮬레이션 전이 빈도 | PASS (order-of-magnitude) |
| 3 | 전이 행렬 행 합=1, 평형 상세 균형 violation≈0 | PASS |
| 4 | 엔트로피 생산률: 평형 Ṡ ≈ 0 (극한 일관성) | PASS |
| 5 | Arrhenius 법칙 (T↑ → rate↑ 방향 확인) | PASS |

---

## 왜 Layer 1이 "토양"인가

| Layer 1 출력 | 이것이 없으면 |
|-------------|-------------|
| Kramers rate | Layer 2(다체) 전이 네트워크 못 만듦 |
| 전이 행렬 | Layer 4(비평형 열역학) Jarzynski 검증 불가 |
| 엔트로피 | Layer 3(게이지), Layer 5(양자) 작용 정의 불가 |
| 상세 균형 지표 | 비평형/평형 판별 기준이 없음 |

---

*GNJz (Qquarts) · CookiieBrain Layer 1*
