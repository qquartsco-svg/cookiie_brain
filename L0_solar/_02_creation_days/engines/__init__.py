"""solar/engines — 독립 실행 가능 엔진 모음

Day1~6 에서 추출한 독립 엔진들.
각 엔진은 solar 패키지 없이도 단독 실행 가능.

판정 기준:
  ① step(dt) 보유 — 시간 적분 가능
  ② 외부 의존 0  — stdlib 만으로 동작
  ③ 역할 완결    — 입력 포트 명확, 출력 단일

TIER 1 — 즉시 독립 (조건 ①②③ 전부)
  StressEngine    : 스트레스 누적 → 임계 → 방전 → 리셋   (Day7 기반)
  RhythmEngine    : 장주기 천문 리듬 (Milankovitch)       (Day7 기반)
  NitrogenEngine  : N 순환 ODE
  OceanEngine     : 조석 → 혼합 → 탄소 펌프
  SeasonEngine    : 계절 위상·온도
  TransportEngine : 보존형 확산 커널
  FoodWebEngine   : Lotka-Volterra 트로픽 ODE
  MutationEngine  : 베르누이 변이 (Day6)
  FeedbackEngine  : genome → env 피드백 (Day6)
  NicheEngine     : 자원 경쟁·점유 (Day6)

TIER 2 — 래퍼 추가 시 독립 (조건 ①③, ② 경량)
  AtmosphereEngine : 대기 컬럼 ODE
  BiosphereEngine  : 생물권 컬럼 ODE
"""

# ── TIER 1 ───────────────────────────────────────────────────────────────────
from L0_solar.day3.gaia_fire.stress_accumulator import (
    StressAccumulator as StressEngine,
    NeuronEvent,
    CellStressState,
    PlanetStressIndex,
)
from L0_solar.day4.cycles.milankovitch import (
    MilankovitchCycle as RhythmEngine,
    MilankovitchState,
)
from L0_solar.day4.nitrogen.cycle import (
    NitrogenCycle as NitrogenEngine,
    NitrogenState,
)
from L0_solar.day4.gravity_tides.ocean_nutrients import (
    OceanNutrients as OceanEngine,
    OceanState,
)
from L0_solar.day4.season_engine import (
    SeasonEngine,
    SeasonState,
)
from L0_solar.day5.seed_transport import (
    SeedTransport as TransportEngine,
    TransportKernel,
)
from L0_solar.day5.food_web import (
    FoodWeb as FoodWebEngine,
    TrophicState,
)
from L0_solar.day6.mutation_engine import (
    MutationEngine,
    MutationEvent,
    make_mutation_engine,
)
from L0_solar.day6.gaia_feedback import (
    GaiaFeedbackEngine as FeedbackEngine,
    GaiaFeedbackResult as FeedbackResult,
    make_gaia_feedback_engine as make_feedback_engine,
)
from L0_solar.day6.niche_model import (
    NicheModel as NicheEngine,
    NicheState,
    make_niche_model as make_niche_engine,
)

# ── TIER 2 ───────────────────────────────────────────────────────────────────
from L0_solar.day2.atmosphere.column import (
    AtmosphereColumn as AtmosphereEngine,
    AtmosphereState,
)
from L0_solar.day3.biosphere.column import (
    BiosphereColumn as BiosphereEngine,
)

__all__ = [
    # TIER 1
    "StressEngine", "NeuronEvent", "CellStressState", "PlanetStressIndex",
    "RhythmEngine", "MilankovitchState",
    "NitrogenEngine", "NitrogenState",
    "OceanEngine", "OceanState",
    "SeasonEngine", "SeasonState",
    "TransportEngine", "TransportKernel",
    "FoodWebEngine", "TrophicState",
    "MutationEngine", "MutationEvent", "make_mutation_engine",
    "FeedbackEngine", "FeedbackResult", "make_feedback_engine",
    "NicheEngine", "NicheState", "make_niche_engine",
    # TIER 2
    "AtmosphereEngine", "AtmosphereState",
    "BiosphereEngine",
]
