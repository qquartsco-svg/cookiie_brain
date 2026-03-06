# solar/em/ — 전자기·복사 환경 레이어 (v1.3.1)

core/(중력/세차) 위에 얹는 환경 필드 레이어.
궤도에 힘을 되먹이지 않는 **관측자 모드**로 동작한다.

이 레이어는 항성 내부 물리(핵융합, 대류, 중심온도)를 풀지 않는다.
주계열 항성을 가정하고, 외부 출력(광도, 자기장, 태양풍, 자기권)만 계산한다.

> *"빛이 있으라"의 기록: [light/](light/) — 폴더를 열면 읽을 수 있다*

---

## 모듈 구조

```
solar/em/
├── solar_luminosity.py   ← Phase 5: 태양 광도 (v1.3.0)
├── magnetic_dipole.py    ← Phase 2: 자기쌍극자장 (v1.1.0)
├── solar_wind.py         ← Phase 3: 태양풍 (v1.2.0)
├── magnetosphere.py      ← Phase 4: 자기권 (v1.2.0)
├── _constants.py         ← EPS_ZERO, EPS_GEOM
├── README.md             ← 이 문서 (EM 기술 참조)
└── light/                ← "빛이 있으라" 기록 (폴더 열면 README로 읽힘)
    └── README.md
```

```
태양 ●━━━━━━━━━━━━━━━━━━━━━━━━● 지구
     │                            │
     │  Phase 5: 태양 광도         │  Phase 2: 자기쌍극자장
     │  L → F(r) → T_eq, P_rad   │  B(r) ∝ 1/r³
     │                            │  자전축에 연동
     │  Phase 3: 태양풍            │
     │  P_sw, 입자, IMF           │
     │  전부 1/r²로 약해짐        │
     │                            │
     └───────────┬────────────────┘
                 │
                 ▼
          Phase 4: 자기권
          자기장 압력 vs 태양풍 동압
          균형점 = 마그네토포즈
```

---

## Phase 2 — 자기쌍극자장 (magnetic_dipole.py)

지구가 자기 내부에서 만들어내는 방어막.
지구 내부의 액체 철 핵이 대류하면서 거대한 자석(쌍극자)을 형성한다.

### 물리

| 특성 | 값 | 이유 |
|------|-----|------|
| 적도 자기장 | B₀ = 1.0 (정규화) | 표면에서 가장 약한 곳 |
| 극 자기장 | 2.0 B₀ | 극에서 자기력선이 수렴 |
| 거리 감쇠 | **1/r³** | 쌍극자(+극/-극 쌍)는 먼 곳에서 상쇄 → 단극자(1/r²)보다 빨리 약해짐 |
| 자기축 기울기 | 자전축에서 11.5° | 지구 내부 다이나모 비대칭 |

수식:

```
B(r) = B₀ · (R/r)³ · [3(m̂·r̂)r̂ − m̂]

m̂ : 자기축 단위벡터 (자전축에서 11.5° 기울어짐)
r̂ : 관측점 방향 단위벡터
R  : 행성 반지름
```

세차와의 연결: 세차로 자전축 ŝ(t)가 25,000년에 한 바퀴 돈다.
자기축은 자전축에 붙어 있으므로 자기장 전체가 세차와 함께 돈다.
코드에서는 매 호출마다 현재 `spin_axis`를 받아 자기축을 유도한다.

### 코드

```python
MagneticDipole(body_name="Earth", B_surface_equator=1.0, tilt_deg=11.5)

# B_surface_equator: 표면 적도 자기장 크기 [B₀ 단위]
#   주의: 자기쌍극자 모멘트(Am²)가 아님. 표면 자기장 스케일.
#   지구 기준: ~31 μT = 1.0 B₀

# 입력: spin_axis → tilt_deg 적용 → magnetic_axis
# 출력: B(r) = B₀(R/r)³ [3(m̂·r̂)r̂ - m̂]

.magnetic_axis(spin_axis)              → ndarray (단위벡터)
.B_field(point, origin, spin_axis, R)  → ndarray [B₀]
# → DipoleFieldPoint (B 벡터, 자기 위도, L-shell)
```

### 파라미터

| 파라미터 | 기본값 | 의미 |
|---------|-------|------|
| `tilt_deg` | 11.5 | 자기축-자전축 기울기 [°] |
| `B_surface_equator` | 1.0 | 표면 적도 자기장 [B₀] (모멘트 Am²가 아님) |

---

## Phase 3 — 태양풍 (solar_wind.py)

태양에서 쏟아지는 하전 입자(양성자, 전자)의 흐름.
**플라즈마만 다룬다.** 복사(photon)는 이 모듈의 범위가 아니다.

### 물리

