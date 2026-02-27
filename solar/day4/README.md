# day4/ — 넷째날 순환 레이어 집합 (core gravity · nitrogen · cycles · gravity_tides)

**역할**: `day4/core/ + day4/data/` 가 만든 **태양계 중력필드** 위에,  
셋째날까지 완성된 `day3/surface/` + `day2/atmosphere/` + `day3/biosphere/` + `day3/fire/` 를 올리고,  
그 위에서 동작하는 넷째날 3개 순환 레이어를 **한 폴더에서 한눈에** 보이게 하는 집합 패키지.

- **중력 필드 (`core/ + data/`)**: EvolutionEngine, Body3D, PlanetData, build_solar_system — 태양계 N-body / 지구·달 중력장 / 세차·조석  
- **순환 1 (`nitrogen/`)**: 질소 고정·탈질·낙엽 분해 → 토양 질소 항상성  
- **순환 2 (`cycles/`)**: Milankovitch 3주기 → 일사량·계절성 진폭 → 빙하기 드라이버  
- **순환 3 (`gravity_tides/`)**: 달·태양 조석 → 해양 혼합·영양염 → 식물플랑크톤 → 탄소 펌프  
- **연결 (`gaia_loop_connector.py`)**: 산불 CO₂, 식생 알베도, 세차 obliquity 루프와의 결합 지점

`day4/` 자체는 **새 구현을 넣지 않고**, core/data + 아래 세 패키지와 Gaia 루프를  
**import/export 로만 모아두는 “지도/인덱스(re‑export index)” 역할**을 한다.

> ⚠️ **재현성 / Reproducibility**  
> - `day4` 는 **re‑export 전용 패키지**이며, 실제 구현은  
>   `solar/day4/core/*`, `solar/day4/data/*`, `solar/day4/nitrogen/*`,  
>   `solar/day4/cycles/*`, `solar/day4/gravity_tides/*` 에 있다.  
> - 예제 코드의 `from solar.day4 import EvolutionEngine` 등은  
>   리포지토리를 **파이썬 패키지(`solar/` 루트 보존)** 로 설치/실행하는 구성을 전제로 한다.  
> - 평면 파일 업로드/복사만 사용할 경우, `solar.day4.*` import 와  
>   넷째날 순환 데모 스크립트의 경로가 깨질 수 있다.

---

## 1. 넷째날 큰 그림 (중력 필드 + 3개 순환)

중력 필드 및 셋째날(Phase 7)까지의 상태:

```text
surface/    — 땅/바다 분리, effective_albedo (land_fraction)
atmosphere/ — 온실·수순환 (T_surface, CO2/O2/H2O, water_phase)
biosphere/  — 토양 형성 ODE + 식물 생애주기 + Gaia Attractor
fire/       — 전지구 산불 엔진 (O2 attractor)
gaia_loop_connector.py — Loop A/B/C (산불 CO2, 알베도, obliquity)
```

넷째날(Phase 7g/Day 4)은 여기에 **장주기·심해·질소** 루프를 더해,

```text
세차(만년) + 질소(수천년) + 조석-해양(수십~수백년)
→ 짧은 주기(yr) 항상성 위에 장주기 파동을 겹친다.
```

그 결과, 다음과 같은 **“자율 조절 행성 OS”** 구조가 된다:

```text
[Milankovitch cycles]  →  [seasonal amplitude, glacial trigger]
      │
      ▼
[fire/ + Gaialoop]  ↔  [biosphere/ + nitrogen/]
      ▲                     │
      │                     ▼
[gravity_tides/]   →  [ocean nutrients → CO2 sink]
```

이 그림에서:

- `nitrogen/` 은 **생물권 GPP에 들어가는 질소 게이트**를 만든다.
- `cycles/` 은 **세차·경사·이심률**로 건기·일사량의 장주기 변조를 만든다.
- `gravity_tides/` 는 **조석 혼합 → 해양 탄소 격리**로 CO₂ 장주기 음의 피드백을 만든다.

---

## 2. 구성 모듈 요약

### 2.1 순환 1 — 질소 루프 (`nitrogen/`)

**핵심 아이디어**:  
대기 질소 \(N_2\) 를 pioneer 생물과 번개가 고정하고,  
식물·사체·탈질을 거쳐 다시 \(N_2\) 로 돌아가는 루프를  
**토양 질소 \(N_{\text{soil}}\)** 하나의 상태 변수로 모델링.

- `fixation.py` — `NitrogenFixation`
  - \(N_{\text{fix}} = K_{\text{fix}} B_{\text{pioneer}} f_{O_2}(O_2) f_T(T) f_W(W)\)
  - 낮은 O₂, 적당한 온도·수분에서 최대 질소 고정.
- `cycle.py` — `NitrogenCycle`
  - \(dN_{\text{soil}}/dt = N_{\text{fix}} + N_{\text{decomp}} - N_{\text{uptake}} - N_{\text{denitrify}} - N_{\text{leach}}\)
  - `N_limitation = N_soil / (N_soil + N_soil_ref)` 로 **GPP 게이트**를 계산.
