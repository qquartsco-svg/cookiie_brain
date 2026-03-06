# PANGEA ROTATION & WATER BUDGET — 회전 동역학을 환경 셋팅에 넣기

**목적**  
지구를 정지한 구가 아니라 **도는 스페이드 지구**로 보고,  
자전·세차·물 분배(궁창/지하/표면)를 **수치 + 레이어 구조**로 고정한다.  
이 문서는 코드 레벨에서 어떤 파라미터를 어디 레이어에 둘지에 대한 **상위 설계 문서**다.

**관련 문서 (서사 연결)**  
- [FEYNMAN_VOL1_AS_PLANET_MOTION.md](FEYNMAN_VOL1_AS_PLANET_MOTION.md) — 회전·대칭·상대론·질량–에너지가 "행성이 어떻게 움직이게 되는가"로 이어지는 논리.  
- [PLANET_DYNAMICS_ENGINE.md](PLANET_DYNAMICS_ENGINE.md) — 파인만 기반 **독립 엔진** 모듈화 가능성, Level 1(Planet Dynamics) → Level 2(Environment) → Level 3(Eden Finder) 계층.  
- [LIFESPAN_ENERGY_BUDGET_CONCEPT.md](LIFESPAN_ENERGY_BUDGET_CONCEPT.md) — 수명·에너지 예산.  
- [NOAH_ARC_SCALING.md](NOAH_ARC_SCALING.md) — 규빗·방주 스케일.

---

## 1. 레이어/층위 분리

동역학 개념이 섞이지 않도록, 다음 네 레이어로 분리한다.

1. **L0 — Geometry & Rotation (형상·회전)**  
   - 지구 형상: 편평 타원체 + “스페이드” 비대칭  
   - 자전 각속도 \(\omega_{\text{spin}}\)  
   - 축 기울기(Obliquity) \(\varepsilon\)  
   - 세차 속도 \(\omega_{\text{prec}}\)

2. **L1 — Water Budget (물 예산)**  
   - 전체 물 부피 \(W_{\text{total}}\)  
   - 표면 해수/호수 \(W_{\text{surface}}\)  
   - 궁창(캐노피) \(W_{\text{canopy}}\)  
   - 지하/맨틀 수분 \(W_{\text{ground}}\)  
   - 이들 사이의 교환율 \(\frac{dW_i}{dt}\)

3. **L2 — Planet Stress & Instability (행성 스트레스·불안정도)**  
   - 판 응력 \(\sigma_{\text{plate}}\)  
   - 지하수 압력 \(P_w\)  
   - 회전·세차에 따른 관성 응력 \(S_{\text{rot}}\)  
   - 한 틱의 합성 스트레스 `planet_stress = f(σ, P_w, S_rot, …)`  
   - `instability = g(planet_stress, W_surface, dW_surface/dt, …)`

4. **L3 — Firmament & Flood Events (궁창·대홍수)**  
   - `FirmamentLayer` 상태 (H2O_canopy, shield_strength S, env_load L_env)  
   - `fl.step(dt_yr, instability)`  
   - 붕괴 조건: `instability >= θ_collapse`  
   - 붕괴 시 `FloodEvent` + `Layer0Snapshot` 변경 → EdenOS / UnderWorld 로 전달

각 레이어는 **아래 레이어를 읽지만, 수정하지 않는다**:

- L3(Firmament)는 L2의 `instability`만 읽고, L2 로직은 모른다.  
- L2는 L1/L0의 파라미터를 읽고 스트레스를 계산할 뿐, 물 예산을 직접 바꾸지 않는다.  
- L1은 L0(형상+회전)를 읽고 저장 위치/압력을 계산한다.

**EdenOS 아키텍처 비유 (조/모 = Macro–Micro)**  
[FEYNMAN_VOL1_AS_PLANET_MOTION.md](FEYNMAN_VOL1_AS_PLANET_MOTION.md) §9에서 채택한 공식 비유와 일치한다:  
- **조 (Joe / Macro)** = L0 + L1 — 거시적 동역학 뼈대(자전, 물 총량, 보존 법칙).  
- **모 (Moe / Micro)** = L2 + L3 — 미시적 환경·생명(스트레스, 궁창 붕괴, 수명).  
코드에서 L0/L1 파라미터는 `InitialConditions` 또는 전용 CONFIG에 두고, L2/L3는 `planet_stress`·`FirmamentLayer`·수명 엔진이 읽는다.

### 1.1 쓰는 단위와 L1↔L3 매핑 (필수 규약)

