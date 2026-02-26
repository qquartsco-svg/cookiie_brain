# solar/ 버전 로그 / Version Log

## v1.8.0 — 셋째날: 식물 생애주기 Phase Gate ODE (Phase 7c)

**날짜**: 2026-02-26 (session 3)
**작업**: 씨→싹→줄기→나무→열매 생애주기 — dt 버그 수정 + softmax allocation + Phase Gate ODE

| 파일 | 설명 |
|------|------|
| `solar/biosphere/column.py` | Phase Gate ODE 전면 재작성 (dt 이중적용 수정, softmax 정규화) |
| `solar/biosphere/_constants.py` | Phase Gate 파라미터 추가 (K_germ, K_sprout_to_stem, K_stem_to_wood, K_fruit) |
| `solar/biosphere/state.py` | B_sprout, B_stem, B_fruit, mineral_layer, succession_phase 추가 |
| `examples/plant_lifecycle_sim.py` | 신규 — 식물 생애주기 시뮬레이션 |

핵심 수정 3가지:
```
1. dt 이중 적용 버그 수정
   이전: to_seed = K × B × dt  →  B += to_seed × dt  (dt²)
   수정: d_rate = K × B [율]   →  B += d_rate × dt   (dt¹, 한 번만)

2. softmax allocation (탄소 회계 정합)
   이전: a_leaf + a_root + a_wood + a_seed ≠ 1 (정규화 없음)
   수정: alloc = softmax(logits(O₂, phase)) → sum = 1 보장

3. Phase Gate ODE (씨→싹→줄기→나무→열매)
   B_seed   → K_germ × g_soil(S) × g_T × f_W            → B_sprout
   B_sprout → K_sprout_to_stem × sigmoid(B_sp/B_sp_half) → B_stem
   B_stem   → K_stem_to_wood   × sigmoid(B_st/B_st_half) → B_wood
   B_wood   → K_fruit × maturity × f_O2                  → B_fruit
   B_fruit  → K_fruit_to_seed                             → B_seed ↺
```

파라미터 (관측 기반):
| 파라미터 | 값 | 근거 |
|----------|-----|------|
| K_GERM | 0.5 /yr | 발아 ~2년 |
| K_SPROUT_TO_STEM | 0.25 /yr | 유묘→줄기 ~4년 |
| K_STEM_TO_WOOD | 0.08 /yr | 목질화 ~12년 |
| K_FRUIT | 0.15 /yr | 첫 결실 ~7년 |
| B_WOOD_FRUIT_TH | 1.0 kg C/m² | 성목 임계 |

시뮬레이션 결과 (plant_lifecycle_sim.py):
```
1yr:  싹 발아 (B_sprout > 0.001)
4yr:  줄기 형성 (B_stem > 0.01)
~5yr: 나무 성장 (B_wood > 0.1)
열매: ★ B_fruit > 0.01 → B_seed ↺ 순환 닫힘
```

셋째날 완성 흐름:
```
[돌땅] →(2739yr)→ 원시토양 →(1yr)→ 싹 →(4yr)→ 줄기 → 나무 → ★열매 → 씨 ↺
```

---

## v1.7.0 — 셋째날: 토양 형성 ODE (Phase 7b — 선구 생물)

**날짜**: 2026-02-26 (session 2)
**작업**: pioneer 로지스틱 성장 + 풍화 + Q10 분해 — 세차운동과 동일한 설계 철학

| 파일 | 설명 |
|------|------|
| `solar/biosphere/pioneer.py` | ODE 3변수 재작성 (d_pioneer, d_organic, d_mineral) |
| `solar/biosphere/_constants.py` | 물리 파라미터 현실화 (관측 기반) |
| `solar/biosphere/column.py` | mineral_layer 상태변수 추가, 3-return 연결 |
| `examples/biosphere_day3_demo.py` | 검증 조건 수정 |
| `examples/soil_formation_sim.py` | 신규 — 토양 형성 시뮬레이션 (2739년) |