- `nitrogen_demo.py`
  - V1~V4 ALL PASS: 질소고정 환경 의존성, 항상성, 혐기성 탈질, 150yr 시계열 검증.

`day4/__init__.py` 에서 재export 되는 이름:

- `NitrogenFixation`, `FixationResult`, `make_fixation_engine`
- `NitrogenCycle`, `NitrogenState`, `make_nitrogen_cycle`

### 2.2 순환 2 — Milankovitch 장주기 드라이버 (`cycles/`)

**핵심 아이디어**:  
세차(26 kyr), 경사(41 kyr), 이심률(100/413 kyr) 3주기를  
합성해서 **고위도 여름 일사량**과 **계절성 진폭**을 만들고,  
이를 통해 **빙하기-간빙기**와 **건기 강도**를 장주기적으로 변조.

- `milankovitch.py`
  - `MilankovitchCycle`, `MilankovitchState`
  - `eccentricity(t)`, `obliquity(t)`, `precession_index(t)`
  - `insolation_summer_solstice(t, φ)` — Berger 1978 하지 일사량 공식
  - `insolation_scale(t, φ)` — 현재( t=0 ) 대비 상대 일사량 스케일
  - `is_glacial(t)` — 65°N 하지 일사량 임계값으로 빙하기 판단
- `insolation.py`
  - `insolation_at(t, φ)` — 위도별 연평균 일사량 근사 (ψ 미포함)
  - `MilankovitchDriver` / `DriverOutput` — GaiaLoopConnector/FireEngine 연결용
  - `make_fire_env_milank(connector, base_env, t_yr, ...)`
    - obliquity, F0 보정, is_glacial 정보를 가진 `FireEnvSnapshot` 생성 헬퍼.
- `milankovitch_demo.py`
  - V1~V4 ALL PASS: 주기 범위, LGM vs 현재, Loop C 연결, 200 kyr 시계열 검증.

> **Insolation 사용 규칙 / Usage rules**  
> - 빙하기 판정(`is_glacial`) 은 **65°N 하지 일사량** `insolation_summer_solstice` (세차각 ψ 포함) 을 기준으로 한다.  
> - 위도 밴드별 에너지 입력/시각화는 `insolation_grid` (연평균 근사, ψ 미포함)를 사용한다.  
> - Loop C (장주기 건기/산불 변조) 에서는 직접적인 Q 값 대신  
>   `obliquity_scale` / `season_amplitude` 와 같은 **무차원 스케일 포트**를 기본으로 사용한다.

`day4/__init__.py` 에서 재export 되는 이름:

- `MilankovitchCycle`, `MilankovitchState`
- `make_earth_cycle`, `make_custom_cycle`
- `insolation_at`, `insolation_grid`
- `MilankovitchDriver`, `DriverOutput`, `make_earth_driver`

### 2.3 순환 3 — 중력-조석 주기 (`gravity_tides/`)

**핵심 아이디어**:  
달·태양 조석력이 해양을 섞어 심층 영양염을 끌어올리고,  
그 결과 식물플랑크톤이 성장하여 **탄소를 심해로 격리**하는  
“생물학적 탄소 펌프”를 모델링.

- `tidal_mixing.py`
  - `TidalField`, `TidalState`, `make_tidal_field`
  - \(F_{\text{tidal}}(t) = F_{\text{moon}}(t) + F_{\text{sun}}(t)\)
  - `mixing_depth = K_mix × F_total` → `nutrient_upwelling_uM` 계산.
- `ocean_nutrients.py`
  - `OceanNutrients`, `OceanState`, `make_ocean_nutrients`
  - \(C_{\text{surface}}\) (표층 영양염) + phyto biomass 동역학
  - `CO2_sink_ppm` 으로 대기 CO₂ 격리량 [ppm/yr] 출력.
- `gravity_tides_demo.py`
  - 사리/조금, C_surface ODE, 닫힌 루프, 1 yr 적분 등 V1~V4 ALL PASS.

`day4/__init__.py` 에서 재export 되는 이름:

- `TidalField`, `TidalState`, `make_tidal_field`
- `OceanNutrients`, `OceanState`, `make_ocean_nutrients`

### 2.4 보조 순환 — SeasonEngine (계절 리듬 드라이버)

계절성은 이미 fire_risk 의 dry_season_modifier 등에서 암묵적으로 쓰이고 있지만,  
넷째날에서는 이를 **독립 엔진(SeasonEngine)** 으로 분리해 재사용 가능하게 만든다.

