# Biosphere 레이어 사양 — 셋째날 이후, 척박→선구→광합성→대기 변화→호흡 식생

**목적**: 창 1:11 “땅은 풀과 씨 맺는 채소와 씨 가진 열매 맺는 나무를 내라”를  
**물리·화학 순환**으로 구현한다.  
단, “환경이 갑자기 준비된” 게 아니라 **척박한 환경에서 선구 생물이 먼저 살아남고**,  
그 위에 광합성이 켜지고, 대기 조성이 바뀌면서 **호흡형(후기) 식생**이 따라나오는 **추론 단계**를 반영한다.

---

## 1. 단계별 로직 (추론 순서)

| 단계 | 환경 상태 | 생물 역할 | 상태변수 / 현상 |
|------|-----------|-----------|------------------|
| **0** | 셋째날 직후 — 땅/바다 분리됐지만 척박 (T 극단, 물 부족, 유기물 없음) | 없음 | surface/만 있음, 대기 조성 원시 |
| **1** | **선구 생태계** — 균사체·이끼·지의류류가 극소 조건에서 생존 | 물·온도만으로도 견딤, 광합성 거의 없거나 극히 낮음 | `pioneer_biomass`, `organic_layer` 증가 |
| **2** | 선구가 **유기층·수분 보유**를 만들면 → 광합성 조건 충족 | 빛 + CO₂ + 물 + T 범위 → GPP | `B_leaf`, `B_root`, `B_wood`, NPP > 0 |
| **3** | 광합성 → **O₂ 배출**, CO₂ 감소 | 대기 조성 변화 | `AtmosphereComposition.O2` 상승, τ(조성) 변화 |
| **4** | O₂가 일정 이상이면 **호흡형(후기) 식생** 가능 | 산소 호흡으로 고에너지 대사, 나무·씨/열매 전략 | `B_wood`, `B_seed` 비중 증가, 또는 별도 풀 |

즉, **“척박 → 선구 생존 → 광합성 → 대기 형성 변화 → 호흡 식물”** 순서를 한 번에 점프하지 않고 **조건부로** 만든다.

---

## 2. 기존 레이어와의 포트 (입력/출력)

### 2.1 Biosphere가 **읽는** 것 (입력)

| 입력 | 의미 | 출처 |
|------|------|------|
| `F_solar_si` | 복사 조도 [W/m²] | `solar_luminosity.irradiance_si(r)` |
| `T_surface` | 표면 온도 [K] | `AtmosphereColumn.state(F).T_surface` |
| `P_surface` | 대기압 [Pa] | `AtmosphereColumn.state(F).P_surface` |
| `CO2`, `H2O`, `O2` | 대기 조성 [mol/mol] | `AtmosphereComposition` |
| `water_phase` | 액체/고체/기체 | `AtmosphereColumn.state(F).water_phase` |
| `surface_heat_flux` | 지표 에너지 수지 [W/m²] | `AtmosphereColumn.surface_heat_flux()` |
| `land_fraction`, `A_eff` | 육지 비율, 유효 알베도 | `SurfaceSchema` |
| (옵션) `soil_moisture` | 토양 수분 0~1 | 선구가 만든 `organic_layer`로부터 유도 또는 별도 상태 |

### 2.2 Biosphere가 **내보내는** 것 (출력 → 상위 레이어 피드백)

| 출력 | 의미 | 반영 위치 |
|------|------|------------|
| `delta_CO2` | 광합성/호흡에 의한 CO₂ 변화율 | `AtmosphereComposition.CO2` 갱신 |
| `delta_O2` | 광합성에 의한 O₂ 증가율 | `AtmosphereComposition.O2` 갱신 |
| `delta_H2O` | 증산에 의한 수증기 증가 | `AtmosphereComposition.H2O` 또는 water_cycle 연동 |
| `latent_heat_flux_biosphere` | 증산 잠열 [W/m²] | `surface_heat_flux`에 가산 |
| `delta_albedo_land` | 식생 피복에 의한 육지 알베도 변화 | `SurfaceSchema` 또는 extension으로 전달 |
| `organic_layer` | 선구가 쌓은 유기물/토양 개선 지표 | Biosphere 내부 + “광합성 허용 조건” 판정에 사용 |

**규칙**: `core/`(궤도·중력)는 건드리지 않는다. `em/`, `atmosphere/`, `surface/`와만 **읽기·쓰기**로 연결한다.

---

## 3. 상태 변수 (최소 집합)

