# solar/biosphere/ — 척박→선구→광합성→대기→호흡 식생 (Phase 7b)

**역할 (셋째날 2·3단계)**  
- Phase 7A: `surface/` 가 **땅/바다 분리 + 유효 알베도**를 만든다. (창 1:9~10)  
- Phase 7B: `biosphere/` 는 그 위에서 **풀·씨·열매·나무(식생)** 를  
  - 척박 → 선구 → 광합성 → 대기 조성 변화 → 호흡 식물  
  - 순서로 동역학적으로 구현한다. (창 1:11)

**엔지니어링 관점 한 줄 요약**  
`biosphere/` 는 지구(또는 우주선 캡슐) 표면에 **하나의 자가순환 생물권 엔진**을 올려서,  
태양 복사 입력을 **탄소 저장·대기 조성·알베도·잠열 플럭스**로 바꾸는 **Work Layer** 이다.

다시 말해:
- Drive  : 태양복사 F(r)  
- Reservoir : 토양 organic_layer, B_leaf/root/wood/seed, 대기·해양 열용량  
- Work : 광합성 GPP/NPP, 증산, 식생 성장, 알베도 변화  
- Sink : 호흡 Resp, 분해, IR 방출, 잠열  
- Phase/Controller : 선구→광합성 on→O₂ 임계→wood/seed 비중↑ (생장 단계)

이 5블록이 뉴런·지구·우주선까지 **공통 순환 템플릿**을 이룬다. (자세한 매핑: `docs/CIRCULATION_TEMPLATE.md`)

---

## 1. 단계 요약 (환경 · 생물 · 상태공간)

| 단계 | 환경 | 생물 | 상태변수 |
|------|------|------|----------|
| 0 | 셋째날 직후, 척박 | 없음 | — |
| 1 | 선구 | 균사·이끼·지의류 (극소 조건 생존) | `pioneer_biomass`, `organic_layer` |
| 2 | 토양 준비됨 | 광합성 활성화 | `B_leaf`, `B_root`, `B_wood`, GPP/NPP |
| 3 | 대기 변화 | O₂↑, CO₂↓ | `AtmosphereComposition` 피드백 |
| 4 | O₂ 임계 이상 | 호흡형·나무·씨/열매 | `f_O2`로 wood/seed 비중 증가 |

**물리적 의미**  
- 0단계: `surface/` + `atmosphere/` 로 땅과 바다, 궁창 까지만 있는 상태 (기본 기후 엔진).  
- 1단계: 아주 열악한 조건에서도 버티는 생물(균사·이끼·지의류)이 **유기물층(organic_layer)** 을 쌓음.  
- 2단계: 토양·수분·온도 조건이 맞으면 광합성 엔진이 켜지고,  
  `B_leaf/root/wood` 가 증가하면서 **에너지가 탄소 풀에 고정**된다.  
- 3단계: GPP/NPP 결과로 **CO₂↓, O₂↑** 가 일어나며, 대기 방사 특성(τ, ε_a)이 바뀐다.  
- 4단계: 충분한 O₂ 가 쌓이면, NPP 분배에서 `B_wood`, `B_seed` 비중이 커져  
  “풀”에서 “나무, 씨, 열매” 중심의 후기 식생으로 넘어간다.

이 전 과정을 **단발 이벤트**가 아니라 **비평형 구동 + 저장 + 피드백**의 순환으로 모델링하는 것이 `biosphere/` 의 목적이다.

---

## 2. 모듈 (레이어 역할 분리)

| 파일 | 역할 |
|------|------|
| `_constants.py` | 선구/광합성/O₂/알베도 상수 (모든 수치는 여기서만 정의) |
| `state.py` | `BiosphereState` (관측·연동용 스냅샷, 분석/로깅 용도) |
| `pioneer.py` | 선구 NPP, `organic_layer` 축적/분해 (척박 환경 생존 전용) |
| `photo.py` | f_I, f_C, f_T, f_O2, GPP, Resp, 증산, latent heat (광합성/호흡 핵심 수식) |
| `column.py` | `BiosphereColumn.step(env, dt)` → 피드백 dict (지구 0D 컬럼 단위) |
| `planet_bridge.py` | biosphere feedback → `AtmosphereComposition`/잠열/알베도 단위 환산 (대기·표면과의 결합 규약) |

---

## 3. 입출력 포트 (엔지니어링 규약)

### 입력 (env dict)

지구 모드에서 `env` 는 보통 `AtmosphereColumn.state()` + `SurfaceSchema` 에서 만들어진다.

- `F_solar_si` : 복사 조도 [W/m²] (`solar_luminosity.irradiance_si(r)`)  
- `T_surface`, `P_surface` : 표면 온도·압력 (대기 column 스냅샷)  
- `CO2`, `H2O`, `O2` : 대기 조성 [mol/mol] (`AtmosphereComposition`)  
- `water_phase` : `"solid" / "liquid" / "gas"` (`AtmosphereColumn.water_phase()`)  
- (옵션) `soil_moisture` : 0~1 (미구현 시, `water_phase` 기반 기본값 사용)  
- (옵션) `land_fraction` : 0~1 (column/biosphere init 시에만 써도 됨)