물리 (세차운동과 동일한 방식):
```
세차: G·M·r  입력 → 25,000년 주기 출력
토양: R·W·ETA·λ 입력 → 2739년 원시토양 출력
```

ODE:
```
dP/dt = R·P·(1-P/K(S))·fT·fW - M·P   [로지스틱]
dM/dt = W_w·P·fT·fW                    [풍화]
dS/dt = ETA·M·P + W_mh·M - λ(T)·S    [humus, Q10]
K(S)  = K0 + K_soil·S                  [양성 피드백]
```

결과:
- 토양 임계 도달: **2739년** (관측 지구 평균 범위 내)
- `biosphere_day3_demo.py`: ALL PASS

---

## v1.6.0 — 셋째날: 땅과 바다의 분리 (Phase 7)

**날짜**: 2026-02-26
**작업**: 땅-바다 분리, 유효 알베도 → atmosphere 연동

| 파일 | 설명 |
|------|------|
| `solar/surface/` | SurfaceSchema, effective_albedo (땅 비율, A_land, A_ocean) |
| `solar/surface/surface_schema.py` | A_eff = f_land×A_land + (1-f_land)×A_ocean |
| `solar/__init__.py` | SurfaceSchema, effective_albedo export |
| `examples/surface_day3_demo.py` | Phase 7 검증 (4항목 ALL PASS) |
| `docs/CREATION_DAYS_AND_PHASES.md` | 창세기 관점 날짜-Phase 대응 |

물리:
- 땅 비율 f_land (지구 ≈ 0.29)
- 육지/해양 알베도 A_land, A_ocean
- 유효 알베도 → AtmosphereColumn albedo 입력

검증 (ALL PASS):
- SurfaceSchema A_eff (지구 f_land=0.29)
- 전 바다 vs 전 육지 알베도 차이
- surface → atmosphere 연동, T_eq 영향
- 땅 비율 증가 시 냉각 (A↑ → T↓)

---

## v1.6.1 — CookiieBrain ↔ BrainCore 연동 (GEAR Phase 1)

**날짜**: 2026-02-26
**작업**: solar 환경 상태를 GlobalState extension으로 노출

| 파일 | 설명 |
|------|------|
| `solar/brain_core_bridge.py` | get_solar_environment_extension, create_default_environment |
| `examples/brain_core_environment_demo.py` | BrainCore 연동 데모 |
| `docs/BRAINCORE_INTEGRATION.md` | extension 형식, 사용법 |
| `docs/MINIMUM_REACTION_MODEL_DESIGN.md` | 자가순환 최소 반응 모델 통합 설계 |

연동:
- `state.set_extension("solar_environment", data)`
- data: bodies[Earth].F_solar, T_surface, P_surface, habitable, water_phase

---

## v1.5.0 — 수순환 / Water Cycle (Phase 6b)

**날짜**: 2026-02-26
**작업**: 증발·응결·잠열 + surface_heat_flux → SurfaceOcean 연동

| 파일 | 설명 |
|------|------|
| `solar/atmosphere/water_cycle.py` | Clausius-Clapeyron, evaporation_rate, latent_heat_flux |
| `solar/atmosphere/column.py` | use_water_cycle, H₂O 피드백, latent heat in step() |
| `solar/core/evolution_engine.py` | SurfaceOcean.update(heat_flux), step(ocean_extras) |
| `examples/water_cycle_demo.py` | Phase 6b 검증 (5항목 ALL PASS) |
| `docs/ATMOSPHERE_NUMERICAL_VERIFICATION.md` | Phase 6a 수치 안정성 기록 |

물리 모델:
- Clausius-Clapeyron: e_sat(T) = 611.2 exp(17.67×T_c/(T_c+243.5))
- 증발율: E = C_E × ρ × U × (q_sat - q_actual)
- 잠열: Q_latent = L_v × E (증발 냉각)
- H₂O 피드백: τ_relax toward q_sat
- ocean_extras: {"Earth": {"heat_flux": float}} → depths 수정