L1(물 예산)은 **부피 [km³]** 로, L3(Firmament)는 **무차원 비율** 을 쓴다.  
이 둘이 서로 다른 세계로 흐르지 않도록 **한 번만 정의**하고 코드·문서 공통으로 쓴다.

- **L1**: `W_canopy_km3` — 궁창에 해당하는 물 부피 [km³].  
- **L3**: `H2O_canopy_frac` — `firmament.py`의 `state.H2O_canopy` [0~0.05 에덴 기준, 0~0.10 상한].

**매핑 규약**:

\[
\text{H2O\_canopy\_frac}
= \frac{W_{\text{canopy\_km3}}}{W_{\text{canopy\_ref\_km3}}}
\times \text{H2O\_canopy\_eden}
\]

- `H2O_canopy_eden = 0.05` (에덴 기준 캐노피 비율).  
- **\(W_{\text{canopy\_ref\_km3}}\)**: "H2O_canopy = 0.05인 상태"에 대응하는 **기준 부피 [km³]**.  
  - 예: 문서 시나리오 A에서 궁창 10 m GEL 상당 → \(W_{\text{canopy\_ref\_km3}} \approx 3.6\times 10^6\ \text{km}^3\) (전 지구 해양 면적 × 10 m).  
  - 이 값을 CONFIG 또는 InitialConditions에 한 번만 두고, L1에서 \(W_{\text{canopy}}\)를 갱신할 때마다 위 식으로 `H2O_canopy_frac`을 계산해 L3(FirmamentLayer)에 넘긴다.

이 규약이 없으면 "물 예산"과 "궁창 상태"가 서로 다른 단위로 놀게 된다.

---

## 2. L0 — Geometry & Rotation: 스페이드 지구 파라미터

### 2.1 기본 값

- 평균 반지름 \(R \approx 6371\,\text{km}\)
- 현재 자전 각속도:
  \[
  \omega_{\text{today}} \approx 7.2921159\times 10^{-5}\ \text{rad/s}
  \]
- 관측 편평도:
  \[
  f_{\text{obs}} = \frac{R_{\text{equator}} - R_{\text{pole}}}{R_{\text{equator}}}
  \approx \frac{21.4}{6378.1} \approx 1/298
  \]

### 2.2 맥로린 타원체 근사

균질 유체 구체의 편평도 \(f\)는 1차 근사로:

\[
f \approx \frac{5}{4}\,\frac{\omega^2 R^3}{G M}
\]

- \(G\): 중력상수  
- \(M\): 지구 질량

현재 \(\omega = \omega_{\text{today}}\) 를 넣으면 **대략 f ~ 1/300 오더**가 나와,  
관측값과 비슷한 수준으로 맞는다.  
즉, **지구의 편평도는 이미 “회전 동역학의 결과”** 라는 점을 확인해 둔다.

### 2.3 에덴/판게아 시나리오에서의 회전

고대 지구는 하루가 더 짧았다(더 빨리 돌았다)는 관측이 있다:

- 약 4억 년 전: 하루 ≈ 22 h  
- 즉 \(\omega\) 가 현재보다 ~9% 정도 컸다.

**Eden/Pangea 모드**에서는:

- `omega_spin_eden ≈ 1.0 ~ 1.1 × ω_today` (튜닝 범위)  
- 아직 “토성 고리”처럼 망가질 정도로 빠르지 않게 유지  
- 하지만 `S_rot`(회전에 의한 행성 응력) 항에는 `omega_spin_eden` 을 사용

**코드 레벨 제안 (InitialConditions)**:

- `InitialConditions` 에 다음 필드를 추가(또는 패라미터로 계산):
  - `omega_spin` — 자전 각속도  
  - `obliquity_deg` — 축 기울기 (예: 23.4°)  
  - `precession_rate` — 세차 속도(1/주기)  
  - `spade_asymmetry` — 질량/형상 비대칭 계수 (0=완전 타원체, 1=스페이드 극단)

이 값들은 **day4/season_engine, planet_stress 계산 모듈이 읽기만 한다.**

---

## 3. L1 — Water Budget: 판게아 하나님 상태

### 3.1 현재 물 예산 (출처·범위)

**출처**: NOAA / USGS 등 수치 — 연도·페이지는 구현 시 CONFIG에 명시.  
**허용 범위**: ± 몇 % 이내로 두고, 하드코딩 대신 "범위 + 근거"만 문서화.

