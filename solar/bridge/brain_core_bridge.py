"""BrainCore 연동: solar/atmosphere/biosphere 환경 상태를 GlobalState extension 형식으로 제공.

GEAR_CONNECTION_STRATEGY Phase 1: CookiieBrain → BrainCore
환경 물리(F, T, P, habitable)를 인지 엔진이 읽을 수 있는 형태로 노출.
옵션으로 biosphere 연결 시 대기 조성·잠열·알베도 피드백 반영 (뉴런→지구→우주선 동일 템플릿).

사용:
  data = get_solar_environment_extension(engine, sun, atmospheres, dt_yr=0.01, ...)
  state.set_extension("solar_environment", data)
"""

from typing import Dict, Any, Optional
import numpy as np

# solar 내부 import
from solar.day4.core import EvolutionEngine, Body3D
from solar.day4.data import build_solar_system
from solar.day1.em import SolarLuminosity
from solar.day2.atmosphere import AtmosphereColumn, AtmosphereComposition
from solar.day3.surface import SurfaceSchema


def get_solar_environment_extension(
    engine: "EvolutionEngine",
    sun: "SolarLuminosity",
    atmospheres: Dict[str, "AtmosphereColumn"],
    dt_yr: float = 0.01,
    surface_schema: Optional["SurfaceSchema"] = None,
    biospheres: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """solar 환경 상태를 BrainCore extension 형식으로 반환.

    engine.step(dt_yr, ocean=False) 및 atmosphere.step() 후 각 body의 F, T, P, habitable 등을 수집.
    biospheres가 주어지면 지구 등 해당 body에 대해 biosphere.step(env, dt_yr) 후
    feedback을 대기 조성(CO2/O2/H2O), 잠열, 알베도에 반영한다.

    Returns:
        {
            "time_yr": float,
            "bodies": { "Earth": {...}, ... },
            "global": {"any_habitable": bool, "body_count": int},
        }
    """
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
            # Build env for biosphere if present
            st = atm.state(F_si)
            env = {
                "F_solar_si": F_si,
                "T_surface": st.T_surface,
                "P_surface": st.P_surface,
                "CO2": atm.composition.CO2,
                "H2O": atm.composition.H2O,
                "O2": atm.composition.O2,
                "water_phase": st.water_phase,
            }
            if surface_schema is not None:
                env["land_fraction"] = surface_schema.land_fraction

            extra_latent = 0.0
            if biospheres and body.name in biospheres:
                from solar.day3.biosphere.planet_bridge import biosphere_feedback_to_atmosphere
                bio = biospheres[body.name]
                fb = bio.step(env, dt_yr)
                converted = biosphere_feedback_to_atmosphere(
                    fb, dt_yr,
                    land_fraction=env.get("land_fraction", 0.29),
                    column_mass=atm.composition.column_mass,
                )
                # Apply composition deltas (clip to physical range)
                atm.composition.CO2 = np.clip(
                    atm.composition.CO2 + converted["delta_CO2_mixing"], 1e-6, 0.5
                )
                atm.composition.O2 = np.clip(
                    atm.composition.O2 + converted["delta_O2_mixing"], 0.0, 0.5
                )
                atm.composition.H2O = np.clip(
                    atm.composition.H2O + converted["delta_H2O_mixing"], 1e-6, 0.5
                )
                extra_latent = converted["extra_latent_heat_Wm2"]
                # Albedo: base from surface_schema + biosphere delta
                if surface_schema is not None:
                    base_land = surface_schema.albedo_land
                    base_ocean = surface_schema.albedo_ocean
                    f_land = surface_schema.land_fraction
                    new_land = base_land + converted["delta_albedo_land"]
                    atm.albedo = f_land * new_land + (1.0 - f_land) * base_ocean

            atm.step(F_si, dt_yr, extra_latent_heat_Wm2=extra_latent if extra_latent != 0 else None)
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
    use_biosphere: bool = False,
) -> tuple:
    """기본 태양계 + 대기 설정. 데모/통합용.

    use_biosphere=True 이면 Earth용 BiosphereColumn을 생성하여 반환.
    get_solar_environment_extension(..., surface_schema=sfc, biospheres=bios) 로 넘기면
    매 스텝 식생→대기 피드백이 적용된다.

    Returns:
        (engine, sun, atmospheres) 또는
        (engine, sun, atmospheres, surface_schema, biospheres) if use_biosphere
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

    if not use_biosphere:
        return engine, sun, atmospheres

    from solar.day3.biosphere import BiosphereColumn
    biospheres = {}
    if sfc is not None:
        biospheres["Earth"] = BiosphereColumn(
            body_name="Earth",
            land_fraction=sfc.land_fraction,
            organic_layer_init=0.12,
        )
    return engine, sun, atmospheres, sfc, biospheres