검증 (ALL PASS):
- e_sat(273K) ≈ 611 Pa, e_sat(373K) ≈ 101 kPa
- 잠열 포함 시 T 감소 (증발 냉각)
- H₂O 포화 수렴
- surface_heat_flux → ocean depths 연동
- 기어 분리: core는 atmosphere import 없음, dE/E < 1e-5

---

## v1.4.0 — 궁창 / Firmament: 대기권 레이어 (Phase 6a)

**날짜**: 2026-02-25
**작업**: 온실 효과 + 열적 관성 + 동적 대기 조성 → 표면 온도·압력·물 상태

| 파일 | 설명 |
|------|------|
| `solar/atmosphere/__init__.py` | 대기권 패키지 공개 API |
| `solar/atmosphere/_constants.py` | 대기 물리 상수 (SI) |
| `solar/atmosphere/greenhouse.py` | τ(composition) → ε_a → T_surface (1-layer 모델) |
| `solar/atmosphere/column.py` | AtmosphereColumn: 열적 관성 ODE + 동적 조성 |
| `solar/__init__.py` | atmosphere/ 패키지 등록 + v1.4.0 |
| `examples/atmosphere_demo.py` | Phase 6a 검증 (8항목 ALL PASS) |

물리 모델:
- 1-layer 복사 전달: ε_a = 1 - exp(-τ), T_s = [F(1-A)/(f·σ·(1-ε_a/2))]^(1/4)
- 열적 관성: C · dT/dt = F_absorbed - F_radiated (linearized implicit)
- 광학 깊이: τ = τ_base + α_CO₂·ln(1+CO₂/ref) + α_H₂O·√(H₂O/ref) + α_CH₄·√(CH₄/ref)
- 대기 조성은 동적 상태 변수 (고정 상수 아님)
- 대기압: P = M_col × g

검증 (ALL PASS):
- 온실 효과: T_eq 254K → T_surface 288K (+34K)
- 대기 없음: τ=0, ε_a=0 → T_surface = T_eq
- CO₂ 대수 응답 (포화): 10× CO₂ → 6.9× τ 증가
- H₂O 주요 기여자: Δτ(H₂O) = 0.643
- 열적 관성: τ_thermal ≈ 2.0 yr (해양 지배)
- Cold/hot start 수렴: 200K/400K → 288K (오차 < 0.001K)
- 대기압: 101,357 Pa (1.000 atm), 액체 물 ✓
- 화성: P=632 Pa, T=210K, 고체 (비거주)
- 초기 지구 (70% Sun): T=289K, 거주 가능 (Faint Young Sun 해결)
- 기어 분리: dE/E = 4.06×10⁻¹² (core 무결)

---

## v1.3.1 — 복사-플라즈마 독립 분리 (피드백 반영)

**날짜**: 2026-02-25
**작업**: 복사(photons)와 플라즈마(solar wind)의 물리적 독립성 확보

| 파일 | 설명 |
|------|------|
| `solar/em/solar_wind.py` | `radiation_ratio` 파라미터 제거, `radiation_pressure()` 메서드 삭제 |
| `solar/em/solar_wind.py` | `SolarWindState`에서 `radiation_pressure` 필드 삭제 — 플라즈마만 남김 |
| `solar/em/solar_luminosity.py` | `P0_sw` 파라미터 제거, `radiation_pressure_normalized()` 삭제 |
| `solar/em/solar_luminosity.py` | `emissivity` (ε) + `redistribution` (f) 파라미터 추가 |
| `solar/em/solar_luminosity.py` | T_eq = [F(1-A)/(f·ε·σ)]^¼ 일반형으로 확장 |
| `examples/let_there_be_light_demo.py` | P5-4를 "복사 vs 플라즈마 독립 입력" 검증으로 재작성 |
| `examples/em_layer_demo.py` | `radiation_pressure` 참조 제거 |