- 전체 물: \(W_{\text{total}} \approx 1.386\times 10^9\ \text{km}^3\)
- 바다 해수: \(\approx 1.332\times 10^9\ \text{km}^3\)
- 나머지(얼음+지하수+대기 등): \(\approx 5.4\times 10^7\ \text{km}^3\)

해당 부피를 **전 지구 해양 면적**으로 나누면 "전 지구 등가 수심" GEL이 나온다.  
GEL 1 m당 부피:

\[
W_{1\text{m}} \approx 3.6\times 10^5\ \text{km}^3
\]

(해양 면적 \(\approx 3.6\times 10^8\ \text{km}^2\) 기준.)

### 3.2 초기 에덴/판게아 상태 목표 — GEL로 통일

목표: **표면 바다 거의 없음, 초대륙 대부분 노출**.  
"해수면 100 m"처럼 지형에 따라 해석이 갈리는 표현은 쓰지 않고, **GEL(전 지구 등가 수심)** 로만 정의한다.

- **GEL_surface_eden_m**: 에덴 시나리오에서의 **표면 물 전 지구 등가 수심 [m]** (시나리오 파라미터).  
  예: 100 m.
- 표면 물 부피:
  \[
  W_{\text{surface, eden}}
  = \text{GEL\_surface\_eden\_m} \times (A_{\text{ocean}}/1000)
  \approx \text{GEL\_surface\_eden\_m} \times 3.6\times 10^5\ \text{km}^3/\text{m}.
  \]
  예: GEL = 100 m → \(W_{\text{surface, eden}} \approx 3.6\times 10^7\ \text{km}^3\).

이때 **빼야 하는 물**(궁창+지하로 보낼 양):

\[
W_{\text{removed}} = W_{\text{ocean,today}} - W_{\text{surface, eden}}
  \approx 1.332\times 10^9 - 3.6\times 10^7
  \approx 1.296\times 10^9\ \text{km}^3
\]

판게아 지형/해양분지(바닥 -4 km 등)가 나중에 들어와도, **GEL을 시나리오 파라미터로 두면** 해석이 틀어지지 않는다.

### 3.3 분배 시나리오 (예시)

#### 시나리오 A — 얇은 궁창

- 궁창:
  \[
  W_{\text{canopy}} \approx 3.6\times 10^6\ \text{km}^3
  \]
  (GEL 10 m 상당. \(W_{\text{canopy\_ref\_km3}}\) 로 쓰면 H2O_canopy_frac = 0.05 대응.)
- 지하:
  \[
  W_{\text{ground}} \approx 1.292\times 10^9\ \text{km}^3
  \]

#### 시나리오 B — 두꺼운 궁창

- 궁창:
  \[
  W_{\text{canopy}} \approx 1.8\times 10^7\ \text{km}^3
  \]
  (GEL 50 m 상당.)
- 지하:
  \[
  W_{\text{ground}} \approx 1.278\times 10^9\ \text{km}^3
  \]

**코드 레벨**에서는:

- `WaterBudget` 구조체를 하나 정의:

```text
WaterBudget:
    W_total
    W_surface
    W_canopy
    W_ground
```

- `InitialConditions` 에 `water_budget_eden` 프리셋을 둔다.

L1은 **오직 이 숫자들만 가지고**:

- 각 저장소의 압력/에너지 상태  
- 교환율 \(dW_i/dt\) (지하수 분출, 궁창 응축 등)을 계산한다.

---

## 4. L2 — Planet Stress & Instability

### 4.1 planet_stress 정의

`planet_stress` 는 **원시값**을 먼저 구한 뒤 **정규화**한다.

**원시값** (한 틱):

```text
planet_stress_raw =
    a1 * σ_plate
  + a2 * (P_w / P_ref)
  + a3 * S_rot
  + a4 * (W_surface / W_total)
  + a5 * dW_surface_dt_norm
```

**정규화 (0~1 또는 기준 구간)**:

```text
planet_stress = normalize(planet_stress_raw; ref_range)
```

- `normalize(x; ref_range)`: 기준 구간 `[ref_min, ref_max]` 에 맞춰 선형 스케일.  
  예: `(x - ref_min) / (ref_max - ref_min)` 후 **saturate** 적용.  
- `ref_range` 는 CONFIG(예: `planet_stress.yaml`)에 정의.  
  이 정의가 없으면 "임계값"과 비교할 때 스케일이 맞지 않는다.

설명:

