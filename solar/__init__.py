"""solar/ — 전체 태양계 N-body 진화 엔진 + 관성 기억 + 전자기장 + 광도 + 대기권
=======================================================================

구조 (기어 분리 — 상호 참조 금지):

  day4/core/ (물리 층):
    evolution_engine.py  → EvolutionEngine, Body3D, SurfaceOcean
    central_body.py      → CentralBody
    orbital_moon.py      → OrbitalMoon
    tidal_field.py       → TidalField

  day4/data/ (데이터 층):
    solar_system_data.py → PlanetData, PLANETS, build_solar_system()

  day1/em/ (전자기 층):
    magnetic_dipole.py   → MagneticDipole, DipoleFieldPoint
    solar_wind.py        → SolarWind, SolarWindState
    magnetosphere.py     → Magnetosphere, MagnetosphereState
    solar_luminosity.py  → SolarLuminosity, IrradianceState  (빛이 있으라)

  day3/surface/ (표면 층) [Phase 7 / 셋째날]:
    surface_schema.py    → SurfaceSchema, effective_albedo (땅-바다 분리)

  day2/atmosphere/ (대기 층):
    greenhouse.py        → optical_depth, effective_emissivity, GreenhouseParams
    column.py            → AtmosphereColumn, AtmosphereState, AtmosphereComposition

  cognitive/ (인지 층):
    ring_attractor.py    → RingAttractorEngine, RingState
    spin_ring_coupling.py→ SpinRingCoupling, CouplingState

의존 방향 (폴더 이동 후 개념적 구조는 동일):
  day4/data/ → day4/core/ ← cognitive/
                        ← day1/em/
                        ← day2/atmosphere/ (em/, surface/ 읽기)
                        ← day3/surface/ (독립)
  core/는 상위를 import하지 않음
  surface/는 의존 없음. atmosphere/가 effective_albedo 읽음
"""

# ── core (물리) ───────────────────────────────────
from .day4.core import (
    EvolutionEngine,
    Body3D,
    SurfaceOcean,
    CentralBody,
    OrbitalMoon,
    TidalField,
)

# ── data (NASA 실측) ──────────────────────────────
from .day4.data import (
    PLANETS,
    SUN_DATA,
    MOON_DATA,
    PlanetData,
    build_solar_system,
)

# ── em (전자기) ───────────────────────────────────
from .day1.em import (
    MagneticDipole,
    DipoleFieldPoint,
    SolarWind,
    SolarWindState,
    Magnetosphere,
    MagnetosphereState,
    SolarLuminosity,
    IrradianceState,
)

# ── surface (표면/땅-바다) [Phase 7] ───────────────
from .day3.surface import SurfaceSchema, effective_albedo

# ── atmosphere (대기/궁창) ────────────────────────
from .day2.atmosphere import (
    AtmosphereColumn,
    AtmosphereState,
    AtmosphereComposition,
    GreenhouseParams,
)

# ── cognitive (인지/기억) ─────────────────────────
from .cognitive import (
    RingAttractorEngine,
    RingState,
    SpinRingCoupling,
    CouplingState,
)

__all__ = [
    # core
    "CentralBody",
    "OrbitalMoon",
    "TidalField",
    "EvolutionEngine",
    "Body3D",
    "SurfaceOcean",
    # data
    "PLANETS",
    "SUN_DATA",
    "MOON_DATA",
    "PlanetData",
    "build_solar_system",
    # em
    "MagneticDipole",
    "DipoleFieldPoint",
    "SolarWind",
    "SolarWindState",
    "Magnetosphere",
    "MagnetosphereState",
    "SolarLuminosity",
    "IrradianceState",
    # surface (Phase 7)
    "SurfaceSchema",
    "effective_albedo",
    # atmosphere
    "AtmosphereColumn",
    "AtmosphereState",
    "AtmosphereComposition",
    "GreenhouseParams",
    # cognitive
    "RingAttractorEngine",
    "RingState",
    "SpinRingCoupling",
    "CouplingState",
]

# ── gaia_bridge (Phase 8: 뉴런-Gaia 연결) ───────────────
from .bridge.gaia_bridge import (
    GaiaBridge,
    GaiaBridgeConfig,
    BrainGaiaState,
    make_bridge,
)

# ── gaia_loop_connector (Phase 8.5: 3개 루프 연결, 항상성 순환) ──
from .bridge.gaia_loop_connector import (
    GaiaLoopConnector,
    LoopState,
    make_connector,
)

__all__ += [
    # gaia_bridge
    "GaiaBridge",
    "GaiaBridgeConfig",
    "BrainGaiaState",
    "make_bridge",
    # gaia_loop_connector
    "GaiaLoopConnector",
    "LoopState",
    "make_connector",
]

# ── cycles (넷째날 순환 2: Milankovitch 장주기 드라이버) ──────────────────────
from .day4.cycles import (
    MilankovitchCycle,
    MilankovitchState,
    make_earth_cycle,
    make_custom_cycle,
    insolation_at,
    insolation_grid,
    MilankovitchDriver,
    DriverOutput,
    make_earth_driver,
)

__all__ += [
    # cycles (넷째날 순환 2)
    "MilankovitchCycle",
    "MilankovitchState",
    "make_earth_cycle",
    "make_custom_cycle",
    "insolation_at",
    "insolation_grid",
    "MilankovitchDriver",
    "DriverOutput",
    "make_earth_driver",
]

# ── nitrogen (넷째날 순환 1: 질소 순환) ───────────────────────────────────────
from .day4.nitrogen import (
    NitrogenFixation,
    FixationResult,
    make_fixation_engine,
    NitrogenCycle,
    NitrogenState,
    make_nitrogen_cycle,
)

__all__ += [
    # nitrogen (넷째날 순환 1)
    "NitrogenFixation",
    "FixationResult",
    "make_fixation_engine",
    "NitrogenCycle",
    "NitrogenState",
    "make_nitrogen_cycle",
]

# ── gravity_tides (넷째날 순환 3: 조석-해양 탄소 펌프) ────────────────────────
from .day4.gravity_tides import (
    TidalField,
    TidalState,
    make_tidal_field,
    OceanNutrients,
    OceanState,
    make_ocean_nutrients,
)

__all__ += [
    # gravity_tides (넷째날 순환 3)
    "TidalField",
    "TidalState",
    "make_tidal_field",
    "OceanNutrients",
    "OceanState",
    "make_ocean_nutrients",
]

__version__ = "2.7.0"
