# joe — Joe Observer Engine (조)

1일 이전 **행성·우주 물리 탐사** (거시). 파인만의 **조(Joe)** = 정지 관측자.

## 서사 위치

- **시점**: Creation Day 0 이전 (Pre-Genesis). 빛이 있기 전, 궤도·질량·물·판이 정해지는 단계.
- **역할**: Macro Observer — 행성 스냅샷만으로 planet_stress·instability를 산출하고 거주가능성 라벨 부여.
- **테라포밍 탐색기**: 조(JOE) → 모(MOE) → 체루빔 중 1단계. [TERRAFORMING_EXPLORER_FLOW.md](../../_meta/20_CONCEPT/maps/TERRAFORMING_EXPLORER_FLOW.md)

## 이식 구조 (기어 분리)

- **PANGEA §4 코어**: `_core.py` — 독립 엔진 Joe_Engine과 **동일한 수식·계수**. 의존성 없음(기어 1개).
- **Coarse Aggregator**: `aggregator.py` — _core를 import해 스냅샷 → stress/instability/label. solar 전용으로 `rotation_stable` 보정만 추가.
- **Feature Layer**: `feature_layers/` — 물리 → 스냅샷 키 변환(cosmic, mass_rotation, retention, water_plate_proxy). 상위 레이어가 아님.
- **Observer / Run**: `observer.py`, `run.py` — Feature Layer로 스냅샷 보강 후 aggregator 호출. 파이프라인 1단계 진입점.

레이어가 섞이지 않도록: _core는 day2/day3를 import하지 않음. creation_days·eden은 joe를 `run(ic, water_snapshot)`·`compute_planet_stress_and_instability`로만 호출.

## 역할

- **observe** → **analyze** → **detect**: rotation, water_budget, plate_stress 등 → planet_stress, instability → collapse 조건.

## 2단계 파이프라인

1. **Feature Layer** (물리 → 스냅샷): `feature_layers/` — cosmic, mass_rotation, retention, water_plate_proxy가 JOE 표준 스냅샷 키를 채움.
2. **Coarse Aggregator** (스냅샷 → stress/instability): `aggregator.py` — _core(PANGEA §4) 사용. 계수는 CONFIG로 오버라이드 가능, 결과에 `config_used` 기록.

## 코드

- `_core.py` — PANGEA §4 코어(독립 Joe_Engine과 동일). DEFAULT_CONFIG, planet_stress_raw, instability_raw, normalize, saturate.
- `snapshot_convention.py` — JOE 표준 키, S_rot = clamp01(centrifugal_ratio).
- `feature_layers/` — 00_cosmic, 01_mass_rotation, 02_retention, 03_water_plate_proxy.
- `aggregator.py` — assess(snapshot, config) → JoeAssessmentResult (config_used 포함). _core 사용 + rotation_stable 보정.
- `observer.py` — build_joe_snapshot + assess; compute_planet_stress_and_instability, assess_planet.
- `run.py` — run(ic, water_snapshot) → 파이프라인 1단계.

## 물리 확장 방향

조를 실제 행성 탐사 엔진으로 확장할 때의 단계:

1. Cosmic Field Scan  
2. Mass & Rotation Stability  
3. Planet Formation  
4. Atmospheric Retention  
5. Surface Hydrology  
6. Magnetic & Radiation Shield  
7. Climate Stability  
8. Biosphere Potential  
9. Terraforming Potential  

상세·변수·계약: `_meta/20_CONCEPT/maps/JOE_PHYSICS_EXPANSION.md`  
흐름(조→모→체루빔): `_meta/20_CONCEPT/maps/TERRAFORMING_EXPLORER_FLOW.md`  
역방향(현재 지구 → 초기 상태 추적): `_meta/20_CONCEPT/maps/JOE_REVERSE_MODE.md`