물리적 수정 근거:
- 복사압 P_rad = F/c (광자 운동량 전달) — 광도(L)에서 유도
- 태양풍 동압 P_sw = ρv² (플라즈마 압력) — 독립 물리량
- 둘은 같은 단위(Pa)이지만 물리적 원인이 다르므로 하나에서 다른 하나를 유도하면 안 됨
- P_rad(1 AU) ≈ 4.54 μPa >> P_sw(1 AU) ≈ 2 nPa (비율 ~2270:1)
- 자기권(magnetopause)은 P_sw만으로 결정됨 (광자는 자기장과 상호작용하지 않음)

검증: ALL PASS (let_there_be_light_demo, em_layer_demo)

---

## v1.3.0 — 빛이 있으라 / Let There Be Light (Solar Luminosity)

**날짜**: 2026-02-25
**작업**: 태양 광도·복사 조도·평형 온도 레이어 + 전체 체인 검증

| 파일 | 설명 |
|------|------|
| `solar/em/solar_luminosity.py` | 질량-광도 관계 L∝M^α, 복사 조도 F=L/(4πr²), 복사압, 평형 온도 |
| `solar/em/__init__.py` | SolarLuminosity, IrradianceState 공개 |
| `solar/__init__.py` | 패키지 공개 API 업데이트 + __version__ = "1.3.0" |
| `examples/let_there_be_light_demo.py` | Phase 5 검증 — 빛이 있으라 |
| `docs/LET_THERE_BE_LIGHT_LOG.txt` | Phase 5 검증 출력 로그 |
| `solar/README.md` | Phase 5 개념 문서 추가 |

검증 (ALL PASS):
- 질량-광도: L(1.0 M☉) = 1.0000 L☉ (오차 0.00)
- 역제곱 법칙: F ∝ 1/r² — 8행성 전부 0.000%
- 지구 평형 온도: 254.0 K (이론 255 K, 오차 0.4%)
- 복사압-태양풍 연동: 비율 1.0000 (5행성)
- 기어 분리: dE/E = 4.49e-10 (core 무결)

의미:
  중력장이 공간을 지배하고, 행성이 궤도를 돌고,
  자기장이 방어막을 세운 그 위에 — 마침내 빛이 켜졌다.
  형태가 생기고, 그림자가 생기고, 존재의 의미가 시작되었다.

---

## v1.2.2 — EM 레이어 개념 문서화

**날짜**: 2026-02-25
**작업**: README에 전자기 레이어 물리 개념 해설 추가

| 파일 | 설명 |
|------|------|
| `solar/README.md` | "전자기 레이어 개념 / EM Layer Concepts" 섹션 추가 |

추가 내용:
- Phase 2 (자기쌍극자): 물리 개념, B ∝ 1/r³ 수식, 세차 연동 원리, 코드 흐름
- Phase 3 (태양풍): 동압·플럭스·복사압·IMF 각각의 역할, 1/r² 감쇠 이유
- Phase 4 (자기권): Chapman-Ferraro 균형, 1/6 지수 유도, 자기권 구조 다이어그램
- 3개 Phase 체인 연결 흐름도
- 1/r³ vs 1/r² 감쇠 법칙 차이와 마그네토포즈 생성 원리

---

## v1.2.1 — 문서 정비 + EPS 중앙 관리

**날짜**: 2026-02-25
**작업**: 피드백 기반 README 강화 + em/ 코드 정비

| 파일 | 설명 |
|------|------|
| `solar/README.md` | 통합 단위 체계(Unit System) 섹션 추가 |
| `solar/README.md` | 파라미터 정책(Parameter Policy) 섹션 추가 |
| `solar/em/_constants.py` | EPS_ZERO, EPS_GEOM 중앙 상수 파일 신설 |
| `solar/em/magnetic_dipole.py` | 매직 넘버 → EPS_ZERO/EPS_GEOM 교체 (13개소) |
| `solar/em/solar_wind.py` | 매직 넘버 → EPS_ZERO 교체 (3개소) |
| `solar/em/magnetosphere.py` | 매직 넘버 → EPS_ZERO 교체 (3개소) |

검증: 기존 em_layer_demo.py 동일 결과 확인 (값 변동 없음)