### 3.1 선구 생태계 (Phase 7b-1: Pioneer)

| 변수 | 단위 | 의미 |
|------|------|------|
| `pioneer_biomass` | [kg C/m²] 또는 무차원 | 균사체·이끼·지의류에 해당하는 생체량. 척박한 조건에서만 성장/사망 |
| `organic_layer` | [kg C/m²] 또는 무차원 | 선구가 만든 유기물·토양 개선. 수분 보유·영양 공급 역할. 감쇠(분해) 있음 |

### 3.2 광합성 식생 (Phase 7b-2: Photosynthetic)

| 변수 | 단위 | 의미 |
|------|------|------|
| `B_leaf` | [kg C/m²] | 잎 생체량 |
| `B_root` | [kg C/m²] | 뿌리 생체량 |
| `B_wood` | [kg C/m²] | 줄기/목질 (나무) |
| `B_seed` | [kg C/m²] | 씨/열매 풀 (잠복·번식) |

### 3.3 호흡형/후기 식생 (Phase 7b-3: Successional, O₂ 의존)

- **옵션 A**: 위와 같은 풀(`B_*`)을 쓰되, **성장률·사망률이 O₂ 농도에 의존**하게 함.  
  O₂ < 임계값이면 “호흡 식물” 성장률 = 0 또는 매우 낮음.
- **옵션 B**: 별도 풀 `B_leaf_successional`, `B_wood_successional` 등을 두고,  
  `O2 > O2_threshold` 일 때만 NPP 분배가 들어가게 함.

**최소 구현**: 옵션 A — 기존 `B_*`에 **O₂ 제한 계수** `f_O2(O2)`를 곱해서 “호흡 식물” 비중을 키움.

---

## 4. 수식 (물리·개념 공식)

### 4.1 선구 생장 (척박 환경 생존)

- **생장률**: 빛·CO₂보다 **물·온도**에 강하게 의존. 광합성은 극히 낮거나 0에 가깝게 둠.

  - 온도: 넓은 범위에서 생존, 최적 아님.
    \[
    f_T^{\text{pioneer}}(T) = \exp\left(-\frac{(T - T_{\text{mid}})^2}{2 \sigma_T^{\text{pioneer}\,2}}\right),\quad \sigma_T^{\text{pioneer}} \gg \sigma_T^{\text{photo}}
    \]
  - 수분: 액체 물이 있거나 혹은 `H2O`(수증기) + `organic_layer`로 “가용 수분” 보간.
    \[
    f_W = \text{clip}(\alpha_{\text{liq}} \cdot \mathbb{1}_{\text{liquid}} + \alpha_{\text{org}} \cdot \text{organic\_layer}, 0, 1)
    \]
  - 선구 순생산(극소):
    \[
    \text{NPP}_{\text{pioneer}} = r_{\text{pioneer}} \cdot f_T^{\text{pioneer}}(T) \cdot f_W
    \]
    여기서 \(r_{\text{pioneer}}\)는 작은 상수. “척박해도 조금은 자란다”를 표현.

- **유기층 축적**: 선구 생체량의 일부가 사망·분해되어 `organic_layer`로 전이.
  \[
  \frac{d\,\text{organic\_layer}}{dt} = \eta_{\text{org}} \cdot m_{\text{pioneer}} \cdot \text{pioneer\_biomass} - \lambda_{\text{decay}} \cdot \text{organic\_layer}
  \]
  \(m_{\text{pioneer}}\): 선구 사망률, \(\eta_{\text{org}}\): 전환 비율, \(\lambda_{\text{decay}}\): 유기물 분해율.

- **선구 생체량 ODE**:
  \[
  \frac{d\,\text{pioneer\_biomass}}{dt} = \text{NPP}_{\text{pioneer}} - m_{\text{pioneer}} \cdot \text{pioneer\_biomass}
  \]
  극한 T·극한 건조에서는 \(m_{\text{pioneer}}\)를 크게 해서 빠르게 줄어들게 함.

### 4.2 광합성 (조건부 활성화)

- **활성화 조건** (둘 다 만족 시에만 GPP > 0):
  1. **환경 준비**: `organic_layer >= L_{\text{thresh}}` 또는 `pioneer_biomass >= B_{\text{thresh}}` (선구가 토양/수분을 준비).
  2. **물리 조건**: 액체 물 가능(`water_phase == "liquid"`), T·F·CO₂가 허용 범위.