태양은 끊임없이 하전 입자를 우주로 내뿜는다.
전부 **1/r²**로 약해진다 — 구면(면적 4πr²)으로 퍼지기 때문.

| 물리량 | 기호 | 1 AU 실측값 | 역할 |
|--------|------|-------------|------|
| 동압 | P_sw | ~2.0 nPa | 자기권 경계 결정 (Phase 4 핵심 입력) |
| 입자 플럭스 | Φ | ~3×10⁸ /cm²/s | 입자 수 밀도 × 속도 |
| 행성간 자기장(IMF) | B_sw | ~5 nT | 자기 재결합 에너지원 |

수성(0.39 AU)은 지구보다 ~6.6배 강한 태양풍을 받고,
해왕성(30 AU)은 ~1/900밖에 안 받는다.

### 코드

```python
SolarWind(P0=1.0, Phi0=1.0, v_sw=1.0, imf_B0=1.0)

# 출력 — 전부 1/r² 감쇠:
.dynamic_pressure(r)   → P₀/r²    [P₀]
.particle_flux(r)      → Φ₀/r²    [Φ₀]
.imf_strength(r)       → B₀/r²    [B_sw₀]
.state_at(pos, sun_pos) → SolarWindState

# radiation_pressure() 제거됨 (v1.3.1)
# 복사압은 solar_luminosity에서만 유도
```

### 파라미터

| 파라미터 | 기본값 | 의미 |
|---------|-------|------|
| `P0` | 1.0 | 1 AU 동압 [P₀] |
| `Phi0` | 1.0 | 1 AU 플럭스 [Φ₀] |
| `v_sw` | 1.0 | 태양풍 속도 [v₀] |
| `imf_B0` | 1.0 | 1 AU IMF [B_sw₀] |

---

## Phase 4 — 자기권 (magnetosphere.py)

자기장(Phase 2)과 태양풍(Phase 3)이 부딪혀서 생기는 방어 경계선.
한쪽은 밀어내고(자기장), 한쪽은 밀고 들어온다(태양풍).
두 힘이 균형을 이루는 지점이 자기권의 경계다.

### 물리

핵심 균형 (Chapman-Ferraro):

```
자기 압력 = 태양풍 동압
B²/(2μ₀) = P_sw

자기장 B ∝ 1/r³ → 자기 압력 B² ∝ 1/r⁶
태양풍 P_sw = 상수 (지구 위치에서 고정)

1/r⁶ = P_sw  →  r_mp = R_eq · (k·B₀²/P_sw)^(1/6)

그래서 마그네토포즈 공식에 1/6 지수가 나온다.
```

자기권이 만드는 구조:

```
    태양풍 →→→→→→→
                    ╲
      보우 쇼크 ──→   ╲  ← 초음속→아음속 전이 (1.3 × r_mp)
                       ╲
      마그네토포즈 ──→  │  ← 자기장 = 태양풍 균형점
                       │
                 ┌─────┤
        극 쿠스프 │     │  ← 자기장 열린 곳. 입자 침투 가능
                 └─────┤
                       │
                 지구 ●│
                       │
                       │  ← 자기꼬리: 밤쪽으로 길게 늘어남
                       │     (~15 × r_mp)
                       │
```

| 출력 | 지구 값 | 의미 |
|------|---------|------|
| 마그네토포즈 (r_mp) | 7.58 R_E | 앞쪽 방어선. 자기장=태양풍 균형점 |
| 보우 쇼크 (r_bs) | 9.86 R_E | 초음속 태양풍이 아음속으로 감속되는 충격파 |
| 자기꼬리 | ~114 R_E | 밤쪽으로 끌려나간 자기장 |
| 차폐율 | 0.78 | 78% 태양풍 차단 |
| 쿠스프 침투율 | 0~1 | 극 근처 열린 자기력선으로의 입자 유입 |
| 에너지 유입률 | 0~1 | 자기 재결합으로 자기권 내부로 들어오는 에너지 |

### 코드

```python
Magnetosphere(dipole, wind, magnetic_pressure_ratio=1.9e5)

# 입력: dipole.B_surface_equator + wind.P_sw
# 핵심 계산: r_mp = R · (k·B₀²/P_sw)^(1/6)  ← Chapman-Ferraro
#   B₀ = dipole.B_surface_equator (표면 적도 자기장, B₀ 단위)
#   P_sw = wind.dynamic_pressure (태양풍 동압, P₀ 단위)
# 복사압(P_rad)은 참여하지 않는다. 광자는 자기장과 상호작용하지 않으므로.

.evaluate(body_pos, R, spin_axis, sun_pos) → MagnetosphereState
```

---

## Phase 5 — 태양 광도 (solar_luminosity.py)

