# day5/ — 다섯째날: 생물 이동 · 정보 네트워크 레이어

**역할**  
Day3 의 **위도 밴드별 독립 biosphere** 위에,  
**움직이는 생명체(새·물고기)** 가 씨드·질소·포식량을 위도 간에 나르는 **transport 항**을 더하는 레이어.

- **물리적 의미**: “땅이 풀과 씨 맺는 나무를 냈다”(Day3) 다음에, **새와 물고기가 그 정보(씨·영양)를 공간적으로 재분포**시키는 단계.
- **엔지니어링 의미**: latitude_bands 간 **결합 없음**을 유지한 채, **보존형 transport 커널**과 **트로픽 ODE**로 Loop F/G/H 를 닫는 확장 레이어.

`day5/` 는 이 레이어의 **모듈을 한곳에서 re-export 하는 인덱스 패키지**이며,  
실제 구현은 `solar/day5/*.py` 에 있다.

> ⚠️ **재현성 / Reproducibility**  
> - `day5` 는 **re-export 전용 패키지**이며, 구현은  
>   `solar/day5/mobility_engine.py`, `seed_transport.py`, `food_web.py`, `_constants.py` 에 있다.  
> - `from solar.day5 import BirdAgent, SeedTransport, FoodWeb` 등은  
>   리포지토리를 **패키지 구조(`solar/` 루트)** 로 둔 환경을 전제로 한다.  
> - 포트·단위 정의는 [`docs/PORTS_AND_UNITS.md`](../docs/PORTS_AND_UNITS.md) 의 Day 5 섹션을 참고한다.

---

## 1. 다섯째날 큰 그림 (물리·엔지니어링 의미)

### 1.1 개념 위치

```text
Day3: 땅·바다·토양·식생·산불 (각 위도 밴드 독립)
        │
        ▼
Day5:  위도 밴드 간 “누가 무엇을 옮기는가”
       → 씨드(B_seed) 분산, 구아노(N), 포식(phyto) → CO₂ 호흡
```

- **창세기 관점**: *“새들은 땅 위 하늘을 날아다녀라”* — 이동하는 생명이 **정보(씨·영양)를 지구 곳곳으로 전달**하는 단계.
- **시스템 관점**: Day3 의 `BiosphereColumn` 은 **로컬 ODE**만 담당하고, band 간 결합은 없다.  
  Day5 는 **transport 항** \( \bigl(\sum_j K_{j\to i} B_j - \sum_j K_{i\to j} B_i\bigr) \) 을 더해,  
  “밴드 \(i\) 의 pioneer / N_soil / phyto” 가 **이웃 밴드와 물리적으로 연결**되도록 한다.

### 1.2 핵심 방정식

밴드 \(i\) 의 스칼라 필드 \(B_i\) (예: pioneer biomass, N_soil) 에 대해:

\[
\frac{\mathrm{d}B_i}{\mathrm{d}t}
= f_{\mathrm{local}}(B_i)
+ \sum_j K_{j\to i}\, B_j
- \sum_j K_{i\to j}\, B_i
\]

- \(f_{\mathrm{local}}\): 기존 Day3 `BiosphereColumn` 등 로컬 항.  
- \(K_{j\to i}\): 밴드 \(j\to i\) 로의 **이동률 [1/yr]** — `BirdAgent` / `FishAgent` 가 제공.  
- **보존**: 전지구 합 \(\sum_i B_i\) 는 source/sink 가 없으면 일정.  
  수치적으로는 `dt_yr * \sum_j K_{i\to j} \le 1` 로 **양수성·안정성**을 보장한다.

---

## 2. Loop F / G / H (Gaia 확장)

Day3 의 Loop A/B/C 에 이어, Day5 는 **생물 이동에 의한 피드백** 3개를 정의한다.

