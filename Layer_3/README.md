# Layer 3 — 게이지/기하학 (Gauge / Geometry)

> **위치에 따라 회전이 달라진다** — trunk의 전역 Coriolis 게이지를 위치 의존 자기장(B-field)으로 확장.

---

## 핵심 아이디어

| 개념 | trunk (기존) | Layer 3 (확장) |
|------|-------------|---------------|
| 회전 | ω = 상수 (전역) | B(x) = 위치 의존 (국소) |
| 힘 | F = ω·J·v | F = B(x)·J·v |
| 에너지 | 보존 (J^T=-J) | 보존 (F·v = 0, 구조적) |
| 기하학 | 없음 | Berry 위상, 곡률, 선속 |

## 수식

### 2D 자기장형 힘

```
F = B(x) · J · v = B(x) · (-v_y, v_x)

J = [[0, -1], [1, 0]]   (symplectic 행렬)
```

### 에너지 보존 증명 (구조적)

```
F · v = B(x) · (-v_y · v_x + v_x · v_y) = 0   ∀ x, v, B(x)
```

자기장형 힘은 **항상** 속도에 수직이므로, 일을 하지 않는다.

### 3D 확장

```
F = v × B(x)     (로렌츠 힘)
F · v = 0         (벡터 삼중곱 성질)
```

### E×B Drift

일정 기울기 퍼텐셜 V(x) + 균일 B에서의 정상 상태 drift:

```
0 = -∂V/∂x − B·v_y   →   v_y = −(∂V/∂x) / B
0 = -∂V/∂y + B·v_x   →   v_x = +(∂V/∂y) / B

v_drift = (∂V/∂y, −∂V/∂x) / B
```

입자는 **퍼텐셜 기울기에 수직**으로 표류한다.

---

## 구성 요소

### MagneticForce

단일 입자에 대한 위치 의존 자기장형 힘.

```python
from Layer_3 import MagneticForce

def B_field(x):
    """원점 근처에 집중된 가우시안 자기장"""
    return 2.0 * np.exp(-np.dot(x, x) / 8.0)

magnetic = MagneticForce(B_func=B_field, dim=2)
```

**ForceLayer 프로토콜 준수** — trunk 수정 없이 `force_layers`에 추가 가능.

### NBodyMagneticForce

N 입자 각각에 위치 의존 자기장을 적용.

```python
from Layer_3 import NBodyMagneticForce

nb_magnetic = NBodyMagneticForce(
    n_particles=10, dim=2,
    B_func=lambda x: 1.0  # 균일 B
)
```

N=1이면 `MagneticForce`와 동일 (극한 일관성).

### GeometryAnalyzer

게이지 기하학 분석 도구:

| 메서드 | 설명 | 수식 |
|--------|------|------|
| `magnetic_flux()` | 원형 영역의 자기 선속 | Φ = ∫∫ B dA |
| `berry_phase_loop()` | 닫힌 경로의 Berry 위상 | Φ = Σ B(centroid) · ΔA |
| `local_curvature()` | 국소 곡률 (2D에서 B 자체) | F₁₂ = B(x) |
| `cyclotron_frequency()` | 사이클로트론 진동수 | ω_c = B/m |
| `cyclotron_radius()` | 사이클로트론 반경 | r_c = mv⊥/\|B\| |
| `exb_drift()` | E×B drift 속도 | v = (∂V/∂y, −∂V/∂x)/B |

### 편의 함수: 기본 자기장 구성

| 함수 | B(x) | 용도 |
|------|------|------|
| `uniform_field(B₀)` | B₀ | 균일 자기장 (사이클로트론) |
| `gaussian_field(B₀, c, σ)` | B₀ · exp(−\|x−c\|²/2σ²) | 국소 집중 자기장 |
| `dipole_field(μ, c, ε)` | μ / (\|x−c\|² + ε²) | 쌍극자형 자기장 |
| `multi_well_field(Bs, cs, σs)` | Σ Bᵢ · exp(−\|x−cᵢ\|²/2σᵢ²) | 다중 우물별 자기장 |

---

## 극한 일관성

| 극한 | 예상 | 보장 타입 |
|------|------|----------|
| B(x) = const = ω | CoriolisGauge와 동일 | 구조적 |
| B(x) = 0 | 자유 입자 (힘 없음) | 구조적 |
| F·v = 0 | 에너지 보존 | 구조적 (J^T = −J) |
| N=1 | 단일 입자와 동일 | 구조적 |
| 사이클로트론 (B=const) | 원 궤도, ω_c=B/m | 적분기 의존 (dt) |
| E×B drift | v_drift = (∂V/∂y, −∂V/∂x)/B | 적분기 의존 (dt) |
| Berry 위상 | ∮A·dl = ∫∫B dA (Stokes) | 수치 적분 정밀도 |

> **"구조적"**: 코드 구조만으로 보장. dt, 적분기 무관.
> **"적분기 의존"**: 이론적으로 정확하나, 수치 정밀도가 dt와 적분기에 의존.

---

## 적분기 관련 주의사항

MagneticForce는 **속도 의존 힘**이다. trunk의 Strang splitting에서:
- 힘을 한 번 평가하고 양쪽 half-kick에 같은 값을 사용
- 위치 의존 보존력에는 2차 정확도 (symplectic-like)
- **속도 의존 힘에는 1차 정확도** — 에너지 drift가 O(dt²)로 bounded

**권장:**
1. `CoriolisGauge(ω)` 또는 `CoriolisGauge(0.0)`으로 Strang splitting 활성화
2. NullGauge (Euler fallback) 사용 시 에너지 drift 심각
3. 높은 정밀도가 필요하면 dt를 줄일 것

향후 Boris integrator 도입 시 속도 의존 힘에 대한 정확한 회전 보장 가능.

---

## 검증 결과 (layer3_verification.py)

| 테스트 | 결과 | 핵심 수치 |
|--------|------|-----------|
| 에너지 보존 (가우시안 B) | PASS | drift < 5% (Strang, dt=0.002) |
| 사이클로트론 (균일 B) | PASS | r_c 오차 < 2%, 원형도 < 1% |
| B=0 극한 | PASS | 궤적 차이 = 0 (exact) |
| E×B drift (collisionless) | PASS | v_drift 오차 < 0.1% |
| Berry 위상 (가우시안 B) | PASS | 면적분 오차 < 2% |

---

## 인지적 해석

Layer 3의 물리적 구조를 인지 시스템에 대응시키면:

| 물리 | 인지 해석 |
|------|----------|
| B(x): 위치 의존 자기장 | 기억 영역마다 다른 "사고 회전" 경향 |
| 사이클로트론 운동 | 특정 기억 주위의 반복적 연상 순환 |
| E×B drift | 외부 자극(기울기)에 대한 횡방향 사고 이동 |
| Berry 위상 | 연상 고리를 한 바퀴 돌았을 때 축적되는 인지 위상차 |
| 곡률 | 사고 공간의 국소적 "비틀림" 정도 |

---

## 향후 확장 방향

1. **비가환 게이지 (Non-Abelian)**: B(x) → A_μ(x) 행렬값 connection
2. **Boris integrator**: 속도 의존 힘의 정확한 회전 처리
3. **게이지 불변성 (Gauge invariance)**: A → A + ∇χ 변환에 대한 물리량 불변 검증
4. **곡률-힘 결합**: R_{μν} → 측지선 이탈 (geodesic deviation)
