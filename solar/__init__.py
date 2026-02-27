"""solar/ — 전체 태양계 N-body 진화 엔진 + 관성 기억 + 전자기장 + 광도 + 대기권
=======================================================================

구조 (기어 분리 — 상호 참조 금지):

  core/ (물리 층):
    evolution_engine.py  → EvolutionEngine, Body3D, SurfaceOcean
    central_body.py      → CentralBody
    orbital_moon.py      → OrbitalMoon
    tidal_field.py       → TidalField

  data/ (데이터 층):
    solar_system_data.py → PlanetData, PLANETS, build_solar_system()

  em/ (전자기 층):
    magnetic_dipole.py   → MagneticDipole, DipoleFieldPoint
    solar_wind.py        → SolarWind, SolarWindState
    magnetosphere.py     → Magnetosphere, MagnetosphereState
    solar_luminosity.py  → SolarLuminosity, IrradianceState  (빛이 있으라)

  surface/ (표면 층) [Phase 7 / 셋째날]:
    surface_schema.py    → SurfaceSchema, effective_albedo (땅-바다 분리)

  atmosphere/ (대기 층):
    greenhouse.py        → optical_depth, effective_emissivity, GreenhouseParams
    column.py            → AtmosphereColumn, AtmosphereState, AtmosphereComposition

  cognitive/ (인지 층):
    ring_attractor.py    → RingAttractorEngine, RingState
    spin_ring_coupling.py→ SpinRingCoupling, CouplingState

의존 방향:
  data/ → core/ ← cognitive/
               ← em/
               ← atmosphere/ (em/, surface/ 읽기)
               ← surface/ (독립)
  core/는 상위를 import하지 않음
  surface/는 의존 없음. atmosphere/가 effective_albedo 읽음
"""

# ── core (물리) ───────────────────────────────────
from .core import (
    EvolutionEngine,
    Body3D,
    SurfaceOcean,
    CentralBody,
    OrbitalMoon,
    TidalField,
)

# ── data (NASA 실측) ──────────────────────────────
from .data import (
    PLANETS,
    SUN_DATA,
    MOON_DATA,
    PlanetData,
    build_solar_system,
)

# ── em (전자기) ───────────────────────────────────
from .em import (
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
from .surface import SurfaceSchema, effective_albedo

# ── atmosphere (대기/궁창) ────────────────────────
from .atmosphere import (
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
from .gaia_bridge import (
    GaiaBridge,
    GaiaBridgeConfig,
    BrainGaiaState,
    make_bridge,
)

# ── gaia_loop_connector (Phase 8.5: 3개 루프 연결, 항상성 순환) ──
from .gaia_loop_connector import (
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
from .cycles import (
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

__version__ = "2.5.0"
