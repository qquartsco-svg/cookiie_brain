# Phase B: 공전 (Orbit)

> 다중 우물 사이의 상태 전이 — 기억 간 순환

**Version:** `0.3.0-dev`

---

## 왜 새로운 퍼텐셜이 필요한가

Phase A에서 사용한 Hopfield 이차 퍼텐셜:

$$V(x) = -\tfrac{1}{2} x^\top W x - b^\top x$$

이것은 **연속 공간에서 단일 최솟값**만 가진다.
공전(우물 사이 전이)을 구현하려면 **여러 개의 최솟값**이 필요하다.

---

## 가우시안 합성 퍼텐셜

$$V(x) = -\sum_i A_i \exp\!\left(-\frac{\|x - c_i\|^2}{2\sigma_i^2}\right)$$

| 기호 | 의미 | 비유 |
|------|------|------|
| $c_i$ | 우물 중심 | 기억 패턴의 위치 |
| $A_i$ | 우물 깊이 (양수) | 기억의 강도 (깊을수록 강함) |
| $\sigma_i$ | 우물 폭 | 유인 범위 (넓을수록 먼 곳에서도 끌림) |

각 가우시안이 하나의 **attractor(기억)**를 형성한다.

### 필드 (gradient → 힘)

$$g(x) = -\nabla V(x) = -\sum_i \frac{A_i}{\sigma_i^2}(x - c_i)\exp\!\left(-\frac{\|x-c_i\|^2}{2\sigma_i^2}\right)$$

우물 중심 방향으로 당기는 힘.

### 안장점과 장벽

두 우물 사이에 **안장점(saddle point)** — 장벽의 꼭대기 — 이 존재한다.

- $E > V_{\text{saddle}}$ → 장벽을 넘어 **전이 가능** (공전)
- $E < V_{\text{saddle}}$ → **하나의 우물 안에 갇힘**

---

## 전체 운동 방정식

$$\ddot{x} = -\nabla V(x) + \omega J v$$

| 항 | 역할 | Phase |
|----|------|-------|
| $-\nabla V(x)$ | 가우시안 다중 우물의 인력 | B |
| $\omega J v$ | 코리올리 자전 (에너지 보존) | A |

자전(Phase A)은 그대로 유지. 퍼텐셜만 교체.

---

## 파일 구조

```
Phase_B/
├── __init__.py               # 모듈 export
├── multi_well_potential.py    # GaussianWell, MultiWellPotential, create_symmetric_wells
└── README.md                 # 이 문서
```

---

## 사용법

```python
from Phase_B import MultiWellPotential, GaussianWell, create_symmetric_wells

# 방법 1: 개별 우물 설정
wells = [
    GaussianWell(center=[-2, 0], amplitude=2.0, sigma=1.0),
    GaussianWell(center=[ 2, 0], amplitude=2.0, sigma=1.0),
]
mwp = MultiWellPotential(wells)

# 방법 2: 대칭 우물 (편의 함수)
mwp = create_symmetric_wells(
    centers=[[-2, 0], [2, 0]],
    amplitude=2.0,
    sigma=1.0,
)

# PotentialFieldEngine에 연결
engine = PotentialFieldEngine(
    potential_func=mwp.potential,
    field_func=mwp.field,
    omega_coriolis=0.5,
    dt=0.005,
)

# 장벽 분석
info = mwp.landscape_info()
barrier = mwp.barrier_height(0, 1)
E_min = mwp.min_energy_for_orbit(0, 1)
```

---

## 검증 항목

| # | 검증 | 조건 | 스크립트 |
|---|------|------|----------|
| 1 | 다중 우물 구조 | V(center) < V(saddle) | `phase_b_orbit_verification.py` |
| 2 | 장벽 양수 | barrier_height > 0 | 〃 |
| 3 | E > V_saddle 순환 | 전이 횟수 ≥ 2 | 〃 |
| 4 | 에너지 보존 | rel_drift < 0.1% | 〃 |
| 5 | E < V_saddle 갇힘 | 전이 횟수 = 0 | 〃 |

---

## 현재 상태

| 단계 | 상태 |
|------|------|
| B-1: 다중 우물 퍼텐셜 | ✔ 구현 |
| B-1: 장벽/안장점 분석 | ✔ 구현 |
| B-1: 최소 공전 검증 | ⏳ 검증 스크립트 |
| B-2: WellFormation 연동 | 미착수 |
| B-3: 에너지 주입/소산 | 미착수 |
