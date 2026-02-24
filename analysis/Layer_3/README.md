# Layer 3 — 게이지/기하학 (Gauge / Geometry)

> **위치에 따라 회전이 달라진다** — trunk의 전역 Coriolis 게이지를 위치 의존 반대칭 연산자 Ω(x)로 확장.

---

## 게이지 ≠ 보존력

Layer 3에서 가장 중요한 구분:

```
mẍ = −∇V(x)  +  Ω(x)v   −  γv  +  σξ(t)
      ─────     ──────      ────    ─────
      Force     Gauge       Thermo  Fluctuation
      (보존력)  (반대칭)    (비가역)  (확률)
```

| | Force (Layer 1,2) | **Gauge (Layer 3)** | Thermo (trunk) |
|---|---|---|---|
| 수학적 정의 | −∇V(x) | Ω(x)·v | −γv + σξ |
| 에너지 교환 | 가능 (위치 에너지 ↔ 운동 에너지) | **불가** (v·Ωv = 0, 구조적) | 비가역 소산 |
| 유도 원천 | 퍼텐셜 V(x) | **없음** (connection 연산자) | 열 저장소 |
| 대칭 구조 | 일반 벡터장 | **반대칭** (Ωᵀ = −Ω) | 양의 정부호 (γ > 0) |
| 물리적 역할 | 가속/감속 | **회전만** (위상 변화) | 에너지 주입/제거 |

Gauge는 **보존력이 아니다.**
Hamiltonian의 symplectic 구조 내 회전 항(geometric phase term)이다.

---

## 핵심 수학

### 반대칭 연산자 Ω(x)

2D에서:
```
Ω(x) = B(x) · J

J = [[0, -1], [1, 0]]    ← 반대칭 (Jᵀ = −J)
B(x) ∈ ℝ                 ← 스칼라
Ω(x) = B(x)·J            ← 반대칭 (스칼라 × 반대칭 = 반대칭)
```

### 에너지 보존 증명 (구조적)

```
d/dt(½m|v|²) = mv · v̇ = mv · Ω(x)v = m · vᵀΩv

Ωᵀ = −Ω  ⟹  vᵀΩv = (vᵀΩv)ᵀ = vᵀΩᵀv = −vᵀΩv  ⟹  vᵀΩv = 0
```

이것은 B(x)의 형태에 **무관**하게 성립한다. 반대칭성만 보장되면 된다.

### 반대칭 검증

코드에서 `check_skew(x)` 메서드로 검증 가능:
```python
gauge = GaugeForce(B_func=my_field, dim=2)
assert gauge.check_skew(x)   # Ω(x) + Ω(x)ᵀ = 0 확인
```

### 3D 확장

```
G(v) = v × B(x)     (로렌츠 항)
v · (v × B) = 0     (벡터 삼중곱 성질 — 반대칭의 3D 표현)
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

### GaugeForce (= MagneticForce)

단일 입자에 대한 위치 의존 반대칭 게이지 연산자.

```python
from analysis.Layer_3 import GaugeForce

def B_field(x):
    """원점 근처에 집중된 가우시안 자기장"""
    return 2.0 * np.exp(-np.dot(x, x) / 8.0)

gauge = GaugeForce(B_func=B_field, dim=2)
```

**구현 참고:** trunk의 GaugeLayer 프로토콜은 `rotate(v, dt)`만 받아 위치 정보가 없다.
따라서 Ω(x)v는 ForceLayer 프로토콜(`force(x, v, t)`)로 전달한다.
이것은 **구현 편의**이며, 물리적 본질은 gauge 연산(반대칭, 비보존력, 비퍼텐셜)이다.

**`MagneticForce`는 `GaugeForce`의 별칭(alias)으로 유지한다** — 하위 호환.

### NBodyGaugeForce (= NBodyMagneticForce)

N 입자 각각에 위치 의존 반대칭 게이지 연산자를 적용.

```python
from analysis.Layer_3 import NBodyGaugeForce

