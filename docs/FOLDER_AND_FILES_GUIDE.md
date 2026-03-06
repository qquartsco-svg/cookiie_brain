# CookiieBrain 폴더·파일 위치 및 생성/수정 요약

**작성**: 2026-02-26  
**목적**: 폴더 구조, 각 파일 역할, 무엇이 어디서 생성/수정됐는지 한눈에 보기

---

## 1. 전체 경로 (기준 루트)

```
/Users/jazzin/Desktop/00_BRAIN/
```

- **00_BRAIN** = 프로젝트 최상위 (데스크탑)
- **CookiieBrain** = 메인 통합 엔진 (태양계·뇌 동역학)
- **solar** = CookiieBrain 안의 태양계·지구환경 레이어

---

## 2. 00_BRAIN 최상위 구조

| 경로 | 종류 | 설명 |
|------|------|------|
| `00_BRAIN/Archive/` | 폴더 | 이전 버전·레거시 보관 |
| `00_BRAIN/BrainCore/` | 폴더 | GlobalState, 엔진 계약 (통합 오케스트레이터) |
| `00_BRAIN/Brain_Disorder_Simulation_Engine/` | 폴더 | 우울·불안 시뮬 등 + WellFormationEngine, PotentialFieldEngine |
| `00_BRAIN/Cognitive_Kernel/` | 폴더 | 인지 레이어 (Thalamus, Amygdala, PFC 등) |
| `00_BRAIN/CookiieBrain/` | 폴더 | **메인 통합 엔진** (solar, trunk, hippo, analysis 포함) |
| `00_BRAIN/docs/` | 폴더 | 00_BRAIN 전체 문서 허브 |
| `00_BRAIN/Engines/` | 폴더 | 활성 엔진 모음 |
| `00_BRAIN/Garage/` | 폴더 | 개발 로그·버전 보관 |
| `00_BRAIN/Hippo_ lego/` | 폴더 | 해마 레고 실험 |
| `00_BRAIN/scripts/` | 폴더 | 스크립트 |
| `00_BRAIN/folder_structure_manager.py` | 파일 | 폴더 구조 관리 |
| `00_BRAIN/module_upgrade_manager.py` | 파일 | 모듈 업그레이드 관리 |
| `00_BRAIN/sync_to_github.sh` | 파일 | GitHub 동기화 |

---

## 3. CookiieBrain 루트 (파일·폴더)

| 경로 | 종류 | 설명 |
|------|------|------|
| `CookiieBrain/analysis/` | 폴더 | Layer 1~6 분석 (통계역학, 다체, 게이지, …) |
| `CookiieBrain/blockchain/` | 폴더 | PHAM 블록체인 서명 체인 (JSON) |
| `CookiieBrain/cookiie_brain/` | 폴더 | 핵심 뇌 모듈 |
| `CookiieBrain/docs/` | 폴더 | CookiieBrain 전용 문서 |
| `CookiieBrain/examples/` | 폴더 | 데모·검증 스크립트 (38개+) |
| `CookiieBrain/hippo/` | 폴더 | HippoMemoryEngine (해마·장기기억) |
| `CookiieBrain/trunk/` | 폴더 | Phase A/B/C (자전·공전·요동) |
| `CookiieBrain/solar/` | 폴더 | **태양계·지구환경** (core, em, atmosphere, surface, biosphere) |
| `CookiieBrain/docs/ARCHITECTURE.md` | 파일 | 레이어 아키텍처 명세 |
| `CookiieBrain/README.md` | 파일 | 프로젝트 개요·수식·버전 |
| `CookiieBrain/docs/QUICK_START.md` | 파일 | 빠른 시작 |
| `CookiieBrain/brain_analyzer.py` | 파일 | Layer 1+5+6 통합 분석 |
| `CookiieBrain/cookiie_brain_engine.py` | 파일 | 통합 오케스트레이터 |
| `CookiieBrain/hippo_memory_engine.py` | 파일 | hippo 래퍼 (루트 호환) |
| `CookiieBrain/pham_chain_*.json` | 파일들 | PHAM 서명 체인 (루트 6개) |

---

## 4. solar/ 폴더 — 위치와 역할