- `σ_plate` — 판 구조 응력 (gaia/tectonics 모듈에서 제공, 없으면 0)  
- `P_w` — 지하수/깊음 수압  
- `S_rot` — 회전·세차에 의한 관성 응력 (L0 값으로부터 계산)  
- `W_surface / W_total` — 표면 물 비율 (바다가 너무 많아져도 스트레스 상승)  
- `dW_surface_dt_norm` — 표면 물 증가 속도(급증=위험)

계수 \(a_i\) 는:

- `CONFIG/planet_stress.yaml` 같은 곳에 범위와 함께 기록:  
  - 예) `a1 in [0.2, 0.5]`, `a3 in [0.1, 0.3]` 등  
  - 코드에는 하드 숫자 대신 **이 설정을 로드**.

### 4.2 instability 함수

**원시값**:

```text
instability_raw =
    b1 * planet_stress
  + b2 * (W_surface / W_total)
  + b3 * dW_surface_dt_norm
```

**0~1 로 만드는 방법 (필수)**:

```text
instability = saturate(instability_raw)
```

- **saturate(x)**: \(x\) 를 \([0, 1]\) 구간으로 제한.  
  - 기본: `saturate(x) = min(max(x, 0), 1)` (클램프).  
  - "클램프 금지" 원칙이면 `saturate(x) = (tanh(x) + 1) / 2` 또는 `softsign` 등 연속 함수로 대체.
- 이 정의가 없으면 `θ_collapse = 0.85` 같은 임계값이 의미를 잃는다.

- \(0 \le instability \le 1\) 로 정규화.  
- `θ_collapse` = 0.85 (현재 FirmamentLayer에서 사용 중).

L2는:

- L0(L1)의 숫자만 읽어서 `planet_stress`, `instability` 를 계산하고,  
- **물 예산(W)을 직접 바꾸지 않는다.**

---

## 5. L3 — Firmament & Flood와의 연결

**인터페이스**: `FirmamentLayer.step(dt_yr, instability=None)`.  
- `instability` 를 넘기면, `instability >= θ_collapse` (0.85) 일 때 자동으로 `collapse_triggered = True`.  
- 코드는 `solar/eden/firmament.py` 에 이미 이 형태로 구현되어 있음.

L2의 출력을 그대로 사용한다.

통합 레이어/Runner에서의 호출 순서는:

1. `planet_stress = compute_planet_stress(ic, water_budget, rotation_state, ...)`
2. `instability   = compute_instability(planet_stress, water_budget, ...)`
3. `firmament.step(dt_yr, instability=instability)`
4. `layer0 = firmament.get_layer0_snapshot()`
5. `scenario_overlay = {..., "shield_strength": layer0.S, "env_load": layer0.env_load, ...}`
6. `world = make_eden_world(ic, scenario_overlay)`
7. `hades.listen(..., layer0_snapshot=layer0)`
8. HomeostasisEngine 가 `world.layer["SCENARIO"]` 에서 S/L_env 를 읽어 수명/통합에 반영.

이렇게 하면:

- **초기 에덴/판게아 상태**는 `water_budget_eden + rotation_state_eden` 으로 정의되고,  
- **대홍수**는 `planet_stress, instability` 가 동역학적으로 임계값을 넘을 때  
  `FirmamentLayer` 가 자동으로 붕괴하는 **결과**가 된다.

---

## 6. 구현 로드맵 (요약)

1. **문서 레벨**  
   - 본 문서 + `NOAH_ARC_SCALING.md` + `LIFESPAN_ENERGY_BUDGET_CONCEPT.md` 를  
     상호 참조하도록 링크/요약 추가.

2. **파라미터 정의 레벨**  
   - `InitialConditions` 에 `omega_spin`, `obliquity`, `water_budget_eden` 추가.  
   - (별도 모듈) `planet_stress_config.yaml` 또는 상수 모듈에 \(a_i, b_i\) 범위 정의.

3. **코드 레벨**  
   - `day4/season_engine` 가 `omega_spin`, `obliquity` 를 읽도록 확장.  
   - `planet_stress` / `instability` 계산 헬퍼 함수 추가 (새 모듈).  
   - Runner(예: `eden_os_runner`) 가 이 값을 사용해  
     `firmament.step(instability=...)` 를 호출하도록 점진적 리팩터.

이 로드맵을 따르면,  
“정지한 구형 지구”가 아니라 **도는 스페이드 지구 + 판게아 물 예산**이  
EdenOS / Firmament / Flood 전체 로직의 환경 셋팅으로 일관되게 들어가게 된다.

