"""BrainCore 연동: solar/atmosphere 환경 상태를 GlobalState extension 형식으로 제공.

GEAR_CONNECTION_STRATEGY Phase 1: CookiieBrain → BrainCore
환경 물리(F, T, P, habitable)를 인지 엔진이 읽을 수 있는 형태로 노출.

사용:
  data = get_solar_environment_extension(engine, sun, atmospheres, dt_yr=0.01)
  state.set_extension("solar_environment", data)

BrainCore를 import하지 않음. 호출자가 set_extension 수행.
"""

from typing import Dict, Any, Optional
import numpy as np

# solar 내부 import
from .core import EvolutionEngine, Body3D
from .data import build_solar_system
from .em import SolarLuminosity
from .atmosphere import AtmosphereColumn, AtmosphereComposition
from .surface import SurfaceSchema


def get_solar_environment_extension(
    engine: "EvolutionEngine",
    sun: "SolarLuminosity",
    atmospheres: Dict[str, "AtmosphereColumn"],
    dt_yr: float = 0.01,
) -> Dict[str, Any]:
    """solar 환경 상태를 BrainCore extension 형식으로 반환.

    engine.step(dt_yr, ocean=False) 및 atmosphere.step() 후 각 body의 F, T, P, habitable 등을 수집.

    Returns:
        {
            "time_yr": float,
            "bodies": {
                "Earth": {"F_solar": float, "T_surface": float, "P_surface": float,
                         "habitable": bool, "water_phase": str, "r_au": float},
                ...
            },
            "global": {"any_habitable": bool, "body_count": int},
        }
    """
    engine.step(dt_yr)

    engine.step(dt_yr, ocean=False)

    bodies_data = {}
    any_habitable = False
    for body in engine.bodies:
        if body.name == "Sun":
            continue
        r_au = np.linalg.norm(body.pos)
        F_si = sun.irradiance_si(r_au)

        atm = atmospheres.get(body.name)
        if atm is not None:
            atm.step(F_si, dt_yr)
            st = atm.state(F_si)
            bodies_data[body.name] = {
                "F_solar": F_si,
                "T_surface": st.T_surface,
                "P_surface": st.P_surface,
                "habitable": st.habitable,
                "water_phase": st.water_phase,
                "r_au": r_au,
                "T_eq": st.T_eq,
                "greenhouse_dT": st.greenhouse_dT,
            }
            if st.habitable:
                any_habitable = True
        else:
            bodies_data[body.name] = {
                "F_solar": F_si,
                "r_au": r_au,
                "T_surface": None,
                "P_surface": None,
                "habitable": False,
                "water_phase": None,
            }

    return {
        "time_yr": engine.time,
        "bodies": bodies_data,
        "global": {
            "any_habitable": any_habitable,
            "body_count": len(bodies_data),
        },
    }


def create_default_environment(
    use_water_cycle: bool = False,
    use_surface_schema: bool = True,
) -> tuple:
    """기본 태양계 + 대기 설정. 데모/통합용.

    Returns:
        (engine, sun, atmospheres)
    """
    engine = EvolutionEngine()
    for d in build_solar_system():
        if "_moon_config" in d:
            cfg = d["_moon_config"]
            engine.giant_impact(cfg["target"], **{k: v for k, v in cfg.items() if k != "target"})
        else:
            engine.add_body(Body3D(**d))

    sun = SolarLuminosity(mass_solar=1.0)
    sfc = SurfaceSchema(land_fraction=0.29) if use_surface_schema else None

    atmospheres = {}
    for body in engine.bodies:
        if body.name == "Sun":
            continue
        albedo = sfc.effective_albedo() if sfc and body.name == "Earth" else 0.306
        g = 9.81 if body.name == "Earth" else 3.71 if body.name == "Mars" else 8.87
        atmospheres[body.name] = AtmosphereColumn(
            body_name=body.name,
            surface_gravity=g,
            albedo=albedo,
            use_water_cycle=use_water_cycle and body.name == "Earth",
            T_surface_init=288.0 if body.name == "Earth" else 250.0,
        )

    return engine, sun, atmospheres