### 출력 (step 반환)

`BiosphereColumn.step(env, dt_yr)` 는 **플럭스 단위**로만 결과를 돌려준다.  
혼합비로의 변환은 `planet_bridge.py` 쪽에서 담당한다.

- `delta_CO2` : [kg C/(m²·yr)] per land — 순탄소 플럭스 (GPP-Resp)  
- `delta_O2` : [kg O₂/(m²·yr)] per land — 순산소 생성 플럭스  
- `transpiration_kg_per_m2_yr` : [kg H₂O/(m²·yr)] per land — 증산량  
- `latent_heat_biosphere_W` : [W/m²] — biosphere 기여 잠열 (연평균)  
- `delta_albedo_land` : 육지 알베도 변화량 (식생 피복률에 의존)  
- `GPP`, `Resp`, `NPP`, `photo_active` : 디버깅/로그용

`planet_bridge.biosphere_feedback_to_atmosphere()` 가 이 플럭스를 받아:

- column_mass, MU_AIR, 분자량(M_C, M_O2, M_H2O)을 사용해  
  `delta_*_mixing` (mol/mol 증가분) + `extra_latent_heat_Wm2` + `delta_albedo_land` 로 변환한다.

---

## 4. 사용 예 (로컬 컬럼)

```python
from solar.biosphere import BiosphereColumn

bio = BiosphereColumn(body_name="Earth", land_fraction=0.29)
env = {
    "F_solar_si": 1361.0,
    "T_surface": 288.0,
    "P_surface": 101e3,
    "CO2": 400e-6,
    "H2O": 0.01,
    "O2": 0.0,
    "water_phase": "liquid",
}
for _ in range(100):
    feedback = bio.step(env, 0.01)
    # feedback["delta_CO2"], feedback["delta_O2"] → atmosphere 조성 갱신
```

---

## 5. 통합 사용 (atmosphere/BrainCore 연동)

`brain_core_bridge` 를 통해 atmosphere/표면과 결합한 형태:

```python
from solar.brain_core_bridge import get_solar_environment_extension, create_default_environment

engine, sun, atmospheres, sfc, biospheres = create_default_environment(
    use_water_cycle=True,
    use_surface_schema=True,
    use_biosphere=True,
)

for _ in range(50):
    data = get_solar_environment_extension(
        engine, sun, atmospheres, dt_yr=0.02,
        surface_schema=sfc,
        biospheres=biospheres,
    )

earth = data["bodies"]["Earth"]
print(earth["T_surface"], atmospheres["Earth"].composition.CO2, atmospheres["Earth"].composition.O2)
```

이 경로에서:
- `BiosphereColumn.step()` → `planet_bridge.biosphere_feedback_to_atmosphere()` 로 변환  
- `AtmosphereComposition.CO2/O2/H2O`, `AtmosphereColumn.albedo`, 추가 잠열이 업데이트됨.

검증 데모: `examples/biosphere_day3_demo.py`  
- 1년 시뮬레이션에서 CO₂ 감소, O₂ 증가, 알베도 감소, B_leaf/wood/seed 증가를 확인.

---

## 6. 활용성 (지구 ↔ 우주선 ↔ 인지 시스템)

- **지구 모드**:  
  - 태양·대기·표면이 주어졌을 때, 식생이 **얼마나 CO₂를 흡수하고 O₂를 공급하는지**,  
    그리고 그 과정이 **알베도·잠열을 통해 기후를 어떻게 조정하는지**를 실험하는 레이어.  
  - “지구가 스스로 기후를 어떻게 유지/변조하는가?” 를 보는 자가순환 테스트베드.

- **우주선 모드** (향후):  
  - 동일 구조를 우주선 캡슐 내부에 적용하면,  
    제한된 Drive(발전량)·Reservoir(탱크 용량)·Radiator(방열 면적) 하에서  
    **얼마나 많은 식생/승무원을 안정적으로 유지할 수 있는지**를 검증하는 생명유지 엔진이 된다.

- **인지 시스템과의 연결**:  
  - `brain_core_bridge` 를 통해 생물권 상태(예: O₂, CO₂, habitable 여부)를  
    BrainCore/Cognitive_Kernel 이 읽도록 하면,  
    **환경 상태에 반응하는 인지 에이전트** 설계의 입력 레이어로도 사용할 수 있다.

---

## 7. 상세 사양 및 설계 문서

- [docs/BIOSPHERE_LAYER_SPEC.md](../../docs/BIOSPHERE_LAYER_SPEC.md) — 상태변수·수식·포트 전체 명세  
- [docs/DAY3_PROGRESS_CHECK.md](../../docs/DAY3_PROGRESS_CHECK.md) — 셋째날(Phase 7A/7B) 진행 상황 및 검증  
- [docs/CIRCULATION_TEMPLATE.md](../../docs/CIRCULATION_TEMPLATE.md) — 뉴런→지구→우주선 순환 템플릿 매핑
