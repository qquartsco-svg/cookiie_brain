"""solar/ — 전체 태양계 N-body 진화 엔진 + 관성 기억 + 전자기장 + 광도 + 대기권
=======================================================================

World Generation Pipeline (폴더 = 시간 흐름 하나의 축):

  행성 탐사 → 천지창조 day1~7 → 에덴·OS·언더월드 → 궁창 환경시대 → 노아 대홍수 이벤트

실제 패키지: solar/_01_beginnings/, _02_creation_days/, _03_eden_os_underworld/, _04_firmament_era/, _05_noah_flood/.
solar.day1, solar.eden 등은 아래 별칭으로 동일 레이어를 가리킴.
"""

# ── 레이어 로드 및 별칭
import sys

def _register_layer_aliases():
    mod = sys.modules["solar"]
    _map = (
        ("day1", "solar._02_creation_days.day1"),
        ("day2", "solar._02_creation_days.day2"),
        ("day5", "solar._02_creation_days.day5"),
        ("fields", "solar._02_creation_days.fields"),
        ("day3", "solar._02_creation_days.day3"),
        ("surface", "solar._02_creation_days.day3.surface"),
        ("day4", "solar._02_creation_days.day4"),
        ("physics", "solar._02_creation_days.physics"),
        ("eden", "solar._03_eden_os_underworld.eden"),
        ("biosphere", "solar._03_eden_os_underworld.biosphere"),
        ("day6", "solar._02_creation_days.day6"),
        ("cognitive", "solar._03_eden_os_underworld.cognitive"),
        ("governance", "solar._03_eden_os_underworld.governance"),
        ("underworld", "solar._03_eden_os_underworld.underworld"),
        ("monitoring", "solar._03_eden_os_underworld.monitoring"),
        ("bridge", "solar._02_creation_days.bridge"),
        ("engines", "solar._02_creation_days.engines"),
        ("day7", "solar._02_creation_days.day7"),
        ("precreation", "solar._01_beginnings"),
        ("joe", "solar._01_beginnings.joe"),
        ("planet_dynamics", "solar._01_beginnings.joe"),
    )
    for _name, _modpath in _map:
        __import__(_modpath)
        _m = sys.modules[_modpath]
        setattr(mod, _name, _m)
        if _name != "bridge":
            sys.modules[f"solar.{_name}"] = _m

_register_layer_aliases()

PIPELINE_ORDER = (
    "precreation", "physics", "fields", "surface", "biosphere",
    "cognition", "governance", "monitoring",
)

# ── core / data / em / surface / atmosphere / cognitive ──
from ._02_creation_days.day4.core import (
    EvolutionEngine, Body3D, SurfaceOcean, CentralBody, OrbitalMoon, TidalField,
)
from ._02_creation_days.day4.data import PLANETS, SUN_DATA, MOON_DATA, PlanetData, build_solar_system
from ._02_creation_days.day1.em import (
    MagneticDipole, DipoleFieldPoint, SolarWind, SolarWindState,
    Magnetosphere, MagnetosphereState, SolarLuminosity, IrradianceState,
)
from ._02_creation_days.day3.surface import SurfaceSchema, effective_albedo
from ._02_creation_days.day2.atmosphere import (
    AtmosphereColumn, AtmosphereState, AtmosphereComposition, GreenhouseParams,
)
from ._03_eden_os_underworld.cognitive import (
    RingAttractorEngine, RingState, SpinRingCoupling, CouplingState,
)

__all__ = [
    "CentralBody", "OrbitalMoon", "TidalField", "EvolutionEngine", "Body3D", "SurfaceOcean",
    "PLANETS", "SUN_DATA", "MOON_DATA", "PlanetData", "build_solar_system",
    "MagneticDipole", "DipoleFieldPoint", "SolarWind", "SolarWindState",
    "Magnetosphere", "MagnetosphereState", "SolarLuminosity", "IrradianceState",
    "SurfaceSchema", "effective_albedo",
    "AtmosphereColumn", "AtmosphereState", "AtmosphereComposition", "GreenhouseParams",
    "RingAttractorEngine", "RingState", "SpinRingCoupling", "CouplingState",
]

from ._02_creation_days.bridge.gaia_bridge import GaiaBridge, GaiaBridgeConfig, BrainGaiaState, make_bridge
from ._02_creation_days.bridge.gaia_loop_connector import GaiaLoopConnector, LoopState, make_connector
__all__ += ["GaiaBridge", "GaiaBridgeConfig", "BrainGaiaState", "make_bridge",
            "GaiaLoopConnector", "LoopState", "make_connector"]

from ._02_creation_days.day4.cycles import (
    MilankovitchCycle, MilankovitchState, make_earth_cycle, make_custom_cycle,
    insolation_at, insolation_grid, MilankovitchDriver, DriverOutput, make_earth_driver,
)
__all__ += [
    "MilankovitchCycle", "MilankovitchState", "make_earth_cycle", "make_custom_cycle",
    "insolation_at", "insolation_grid", "MilankovitchDriver", "DriverOutput", "make_earth_driver",
]

from ._02_creation_days.day4.nitrogen import (
    NitrogenFixation, FixationResult, make_fixation_engine,
    NitrogenCycle, NitrogenState, make_nitrogen_cycle,
)
__all__ += [
    "NitrogenFixation", "FixationResult", "make_fixation_engine",
    "NitrogenCycle", "NitrogenState", "make_nitrogen_cycle",
]

from ._02_creation_days.day4.gravity_tides import (
    TidalField, TidalState, make_tidal_field, OceanNutrients, OceanState, make_ocean_nutrients,
)
__all__ += [
    "TidalField", "TidalState", "make_tidal_field",
    "OceanNutrients", "OceanState", "make_ocean_nutrients",
]

__version__ = "2.7.0"

# 흐름 엔진 (시간 순서 1→2→3→4→5)
from . import pipeline
run_pipeline = pipeline.run_pipeline
PipelineState = pipeline.PipelineState
run_beginnings = pipeline.run_beginnings
run_creation_days = pipeline.run_creation_days
run_eden_os_underworld = pipeline.run_eden_os_underworld
run_firmament_era = pipeline.run_firmament_era
run_noah_flood = pipeline.run_noah_flood
__all__ += ["run_pipeline", "PipelineState", "run_beginnings", "run_creation_days",
            "run_eden_os_underworld", "run_firmament_era", "run_noah_flood", "pipeline"]
