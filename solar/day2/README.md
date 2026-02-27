# day2/ — 둘째날: 궁창 / Firmament (Atmosphere Layer)

**창세기 구절**  
> *“하나님이 궁창을 만드사 궁창 아래의 물과 궁창 위의 물로 나뉘게 하시니라”*

**엔진 해석**  
둘째날은 **우물에 고인 물(SurfaceOcean)** 위에 태양 복사가 가해져  
**액체 바다와 기체 대기**가 분리되고, 온실 효과와 열적 관성이 생기는 단계다.  
`solar/day2/atmosphere/` (원래 `solar/atmosphere/`) 레이어가 이 역할을 담당한다.

`day2/` 폴더는 이 대기 레이어의 핵심 기어를  
**둘째날 관점에서 묶어 보여주는 집합 패키지(re‑export index)** 다.

> ⚠️ **재현성 / Reproducibility**  
> - `day2` 는 **re‑export 전용 패키지**이며, 실제 구현은 `solar/day2/atmosphere/*.py` 에 있다.  
> - 예제 코드의 `from solar.day2 import AtmosphereColumn` 은  
>   리포지토리를 **패키지 구조(`solar/` 루트 유지)** 로 설치했을 때 기준이다.  
> - 파일만 평면으로 복사해서 쓸 경우, `solar.day2.*` import 가 동작하지 않을 수 있다.

---

## 1. 포함되는 모듈 / 기어

`day2/__init__.py` 에서 재export 되는 이름:

- `AtmosphereColumn` — 0D 대기 컬럼 (온실 + 열적 관성 + 대기압 + 물 상태)
- `AtmosphereState` — 스냅샷 (T_surface, P_surface, water_phase 등)
- `AtmosphereComposition` — CO₂ / H₂O / O₂ / CH₄ / column_mass
- `GreenhouseParams` — 온실 파라미터 구조체

실제 구현 파일:

- `solar/atmosphere/greenhouse.py`
- `solar/atmosphere/column.py`
- `solar/atmosphere/_constants.py`

---

## 2. 둘째날 동역학 개요

```text
em/SolarLuminosity   →  F_solar(r) [W/m²]
surface/SurfaceSchema → A_eff (유효 알베도)
core/EvolutionEngine → 행성 질량·반지름, 중력가속도
          │
          ▼
atmosphere/AtmosphereColumn
  → T_surface, P_surface, water_phase, habitable
  → surface_heat_flux (Phase 6b: 수순환/해양 연동 포트)
```

- 광도 레이어(`day1`)가 만든 \(F(r)\) 와 표면 레이어의 `effective_albedo()` 를 받아,  
  대기 컬럼이 **온도·압력·물 상태**를 결정한다.
- 이 결과가 셋째날 `surface/`, `biosphere/` 의 **환경 입력(env dict)** 으로 들어간다.

---

## 3. 사용 예시

```python
from solar.day1 import SolarLuminosity
from solar.day2 import AtmosphereColumn, AtmosphereComposition

sun = SolarLuminosity(mass_solar=1.0)
atm = AtmosphereColumn(
    body_name="Earth",
    T_surface_init=288.0,
    composition=AtmosphereComposition(CO2=400e-6, O2=0.21),
)

dt_yr = 0.01
for _ in range(100):
    F = sun.irradiance_si(1.0)  # 1 AU
    atm.step(F_solar_si=F, dt_yr=dt_yr)

state = atm.state(F)
print(state.T_surface, state.P_surface, state.water_phase)
```

---

## 4. 참고 문서 및 블록체인 서명

- `solar/atmosphere/README.md` — 궁창/대기권 레이어 상세 설계.
- `docs/CREATION_DAYS_AND_PHASES.md` — 둘째날 ↔ Phase 6a/6b 정리.
- 블록체인 체인: `blockchain/pham_chain_em_layer_demo.json`,  
  `blockchain/pham_chain_LAYER6_verification.json` (대기 레이어 검증 로그, naming 참고).

```text
PHAM_CHAIN:
  - em_layer / atmosphere 관련 체인들 — 궁창/대기권 수치 검증 (A_HIGH)
```

*v1.4.x · PHAM Signed · GNJz (Qquarts) + Claude 5.1*