태양(주계열 항성)의 질량에서 광도를 유도하고,
거리에 따른 복사 조도·평형 온도·복사압을 계산한다.

### 물리

| 물리량 | 수식 | 의미 |
|--------|------|------|
| 광도 | L/L☉ = (M/M☉)^α | 질량-광도 관계 (주계열, α≈4.0, ~0.5–2 M☉ 근방 근사) |
| 복사 조도 | F(r) = L/(4πr²) | 역제곱 감쇠 (1 AU = 1361 W/m²) |
| 복사압 | P_rad = F/c | 광자 운동량 전달 |
| 평형 온도 | T_eq = [F(1-A)/(f·ε·σ)]^¼ | 흡수-방출 균형 |

### 코드

```python
SolarLuminosity(mass_solar=1.0, alpha=4.0, emissivity=1.0, redistribution=4.0)

# 내부 상태:
#   luminosity = M^α                       [L☉]
#   _F0 = luminosity                       [F☉] (1 AU 기준 = 1.0)
#   _F0_si = luminosity * 1361.0           [W/m²]

.irradiance(r)                → L/r²           [F☉]
.irradiance_si(r)             → L*1361/r²      [W/m²]
.radiation_pressure_si(r)     → F/c            [Pa]
.equilibrium_temperature(r, A, ε, f)  → [F(1-A)/(f·ε·σ)]^¼  [K]
.state_at(pos, star_pos)      → IrradianceState
.illuminate_system(positions) → Dict[name, IrradianceState]
```

### 파라미터

| 파라미터 | 기본값 | 의미 | 비고 |
|---------|-------|------|------|
| `alpha` | 4.0 | 질량-광도 지수 | 구간별 piecewise 확장 가능 |
| `emissivity` | 1.0 | 표면 방출율 ε | 대기 레이어 연결 포트 |
| `redistribution` | 4.0 | 열 재분배 f (4=전구면) | 조석 고정 행성은 1.0~2.0 |
| `luminosity_override` | None | L 직접 지정 | 비주계열 항성용 |

---

## 1/r³ vs 1/r² — 왜 감쇠 법칙이 다른가

| 모듈 | 감쇠 | 이유 |
|------|------|------|
| 자기장 (Phase 2) | 1/r³ | 쌍극자(+극/-극 쌍)는 먼 거리에서 서로 상쇄 → 단극자보다 빠르게 감소 |
| 태양풍 (Phase 3) | 1/r² | 태양에서 나온 에너지가 구면(4πr²)으로 균일 확산 → 면적당 세기 감소 |
| 광도 (Phase 5) | 1/r² | 동일한 구면 확산 원리 |

자기장(1/r³)은 가까운 데서만 강하고, 태양풍(1/r²)은 더 먼 데까지 살아남는다.
그래서 반드시 "자기장이 태양풍을 이기다가 지는 지점"이 생기고,
그것이 **마그네토포즈**다.

---

## 물리 분리: 복사 vs 플라즈마

두 현상은 같은 별(태양)에서 나오지만 물리적으로 독립이다.

| 구분 | 복사 (photons) | 플라즈마 (solar wind) |
|------|---------------|---------------------|
| 담당 모듈 | `solar_luminosity.py` | `solar_wind.py` |
| 원인 | 핵융합 → 전자기파 방출 | 코로나 가열 → 하전 입자 방출 |
| 감쇠 | F ∝ 1/r² | P_sw ∝ 1/r² |
| 1 AU 크기 | P_rad ≈ 4.54 μPa | P_sw ≈ 2 nPa |
| 비율 | ~2,270x 더 큼 | 1x |
| 자기장 상호작용 | 없음 (광자는 무전하) | 있음 (하전 입자) |
| 자기권 결정 | 참여 안 함 | **r_mp를 결정** |
| 환경 효과 | 온도, 기후, 광합성 | 자기폭풍, 오로라 |

따라서 `magnetosphere.py`는 `P_sw`만으로 마그네토포즈를 계산한다.
`P_rad`는 관여하지 않는다. 이것이 두 모듈을 분리한 물리적 근거다.

---

## 의존 방향

```
core/EvolutionEngine
  │
  │  pos(t), vel(t), spin_axis(t)  [읽기 전용]
  │
  ├─→ em/solar_luminosity   (mass → L → F → T → P_rad)
  ├─→ em/solar_wind          (pos  → P_sw, Φ, IMF)
  ├─→ em/magnetic_dipole     (spin_axis → B field)
  │        │                      │
  │        └──────────┬───────────┘
  │                   ▼
  │         em/magnetosphere  (B vs P_sw → r_mp, shielding)
  │
  └─→ cognitive/ring_attractor  (spin_axis → phase memory)
```

