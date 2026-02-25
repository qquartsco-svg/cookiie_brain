# solar/em/ — 전자기·복사 환경 레이어 (v1.3.1)

core/ 위에 얹는 관측자 레이어. 궤도·스핀을 읽기만 하고 수정하지 않는다.

---

## 이 레이어가 해결하는 문제

v1.2.0까지의 태양은 **중력(점질량) + 태양풍(상수 모델)**만 있었다.
광도(L), 복사 조도(F), 온도(T) 출력이 없었다.
즉 "어둡지만 바람은 부는 별" — 논리적으로 불완전한 상태.

v1.3.0에서 `solar_luminosity.py`를 추가하여 이 공백을 메웠다.
질량(M)으로부터 광도(L)를 유도하고, 거리에 따른 조도·온도·복사압을
계산하는 출력 레이어를 완성했다.

v1.3.1에서 복사(photon)와 플라즈마(solar wind)의 **물리적 독립성**을 확보했다.
`solar_wind.py`에서 `radiation_ratio` 하드코딩을 제거하고,
복사압을 오직 `solar_luminosity.py`에서만 `P_rad = F/c`로 유도하도록 정리했다.

---

## 모듈 구조

```
solar/em/
├── solar_luminosity.py   ← Phase 5 (v1.3.0)
├── magnetic_dipole.py    ← Phase 2 (v1.1.0)
├── solar_wind.py         ← Phase 3 (v1.2.0)
├── magnetosphere.py      ← Phase 4 (v1.2.0)
├── _constants.py         ← EPS_ZERO, EPS_GEOM
└── README.md
```

### 모듈별 입출력

| 모듈 | 입력 (core에서 읽음) | 출력 | 상태 벡터 |
|------|---------------------|------|----------|
| `solar_luminosity` | `Body.mass`, `Body.pos` | L, F(r), T_eq, P_rad | `IrradianceState` |
| `magnetic_dipole` | `Body.spin_axis`, `Body.pos` | B(x,t) | `DipoleFieldPoint` |
| `solar_wind` | `Body.pos` (태양+행성) | P_sw, Φ, IMF | `SolarWindState` |
| `magnetosphere` | dipole + wind 출력 | r_mp, shielding | `MagnetosphereState` |

---

## 코드 상태공간

### SolarLuminosity

```python
SolarLuminosity(mass_solar=1.0, alpha=4.0, emissivity=1.0, redistribution=4.0)

# 내부 상태:
#   luminosity = M^α                       [L☉]
#   _F0 = luminosity                       [F☉] (1 AU 기준 = 1.0)
#   _F0_si = luminosity * 1361.0           [W/m²]

# 메서드 → 출력:
.irradiance(r)                → L/r²           [F☉]
.irradiance_si(r)             → L*1361/r²      [W/m²]
.radiation_pressure_si(r)     → F/c            [Pa]
.equilibrium_temperature(r, A, ε, f)  → [F(1-A)/(f·ε·σ)]^¼  [K]
.state_at(pos, star_pos)      → IrradianceState
.illuminate_system(positions) → Dict[name, IrradianceState]
```

### SolarWind (플라즈마 전용)

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

### MagneticDipole

```python
MagneticDipole(body_name="Earth", B_surface_equator=1.0, tilt_deg=11.5)

# B_surface_equator: 표면 적도 자기장 크기 [B₀ 단위]
#   주의: 자기쌍극자 모멘트(Am²)가 아님. 표면 자기장 스케일.
#   지구 기준: ~31 μT = 1.0 B₀
# 입력: spin_axis → tilt_deg 적용 → magnetic_axis
# 출력: B(r) = B₀(R/r)³ [3(m̂·r̂)r̂ - m̂]
.B_field(point, origin, spin_axis, R)  → ndarray [B₀]
.magnetic_axis(spin_axis)              → ndarray (단위벡터)
```

### Magnetosphere

