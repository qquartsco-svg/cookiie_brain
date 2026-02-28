# 에덴 엔진 × Grid Engine 확장 점검

## 적용 현황 (점검일: 2026-02-27)

### 1. 행성 탐사 확장 (EdenExplorationGrid)
- **solar/eden/exploration.py**
  - `EdenExplorationGrid`: 12밴드별 `band_best_score`, Grid Engine 탐사 포커스(`_grid_agent`)
  - `focus_band()`, `update_from_candidate()`, `step_explore()`, `use_grid()`
  - `trim_candidates_by_exploration()`: 트림 시 포커스 밴드 점수 반영

### 2. 에덴 탐색 엔진 연동 (search.py)
- **solar/eden/search.py**
  - `search()` 시작 시 `EdenExplorationGrid()` 생성, `trim_candidates_by_exploration` 임포트
  - 후보 추가 시 `exploration.update_from_candidate(c)`
  - 후보 수 ≥ max_candidates*3 시 `trim_candidates_by_exploration()` 사용
  - 최종 정렬/트림도 동일 함수 사용
  - 결과 `grid_agent`: `exploration._grid_agent` 우선, 없으면 1등 후보 밴드로 `create_latitude_grid_agent()` fallback

### 3. 데모 출력
- **solar/eden/eden_search_demo.py**
  - `result_a.grid_agent` 존재 시 "[Grid Engine 연동]" 블록 출력 (포커스 밴드, step 예시)

### 4. Grid Engine 브리지 (2D~7D 확장)
- **solar/bridge/grid_engine_bridge.py**
  - 2D: `Grid2DEngine`, `LatitudeGridAdapter`, `create_latitude_grid_agent()` (에덴 12밴드용)
  - 확장: 3D~7D `grid_engine.dimensions.dim*d` 로드, `_GRID_ENGINES_ND`, `_MAX_GRID_DIMENSION`
  - `get_max_grid_dimension()`, `get_grid_dimensions_available()`, `create_grid_engine_nd(dimension)`

### 5. Ring Attractor shim
- **solar/bridge/ring_attractor_shim/hippo_memory/ring_engine.py**
  - Grid 2D~7D 의존성 `hippo_memory.ring_engine` API를 solar 경량 `RingAttractorEngine`으로 제공
  - 2.Ring_Attractor_Engine 미설치/의존성 실패 시에도 데모에서 Grid 연동 동작

## 확인 명령
```bash
python -m solar.eden.eden_search_demo   # [Grid Engine 연동] 블록 출력 확인
python -c "
from solar.bridge import grid_engine_bridge as B
print('max_dim:', B.get_max_grid_dimension(), 'dims:', B.get_grid_dimensions_available())
"
```
