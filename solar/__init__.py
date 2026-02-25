"""solar/ — 전체 태양계 N-body 진화 엔진 + 관성 기억 + 전자기장
=============================================================

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

  cognitive/ (인지 층):
    ring_attractor.py    → RingAttractorEngine, RingState
    spin_ring_coupling.py→ SpinRingCoupling, CouplingState

의존 방향:
  data/ → core/ ← cognitive/
                ← em/
  core/는 상위를 import하지 않음
  em/과 cognitive/는 서로 참조하지 않음
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
    # cognitive
    "RingAttractorEngine",
    "RingState",
    "SpinRingCoupling",
    "CouplingState",
]

__version__ = "1.2.2"
