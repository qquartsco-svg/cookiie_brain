# 3계층 중력 동역학 — 태양 · 지구(바다) · 달(조석)

> **한 문장**: 거대질량(태양)이 장을 지배하고, 중간질량(지구/우물)이 상태를 가두고,
> 소질량(달)이 조석 흐름을 만든다 — 이 세 스케일이 결합해야 "살아있는 궤도"가 나온다.

---

## 0. 왜 필요한가

v0.6.0 HippoMemoryEngine은 우물을 **만들고 없앨 수 있다** (태양).
하지만 우물 안에서 상태점은 **바닥에 가라앉는다** (감쇠 때문).

```
현재: 상태점 → 우물 바닥 → 정지 (죽은 기억)
목표: 상태점 → 우물 안에서 타원 순환 (살아있는 기억)
```

태양계에서 행성이 태양에 떨어지지 않는 이유:
**각운동량 보존 + 1/r 중력의 닫힌 궤도**.

뇌 모델에서 기억이 "죽지 않는" 이유:
**리듬(조석력)이 상태에 주기적 에너지를 넣어주기 때문.**

---

## 1. 3계층 구조

```
┌─────────────────────────────────────────────────┐
│  Tier 1: 태양 (Sun)                              │
│  ─────────────────                                │
│  장거리 중심 퍼텐셜: 전체 시스템 지배               │
│  V_sun(r) = -G·M_sun / (r + ε)                   │
│  → 모든 우물(행성)을 묶는 중력                      │
│  → CookiieBrain: HippoMemoryEngine               │
│                                                   │
│  ┌─────────────────────────────────────────────┐  │
│  │  Tier 2: 지구/바다 (Earth/Ocean)             │  │
│  │  ─────────────────────────                   │  │
│  │  국소 우물: 상태점을 가두는 매질               │  │
│  │  V_well(x) = -A·exp(-‖x-c‖²/2σ²)           │  │
│  │  → 기억의 실체, 상태가 머무는 곳              │  │
│  │  → CookiieBrain: GaussianWell                │  │
│  │                                              │  │
│  │  ┌────────────────────────────────────────┐  │  │
│  │  │  Tier 3: 달 (Moon)                     │  │  │
│  │  │  ─────────────────                     │  │  │
│  │  │  주기적 교란: 우물 안에 조석 흐름 생성   │  │  │
│  │  │  x_moon(t) = c + R·[cos(Ωt), sin(Ωt)] │  │  │
│  │  │  F_tidal = -∇V_moon(x) 의 공간 기울기   │  │  │
│  │  │  → 밀물/썰물 = 타원 유속 = 인지 리듬     │  │  │
│  │  │  → CookiieBrain: TidalField             │  │  │
│  │  └────────────────────────────────────────┘  │  │
│  └─────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

---

## 2. 수학

### 전체 운동 방정식 (v0.7.0)

```
m ẍ = -∇V_sun(x)        Tier 1: 중심 중력 (장거리)
    + -∇V_wells(x,t)     Tier 2: 우물 끌림 (중거리, 동적)
    + -∇V_moon(x,t)      Tier 3: 달 조석력 (주기적 교란)
    + ωJv                 Phase A: 코리올리 자전
    - γv                  감쇠
    + I(x,v,t)            Hippo 에너지 주입
    + σξ(t)               Phase C: 열적 요동
```

### Tier 1: 태양 — 중심 퍼텐셜

```
V_sun(r) = -G · M_sun / (r + ε)

r = ‖x - x_sun‖
ε = softening (수치 안정성)
```

특성:
- 1/r: 멀어져도 끌림이 살아있음 (Gaussian과 결정적 차이)
- 모든 우물(행성)이 태양 주위에 묶임
- 안정 원궤도 조건: `v = √(GM/r)`

인지 해석:
- 장기기억의 "중심 인력" — 모든 단기 상태가 장기기억 체계 안에 묶임

### Tier 2: 지구/바다 — 국소 우물

```
V_wells(x,t) = -Σ A_i(t) · exp(-‖x - c_i‖² / (2σ_i²))
```

이미 구현됨 (MemoryStore).
amplitude A_i(t)가 시간에 따라 변함 (강화/망각).

인지 해석:
- 개별 기억 — 특정 패턴에 대한 끌림 (attractor)
- 바다 = 우물 내부의 연속적 상태 공간

### Tier 3: 달 — 공전 + 조석력

```
달 위치 (공전):
  x_moon(t) = c_host + R_orbit · [cos(Ω·t), sin(Ω·t)]

달 중력:
  V_moon(x,t) = -G_moon · M_moon / (‖x - x_moon(t)‖ + ε)

조석력 (핵심):
  F_tidal(x,t) = -∇V_moon(x,t)
```

조석(tidal)의 물리적 의미:
- 달의 중력이 우물의 **모든 위치에 균등하게** 작용하면 조석은 없다
- 조석은 달 중력의 **공간적 기울기 차이** (tidal gradient)
- 달에 가까운 쪽은 더 강하게 당겨지고, 먼 쪽은 덜 당겨짐
- 이 차이가 우물 안의 상태점을 **타원형으로 순환**시킴

인지 해석:
- 외부 리듬 (수면 주기, 주의 주기, 호흡 리듬)
- 같은 기억이라도 "지금 주기의 어느 위상인가"에 따라 활성도가 달라짐
- 조석 = 공명 조건에서 큰 전이 유도

---

## 3. 핵심 물리: 왜 Gaussian만으로는 안 되는가

| | Gaussian 우물 | 1/r 중력 |
|---|---|---|
| 장거리 | 지수적 감소 (σ 밖 ≈ 0) | 역제곱 법칙 (느리게 감소) |
| 안정 공전 | 특정 r에서만 잠깐 (감쇠 → 낙하) | 모든 r에서 가능 (v=√(GM/r)) |
| 닫힌 궤도 | 없음 (일반적으로) | 타원/원 (Kepler) |
| 에너지 구속 | 약함 | 강함 (E<0이면 영원히 묶임) |

해결: **Gaussian 우물 + 1/r 중심장 합성**

```
V_total(x,t) = V_sun(r) + V_wells(x,t) + V_moon(x,t)
                ─────────   ────────────   ────────────
                Tier 1       Tier 2         Tier 3
                장거리 구속   국소 끌림      주기적 교란
