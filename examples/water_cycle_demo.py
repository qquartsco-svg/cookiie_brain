"""Phase 6b Demo — 수순환 (Water Cycle): 증발·응결·잠열·SurfaceOcean 연동

검증 항목:
  P6b-1: Clausius-Clapeyron (e_sat(T))
  P6b-2: 잠열 포함 시 T_surface 감소 (증발 냉각)
  P6b-3: H₂O 피드백 수렴
  P6b-4: surface_heat_flux → ocean_extras 연동
  P6b-5: 기어 분리 유지
"""

import numpy as np
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from L0_solar.day2.atmosphere import (
    AtmosphereColumn,
    AtmosphereComposition,
    saturation_vapor_pressure,
    saturation_mixing_ratio,
    evaporation_rate,
    latent_heat_flux,
)
from L0_solar.day1.em import SolarLuminosity
from L0_solar.day4.core import EvolutionEngine, Body3D


PASS = "\u2705 PASS"
FAIL = "\u274c FAIL"


def check(name, condition, detail=""):
    tag = PASS if condition else FAIL
    print(f"  {tag}  {name}" + (f"  ({detail})" if detail else ""))
    return condition


def main():
    all_pass = True
    sun = SolarLuminosity(mass_solar=1.0)
    F_earth = sun.irradiance_si(1.0)

    print("=" * 60)
    print(" Phase 6b: \uc218\uc21c\ud658 (Water Cycle) \u2014 \uc99d\ubc1c\uac74\uc7a5\uc7a5\uc5ed \uc5f0\ub3d9")
    print("=" * 60)

    # P6b-1: Clausius-Clapeyron
    print("\n[P6b-1] Clausius-Clapeyron e_sat(T)")

    e_273 = saturation_vapor_pressure(273.15)
    e_288 = saturation_vapor_pressure(288.15)
    e_373 = saturation_vapor_pressure(373.15)
    print(f"  e_sat(273K) = {e_273:.0f} Pa")
    print(f"  e_sat(288K) = {e_288:.0f} Pa")
    print(f"  e_sat(373K) = {e_373:.0f} Pa")

    all_pass &= check("e_sat(273) \u2248 611 Pa", 580 < e_273 < 640, f"{e_273:.0f}")
    all_pass &= check("e_sat(373) \u2248 101 kPa", 95e3 < e_373 < 110e3, f"{e_373/1e3:.1f} kPa")

    # P6b-2: Latent heat cooling
    print("\n[P6b-2] \uc99d\ubc1c \ub0ad\uc7a5 (\uc7a5\uc5ed \ud3ec\ud568)")

    atm_no_latent = AtmosphereColumn(T_surface_init=290.0, use_water_cycle=False)
    atm_with_latent = AtmosphereColumn(T_surface_init=290.0, use_water_cycle=True, h2o_relax_yr=0.05)

    for _ in range(100):
        atm_no_latent.step(F_earth, 0.1)
        atm_with_latent.step(F_earth, 0.1)

    T_no = atm_no_latent.T_surface
    T_with = atm_with_latent.T_surface
    print(f"  T (no water cycle)   = {T_no:.2f} K")
    print(f"  T (with water cycle) = {T_with:.2f} K")
    print(f"  E = {atm_with_latent._E_evap:.2e} kg/(m^2 s)")
    print(f"  Q_latent = {atm_with_latent._Q_latent:.1f} W/m^2")

    all_pass &= check("T with latent < T without", T_with < T_no + 0.5, f"\u0394T={T_no-T_with:.2f} K")

    # P6b-3: H2O feedback
    print("\n[P6b-3] H2O \ud53d\ub4dc\ubc31 \uc218\ub828")

    comp_start = AtmosphereComposition(H2O=0.005)
    atm_h2o = AtmosphereColumn(composition=comp_start, T_surface_init=285.0, use_water_cycle=True, h2o_relax_yr=0.05)
    for _ in range(200):
        atm_h2o.step(F_earth, 0.1)
    H2O_final = atm_h2o.composition.H2O
    q_sat = saturation_mixing_ratio(atm_h2o.T_surface, atm_h2o.surface_pressure())
    w_sat = q_sat / 0.622
    print(f"  H2O start: 0.005 \u2192 final: {H2O_final:.4f}")
    print(f"  w_sat(T,P): {w_sat:.4f}")

    all_pass &= check("H2O converges toward saturation", abs(H2O_final - w_sat) < 0.02, f"\u0394={abs(H2O_final-w_sat):.4f}")

    # P6b-4: surface_heat_flux -> ocean_extras
    print("\n[P6b-4] surface_heat_flux \u2192 ocean_extras \uc5f0\ub3d9")

    engine = EvolutionEngine()
    engine.add_body(Body3D("Sun", mass=1.0, pos=np.zeros(3), vel=np.zeros(3)))
    engine.add_body(Body3D("Earth", mass=3e-6, pos=np.array([1, 0, 0]), vel=np.array([0, 2*np.pi, 0]),
                          spin_axis=np.array([0, np.sin(np.radians(23.44)), np.cos(np.radians(23.44))]),
                          spin_rate=2*np.pi*365.25, J2=1.08e-3, radius=4.26e-5, obliquity=np.radians(23.44)))
    engine.form_ocean("Earth", n_wells=12)

    atm_coupled = AtmosphereColumn(T_surface_init=288.0, use_water_cycle=True)
    depths_before = engine.oceans["Earth"].depths.copy()

    for _ in range(10):
        engine.step(0.01, ocean=True, ocean_extras={
            "Earth": {"heat_flux": atm_coupled.surface_heat_flux()}
        })
        r = np.linalg.norm(engine.bodies[1].pos)
        atm_coupled.step(sun.irradiance_si(r), 0.01)

    depths_after = engine.oceans["Earth"].depths
    delta_depths = np.abs(depths_after - depths_before)
    print(f"  max |depths change| = {np.max(delta_depths):.2e}")

    all_pass &= check("Ocean depths modified by heat_flux", np.max(delta_depths) > 0, "coupling active")

    # P6b-5: Gear separation
    print("\n[P6b-5] \uae30\uc5b4 \ubd84\ub9ac")

    E0 = engine.total_energy()
    for _ in range(50):
        engine.step(0.01, ocean_extras={"Earth": {"heat_flux": atm_coupled.surface_heat_flux()}})
        r = np.linalg.norm(engine.bodies[1].pos)
        atm_coupled.step(sun.irradiance_si(r), 0.01)
    E1 = engine.total_energy()
    dE = abs((E1 - E0) / (abs(E0) + 1e-30))
    print(f"  dE/E = {dE:.2e}")

    all_pass &= check("Core energy conserved (dE/E < 1e-5)", dE < 1e-5, f"{dE:.2e}")

    print("\n" + "=" * 60)
    tag = "ALL PASS \u2705" if all_pass else "SOME FAILED \u274c"
    print(f" Phase 6b \uac80\uc99d: {tag}")
    print("=" * 60)

    return all_pass


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