- `season_engine.py`
  - `SeasonEngine`, `SeasonState`
  - 상태:
    - `t_in_year ∈ [0,1)` 또는 `phase ∈ [0,2π)` — 봄·여름·가을·겨울 위상
  - 위도별 출력:
    - `delta_T` — 계절 온도 편차 [K]
    - `dry_season_modifier` — 건기 강도 계수 (1 = 기준, >1 = 더 건조)
  - 입력:
    - 향후 Milankovitch 의 `obliquity_scale` / `season_amplitude` 를
      amplitude 파라미터로 받아, 장주기적으로 계절 강도를 조절할 수 있다.

SeasonEngine 결과는 Day2~Day3 레이어(Atmosphere/Biosphere/Fire)가  
**“지금이 연중 어느 시점인지, 계절 진폭이 얼마나 큰지”** 를 공유하는 공통 리듬 포트로 쓰인다.

---

## 3. Gaia 루프와의 연결

넷째날 순환 1~3은 **셋째날 Gaia 루프(Loop A/B/C)** 와 다음처럼 만난다:

```text
[NitrogenCycle]        →  N_limitation  ┐
[BiosphereColumn] GPP  ────────────────┘  → Loop B (알베도) / O2·CO2 피드백

[MilankovitchCycle]    →  obliquity_deg(t) ──► GaiaLoopConnector.obliquity_scale
                                           └─► FireEnvSnapshot.F0 (이심률 보정)

[TidalField + OceanNutrients] → CO2_sink_ppm
                             └→ atmosphere.composition.CO2 (미래 연결)
```

Gaia 루프 자체 구현은:

- `solar/bridge/gaia_loop_connector.py` — Loop A/B/C (셋째날)
- `docs/DAY4_DESIGN.md` — `day4_loop_connector.py` 설계 (넷째날 확장 안)

---

## 4. 사용 예시

### 4.1 질소 + biosphere 연동 (개념 스케치)

```python
from solar.biosphere import BiosphereColumn
from solar.day4 import NitrogenCycle, make_nitrogen_cycle

bio = BiosphereColumn(body_name="Earth", land_fraction=0.29)
nitro = make_nitrogen_cycle(N_soil_init=2.0)

for yr in range(100):
    env = {...}  # atmosphere/surface에서 가져온 env
    fb = bio.step(env, dt_yr=1.0)

    state_N = nitro.step(
        dt=1.0,
        B_pioneer=bio.pioneer_biomass,
        GPP_rate=fb["GPP"],
        O2_frac=env["O2"],
        T_K=env["T_surface"],
        W_moisture=env.get("soil_moisture", 0.5),
    )

    # N_limitation을 다음 스텝 biosphere GPP 게이트에 주입 (미래 연동 지점)
    N_lim = state_N.N_limitation
```

### 4.2 Milankovitch → FireEnvSnapshot (Loop C, 장주기 건기 변조)

```python
from solar.day4 import (
    MilankovitchCycle, MilankovitchDriver,
    make_earth_cycle, make_fire_env_milank,
)
from solar.gaia_loop_connector import make_connector
from solar.fire import FireEnvSnapshot, FireEngine

atm, connector = make_connector(T_init=288.0, CO2_ppm=400.0)
engine = FireEngine()
cycle = make_earth_cycle()

base_env = FireEnvSnapshot(O2_frac=0.21, CO2_ppm=400.0, time_yr=0.5)

for kyr in range(-100_000, 100_001, 1_000):
    env_t, out = make_fire_env_milank(
        connector=connector,
        base_env=base_env,
        t_yr=float(kyr),
        cycle=cycle,
    )
    results = engine.predict(env_t)
    gfi = engine.global_fire_index(results)
    # gfi 및 out.obliquity_scale, out.is_glacial 으로 장주기 패턴 분석
```

### 4.3 조석-해양 탄소 펌프 단독 테스트

```python
from solar.day4 import TidalField, OceanNutrients

tf = TidalField()
oc = OceanNutrients()

for yr in range(100):
    ts = tf.compute(t_yr=float(yr))
    os = oc.step(dt=1.0, upwelling_uM=ts.upwelling_uM)
    # os.CO2_sink_ppm 을 누적해서 대기 CO2 장주기 sink 추정
```

---

## 5. 버전 및 블록체인 서명

- 넷째날 순환 레이어 최초 통합: `solar` v2.5.0 ~ v2.7.0  
  - v2.5.0 — `cycles/` (Milankovitch)  
  - v2.6.0 — `nitrogen/` (질소 순환)  
  - v2.7.0 — `gravity_tides/` (조석-해양 탄소 펌프)  
- 상세 로그: `docs/VERSION_LOG.md` 의 v2.5.0~v2.7.0 항목 참고.
- 레이어 설계 체인: `blockchain/pham_chain_LAYERS.json`

```text
PHAM_CHAIN:
  pham_chain_LAYERS.json — solar 개념 레이어 정의 (A_HIGH)
  label = "A_HIGH", score = 1.0  → 구조/문서 레벨 합의 완료
```

*v2.7.0 · PHAM Signed · GNJz (Qquarts) + Claude 5.1*

