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

## 7. 토양 형성 ODE — 세차운동과 동일한 설계 철학

### 핵심 개념

세차운동 방식과 동일:

| 구분 | 입력 | 출력 |
|------|------|------|
| 세차운동 | G, M, r (물리 상수) | 25,000년 주기 |
| **토양 형성** | R, W, ETA, λ (물리 법칙) | **2739년 원시토양** |

"물리 법칙과 관측값을 수식에 넣으면, 결과가 자연스럽게 나온다"

### ODE 시스템 (3변수)

```
상태변수:
  P  = pioneer_biomass  [kg C/m²]  (균사·이끼·지의류)
  M  = mineral_layer    [kg/m²]    (풍화 광물)
  S  = organic_layer    [kg C/m²]  (humus — 토양 임계의 핵심)

방정식:
  dP/dt = R·P·(1 - P/K(S))·fT·fW - M_mort·P    [로지스틱 성장]
  dM/dt = W_w·P·fT·fW                             [풍화: pioneer → 광물]
  dS/dt = ETA·M_mort·P + W_mh·M - λ(T)·S         [humus 축적]

양성 피드백:
  K(S) = K0 + K_soil·S    (유기물↑ → 부양력↑ → pioneer↑ → 유기물↑)

Q10 온도 의존 분해:
  λ(T) = λ_base × 2^((T-283)/10)
```

### 파라미터 (관측 기반)

| 파라미터 | 값 | 단위 | 근거 |
|----------|-----|------|------|
| R_PIONEER | 0.08 | /yr | 지의류 성장률 |
| M_PIONEER | 0.005 | /yr | 수명 ~200년 |
| K0_CARRYING | 0.05 | kg C/m² | 돌땅 최소 부양력 |
| K_SOIL_FEEDBACK | 8.0 | — | 양성 피드백 강도 |
| W_WEATHERING | 0.002 | kg/(kg·yr) | 풍화율 |
| W_MINERAL_HUMUS | 0.0003 | kg C/(kg·yr) | 광물→humus 기여 |
| ETA_ORGANIC | 0.08 | — | 사체→humus 8% |
| LAMBDA_DECAY | 0.003 | /yr | 반감기 ~330yr |
| ORGANIC_THRESHOLD | 0.5 | kg C/m² | 식물 착근 임계 |

### 시뮬레이션 결과

```
0yr:    돌땅 (pioneer=0.001 kg C/m²)
30yr:   pioneer 착생 시작
175yr:  풍화 진행 중 (mineral 축적)
2000yr: humus 축적 중
2739yr: ★ 원시토양 완성 (organic=0.5007 kg C/m²)
```

관측 비교:
- 용암지대(하와이): 300~500년
- 빙하 후퇴지: 200~600년
- 고위도 암반: 1,000~3,000년
- 지구 전체 0D 평균: **2739년** ← 모델 결과 ✓

### English Summary

**Soil Formation ODE — same design as Precession simulation**

Input physical laws (R, W, ETA, λ) → 2739-year soil threshold emerges naturally.
Three coupled ODEs: logistic pioneer growth + weathering + Q10 decomposition.
Positive feedback: K(S) = K0 + K_soil·S (more organic → higher carrying capacity).

검증: `examples/soil_formation_sim.py`

---

## 8. 식물 생애주기 Phase Gate ODE (Phase 7c — v1.8.0)

### 핵심 개념

토양 ODE와 동일한 설계:

| 구분 | 입력 | 출력 |
|------|------|------|
| 토양 형성 | R, W, ETA, λ | 2739년 원시토양 |
| **식물 생애주기** | K_germ, K_gate, NPP | 씨→싹→줄기→나무→열매 전이 |

"if-else 없이, 연속 ODE로 단계 전이가 자연스럽게 나온다"

### Phase Gate ODE 시스템