```python
Magnetosphere(dipole, wind, magnetic_pressure_ratio=1.9e5)

# 입력: dipole.B_surface_equator + wind.P_sw
# 핵심 계산: r_mp = R · (k·B₀²/P_sw)^(1/6)  ← Chapman-Ferraro
#   B₀ = dipole.B_surface_equator (표면 적도 자기장, B₀ 단위)
#   P_sw = wind.dynamic_pressure (태양풍 동압, P₀ 단위)
# 복사압(P_rad)은 참여하지 않는다.
# 광자는 자기장과 상호작용하지 않으므로.
.evaluate(body_pos, R, spin_axis, sun_pos) → MagnetosphereState
```

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
`P_rad`는 관여하지 않는다. 이것이 두 모듈을 분리한 근거다.

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
| 자기장 B | B₀ = 1.0 (표면 적도) | ~31,000 nT (지구) |
| 플럭스 Φ | Φ₀ = 1.0 (1 AU) | ~3 × 10⁸ cm⁻²s⁻¹ |
| 거리 | AU | 1.496 × 10¹¹ m |
| 온도 | K (정규화 안 함) | — |
| 복사압 | Pa (정규화 안 함) | 4.54 × 10⁻⁶ Pa (1 AU) |

---

## 파라미터

### solar_luminosity.py

| 파라미터 | 기본값 | 의미 | CONFIG 분리 |
|---------|-------|------|------------|
| `alpha` | 4.0 | 질량-광도 지수 | 구간별 piecewise 확장 가능 |
| `emissivity` | 1.0 | 표면 방출율 ε | 대기 레이어 연결 포트 |
| `redistribution` | 4.0 | 열 재분배 f (4=전구면) | 조석 고정 행성은 1.0~2.0 |
| `luminosity_override` | None | L 직접 지정 | 비주계열 항성용 |

### solar_wind.py

| 파라미터 | 기본값 | 의미 |
|---------|-------|------|
| `P0` | 1.0 | 1 AU 동압 [P₀] |
| `Phi0` | 1.0 | 1 AU 플럭스 [Φ₀] |
| `v_sw` | 1.0 | 태양풍 속도 [v₀] |
| `imf_B0` | 1.0 | 1 AU IMF [B_sw₀] |

### magnetic_dipole.py

| 파라미터 | 기본값 | 의미 |
|---------|-------|------|
| `tilt_deg` | 11.5 | 자기축-자전축 기울기 [°] |
| `B_surface_equator` | 1.0 | 표면 적도 자기장 [B₀] (모멘트 Am²가 아님) |

---

## 검증 결과

### v1.3.0 + v1.3.1

| 항목 | 결과 | 비고 |
|------|------|------|
| L(1.0 M☉) = 1.0 L☉ | PASS | 오차 0.00 |
| F ∝ 1/r² | PASS | 8행성 0.000% |
| T_eq(Earth, A=0.306) | 254 K | NASA 255 K, 0.4% |
| P_rad = F/c 일관성 | PASS | 4.54e-6 Pa at 1 AU |
| core dE/E | 4.49×10⁻¹⁰ | 관측자 모드 확인 |

### v1.2.0

| 항목 | 결과 |
|------|------|
| B 표면 (적도=1.0, 극=2.0) | PASS, 0.00% |
| B ∝ 1/r³ | PASS, 0.00% |
| P_sw ∝ 1/r² | PASS, 5행성 0.00% |
| r_mp = 7.58 R_E | PASS |
| shielding = 0.78 | PASS |
| 세차-자기권 연동 | PASS |
| core dE/E | 8.20×10⁻¹¹ |

---

## "빛이 있으라"의 엔지니어링 의미

v1.3.0 이전 시스템 상태:

```
태양 = { mass: 1.0, pos: [0,0,0], gravity: ON, luminosity: MISSING }
→ 출력 채널: F(r) = ?, T(r) = ?, P_rad(r) = ?  ← 전부 undefined
→ solar_wind.radiation_pressure = 0.002 * P_sw   ← 원인(L)이 아닌 결과(P_sw)에 종속
```

v1.3.1 이후:

```
태양 = { mass: 1.0, pos: [0,0,0], gravity: ON, luminosity: M^4.0 = 1.0 L☉ }
→ 출력 채널:
   F(r) = 1.0/r²  [F☉]  = 1361/r²  [W/m²]      ← L에서 유도
   T(r) = [F(1-A)/(f·ε·σ)]^¼                      ← F에서 유도
   P_rad(r) = F/c                                  ← F에서 유도 (solar_wind와 독립)
```

빠져 있던 출력 레이어가 채워졌고,
하드코딩 비율이 물리 유도 체인으로 교체되었다.

---

*v1.3.1 · 2026-02-25 · PHAM Signed · GNJz (Qquarts)*
