"""solar/eden — 에덴 시스템 (창세기 2장)  v0.2.0

천지창조(Day1~7)가 완성된 행성 위에 올라오는 에이전트·환경 레이어.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 구조
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  solar/eden/
  │
  ├─ (기존) 물리 환경 레이어
  │    firmament.py        궁창 물리 모델
  │    flood.py            대홍수 전이 곡선
  │    initial_conditions.py  6개 파라미터 → 지구 동역학
  │    geography.py        자기장 + 시대별 지형
  │    search.py           Eden Basin Finder
  │    biology.py          물리 → 수명/체형
  │
  └─ (신규 v0.2.0) EdenOS — 행성 운영 체제
       eden_os/
         eden_world.py     [L0] 궁창시대 환경 스냅샷 (읽기전용)
         rivers.py         [L1] 4대강 방향 그래프
         tree_of_life.py   [L2] 생명나무 + 선악과 상태 머신
         cherubim_guard.py [L3] 체루빔 접근 제어
         adam.py           [L4] 시스템 관리자 에이전트
         eve.py            [L4] 보조 프로세서 + 계승 트리거
         lineage.py        [L5] 관리자 계승 그래프 (아담→네오)
         eden_os_runner.py [L6] 7단계 통합 실행기

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 연결 구조
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  solar.day7.PlanetRunner   ← 행성 물리 (Day1~7)
       ↑ initial_conditions=runner_kwargs
  solar.eden.InitialConditions  ← 에덴 환경 파라미터
       ↑ make_antediluvian()
  solar.eden.eden_os        ← EdenOS (관리자·4강·생명나무·체루빔)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 빠른 시작
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  # EdenOS 단독 실행
  from solar._03_eden_os_underworld.eden.eden_os import make_eden_os_runner
  runner = make_eden_os_runner()
  runner.run(steps=24)
  runner.print_report()

  # Day7 + Eden 연결 실행
  from solar.eden import make_antediluvian
  from solar.day7 import make_planet_runner
  ic     = make_antediluvian()
  runner = make_planet_runner(initial_conditions=ic.to_runner_kwargs())
  snap   = runner.step()
"""

from .firmament import (
    FirmamentLayer,
    FirmamentState,
    FloodEvent,
    Layer0Snapshot,
    make_firmament,
)
from .flood import (
    FloodEngine,
    FloodSnapshot,
    make_flood_engine,
)
from .initial_conditions import (
    InitialConditions,
    EarthBandState,
    make_antediluvian,
    make_postdiluvian,
    make_flood_peak,
)
from .geography import (
    EdenGeography,
    ArcticBasinState,
    MagneticFrameGeography,
    ExposedRegion,
    make_eden_geography,
    make_postdiluvian_geography,
    magnetic_protection_factor,
)
from .search import (
    EdenCriteria,
    EdenCandidate,
    SearchSpace,
    SearchResult,
    EdenSearchEngine,
    compute_eden_score,
    make_eden_search,
    make_antediluvian_space,
    make_postdiluvian_space,
    make_exoplanet_space,
    make_antediluvian_exoplanet_space,
)
from .biology import (
    BiologyFactors,
    EdenBiologyState,
    compute_biology,
    compare_biology,
    make_biology,
    LIFESPAN_PHYSICAL_MAX_YR,
    BODY_SIZE_PHYS_MAX_RATIO,
)

__version__ = "0.2.0"

# ── EdenOS v2.0 서브패키지 (신규) ────────────────────────────────────────────
from .eden_os import (
    # L0 환경
    EdenWorldEnv, BandInfo, make_eden_world,
    # L1 4대강
    RiverNetwork, make_river_network,
    # L2 생명나무
    TreeState, KnowledgeState, TreeOfLife, KnowledgeTree, make_trees,
    # L3 체루빔
    GuardVerdict, GuardDecision, CherubimGuard, make_cherubim_guard,
    # L4 에이전트
    AdminStatus, Observation, Intent, ActionResult,
    Adam, make_adam, SuccessionEvent, Eve, make_eve,
    # L5 계승
    LineageNode, LineageGraph, make_lineage,
    # L6 실행기
    TickLog, EdenOSRunner, make_eden_os_runner,
)

__all__ = [
    # firmament
    "FirmamentLayer",
    "FirmamentState",
    "FloodEvent",
    "Layer0Snapshot",
    "make_firmament",
    # flood
    "FloodEngine",
    "FloodSnapshot",
    "make_flood_engine",
    # initial_conditions
    "InitialConditions",
    "EarthBandState",
    "make_antediluvian",
    "make_postdiluvian",
    "make_flood_peak",
    # geography
    "EdenGeography",
    "ArcticBasinState",
    "MagneticFrameGeography",
    "ExposedRegion",
    "make_eden_geography",
    "make_postdiluvian_geography",
    "magnetic_protection_factor",
    # search
    "EdenCriteria",
    "EdenCandidate",
    "SearchSpace",
    "SearchResult",
    "EdenSearchEngine",
    "compute_eden_score",
    "make_eden_search",
    "make_antediluvian_space",
    "make_postdiluvian_space",
    "make_exoplanet_space",
    "make_antediluvian_exoplanet_space",
    # biology
    "BiologyFactors",
    "EdenBiologyState",
    "compute_biology",
    "compare_biology",
    "make_biology",
    "LIFESPAN_PHYSICAL_MAX_YR",
    "BODY_SIZE_PHYS_MAX_RATIO",
]