| 루프 | 설명 | 제공 모듈 | 연결 포트 |
|------|------|-----------|-----------|
| **F** | 씨드 분산 → pioneer 원거리 확산 | `BirdAgent` + `SeedTransport` | `seed_flux(B_pioneer)` → `SeedTransport.step(B)` → 각 밴드 `pioneer += Δ` |
| **G** | 구아노 N → 토양 질소 | `BirdAgent` | `guano_flux()` → `NitrogenCycle` 또는 `N_soil[i] += Δ` |
| **H** | 포식 → phyto 감소 → CO₂ 호흡 | `FishAgent` + `FoodWeb` | `predation_flux(phyto)` → `env["fish_predation"]` → `FoodWeb.step` → `co2_resp_yr` → 대기 CO₂ |

- **Loop F**: 새가 씨를 먼 밴드로 옮김 → pioneer 분포가 **공간적으로 완만해짐** (확산 효과).  
- **Loop G**: 새의 배설물(구아노)이 **N_soil** 을 보강 → Day4 `NitrogenCycle` 의 입력.  
- **Loop H**: 물고기 포식으로 phyto 감소 → **호흡 CO₂** 증가 → Day2 대기 조성과 연결.

Gaia 루프 통합 설계는 [`solar/bridge/README.md`](../bridge/README.md) 및 `gaia_loop_connector` 확장 시 이 표를 기준으로 한다.

---

## 3. 구성 모듈 요약

| 모듈 | 역할 | 대표 API |
|------|------|----------|
| **mobility_engine** | 이동 에이전트 (Bird/Fish). 위도별 이동률·씨드/구아노/포식 플럭스 | `BirdAgent`, `FishAgent`, `make_bird_agent`, `make_fish_agent`, `migration_rates()`, `seed_flux()`, `guano_flux()`, `predation_flux()` |
| **seed_transport** | 보존형 위도 밴드 간 transport | `SeedTransport`, `TransportKernel`, `make_transport`, `step(B, dt_yr)`, `step_with_source(B, source_flux, dt_yr)` |
| **food_web** | 단순 트로픽 ODE (phyto → herbivore → carnivore) + CO₂ 호흡 | `FoodWeb`, `TrophicState`, `make_food_web`, `step(state, env, dt_yr)`, `net_co2_flux()` |
| **_constants** | Day5 공유 상수 (규약: 리터럴 상수 집중) | `R_SEED_DISPERSAL`, `R_GUANO_N`, `R_PREDATION`, `R_RESP_CO2`, `ALPHA_CO2_ABS`, `DEFAULT_*`, `M_CARNIVORE` |

- **이동률 수식 (BirdAgent)**  
  \[
  \mathrm{rate}_i = \mathrm{base\_rate}
  \times \max\bigl(0,\; 1 + \alpha_{\mathrm{O_2}}(O_{2,i} - O_{2,\mathrm{ref}})\bigr)
  \]  
  O₂ 가 높을수록 이동이 활발하다고 가정 (선택적 파라미터).
- **Transport 보존**  
  `SeedTransport.step(B, dt_yr)` 은 \(\sum_i B_i\) 를 유지.  
  `step_with_source` 는 외부 source 플럭스(예: 구아노)를 더한 뒤 같은 보존 연산.
- **FoodWeb CO₂**  
  `TrophicState.co2_resp_yr` 은 **해당 스텝의 연간 환산 호흡 플럭스** [kgC/m²/yr].  
  `net_co2_flux(state, gpp)` 는 GPP 기반 흡수와 호흡을 합산해 **대기 CO₂ 가산**으로 쓴다.

자세한 수식·단위·제약은 각 모듈 docstring 과 [`docs/PORTS_AND_UNITS.md`](../docs/PORTS_AND_UNITS.md) Day 5 섹션 참고.

---

## 4. 사용 예시

### 4.1 BirdAgent + SeedTransport (Loop F)