---

## v1.2.0 — 전자기 레이어 완비 (Phase 2+3+4)

**날짜**: 2026-02-25
**작업**: 자기쌍극자 + 태양풍 + 자기권

| 파일 | 설명 |
|------|------|
| `solar/em/magnetic_dipole.py` | 자기쌍극자장 B(x,t) ∝ 1/r³, 11.5° 기울기 |
| `solar/em/solar_wind.py` | 태양풍 동압+복사압+IMF ∝ 1/r² |
| `solar/em/magnetosphere.py` | Chapman-Ferraro 자기권: r_mp, 보우쇼크, 차폐 |
| `examples/em_layer_demo.py` | Phase 2+3+4 통합 검증 (ALL PASS) |
| `docs/EM_LAYER_LOG.txt` | 통합 검증 출력 로그 |

검증:
- 표면 자기장 정확도: 0.00%
- 1/r³ 감쇠: 0.00%
- 태양풍 1/r²: 5행성 0.00%
- 마그네토포즈: 7.58 R_E
- 차폐: 0.78
- 세차-자기권 연동: PASS
- 에너지 보존: dE/E = 8.20e-11

---

## v1.1.0 — 자기쌍극자장 (Phase 2)

**날짜**: 2026-02-25
**작업**: em/ 레이어 신설, 자기쌍극자

| 파일 | 설명 |
|------|------|
| `solar/em/__init__.py` | 전자기 레이어 공개 API |
| `solar/em/magnetic_dipole.py` | 쌍극자 B필드, DipoleFieldPoint |
| `examples/magnetic_dipole_demo.py` | Phase 2 단독 검증 (ALL PASS) |
| `docs/MAGNETIC_DIPOLE_LOG.txt` | Phase 2 검증 출력 로그 |

---

## v1.0.0 — 전체 태양계 N-body (Phase 1) + 기어 분리

**날짜**: 2026-02-25
**작업**: 8행성 NASA 데이터 + core/data/cognitive/ 폴더 구조화

| 파일 | 설명 |
|------|------|
| `solar/data/solar_system_data.py` | NASA/JPL 8행성+태양+달 실측 상수 |
| `solar/core/` | 물리 코어 분리 (evolution_engine 등) |
| `solar/cognitive/` | 인지 레이어 분리 (ring_attractor 등) |
| `examples/full_solar_system_demo.py` | 10-body 100년 검증 (ALL PASS) |
| `docs/FULL_SOLAR_SYSTEM_LOG.txt` | 10-body 검증 출력 로그 |

검증:
- 에너지 보존: dE/E = 3.20e-10
- 각운동량 보존: dL/L = 3.04e-14
- 세차 주기: 24,763년 (NASA 25,772년, 3.9%)
- 전 행성 궤도 편차: < 1%

---

## v0.9.0 — Ring Attractor 결합

**날짜**: 2026-02-25
**작업**: 관성 기억 엔진 + 커플링 레이어

| 파일 | 설명 |
|------|------|
| `solar/ring_attractor.py` | Mexican-hat bump attractor |
| `solar/spin_ring_coupling.py` | 물리↔인지 필드 연결 |
| `examples/spin_ring_coupling_demo.py` | 커플링 검증 (ALL PASS) |
| `docs/SPIN_RING_COUPLING_LOG.txt` | 커플링 검증 출력 로그 |

---

## v0.8.0 — 3체 세차운동

**날짜**: 2026-02-25
**작업**: EvolutionEngine 신설, 세차운동 첫 재현

| 파일 | 설명 |
|------|------|
| `solar/evolution_engine.py` | N-body + 스핀-궤도 + 해양 |
| `examples/planet_evolution_demo.py` | 6단계 전과정 데모 |
| `docs/PRECESSION_VERIFICATION_LOG.txt` | 세차 검증 출력 로그 |

검증:
- 세차 주기: 24,575년 (NASA 25,772년, 4.6%)
- 에너지 보존: dE/E = 2.06e-15
