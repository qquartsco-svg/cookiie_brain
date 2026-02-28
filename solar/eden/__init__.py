"""solar/eden — 에덴 시스템 (창세기 2장)

천지창조(Day1~7)가 완성된 행성 위에 올라오는 에이전트·환경 레이어.

챕터 구조:
  Day1~7 (창세기 1장) → 행성 물리 완성
  Eden   (창세기 2장) → 에이전트 + 특수 환경 조건

핵심 모듈:
  firmament  — 궁창(Raqia): 상층 수증기 캐노피 물리 모델
  flood      — 대홍수 이벤트: 궁창 붕괴 → 환경 전이 곡선

환경 3단계:
  antediluvian  — 대홍수 이전 (궁창 존재, 에덴)
  flood         — 대홍수 진행 (궁창 붕괴)
  postdiluvian  — 대홍수 이후 (현재 Day7 기준점)

사용 예:
    from solar.eden import make_firmament, make_flood_engine

    # 에덴 환경 초기화
    fl = make_firmament(phase='antediluvian')
    env = fl.get_env_overrides()
    print(env['T_surface_estimate'])

    # 대홍수 발동
    event = fl.trigger_flood()
    flood = make_flood_engine()
    for _ in range(12):
        snap = flood.step(dt_yr=1.0)
        print(snap.flood_phase, snap.T_surface_K)
"""

from .firmament import (
    FirmamentLayer,
    FirmamentState,
    FloodEvent,
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

__version__ = "0.1.0"

__all__ = [
    # firmament
    "FirmamentLayer",
    "FirmamentState",
    "FloodEvent",
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
    # biology
    "BiologyFactors",
    "EdenBiologyState",
    "compute_biology",
    "compare_biology",
    "make_biology",
    "LIFESPAN_PHYSICAL_MAX_YR",
    "BODY_SIZE_PHYS_MAX_RATIO",
]