- **반응률 형태** (포화·종형):
  \[
  f_I(F) = \frac{F}{F + F_{1/2}},\quad
  f_C(CO_2) = \frac{CO_2}{CO_2 + K_C},\quad
  f_T(T) = \exp\left(-\frac{(T - T_{\text{opt}})^2}{2\sigma_T^2}\right),\quad
  f_W = \text{clip}(W, 0, 1)
  \]
  \[
  \text{GPP} = P_{\max}\, f_I(F)\, f_C(CO_2)\, f_T(T)\, f_W
  \]
  호흡:
  \[
  \text{Resp} = k_{\text{leaf}} B_{\text{leaf}} + k_{\text{root}} B_{\text{root}} + k_{\text{wood}} B_{\text{wood}}
  \]
  \[
  \text{NPP} = \text{GPP} - \text{Resp}
  \]

- **생체량 분배** (NPP를 잎·뿌리·목질·씨로):
  \[
  \frac{dB_{\text{leaf}}}{dt} = a_{\text{leaf}} \cdot \text{NPP} - m_{\text{leaf}} B_{\text{leaf}},\quad
  \frac{dB_{\text{root}}}{dt} = a_{\text{root}} \cdot \text{NPP} - m_{\text{root}} B_{\text{root}},\quad
  \frac{dB_{\text{wood}}}{dt} = a_{\text{wood}} \cdot \text{NPP} - m_{\text{wood}} B_{\text{wood}}
  \]
  씨: 생체량이 임계 이상일 때 일부를 `B_seed`로 전이, 발아·소실 항 추가 (이전 분석과 동일).

### 4.3 대기 피드백 (O₂, CO₂)

- **광합성 시**:
  \[
  \Delta CO_2 = -\frac{1}{A_{\text{land}}} \cdot \frac{\text{GPP}}{M_C},\quad
  \Delta O_2 = +\frac{1}{A_{\text{land}}} \cdot \frac{\text{GPP}}{M_O}
  \]
  (단위 맞추기: GPP [kg C/m²/yr], 대기 컬럼 mol/mol 변환은 column_mass 등으로 스케일.)
- **호흡 시**: 반대 부호.  
  실제 구현에서는 `delta_CO2`, `delta_O2`를 **연간 또는 dt당 변화율**로 두고,  
  `AtmosphereColumn` 또는 호출자가 조성에 반영.

### 4.4 호흡형(후기) 식생 (O₂ 의존)

- **O₂ 계수**:
  \[
  f_{O2}(O_2) = \frac{O_2}{O_2 + K_{O2}}
  \]
  또는 계단: \(O_2 \ge O_{2,\text{thresh}}\) 일 때만 “후기” NPP 분배를 넣음.
- **나무·씨 비중**: \(f_{O2}\)가 클수록 \(a_{\text{wood}}\), \(a_{\text{seed}}\)를 키우면 “O₂가 올라가면 나무·열매가 늘어난다”는 로직이 됨.

---

## 5. 의존 방향 및 호출 순서

```
data/ → core/ ← em/
              ← atmosphere/  ← biosphere/
              ← surface/        │
                                ├ 읽기: F, T, P, CO2, H2O, O2, water_phase, land_fraction, A_eff
                                └ 쓰기: delta_CO2, delta_O2, delta_H2O, latent_heat_flux_biosphere, delta_albedo_land
```

- **한 스텝 안에서**: `atmosphere.step(F, dt)` 후에 `biosphere.step(env, dt)` 호출.  
  biosphere가 내보낸 `delta_*`를 다음 스텝의 `AtmosphereComposition`에 반영하거나,  
  같은 스텝 끝에서 composition을 갱신해도 됨 (명세만 맞추면 됨).

---

## 6. 요약

- **셋째날**까지는 땅/바다만 분리되고, **환경은 아직 척박**하다고 가정.
- **선구 생물**(균사·이끼·지의류)이 **극소 조건**에서만 생장·사망하며 **organic_layer**를 쌓고,
- **organic_layer(또는 pioneer_biomass)**가 임계를 넘고 물리 조건이 맞을 때 **광합성**이 켜지고,
- 광합성으로 **O₂ 상승·CO₂ 감소**가 나오면,
- **O₂ 임계 이상**에서 **호흡형(후기) 식생**(나무·씨/열매 비중 증가)이 가능해진다.

이 순환 구조를 **상태변수·수식·포트**로 구현하는 것이 Biosphere 레이어의 목표다.