| 경로 | 종류 | 역할 |
|------|------|------|
| **solar/core/** | 폴더 | 물리 코어 (N-body, 세차, 조석, 해양) |
| `solar/core/evolution_engine.py` | 파일 | EvolutionEngine, Body3D, SurfaceOcean |
| `solar/core/central_body.py` | 파일 | 태양 1/r 중력 |
| `solar/core/orbital_moon.py` | 파일 | 달 궤도·조석 |
| `solar/core/tidal_field.py` | 파일 | 태양+달 힘 합성 |
| **solar/data/** | 폴더 | NASA/JPL 실측 데이터 |
| `solar/data/solar_system_data.py` | 파일 | 8행성+태양+달, build_solar_system() |
| **solar/em/** | 폴더 | 전자기 레이어 (빛이 있으라) |
| `solar/em/solar_luminosity.py` | 파일 | L=M^α, 조도, T_eq |
| `solar/em/magnetic_dipole.py` | 파일 | 자기쌍극자 B∝1/r³ |
| `solar/em/solar_wind.py` | 파일 | 태양풍 P∝1/r² |
| `solar/em/magnetosphere.py` | 파일 | 자기권 경계 |
| **solar/atmosphere/** | 폴더 | 궁창·대기권 (Phase 6a/6b) |
| `solar/atmosphere/column.py` | 파일 | AtmosphereColumn (온실, 열관성, 수순환) |
| `solar/atmosphere/greenhouse.py` | 파일 | τ→ε_a, T_surface |
| `solar/atmosphere/water_cycle.py` | 파일 | 증발·잠열·H2O 피드백 |
| **solar/surface/** | 폴더 | 땅·바다 분리 (Phase 7A) |
| `solar/surface/surface_schema.py` | 파일 | SurfaceSchema, effective_albedo |
| **solar/biosphere/** | 폴더 | 풀·씨·열매·토양 (Phase 7B) — **아래 4절에서 상세** |
| **solar/cognitive/** | 폴더 | Ring Attractor, 물리↔인지 커플링 |
| `solar/brain_core_bridge.py` | 파일 | solar → BrainCore extension 조립 |
| `solar/LAYERS.md` | 파일 | 개념 레이어 순서 (0~4일) |
| `solar/README.md` | 파일 | solar 전체 설명 |
| `solar/evolution_engine.py` 등 | 파일 | core/ 로 가는 하위호환 shim |

---

## 5. solar/biosphere/ — 파일별 역할과 생성/수정

| 파일 | 역할 | 생성/수정 |
|------|------|-----------|
| `biosphere/__init__.py` | 패키지 공개 (BiosphereColumn, pioneer, photo) | 기존 |
| `biosphere/_constants.py` | 선구·광합성·O2·알베도 상수 | **수정** (Claude: 현실 스케일, ORGANIC_THRESHOLD, PIONEER_THRESHOLD 비활성, K_SOIL_FEEDBACK, W_WEATHERING, mineral 관련 상수) |
| `biosphere/state.py` | BiosphereState 스냅샷 (로깅용) | 기존 |
| `biosphere/pioneer.py` | 선구 ODE (pioneer, organic, **mineral**) | **수정** (Claude: 3변수 ODE, 로지스틱 K(organic), 풍화 d_mineral, Q10 분해) |
| `biosphere/photo.py` | 광합성 GPP/호흡/증산/f_O2 | 기존 (photo_ready 등은 상수 참조) |
| `biosphere/column.py` | BiosphereColumn.step() — pioneer+photo+feedback | **수정** (Claude: mineral_layer 필드 추가, d_pioneer_dt 3-return 호출) |
| `biosphere/planet_bridge.py` | biosphere 플럭스 → 대기 혼합비/잠열/알베도 환산 | 기존 |
| `biosphere/README.md` | Phase 7b 개념·입출력·사용법 | 기존 |

---

## 6. examples/ — 관련 데모만

| 파일 | 역할 | 생성/수정 |
|------|------|-----------|
| `examples/biosphere_day3_demo.py` | Phase 7b: surface+atmosphere+biosphere 루프 검증 | **수정** (Claude: 단기 1년 검증 조건 → pioneer·mineral 증가 + 루프 안정만 확인) |
| `examples/soil_formation_sim.py` | 토양 형성만 단독 시뮬 (pioneer→organic→임계 도달 연수) | **신규** (Claude: 세차운동처럼 물리 ODE만 돌려서 “몇 년에 토양 임계” 나오는지 확인) |
| `examples/surface_day3_demo.py` | Phase 7A 땅·바다·알베도 검증 | 기존 |
| `examples/atmosphere_demo.py` | Phase 6a 대기권 검증 | 기존 |
| `examples/water_cycle_demo.py` | Phase 6b 수순환 검증 | 기존 |
| `examples/brain_core_environment_demo.py` | BrainCore extension 연동 데모 | 기존 |

---

## 7. “뭘 했는지” 요약 (Claude 작업분)

### 7.1 목표

- **세차운동처럼**: 물리 법칙/관측값을 수식으로 넣으면, **토양이 쌓이는 시간**이 시뮬레이션에서 자연스럽게 나오게 하기.
- **토양 = 유기물이 생성·반복으로 쌓이는 개념** → organic_layer + (선구 생물 pioneer + 풍화 mineral) ODE로 구현.

### 7.2 한 일

1. **biosphere/_constants.py**  
   - pioneer·humus·분해 관련 상수를 **현실 스케일**(지의류 NPP, 수명, 용암지대/빙하 후퇴지 연수)에 맞게 조정.  
   - `ORGANIC_THRESHOLD = 0.5`, `PIONEER_THRESHOLD = 999` 로 **토양 임계는 organic_layer만** 보도록 변경.  
   - `K_SOIL_FEEDBACK`, `W_WEATHERING`, `W_MINERAL_HUMUS`, `LAMBDA_DECAY` 등 **토양·풍화·양성 피드백**용 상수 추가/정리.

2. **biosphere/pioneer.py**  
   - **3변수 ODE** 도입: `pioneer_biomass`, `organic_layer`, `mineral_layer`.  
   - **로지스틱 성장**: K = K0 + K_soil × organic → 토양이 쌓일수록 pioneer 수용력 증가 (양성 피드백).  
   - **풍화**: d(mineral)/dt = W_WEATHERING × pioneer × f_T × f_W.  
   - **organic**: 사체→humus(ETA), mineral 안정화 기여(W_MINERAL_HUMUS), Q10 온도 의존 분해 λ(T).  
   - `d_pioneer_dt(..., mineral_layer)` → 반환 `(d_pioneer, d_organic, d_mineral)`.

3. **biosphere/column.py**  
   - 상태에 `mineral_layer` 추가.  
   - `step()` 안에서 `d_pioneer, d_organic, d_mineral = pioneer.d_pioneer_dt(...)` 호출해 세 변수 모두 적분.

4. **examples/biosphere_day3_demo.py**  
   - 1년짜리 통합 루프에서는 CO2/O2 큰 변화를 기대할 수 없으므로,  
     검증을 **“pioneer·mineral 증가 + 루프 오류 없음”** 으로 완화.

5. **examples/soil_formation_sim.py** (신규)  
   - **biosphere ODE만** 사용해, 척박한 돌땅(pioneer 극소, organic=0, mineral=0)에서 시작해  
     매년 `d_pioneer_dt`로 적분.  
   - `organic >= ORGANIC_THRESHOLD` 가 되는 **연수**를 출력 (세차 25,000년이 나오듯, 토양 임계 연수가 나옴).

### 7.3 생성된 것 vs 수정된 것

| 구분 | 항목 |
|------|------|
| **신규 생성** | `examples/soil_formation_sim.py` |
| **수정** | `solar/biosphere/_constants.py`, `solar/biosphere/pioneer.py`, `solar/biosphere/column.py`, `examples/biosphere_day3_demo.py` |

`brain_core_bridge.py`, `atmosphere/`, `surface/`, `core/` 등은 이번 Claude 세션에서 **수정하지 않음**.  
(이미 예전에 biosphere를 연동한 상태로 두고, 위 biosphere·예제만 손댐.)

---

## 8. 실행 위치 참고

- **CookiieBrain 루트에서**  
  - `python examples/biosphere_day3_demo.py`  
  - `python examples/soil_formation_sim.py`
- **solar만 쓰는 코드**  
  - `from solar.brain_core_bridge import get_solar_environment_extension, create_default_environment`  
  - `from solar.biosphere import BiosphereColumn`

이 문서는 `CookiieBrain/docs/FOLDER_AND_FILES_GUIDE.md` 에 저장됨.
