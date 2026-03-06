# Phase B: 공전 (Orbit)

> 다중 우물 사이의 주기적 순환 — 기억 간 전이

**Version:** `0.3.0-dev`

---

## 공전이란

상태가 여러 우물(기억)을 **한 방향으로 주기적으로 순환**하는 것.

- 우물 2개, 직선 배치 → 왕복만 가능 (공전 아님)
- **우물 3개, 삼각형 배치 + ωJv** → 한쪽 방향으로 꺾임 → **공전**

검증 결과 (3-우물, 삼각형):
```
전이 횟수: 39
순환 횟수: 8  (2→0→1 반복)
주 순환 방향: 88%
에너지 보존: 0.0006%
```

---

## 왜 새로운 퍼텐셜이 필요한가

Phase A에서 사용한 Hopfield 이차 퍼텐셜:

$$V(x) = -\tfrac{1}{2} x^\top W x - b^\top x$$

이것은 연속 공간에서 **지역 최솟값이 최대 1개**인 구조다 (W의 성질에 따라 최소/안장/무한 하강).
공전(우물 사이 순환)을 구현하려면 **분리된 여러 최솟값**이 필요하다.

---

## 가우시안 합성 퍼텐셜

$$V(x) = -\sum_i A_i \exp\!\left(-\frac{\|x - c_i\|^2}{2\sigma_i^2}\right)$$

| 기호 | 의미 | 비유 |
|------|------|------|
| $c_i$ | 우물 중심 | 기억 패턴의 위치 |
| $A_i$ | 우물 깊이 (양수) | 기억의 강도 |
| $\sigma_i$ | 우물 폭 | 유인 범위 |

### 필드 (gradient → 힘)

$$g(x) = -\nabla V(x) = -\sum_i \frac{A_i}{\sigma_i^2}(x - c_i)\exp\!\left(-\frac{\|x-c_i\|^2}{2\sigma_i^2}\right)$$

### 안장점과 장벽

- $E > V_{\text{saddle}}$ → 장벽 통과 → 전이 가능
- $E < V_{\text{saddle}}$ → 하나의 우물 안에 갇힘

※ 장벽/안장점 계산은 두 우물 중심을 잇는 **직선 경로 상 최대값**(근사). 비대칭/고차원에서는 실제 안장점과 다를 수 있다.

---

## 공전의 조건

$$\ddot{x} = -\nabla V(x) + \omega J v$$

| 조건 | 역할 |
|------|------|
| 3개 이상 우물, 비직선 배치 | 순환 경로 존재 |
| E > V_saddle | 장벽 통과 가능 |
| ωJv (코리올리 자전) | 궤도를 한 방향으로 꺾어 순환 방향 생성 |
| ω 적절한 크기 | 너무 크면 우물 내부에서만 회전, 너무 작으면 방향성 없음 |

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
from Phase_B import create_symmetric_wells
from potential_field_engine import PotentialFieldEngine
import numpy as np

# 삼각형 배치 (공전의 핵심)
r = 2.5
centers = [
    np.array([r * np.cos(2*np.pi*k/3), r * np.sin(2*np.pi*k/3)])
    for k in range(3)
]
mwp = create_symmetric_wells(centers=centers, amplitude=2.0, sigma=1.2)

# PotentialFieldEngine에 연결
engine = PotentialFieldEngine(
    potential_func=mwp.potential,
    field_func=mwp.field,
    omega_coriolis=0.3,   # 공전에 적합한 범위
    dt=0.005,
)

# 장벽 분석
barrier = mwp.barrier_height(0, 1)
E_min = mwp.min_energy_for_orbit(0, 1)
```

---

## 검증 항목

| # | 검증 | 결과 |
|---|------|------|
| 1 | 다중 우물 구조 | ✔ PASS |
| 2 | 장벽 양수 | ✔ PASS |
| 3 | 전이 가능성 (3우물 방문) | ✔ PASS |
| 4 | 순환 궤도 — 공전 | ✔ PASS (8순환, 88% 단일 방향) |
| 5 | 에너지 보존 | ✔ PASS (0.0006%) |
| 6 | E < V_saddle 갇힘 | ✔ PASS |

---

## 파일 구조 (업데이트)

```
Phase_B/
├── __init__.py               # 모듈 export
├── multi_well_potential.py    # GaussianWell, MultiWellPotential
├── well_to_gaussian.py        # WellFormation → Gaussian 브릿지
└── README.md                 # 이 문서
```

## WellFormation → Gaussian 브릿지

경험(episodes) → WellFormation → W, b → **자동 변환** → GaussianWell → 공전

### 변환 수식
- **center**: `mean(post_activity)` (pattern 모드) 또는 `-(W+εI)⁻¹b` (solve 모드)
- **amplitude**: `spectral_radius(W) × scale` (기억 강도)
- **sigma**: `scale / √(mean|λ_neg|)` (유인 범위)

### WellRegistry
- 우물 누적 저장소, 거리 기반 중복 제거(병합)
- `count ≥ min_wells_for_orbit` → Gaussian 모드 자동 전환
- `cookiie_brain_engine.py`에 통합됨

---

## 현재 상태

| 단계 | 상태 |
|------|------|
| 다중 우물 퍼텐셜 | ✔ |
| 장벽/안장점 분석 | ✔ |
| 공전 검증 (3-우물 순환) | ✔ |
| WellFormation → Gaussian 브릿지 | ✔ |
| cookiie_brain_engine 통합 | ✔ |
| 에너지 주입/소산 | ✔ (γv 감쇠 + I(x,v,t) 주입) |
| 요동 (Phase C) | ✔ (σξ(t) Langevin noise) |
