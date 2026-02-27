## PORTS_AND_UNITS — 레이어 간 포트 및 단위 요약

Creation Days 레이어들이 닫힌 루프로 연결되기 위해,  
각 모듈이 **무엇을 어떤 단위로 입력/출력하는지**를 한 곳에 정리한 표입니다.

### 1. Atmosphere / Surface / Radiation

| Layer / Struct | Port 이름 | 의미 | 단위 |
|----------------|----------|------|------|
| `SolarLuminosity` | `irradiance_si(r)` | 거리 r에서의 태양 복사 조도 | W/m² |
| `SolarLuminosity` | `equilibrium_temperature` | 대기 없는 평형 온도 | K |
| `SurfaceSchema` | `land_fraction` | 육지 비율 | - |
| `SurfaceSchema` | `albedo_land`, `albedo_ocean` | 땅/바다 알베도 | - |
| `SurfaceSchema` | `effective_albedo()` | 전체 행성 유효 알베도 | - |
| `AtmosphereComposition` | `CO2`, `O2`, `H2O`, `CH4` | 대기 조성 몰분율(mixing ratio) | mol/mol (예: 400e-6) |
| `AtmosphereComposition` | `column_mass` | 대기 기둥 질량 | kg/m² |
| `AtmosphereColumn.state` | `T_surface` | 지표 온도 | K |
| `AtmosphereColumn.state` | `P_surface` | 지표 기압 | Pa |
| `AtmosphereColumn.state` | `water_phase` | 물 상태 | `"ice"`, `"liquid"`, `"vapor"` |
| `AtmosphereColumn` | `surface_heat_flux()` | 표면 열 플럭스 | W/m² |

### 2. Biosphere / Fire / Gaia (Day 3)

| Layer / Struct | Port 이름 | 의미 | 단위 |
|----------------|----------|------|------|
| `BiosphereColumn.step` | `delta_CO2` | 육지 단위 면적당 대기 CO₂ 플럭스 | kg C/m²/yr |
| `BiosphereColumn.step` | `delta_O2` | 육지 단위 면적당 대기 O₂ 플럭스 | kg O₂/m²/yr |
| `BiosphereColumn.step` | `delta_H2O` | 육지 단위 면적당 대기 H₂O 플럭스 | kg H₂O/m²/yr |
| `BiosphereColumn.step` | `delta_albedo_land` | 육지 알베도 변화량 | - / yr |
| `BiosphereColumn.step` | `GPP`, `Resp`, `NPP` | 탄소 플럭스 | kg C/m²/yr |
| `biosphere_feedback_to_atmosphere` | `delta_CO2_mixing` | 조성 변화 | mol/mol per step |
| `biosphere_feedback_to_atmosphere` | `delta_O2_mixing` | 조성 변화 | mol/mol per step |
| `biosphere_feedback_to_atmosphere` | `delta_H2O_mixing` | 조성 변화 | mol/mol per step |
| `biosphere_feedback_to_atmosphere` | `extra_latent_heat_Wm2` | 추가 잠열 플럭스 | W/m² |
| `FireEnvSnapshot` | `O2_frac` | 대기 O₂ 분율 | mol/mol |
| `FireEnvSnapshot` | `CO2_ppm` | 대기 CO₂ | ppm |
| `FireEnvSnapshot` | `time_yr` | 연 단위 시간 | yr |
| `FireEngine.predict` | `CO2_source_kgC` | 산불에 의한 탄소 소스 | kg C/m²/yr |
| `FireEngine.predict` | `O2_sink_kg` | 산불에 의한 산소 소비 | kg O₂/m²/yr |
| `FireEngine.predict` | `global_fire_index` | 전지구 산불 지수 | - |

### 3. Nitrogen (Day 4 — 순환 1)

| Layer / Struct | Port 이름 | 의미 | 단위 |
|----------------|----------|------|------|
| `NitrogenFixation` | `rate_fix` | 질소 고정 속도 | g N/m²/yr |
| `NitrogenCycle.state` | `N_soil` | 토양 질소 저장량 | g N/m² |
| `NitrogenCycle.state` | `N_limitation` | GPP 제한 계수 | - |

### 4. Milankovitch / Insolation (Day 4 — 순환 2)

| Layer / Struct | Port 이름 | 의미 | 단위 |
|----------------|----------|------|------|
| `MilankovitchCycle` | `eccentricity(t)` | 궤도 이심률 | - |
| `MilankovitchCycle` | `obliquity(t)` | 경사각 | rad 또는 deg (README에서 명시) |
| `MilankovitchCycle` | `insolation_summer_solstice(t, φ)` | 하지 일사량 | W/m² |
| `MilankovitchCycle` | `insolation_scale(t, φ)` | 현재 대비 상대 하지 일사량 | - |
| `insolation_at` | `Q(t, φ)` | 위도별 연평균 일사량(ψ 미포함) | W/m² |
| `MilankovitchDriver` | `DriverOutput.obliquity_deg` | 경사각 | deg |
| `MilankovitchDriver` | `DriverOutput.is_glacial` | 빙하기 여부 플래그 | bool |

### 5. Gravity Tides / Ocean (Day 4 — 순환 3)

| Layer / Struct | Port 이름 | 의미 | 단위 |
|----------------|----------|------|------|
| `TidalField` | `upwelling_uM` | 심층 영양염 용승 | μmol/L/yr (approx) |
| `OceanNutrients.state` | `C_surface` | 표층 영양염 농도 | μmol/L |
| `OceanNutrients.state` | `phyto_biomass` | 식물플랑크톤 질량 | arbitrary units |
| `OceanNutrients.state` | `CO2_sink_ppm` | 대기 CO₂ 격리량 | ppm/yr |

### 6. Day 5 — 생물 이동 / 정보 네트워크

| Layer / Struct | Port 이름 | 의미 | 단위 |
|----------------|----------|------|------|
| `BirdAgent` | `migration_rates(o2_frac)` | 위도별 이동률 | 1/yr |
| `BirdAgent` | `seed_flux(B_pioneer)` | 밴드별 씨드 분산 플럭스 (Loop F) | 1/yr (rate) |
| `BirdAgent` | `guano_flux()` | 밴드별 구아노 N 플럭스 (Loop G) | g N/m²/yr |
| `FishAgent` | `predation_flux(phyto_by_band)` | 밴드별 phyto 포식 플럭스 (Loop H) | 1/yr (rate) |
| `SeedTransport` | `step(B, dt_yr)` | 보존형 스칼라 필드 transport | B 동일 단위 |
| `SeedTransport` | `step_with_source(B, source_flux, dt_yr)` | source 가산 보존형 transport | B 동일 단위 |
| `TrophicState` | `phyto`, `herbivore`, `carnivore` | 트로픽 바이오매스 | arbitrary (일관된 스케일) |
| `TrophicState` | `co2_resp_yr` | 해당 스텝 연간 환산 호흡 CO₂ | kgC/m²/yr |
| `FoodWeb` | `net_co2_flux(state, gpp)` | GPP 흡수 − 호흡 (대기 CO₂ 가산) | kgC/m²/yr |

> 이 문서는 코드와 함께 유지보수되어야 하며,  
> 포트 단위가 변경될 경우 **반드시 이 표를 업데이트** 해야 합니다.

