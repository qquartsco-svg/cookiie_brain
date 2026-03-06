# CookiieBrain 서사 ↔ 코어·ENGINE_HUB 연동 점검

**목적**: 메인 서사 폴더(CookiieBrain)에서 코어·ENGINE_HUB·엔진이 제대로 반영되어 흐르는지 확인.

---

## 1. 정리

| 대상 | 역할 | CookiieBrain에서 참조 방식 |
|------|------|---------------------------|
| **코어** | 실제 코드 (BrainCore, Cognitive_Kernel, BDS, Hippo_lego) | `cookiie_brain_engine.py`에서 `00_BRAIN/코어/BrainCore`, `00_BRAIN/코어/Brain_Disorder_Simulation_Engine` 경로로 sys.path 추가 후 import |
| **ENGINE_HUB** | 레이어별 엔진 지도/인덱스 (링크만) | 서사 런타임에서는 **직접 import 안 함**. 조/모 독립 데모는 `ENGINE_HUB/scripts/run_joe_moe.py`. solar 서사는 `solar/_01_beginnings/joe` 로컬 구현. 독립엔진은 00_BRAIN/ENGINE_HUB. |
| **Archive** | 과거 엔진 (Cerebellum, Grid, Ring Attractor 등) | `cookiie_brain_engine.py` → `00_BRAIN/Archive/Integrated/5.Cerebellum_Engine`. `grid_engine_bridge.py` → `00_BRAIN/Archive/Integrated/3.Grid_Engine`, `2.Ring_Attractor_Engine` |
| **Hippo_Memory_Engine** (00_BRAIN) | ENGINE_HUB 20_LIMBIC_LAYER/Hippo_memory, Archive 4.Hippo_Memory_Engine | **CookiieBrain에 연동 안 됨.** CookiieBrain은 hippo/(우물 기억)만 사용. → [히포메모리_연동_현황.md](히포메모리_연동_현황.md) |

---

## 2. 수정 반영 사항 (2026-03-06)

- **cookiie_brain_engine.py**
  - `_00_BRAIN = Path(__file__).resolve().parent.parent` (CookiieBrain → 00_BRAIN).
  - BrainCore: `_00_BRAIN / "코어" / "BrainCore" / "src"`.
  - WellFormation / PotentialField (BDS): `_00_BRAIN / "코어" / "Brain_Disorder_Simulation_Engine" / "Unsolved_Problems_Engines" / ...`.
  - Cerebellum: `_00_BRAIN / "Archive" / "Integrated" / "5.Cerebellum_Engine" / "package"` (변경 없음).
- **grid_engine_bridge.py**
  - `_COOKIIE_ROOT` = `parent.parent.parent.parent` (CookiieBrain), `_00_BRAIN` = `_COOKIIE_ROOT.parent` (00_BRAIN).  
  - Archive 경로(`3.Grid_Engine`, `2.Ring_Attractor_Engine`)는 00_BRAIN 기준으로 정상 동작.

---

## 3. Active 폴더

- **Engines/Active** 는 문서(DESKTOP_00_BRAIN_ENGINES_MAP.md 등)에서만 언급됨.  
- 현재 00_BRAIN 루트에는 `Engines` 폴더 없음. 엔진 인덱스는 **ENGINE_HUB** (레이어별 링크), 실제 코드는 **코어**·**Archive**·**ENGINE_HUB 내 실체**(예: Joe_Engine, Moe_Engine)에 있음.  
- 서사 로직은 **코어** + **Archive** + **solar 내부** 로 흐르면 됨.

---

## 4. 서사 흐름 요약

1. **CookiieBrainEngine** (통합 엔진): BrainCore, WellFormation, PotentialField, Cerebellum, Hippo, Tidal 등 → **코어**·**Archive** 경로로 로드.
2. **solar**: creation_days, joe(로컬), eden, underworld, bridge(brain_core_bridge, grid_engine_bridge) → 코어의 BrainCore는 **cookiie_brain_engine** 경유, Grid/Ring은 **Archive** 경유.
3. **ENGINE_HUB**: 조→모 데모(`run_joe_moe.py`) 등 **독립 실행**용. CookiieBrain 서사와 같은 스냅샷 규약을 쓰지만, 서사 런타임에서는 ENGINE_HUB를 직접 import하지 않음.

이 구성을 기준으로 코어·ENGINE_HUB·Archive가 서사에 반영된 상태로 정리됨.
