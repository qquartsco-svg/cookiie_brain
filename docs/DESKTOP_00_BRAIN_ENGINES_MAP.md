# 데스크탑 00_BRAIN — 엔진·파일 위치 맵

**기준 경로**: `/Users/jazzin/Desktop/00_BRAIN/`  
데스크탑에 있는 엔진·주요 폴더 전부 정리.

---

## 1. 루트 폴더 (00_BRAIN 바로 아래)

| 폴더/파일 | 설명 |
|-----------|------|
| **Archive** | 아카이브 (과거 Integrated·Brain_Modules·Grid_Engine 등) |
| **Brain_Disorder_Simulation_Engine** | 뇌 장애 시뮬레이션 + Boundary_Convergence_Engine, Unsolved_Problems_Engines |
| **BrainCore** | brain_core 패키지 (engines, cingulate_cortex 등) |
| **Cognitive_Kernel** | 인지 커널 (engines: amygdala, basal_ganglia, thalamus, pfc 등) |
| **CookiieBrain** | 현재 레포 (solar, eden, examples, bridge 등) |
| **docs** | 00_BRAIN 공용 문서 |
| **Engines** | 활성 엔진 정리 (Independent, Active, Main) |
| **Garage** | versions/engines 등 |
| **Hippo_ lego** | 해마 레고 |
| **scripts** | 스크립트 |
| **folder_structure_manager.py** | 폴더 구조 관리 |
| **module_upgrade_manager.py** | 모듈 업그레이드 관리 |
| **sync_to_github.sh** | GitHub 동기화 |

---

## 2. 엔진 위치 (전체)

### 2.1 Archive / Integrated (패키지 형태)

| 경로 | 비고 |
|------|------|
| `00_BRAIN/Archive/Integrated/2.Ring_Attractor_Engine` | Ring Attractor |
| `00_BRAIN/Archive/Integrated/3.Grid_Engine` | **Grid Engine** (package/ 안에 grid_engine 2D·3D·4D·5D) |
| `00_BRAIN/Archive/Integrated/4.Hippo_Memory_Engine` | Hippo Memory |
| `00_BRAIN/Archive/Integrated/5.Cerebellum_Engine` | Cerebellum |
| `00_BRAIN/Archive/Integrated/8.Hypothalamus_Engine` | Hypothalamus |
| `00_BRAIN/Archive/Integrated/9.Basal_Ganglia_Engine` | Basal Ganglia |
| `00_BRAIN/Archive/Integrated/10.Prefrontal_Cortex_Engine` | PFC |
| `00_BRAIN/Archive/Integrated/11.MemoryRank_Engine` | MemoryRank |
| `00_BRAIN/Archive/Integrated/12.Panorama_Memory_Engine` | Panorama |

**Grid Engine 실제 패키지**:  
`00_BRAIN/Archive/Integrated/3.Grid_Engine/package/`  
→ 여기서 `grid_engine` (dim2d, dim3d, dim4d, dim5d, cerebellum, hippocampus) 임포트.

### 2.2 Archive / Brain_Modules

| 경로 |
|------|
| `00_BRAIN/Archive/Brain_Modules/01_Neurons_Engine` |
| `00_BRAIN/Archive/Brain_Modules/02_Ring_Attractor_Engine` |
| `00_BRAIN/Archive/Brain_Modules/03_Grid_Engine` (→ 심링크로 다른 grid-engine 경로 가리킴) |
| `00_BRAIN/Archive/Brain_Modules/04_Hippo_Memory_Engine` |
| `00_BRAIN/Archive/Brain_Modules/05_Cerebellum_Engine` |

### 2.3 Engines / Independent (독립 엔진)

| 경로 |
|------|
| `00_BRAIN/Engines/Independent/6.Thalamus_Engine` |
| `00_BRAIN/Engines/Independent/7.Amygdala_Engine` |
| `00_BRAIN/Engines/Independent/ADHD_Simulation_Engine` |
| `00_BRAIN/Engines/Independent/Boundary_Convergence_Engine` |
| `00_BRAIN/Engines/Independent/Dynamics_Engine` |
| `00_BRAIN/Engines/Independent/GaiaFire_Engine` |

### 2.4 Engines / Active (Cognitive_Kernel 링크)

`00_BRAIN/Engines/Active/` 아래는 모두 `Cognitive_Kernel/src/cognitive_kernel/engines/` 로 연결:

- amygdala_engine → cognitive_kernel/engines/amygdala  
- basal_ganglia_engine → cognitive_kernel/engines/basal_ganglia  
- dynamics_engine → cognitive_kernel/engines/dynamics  
- hypothalamus_engine → cognitive_kernel/engines/hypothalamus  
- memoryrank_engine → cognitive_kernel/engines/memoryrank  
- panorama_engine → cognitive_kernel/engines/panorama  
- pfc_engine → cognitive_kernel/engines/pfc  
- thalamus_engine → cognitive_kernel/engines/thalamus  

### 2.5 Engines / Main (통합용 링크)

`00_BRAIN/Engines/Main/` 에서 1.Panorama ~ 9.Boundary_Convergence_Engine 까지  
Cognitive_Kernel engines 로 링크.

### 2.6 Cognitive_Kernel 실제 엔진 (소스)

`00_BRAIN/Cognitive_Kernel/src/cognitive_kernel/engines/`

- amygdala, basal_ganglia, boundary_convergence, dynamics  
- hypothalamus, memoryrank, panorama, pfc, thalamus  

### 2.7 Brain_Disorder_Simulation_Engine

| 경로 |
|------|
| `00_BRAIN/Brain_Disorder_Simulation_Engine/Boundary_Convergence_Engine` |
| `00_BRAIN/Brain_Disorder_Simulation_Engine/Unsolved_Problems_Engines/` |
| ├── PotentialFieldEngine, WellFormationEngine, StateManifoldEngine |
| ├── TransparencyEngine, PublicTransparencyEngine, ThreeBodyBoundaryEngine |
| └── UP-2_BoundarySafeSearchEngine |

### 2.8 CookiieBrain 내부 엔진

| 경로 |
|------|
| `00_BRAIN/CookiieBrain/solar/engines/` | 12 Well (01_solar ~ 12_evos) |
| `00_BRAIN/CookiieBrain/solar/bridge/` | grid_engine_bridge, gaia_loop_connector, gaia_bridge |
| `00_BRAIN/CookiieBrain/hippo/` | hippo_memory_engine |

---

## 3. CookiieBrain에서 데스크탑 엔진 경로 잡을 때

- **00_BRAIN 루트**:  
  `Path(__file__).resolve().parent.parent.parent` (CookiieBrain 기준 상위 한 단계)  
  → 예: `solar/bridge/grid_engine_bridge.py` 에서는 `.parent.parent.parent` = CookiieBrain, 그 다음 `.parent` = 00_BRAIN.
- **Grid Engine 패키지**:  
  `00_BRAIN / "Archive" / "Integrated" / "3.Grid_Engine" / "package"`
- **다른 Integrated 엔진**:  
  `00_BRAIN / "Archive" / "Integrated" / "4.Hippo_Memory_Engine"` 등.

---

## 4. 요약

- **데스크탑에 다 있는 엔진·파일** = 위 00_BRAIN 루트와 Archive / Engines / Cognitive_Kernel / Brain_Disorder_Simulation_Engine / CookiieBrain 전부.
- **Grid Engine** = `Archive/Integrated/3.Grid_Engine/package` (실제 Python 패키지).
- **연결** = CookiieBrain은 `solar/bridge/grid_engine_bridge.py` 에서 위 경로로 Grid Engine을 불러와 12 위도밴드와 연결.