```python
from solar.day5 import make_bird_agent, make_transport

bird = make_bird_agent(n_bands=12)
rates = bird.migration_rates()   # 또는 bird.migration_rates(o2_by_band)
transport = make_transport(
    n_bands=12,
    neighbors=bird.neighbors,
    rates=rates,
)
B_pioneer = [0.1] * 12
B_pioneer[6] = 0.5
B_new = transport.step(B_pioneer, dt_yr=1.0)
# B_new 합 = B_pioneer 합 (보존)
```

### 4.2 Loop G — 구아노 → N_soil

```python
guano = bird.guano_flux()   # [g N/m²/yr] per band
# NitrogenCycle.step(..., external_N_source=guano[i]) 또는
# N_soil[i] += guano[i] * dt_yr (통합 시 연결 지점)
```

### 4.3 FoodWeb + FishAgent (Loop H)

```python
from solar.day5 import make_food_web, make_fish_agent, TrophicState

fw = make_food_web()
fish = make_fish_agent(n_bands=12)
phyto_by_band = [0.4] * 12
fish_pred = fish.predation_flux(phyto_by_band)

state = TrophicState(phyto=0.5, herbivore=0.2, carnivore=0.1, co2_resp_yr=0.0)
state = fw.step(
    state,
    env={"GPP": 0.5, "fish_predation": fish_pred[6]},
    dt_yr=1.0,
)
# state.co2_resp_yr → atmosphere CO₂ 가산
delta_co2 = fw.net_co2_flux(state, gpp=0.5)
```

### 4.4 검증 데모

```bash
python solar/day5/day5_demo.py
```

Loop F/G/H, 보존성, O₂ 반응, 극지 topology, FishAgent→FoodWeb 포트까지 한 번에 검증한다.

---

## 5. Day3 / Day4 와의 연결

- **Day3**  
  - `BiosphereColumn` 은 **로컬** pioneer / GPP / 호흡만 계산.  
  - Day5 `SeedTransport.step(B_pioneer)` 결과를 **외부에서** 각 밴드 `pioneer` 에 더해 주면 Loop F 가 닫힌다.  
  - `BirdAgent.guano_flux()` → Day4 `NitrogenCycle` 또는 N_soil 입력으로 주입하면 Loop G.  
- **Day4**  
  - `NitrogenCycle.N_limitation` 은 그대로 biosphere GPP 게이트로 사용.  
  - 구아노는 **추가 N 소스**로 `N_soil` 에 더하면 된다.  
- **SeasonEngine (Day4)**  
  - 이동률을 계절(건기/우기)에 따라 변조하려면, `BirdAgent.migration_rates()` 호출 시  
    Day4 `SeasonEngine.state(lat_deg)` 의 `dry_season_modifier` 등을 반영한 rate 스케일을 넣을 수 있다 (확장 포인트).

---

## 6. 참고 문서 및 블록체인 서명

| 문서 | 내용 |
|------|------|
| [`docs/PORTS_AND_UNITS.md`](../docs/PORTS_AND_UNITS.md) | Day 5 포트 이름·의미·단위 표 |
| [`solar/bridge/README.md`](../bridge/README.md) | Gaia Loop A/B/C 및 확장 시 Loop F/G/H 연결 |
| [`solar/day3/README.md`](../day3/README.md) | 셋째날 biosphere·fire·Gaia 루프 |
| [`solar/day4/README.md`](../day4/README.md) | 넷째날 질소·Milankovitch·조석·SeasonEngine |

- **버전**: Day5 레이어 최초 통합 — `solar` v2.8.0  
- **상세 로그**: `docs/VERSION_LOG.md` (해당 버전 항목 참고).  
- **레이어 설계 체인**: `blockchain/pham_chain_LAYERS.json`

```text
PHAM_CHAIN:
  pham_chain_LAYERS.json — solar 개념 레이어 정의 (A_HIGH)
  Day5 = 생물 이동·정보 네트워크 레이어 (Loop F/G/H)
```

*v2.8.0 · PHAM Signed · GNJz (Qquarts) + Claude*
