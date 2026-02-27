# day1/ — 첫째날: 빛이 있으라 (Solar EM Layer)

**창세기 구절**  
> *“하나님이 이르시되 빛이 있으라 하시니 빛이 있었고”*

**엔진 해석**  
첫째날은 **태양 광도·복사·전자기 환경**이 켜지는 단계다.  
`core/`(중력/세차)가 만들어 놓은 궤도 위에, `em/` 레이어가  
빛과 자기장, 태양풍, 자기권을 **상태공간 모드(state-space mode)** 로 얹는다.

`day1/` 폴더는 실제 코드를 다시 구현하지 않고,  
`solar/day1/em/` (원래 `solar/em/`) 의 핵심 기어들을  
**첫째날 관점에서 한눈에 모아 보여주는 집합 패키지(re‑export index)** 다.

> ⚠️ **재현성 / Reproducibility**  
> - `day1` 은 **re‑export 전용 패키지**이며, 실제 구현은 `solar/day1/em/*.py` 에 있다.  
> - 예제 코드의 `from solar.day1 import SolarLuminosity` 는  
>   이 리포지토리를 **파이썬 패키지(`solar/` 루트 유지)** 로 설치/실행하는 구성을 전제로 한다.  
> - 업로드된 평면 파일만 복사해서 쓸 경우, `solar.day1.*` import 가 깨질 수 있다.

---

## 1. 포함되는 모듈 / 기어

`day1/__init__.py` 에서 다음 클래스를 재export 한다:

- `SolarLuminosity`, `IrradianceState`  
  - 태양 질량 → 광도 \(L\) → 복사 조도 \(F(r)\) → 평형 온도 \(T_{\text{eq}}\), 복사압 \(P_{\text{rad}}\).
- `MagneticDipole`, `DipoleFieldPoint`  
  - 자전축에 붙어 있는 자기쌍극자장 \(B(r) ∝ 1/r^3\).
- `SolarWind`, `SolarWindState`  
  - 태양풍 동압·입자 플럭스·IMF, 모두 \(1/r^2\) 감쇠.
- `Magnetosphere`, `MagnetosphereState`  
  - 자기장 vs 태양풍 동압 균형 → 마그네토포즈 \(r_{\text{mp}}\), 차폐율.

실제 구현 파일은 여기(day1/em) 아래에 있다:

- `solar/day1/em/solar_luminosity.py`
- `solar/day1/em/magnetic_dipole.py`
- `solar/day1/em/solar_wind.py`
- `solar/day1/em/magnetosphere.py`

---

## 2. 첫째날 동역학 개요

```text
data/ (행성 질량·반지름) ──► core/EvolutionEngine
                             │
                             ├─► day1/em/SolarLuminosity   — L=M^α, F(r), T_eq, P_rad
                             ├─► day1/em/MagneticDipole    — B ∝ 1/r³
                             ├─► day1/em/SolarWind         — P_sw, Φ, IMF (1/r²)
                             └─► day1/em/Magnetosphere     — r_mp, shielding

Magnetosphere 의 `shielding` 값은 \([0,1]\) 범위의 **상대 차폐 지표(surrogate)** 로,  
실제 방사선량이 아니라 “태양풍 동압에 비해 자기권이 제공하는 보호 강도 스케일”을 의미한다.
```

- `core/` 의 궤도와 자전은 **빛·자기장 없이도** 돌아갈 수 있다.  
- 첫째날에서 `em/` 레이어를 켜면,
  - 행성마다 **얼마나 받는 빛이 다른지** (거리에 따른 조도),
  - **어느 정도의 자기 방패를 갖는지** (마그네토포즈, 차폐율),
  - **평형 온도**가 얼마인지가 계산된다.

이 출력은 둘째날 `atmosphere/`(궁창), 셋째날 `surface/`, 이후 레이어들의  
**환경 입력 포트** 역할을 한다.

---

## 3. 사용 예시

### 3.1 태양 광도 + 지구 평형 온도

```python
from solar.day1 import SolarLuminosity

sun = SolarLuminosity(mass_solar=1.0)  # 1 M☉

F_earth = sun.irradiance_si(r=1.0)      # 1 AU
T_eq = sun.equilibrium_temperature(r=1.0, A=0.306, emissivity=1.0, redistribution=4.0)

print(F_earth)  # ≈ 1361 W/m²
print(T_eq)     # ≈ 254 K (대기 없는 평형 온도)
```

### 3.2 자기권 크기 평가

```python
from solar.day1 import MagneticDipole, SolarWind, Magnetosphere

dipole = MagneticDipole(body_name="Earth", B_surface_equator=1.0, tilt_deg=11.5)
wind = SolarWind(P0=1.0)
ms = Magnetosphere(dipole, wind)

state = ms.evaluate(body_pos=[1, 0, 0], R=1.0, spin_axis=[0, 0, 1], sun_pos=[0, 0, 0])
print(state.r_mp)        # ≈ 7.6 R_E
print(state.shielding)   # ≈ 0.78
```

---

## 4. 참고 문서 및 블록체인 서명

- `solar/em/README.md` — EM 레이어 전체 설계·물리·검증.
- `docs/CREATION_DAYS_AND_PHASES.md` — 첫째날 ↔ Phase 5 매핑.
- 블록체인 체인: `blockchain/pham_chain_em_layer_demo.json`,  
  `blockchain/pham_chain_solar_luminosity.json` (EM/빛 레이어 검증 로그).

```text
PHAM_CHAIN:
  - pham_chain_em_layer_demo.json      — EM 레이어 통합 검증 (A_HIGH)
  - pham_chain_solar_system_data.json  — 태양계 상수 세트 (A_HIGH)
```

*v1.3.x · PHAM Signed · GNJz (Qquarts) + Claude 5.1*