```
상태변수 (Phase 7c):
  B_seed   [kg C/m²]  씨 (번식·저장 풀)
  B_sprout [kg C/m²]  싹 (발아 직후 유묘)
  B_stem   [kg C/m²]  줄기 (초본/관목)
  B_wood   [kg C/m²]  목본 (나무)
  B_fruit  [kg C/m²]  열매 (결실)

전이 수식:
  씨  → 싹:  K_germ × g_soil(S) × g_T(T) × f_W
              g_soil = S / (S + S_half)          [Michaelis-Menten, 연속]
              g_T    = 온도 삼각형 함수 (T_min~T_opt~T_max)

  싹  → 줄기: K_spr × sigmoid(B_sp / B_sp_half) × B_sprout
  줄기→ 나무: K_stw × sigmoid(B_st / B_st_half) × B_stem
  나무→ 열매: K_fruit × sigmoid(B_wd / B_wd_th) × f_O2 × B_wood
  열매→ 씨:   K_fts × B_fruit                              [순환 닫힘 ↺]

NPP 분배 (softmax — 탄소 회계 정합):
  logits = {leaf, root, stem, wood, fruit} = base + Δ(O₂, phase)
  alloc  = softmax(logits)   →   sum(alloc) = 1 보장
```

### 파라미터 (관측 기반)

| 파라미터 | 값 | 단위 | 근거 |
|----------|-----|------|------|
| K_GERM | 0.5 | /yr | 발아 ~2년 |
| GERM_T_OPT | 295 | K | 최적 온도 22°C |
| K_SPROUT_TO_STEM | 0.25 | /yr | 유묘→줄기 ~4년 |
| K_STEM_TO_WOOD | 0.08 | /yr | 목질화 ~12년 |
| K_FRUIT | 0.15 | /yr | 첫 결실 ~7년 |
| B_WOOD_FRUIT_TH | 1.0 | kg C/m² | 성목 결실 임계 |
| K_FRUIT_TO_SEED | 0.8 | /yr | 1계절 내 씨 성숙 |

### 시뮬레이션 결과

```
시작: 토양 완성 직후 (organic=0.52 kg C/m², B_seed=0.001)
  1년:  싹 발아  (B_sprout > 0.001 kg C/m²)
  4년:  줄기 형성 (B_stem > 0.01 kg C/m²)
  ~5년: 나무 성장 (B_wood ~3.6 kg C/m² 안정)
  열매: ★ B_fruit 생산 → B_seed ↺ 순환 안정
```

### English Summary

**Plant Lifecycle Phase Gate ODE — same design philosophy**

Input: K_germ, K_gate parameters (observation-based)
Output: seed→sprout→stem→wood→fruit transitions emerge naturally via continuous ODEs.
No if-else branches — all transitions are Michaelis-Menten or sigmoid gates.
NPP allocation via softmax ensures carbon mass conservation (sum=1).

검증: `examples/plant_lifecycle_sim.py`

### 셋째날 완성 타임라인

```
0yr    → [돌땅]       pioneer 착생 시작
30yr   → [pioneer 성장] 풍화 진행 중
2739yr → [★원시토양]  organic = 0.5 kg C/m²
+1yr   → [싹 발화]    B_sprout 출현
+4yr   → [줄기 형성]  B_stem 성장
+수십년→ [나무]       B_wood ~3.6 kg C/m²
+결실  → [★열매]      B_fruit → B_seed ↺ 닫힌 루프
```

---

## 9. 상세 사양 및 설계 문서

- [docs/BIOSPHERE_LAYER_SPEC.md](../../docs/BIOSPHERE_LAYER_SPEC.md) — 상태변수·수식·포트 전체 명세
- [docs/DAY3_PROGRESS_CHECK.md](../../docs/DAY3_PROGRESS_CHECK.md) — 셋째날(Phase 7A/7B/7C) 진행 상황 및 검증
- [docs/CIRCULATION_TEMPLATE.md](../../docs/CIRCULATION_TEMPLATE.md) — 뉴런→지구→우주선 순환 템플릿 매핑
- [docs/WORK_LOG_2026-02-26.md](../../docs/WORK_LOG_2026-02-26.md) — 작업 로그 (session 2: 토양 / session 3: 생애주기)
- [docs/VERSION_LOG.md](../../docs/VERSION_LOG.md) — v1.7.0 토양 / v1.8.0 생애주기