```

---

## 4. 구현 설계

### 새 모듈: `trunk/Phase_A/tidal.py`

```python
@dataclass
class OrbitalMoon:
    host_center: np.ndarray     # 공전 중심 (어떤 우물의 center)
    orbit_radius: float         # 궤도 반경
    orbit_frequency: float      # Ω (rad/s)
    mass: float                 # 달 질량
    G: float                    # 중력 상수
    softening: float            # 수치 안정성

    def position(self, t: float) -> np.ndarray:
        """시각 t에서의 달 위치"""

    def gravity(self, x: np.ndarray, t: float) -> np.ndarray:
        """시각 t에서 위치 x에 작용하는 달 중력"""


class TidalField:
    """달 공전 + 조석력 생성기"""

    def __init__(self, moons: List[OrbitalMoon]):
        ...

    def force(self, x: np.ndarray, t: float) -> np.ndarray:
        """모든 달의 조석력 합"""

    def potential(self, x: np.ndarray, t: float) -> float:
        """모든 달의 퍼텐셜 합"""
```

### 새 모듈 또는 확장: 중심 퍼텐셜

```python
@dataclass
class CentralBody:
    position: np.ndarray        # 태양 위치
    mass: float                 # 태양 질량
    G: float                    # 중력 상수
    softening: float            # 수치 안정성

    def potential(self, x: np.ndarray) -> float:
        """V = -GM/(r+ε)"""

    def field(self, x: np.ndarray) -> np.ndarray:
        """-∇V = -GM·(x-x_sun)/(r+ε)³"""
```

### CookiieBrainEngine 확장 (v0.7.0)

```python
# 기존 update() 루프에 추가:
# 2.5. TidalField 실행 (Phase A 확장)
if self.tidal_field:
    tidal_force = self.tidal_field.force(x, t)
    # PFE의 injection에 합산 또는 별도 적용
```

---

## 5. 실험 설계

### 실험 1: 순수 공전 (2D, 감쇠 없음)

```
설정:
  태양: 원점, M=10.0
  행성(우물): r=5.0, A=1.0
  상태점: (5.0, 0.0), 초기 속도 (0, v_circ)
  γ=0, σ=0, I=0 (순수 역학)

v_circ = √(GM/r)

확인:
  타원/원 궤도가 나오는가?
  에너지 보존이 되는가?
```

### 실험 2: 감쇠 + 코리올리

```
설정:
  실험 1 + γ=0.01 + ω=1.0

확인:
  나선 낙하 vs 준안정 공전
  ω가 γ를 보상하는 조건은?
```

### 실험 3: 달 조석

```
설정:
  실험 2 + 달 (R=1.0, Ω=2.0, M_moon=0.1)

확인:
  우물 안에서 타원 유속이 나오는가?
  상태점이 바닥에 가라앉지 않고 순환하는가?
```

### 실험 4: 전체 시스템 + Layer 분석

```
설정:
  실험 3 + HippoMemory + BrainAnalyzer

분석:
  Layer 1: 전이 확률 (궤도 유지 vs 탈출 vs 붕괴)
  Layer 5: 확률 밀도 (궤도 반경 분포)
  Layer 6: Fisher 곡률 (파라미터 민감도)
```

---

## 6. 세 관점 매핑 (최종)

| 수학 항 | 천체역학 | 인지역학 | 코드 모듈 |
|---------|---------|---------|----------|
| `V_sun(r)` | 태양 중력 | 장기기억 중심 인력 | CentralBody |
| `V_wells(x,t)` | 행성 (국소 중력) | 개별 기억 (attractor) | MemoryStore |
| `V_moon(x,t)` | 달 조석력 | 외부 리듬/주기적 자극 | TidalField |
| `ωJv` | 코리올리 (각운동량) | 위상 리듬 (자전) | Phase A |
| `-γv` | 조석 마찰 | 주의 감쇠 | PFE 감쇠 |
| `I(x,v,t)` | 추진력 (항법) | 탐색/정착/리콜 | EnergyBudgeter |
| `σξ(t)` | 미소 교란 | 연상 전이 | Phase C |

---

## 7. 안정 공전 조건 (이론)

중심 퍼텐셜 `V = -GM/r`에서:

```
원궤도 조건:    v_circ = √(GM/r)
탈출 속도:      v_esc  = √(2GM/r)
타원 궤도:      v_circ < v < v_esc
구속 조건:      E = ½mv² + V(r) < 0
```

감쇠가 있을 때:
```
에너지 손실률:   dE/dt = -γ|v|²
보상 조건:       I(x,v,t)가 γ|v|²를 보상해야 궤도 유지
또는:            달 조석이 주기적으로 에너지 주입
```

---

*GNJz (Qquarts) · CookiieBrain v0.7.0 설계*
*"태양이 장을 만들고, 지구가 기억을 담고, 달이 리듬을 만든다."*