nb_gauge = NBodyGaugeForce(
    n_particles=10, dim=2,
    B_func=lambda x: 1.0  # 균일 Ω
)
```

N=1이면 `GaugeForce`와 동일 (극한 일관성).

### GeometryAnalyzer

게이지 기하학 분석 도구:

| 메서드 | 설명 | 수식 |
|--------|------|------|
| `magnetic_flux()` | 원형 영역의 자기 선속 | Φ = ∫∫ B dA |
| `flux_through_loop()` | 닫힌 경로의 선속 기반 위상 축적 | Φ = Σ B(centroid) · ΔA |
| `local_curvature()` | 국소 곡률 (2D에서 B 자체) | F₁₂ = B(x) |
| `cyclotron_frequency()` | 사이클로트론 진동수 | ω_c = B/m |
| `cyclotron_radius()` | 사이클로트론 반경 | r_c = mv⊥/\|B\| |
| `exb_drift()` | E×B drift 속도 | v = (∂V/∂y, −∂V/∂x)/B |

### 편의 함수: 기본 B(x) 구성

| 함수 | B(x) | 용도 |
|------|------|------|
| `uniform_field(B₀)` | B₀ | 균일 (사이클로트론) |
| `gaussian_field(B₀, c, σ)` | B₀ · exp(−\|x−c\|²/2σ²) | 국소 집중 |
| `dipole_field(μ, c, ε)` | μ / (\|x−c\|² + ε²) | 쌍극자형 |
| `multi_well_field(Bs, cs, σs)` | Σ Bᵢ · exp(−\|x−cᵢ\|²/2σᵢ²) | 다중 우물별 |

---

## 극한 일관성

| 극한 | 예상 | 보장 타입 |
|------|------|----------|
| Ω(x) = ω·J (const) | CoriolisGauge와 동일 | 구조적 |
| B(x) = 0 | Ω = 0, 자유 입자 | 구조적 |
| vᵀΩv = 0 | 에너지 보존 | 구조적 (Ωᵀ = −Ω) |
| N=1 | 단일 입자와 동일 | 구조적 |
| 사이클로트론 (B=const) | 원 궤도, ω_c=B/m | 적분기 의존 (dt) |
| E×B drift | v_drift = (∂V/∂y, −∂V/∂x)/B | 적분기 의존 (dt) |
| 선속 기반 위상 축적 | Φ = ∫∫B dA (Abelian) | 수치 적분 정밀도 |

> **"구조적"**: 반대칭성 Ωᵀ=−Ω 만으로 보장. dt, 적분기 무관.
> **"적분기 의존"**: 이론적으로 정확하나, 수치 정밀도가 dt와 적분기에 의존.

### Berry phase vs 자기 선속 — 용어 구분

현재 구현은 **B(x)의 면적분** `∫∫ B dA`으로 위상을 계산한다.
Abelian case에서 Stokes 정리에 의해 이것은 `∮A·dl`과 동일하지만,
벡터 퍼텐셜 A(x)를 명시적으로 정의하지 않는다.

엄밀한 Berry phase는:
1. A(x) connection 정의
2. gauge choice (대칭 게이지, 쿨롱 게이지 등)
3. `∮A·dl` 선적분

이 필요하다. 따라서 현재 단계를 **"Abelian 자기 선속 기반 위상 축적"**으로 표기한다.
Non-Abelian 확장 시 A_μ(x) 도입은 향후 Layer 4 대상이다.

---

## 적분기 관련 주의사항

GaugeForce는 **속도 의존 연산자**이다. trunk의 Strang splitting에서:
- 연산자를 한 번 평가하고 양쪽 half-kick에 같은 값을 사용
- 위치 의존 보존력에는 2차 정확도 (symplectic-like)
- **속도 의존 연산자에는 1차 정확도** — 에너지 drift가 O(dt²)로 bounded

**권장:**
1. `CoriolisGauge(ω)` 또는 `CoriolisGauge(0.0)`으로 Strang splitting 활성화
2. NullGauge (Euler fallback) 사용 시 에너지 drift 심각
3. 높은 정밀도가 필요하면 dt를 줄일 것

향후 Boris integrator 도입 시 반대칭 회전의 정확한 처리 가능.

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

| 물리 | 인지 해석 |
|------|----------|
| Ω(x): 위치 의존 반대칭 연산자 | 기억 영역마다 다른 "사고 회전" 경향 |
| 사이클로트론 운동 | 특정 기억 주위의 반복적 연상 순환 |
| E×B drift | 외부 자극(기울기)에 대한 횡방향 사고 이동 |
| Berry 위상 | 연상 고리를 한 바퀴 돌았을 때 축적되는 인지 위상차 |
| 곡률 F₁₂ = B(x) | 사고 공간의 국소적 "비틀림" 정도 |

---

## 향후 확장 방향

1. **비가환 게이지 (Non-Abelian)**: B(x) → A_μ(x) 행렬값 connection. Ω가 행렬이 되면 [Ω_i, Ω_j] ≠ 0
2. **Boris integrator**: 반대칭 회전의 정확한 분리 처리
3. **게이지 불변성 (Gauge invariance)**: A → A + ∇χ 변환에 대한 물리량 불변 검증
4. **곡률-힘 결합**: R_{μν} → 측지선 이탈 (geodesic deviation)