**규칙:**
- `core/*`는 `em/*`를 import하지 않는다
- `em/*`는 `core/`를 읽기만 한다 (관측자 모드)
- `em/*`과 `cognitive/*`는 서로 참조하지 않는다
- 복사(`solar_luminosity`)와 플라즈마(`solar_wind`)는 서로 import하지 않는다

---

## 모듈별 입출력 요약

| 모듈 | 입력 (core에서 읽음) | 출력 | 상태 벡터 |
|------|---------------------|------|----------|
| `solar_luminosity` | `Body.mass`, `Body.pos` | L, F(r), T_eq, P_rad | `IrradianceState` |
| `magnetic_dipole` | `Body.spin_axis`, `Body.pos` | B(x,t) | `DipoleFieldPoint` |
| `solar_wind` | `Body.pos` (태양+행성) | P_sw, Φ, IMF | `SolarWindState` |
| `magnetosphere` | dipole + wind 출력 | r_mp, shielding | `MagnetosphereState` |

---

## 지배 방정식

| 물리량 | 수식 | 감쇠 | 모듈 |
|--------|------|------|------|
| 광도 | L = M^α | — | solar_luminosity |
| 복사 조도 | F = L/(4πr²) | 1/r² | solar_luminosity |
| 복사압 | P_rad = F/c | 1/r² | solar_luminosity |
| 평형 온도 | T = [F(1-A)/(f·ε·σ)]^¼ | r^(-1/2) | solar_luminosity |
| 쌍극자장 | B = B₀(R/r)³[3(m̂·r̂)r̂ - m̂] | 1/r³ | magnetic_dipole |
| 태양풍 동압 | P_sw = P₀(r₀/r)² | 1/r² | solar_wind |
| 입자 플럭스 | Φ = Φ₀(r₀/r)² | 1/r² | solar_wind |
| 행성간 자기장 | B_sw = B₀_sw(r₀/r)² | 1/r² | solar_wind |
| 마그네토포즈 | r_mp = R(k·B₀²/P_sw)^(1/6) | — | magnetosphere |

---

## 단위계

| 물리량 | 정규화 단위 | SI 참값 |
|--------|-----------|--------|
| 광도 L | L☉ = 1.0 | 3.828 × 10²⁶ W |
| 조도 F | F☉ = 1.0 (1 AU) | 1,361 W/m² |
| 동압 P_sw | P₀ = 1.0 (1 AU) | ~2 nPa |

> 정규화 단위는 내부 계산용이며, `irradiance_si()` 등 `_si` 접미 메서드에서만 SI 단위를 반환한다.
| 자기장 B | B₀ = 1.0 (표면 적도) | ~31,000 nT (지구) |
| 플럭스 Φ | Φ₀ = 1.0 (1 AU) | ~3 × 10⁸ cm⁻²s⁻¹ |
| 거리 | AU | 1.496 × 10¹¹ m |
| 온도 | K (정규화 안 함) | — |
| 복사압 | Pa (정규화 안 함) | 4.54 × 10⁻⁶ Pa (1 AU) |

---

## 검증 결과

### v1.3.0 + v1.3.1 (광도 + 복사-플라즈마 분리)

| 항목 | 결과 | 비고 |
|------|------|------|
| L(1.0 M☉) = 1.0 L☉ | PASS | 오차 0.00 |
| F ∝ 1/r² | PASS | 8행성 0.000% |
| T_eq(Earth, A=0.306) | 254 K | NASA 255 K, 0.4% |
| P_rad = F/c 일관성 | PASS | 4.54e-6 Pa at 1 AU |
| core dE/E | 4.49×10⁻¹⁰ | 관측자 모드 확인 |

### v1.2.0 (자기장 + 태양풍 + 자기권)

| 항목 | 결과 |
|------|------|
| B 표면 (적도=1.0, 극=2.0) | PASS, 0.00% |
| B ∝ 1/r³ | PASS, 0.00% |
| P_sw ∝ 1/r² | PASS, 5행성 0.00% |
| r_mp = 7.58 R_E | PASS |
| shielding = 0.78 | PASS |
| 세차-자기권 연동 | PASS |
| core dE/E | 8.20×10⁻¹¹ |

**기어 분리의 수치적 의미:**
em/ 레이어(광도, 자기장, 태양풍, 자기권)를 전부 얹어도
core/의 에너지 보존은 dE/E ~ 10⁻¹⁰ 수준을 유지한다.
관측자 레이어를 아무리 쌓아도 물리 코어의 무결성은 훼손되지 않는다.

---

*v1.3.1 · 2026-02-25 · PHAM Signed · GNJz (Qquarts)*
