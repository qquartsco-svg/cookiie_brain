# 셋째날 진행 점검 — 열매·과일이 맺히는 물리 현상의 구현 분석

**관점**: 상태·중력·필드 위 한 점에서 시작한 운동이 물리 법칙과 맞닿아 환경이 설정되는 구조. 기어·포트·상태공간만으로 서술.

---

## 1. “열매·과일이 맺힌다”를 물리·상태공간으로 정의

시스템 안에서 **재현해야 할 현상**은 다음 네 가지로 고정한다.

| 현상 | 상태변수 / 물리량 | 조건 |
|------|-------------------|------|
| **풀·잎 성장** | B_leaf, B_root 증가 | NPP > 0, 광합성 조건 충족 (F, CO2, T, water_phase, organic_layer) |
| **목질(나무) 축적** | B_wood 증가 | 위 + O2 ≥ O2_threshold → NPP 분배에서 a_wood 비중 증가 |
| **씨·열매 풀 축적** | B_seed 증가 | B_leaf + B_root + B_wood ≥ B_threshold_seed 일 때 NPP 일부를 B_seed로 전이 |
| **씨 발아·재진입** | B_seed 감소 → B_leaf/root 증가 | T·수분 조건 만족 시 germ_rate × B_seed 만큼 생체량으로 전환 |

즉, **열매·과일이 맺힌다** =  
- **B_seed**가 임계 이상 생체량에서 **시간에 따라 누적**되고,  
- **B_wood**가 O2 상승 구간에서 **NPP의 일부가 목질로 배분**되며,  
- **B_seed**는 조건이 맞을 때 **발아**로 다시 B_leaf/root로 들어가는 **폐루프**.

이걸 **입력(env) → 상태 갱신 → 출력(feedback)** 한 번에 처리하는 기어가 **BiosphereColumn**이다.

---

## 2. 현재 구현 상태 (코드 기준)

### 2.1 땅·바다 분리 (surface) — 완료·연동됨

| 항목 | 파일 | 상태 |
|------|------|------|
| 유효 알베도 | solar/surface/surface_schema.py | SurfaceSchema, effective_albedo() 구현됨 |
| surface → atmosphere | brain_core_bridge.create_default_environment() | albedo = sfc.effective_albedo() 로 column에 전달 |
| 검증 | examples/surface_day3_demo.py | P7-1~P7-4 |

→ **셋째날 1단계(땅·바다, A_eff)** 는 한 기어로 정합되어 있고, 브릿지·데모에서 사용 중.

### 2.2 식생(풀·나무·씨) 상태 갱신 (biosphere) — 구현됨, 미연동

| 항목 | 파일 | 상태 |
|------|------|------|
| 선구·유기층 | solar/biosphere/pioneer.py | NPP_pioneer, organic_layer ODE 구현 |
| 광합성 조건 | solar/biosphere/photo.py | photo_ready(organic_layer, pioneer, water_phase) |
| GPP/NPP·호흡 | solar/biosphere/photo.py | gpp(), respiration() |
| B_leaf/root/wood ODE | solar/biosphere/column.py | NPP 분배, a_leaf/root/wood/seed, O2에 따른 a_wood/a_seed 증가 |
| B_seed 축적·발아·소실 | solar/biosphere/column.py | B_total ≥ B_THRESHOLD_SEED → to_seed, germ, M_SEED |
| 피드백 계산 | solar/biosphere/column.py | delta_CO2, delta_O2, transpiration, latent_heat_W, delta_albedo_land 반환 |

→ **열매·과일이 맺히는 물리 현상**은 **BiosphereColumn.step(env, dt)** 안에 이미 구현되어 있음.  
부족한 것은 **이 기어를 메인 루프에 끼우고, 출력을 대기/표면에 되먹이는 배선**이다.

### 2.3 브릿지·대기와의 배선 — 미완

| 항목 | 현재 | 문제 |
|------|------|------|
| biosphere 호출 | brain_core_bridge.py | **없음**. get_solar_environment_extension() 에서 engine + atmospheres 만 사용 |
| env 구성 | — | F_solar_si, T_surface, P_surface, CO2, H2O, O2, water_phase, land_fraction 을 atmosphere.state() + surface 에서 모아서 biosphere에 넘겨야 함 |
| delta_CO2 / delta_O2 | — | BiosphereColumn 반환값을 **대기 조성(composition)** 에 반영하는 경로 없음. AtmosphereColumn.composition 은 수정 가능 객체이나, 호출하는 쪽에서 갱신하지 않음 |
| delta_H2O / 잠열 | — | column.step() 내부의 water_cycle 은 있으나, biosphere 증산·잠열을 더해 넣는 경로 없음 |
| delta_albedo_land | — | SurfaceSchema.albedo_land 는 생성 시 고정. Biosphere 피드백으로 육지 알베도를 갱신하는 경로 없음. AtmosphereColumn.albedo 도 step() 마다 갱신되지 않음 |

