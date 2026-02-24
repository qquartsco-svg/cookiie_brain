# Layer 2 — 다체/장론 (Many-body / Field Theory)

## 위치

```
Layer 1 (통계역학 토양)
  └─ Layer 2 (다체 동역학)  ← 여기
       └─ Layer 3 (게이지/기하학) — 미구현
```

## 핵심 원리

**trunk은 이미 N-body를 지원한다.**

trunk의 state_vector = `[x₁...xₙ, v₁...vₙ]`는 N 입자 × d 차원을 평탄(flat) 벡터로 표현한다.
trunk은 이 벡터의 내부 구조를 알 필요 없이 그대로 적분한다.
Layer 2는 N-body 전용 **레이어**(힘/게이지)를 제공할 뿐이다.

## 구성

| 클래스 | 역할 | duck-typing 프로토콜 |
|--------|------|---------------------|
| `NBodyState` | flat ↔ (N,d) reshape 유틸리티 | — |
| `InteractionForce` | 쌍체 상호작용 Σ_{i<j} φ(r_ij) | ForceLayer |
| `ExternalForce` | 입자별 외부 퍼텐셜 Σᵢ V(xᵢ) | ForceLayer |
| `NBodyGauge` | 입자별 코리올리 회전 | GaugeLayer |

### 힘 부호 규약

`InteractionForce`의 `pair_force`는 **φ'(r) = dφ/dr** 을 받는다.
실제 힘은 다음과 같이 계산된다:

```
F_ij = -φ'(r_ij) · r̂_ij    (r̂_ij = (xᵢ - xⱼ)/r_ij)
```

따라서:
- φ'(r) > 0 → F_ij가 i를 j 쪽으로 끌어당김 (인력)
- φ'(r) < 0 → F_ij가 i를 j로부터 밀어냄 (척력)

softening은 `InteractionForce` 내부에서 거리 계산 시 적용된다:
`r = √(|xᵢ - xⱼ|² + ε²)` (ε = softening 파라미터)

### 편의 함수 (기본 상호작용)

| 함수 | φ(r) | φ'(r) | 힘 방향 |
|------|------|-------|---------|
| `gravitational_interaction()` | -G/r | +G/r² | 인력 |
| `spring_interaction()` | ½k(r-r₀)² | k(r-r₀) | 복원력 |
| `coulomb_interaction()` | q²/r | -q²/r² | 척력 (동종 전하) |

## 극한 일관성

| 극한 | 기대 동작 | 보장 타입 | 검증 |
|------|----------|----------|------|
| N=1 | 단일 입자 trunk과 동일 | **구조적** — 쌍체 힘 비활성화 시 자동 환원 | Test 3: 차이 0.0 |
| F_ij = -F_ji | 운동량 보존 | **구조적** — `F[i]+=fij, F[j]-=fij` 코드로 강제 | Test 1: 변화 3.2e-14 |
| 중심력 | 각운동량 보존 | **구조적** — 힘이 항상 r̂ 방향(central) | Test 5: 변화 5.3e-15 |
| γ=0, σ=0 | 에너지 보존 | **적분기 의존** — 보존계 환원은 모델 차원에서 보장되나, 수치 drift는 적분기/dt에 의존 | Test 2: drift < 0.23% |
| FDT + N 입자 | 등분배 수렴 | **적분기 의존** — FDT는 trunk에서 보장, 수렴 속도는 dt와 γ에 의존 | Test 4: 오차 2.0% |

> **N→∞ 극한**: 단순히 N을 키운다고 장론(field theory)이 되지 않는다. 연속체/평균장 극한에는 밀도 고정(박스 스케일링), 상호작용 스케일링(1/N), coarse-graining 정의 등 추가적인 극한 정의가 필요하다. 이는 Layer 2의 현재 범위 밖이며, 향후 확장 방향에 해당한다.

## 수식

### 운동 방정식 (N 입자)

```
m ẍᵢ = -∇ᵢ V(xᵢ) + Σ_{j≠i} F_ij(xᵢ, xⱼ) + G(vᵢ, dt) - γvᵢ + σξᵢ(t)
```

### Newton 제3법칙 (구조적 보장)

```
F_ij = -φ'(r_ij) · (xᵢ - xⱼ) / r_ij
F_ji = -φ'(r_ji) · (xⱼ - xᵢ) / r_ji = -F_ij
→ Σᵢ F_ij = 0 → dp/dt = 0 (총 운동량 보존)
```

### 등분배 정리

```
⟨½m|vᵢ,α|²⟩ = T/2  (per DOF)
```

FDT가 이미 Layer 0(trunk)에서 보장되므로, N 입자로 확장해도 자동 성립.

## 검증 결과

```
Layer 2 — 다체/장론 검증
============================================================
  [PASS ✓]  Newton 제3법칙 — 운동량 보존
  [PASS ✓]  에너지 보존 — 보존계
  [PASS ✓]  N=1 극한 — 단일 입자와 동일
  [PASS ✓]  등분배 정리 — 열평형
  [PASS ✓]  2체 순환 — 각운동량 보존

  총 5/5 PASS
```

## 사용 예시

```python
from analysis.Layer_2.nbody import NBodyState, InteractionForce, ExternalForce, spring_interaction
from potential_field_engine import PotentialFieldEngine
from layers import LangevinThermo, NullGauge

N, d = 10, 2
nbs = NBodyState(N, d)

interaction = spring_interaction(N, d, k=1.0, r0=2.0)

engine = PotentialFieldEngine(
    force_layers=[interaction],
    gauge_layer=NullGauge(),
    thermo_layer=LangevinThermo(gamma=1.0, temperature=0.5),
    dt=0.005,
    noise_seed=42,
)

# state_vector = [x1,y1, x2,y2, ..., xN,yN, vx1,vy1, ..., vxN,vyN]
state = make_state(nbs.make_state_vector(X0, V0))
for _ in range(10000):
    state = engine.update(state)
```

## 향후 확장 방향

- **N→∞ / mean-field**: 밀도 고정 + 상호작용 1/N 스케일링 + coarse-graining → 연속체 극한
- **장거리 상호작용**: Ewald summation, Barnes-Hut tree 등 O(N log N) 알고리즘
- **다종 입자**: 질량/전하가 다른 혼합계 (mass vector 확장)
- **Layer 3 연결**: 게이지 대칭 + 곡률 → 위치 의존 상호작용