→ **열매·과일이 맺히는 루프**가 **대기·표면과 닫히려면**,  
브릿지(또는 동등한 오케스트레이션)에서 **biosphere 실행 + feedback 적용**이 필요하다.

---

## 3. 갭 정리 — 완성을 위해 필요한 것

### 3.1 필수 (루프 닫기)

1. **브릿지에서 BiosphereColumn 생성·유지**  
   - create_default_environment() 또는 동등한 진입점에서, 지구용 BiosphereColumn 인스턴스 생성 (land_fraction 등 surface와 일치).

2. **get_solar_environment_extension() 내부에서 매 스텝**  
   - engine.step() 후, 각 body에 대해 atmosphere.step(F, dt) 까지 한 뒤,  
   - 해당 body용 env dict 구성:  
     F_solar_si, T_surface, P_surface, composition.CO2, composition.H2O, composition.O2, water_phase, (옵션) land_fraction, soil_moisture.  
   - 지구면 biosphere.step(env, dt_yr) 호출.  
   - 반환된 feedback으로:  
     - **대기 조성**: composition.CO2, composition.O2, composition.H2O 에 feedback["delta_CO2"], feedback["delta_O2"], (증산에 상응하는 delta_H2O) 를 **단위 맞춰** 가산.  
     - **잠열**: column이 받을 수 있도록 surface_heat_flux 또는 내부 _Q_latent 에 feedback["latent_heat_biosphere_W"] 가산.  
     - **알베도**: SurfaceSchema.albedo_land 갱신 또는 column.albedo 갱신(column이 albedo를 step()에서 읽도록 되어 있다면).  

3. **단위 환산**  
   - delta_CO2, delta_O2: BiosphereColumn은 [kg C/m²/yr], [kg O2/m²/yr] 형태로 줄 수 있음.  
   - 대기 조성은 [mol/mol]. column_mass, 몰질량으로 “연간 변화율 → dt_yr 만큼 썼을 때 mixing ratio 변화량”으로 변환하는 식을 한 곳에 명시.

### 3.2 선택 (안정성·관측)

4. **AtmosphereColumn**  
   - albedo를 step() 마다 외부에서 줄 수 있게 하거나, set_albedo() 같은 setter 추가.  
   - (선택) apply_biosphere_feedback(delta_CO2_mol, delta_O2_mol, delta_H2O_mol, delta_LE_Wm2) 같은 API로 한 번에 넣을지 결정.

5. **SurfaceSchema**  
   - albedo_land를 mutable로 두고, 브릿지에서 feedback["delta_albedo_land"]로 매 스텝 갱신할지,  
   - 또는 “base_land_albedo + biosphere_delta”를 별도 변수로 두고 column에만 넘길지 결정.

6. **검증 데모**  
   - biosphere_evolution_demo.py 또는 기존 데모 확장:  
     engine + atmospheres + surface + **biosphere** 를 묶어서,  
     시간 진행에 따라 B_leaf, B_wood, B_seed, O2, CO2, albedo 가 변하는지 수치로 확인.

---

## 4. 요약 표

| 구분 | 내용 | 상태 |
|------|------|------|
| **땅·바다** | surface_schema, A_eff, 브릿지·데모 연동 | ✅ 완료 |
| **풀·나무·씨 물리** | B_leaf/root/wood/seed ODE, B_seed 축적·발아, O2에 따른 a_wood/a_seed | ✅ biosphere/column.py 에 구현됨 |
| **브릿지에서 biosphere 호출** | env 구성 → step() → feedback 수집 | ❌ 미구현 |
| **feedback → 대기** | delta_CO2, delta_O2, delta_H2O, 잠열 → composition / column | ❌ 미구현 |
| **feedback → 표면** | delta_albedo_land → albedo 반영 | ❌ 미구현 |
| **단위 환산** | kg C·O2/m²/yr → mol/mol, 잠열 가산 | ❌ 미구현 |
| **데모** | biosphere 포함 루프·수치 검증 | ❌ 없음 |

---

## 5. 결론

- **“열매·과일이 맺히는” 현상**은 **상태변수 B_seed, B_wood**의 누적·발아·분배로 이미 **BiosphereColumn** 안에 정의되어 있다.  
- **갭**은 **이 기어를 메인 환경 루프에 끼우고, 출력(delta_CO2, delta_O2, 증산, 잠열, delta_albedo_land)을 대기·표면에 되먹이는 배선**이다.  
- 완성을 위해 필요한 작업은 **브릿지(또는 동등 레이어)에서 biosphere 생성·step 호출·feedback 적용·단위 환산**을 추가하고, 필요 시 column/surface 쪽에 albedo·조성 갱신 API를 두는 것이다.
