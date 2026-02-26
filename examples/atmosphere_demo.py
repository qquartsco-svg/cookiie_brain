"""Phase 6a Demo — 궁창 / Firmament: Greenhouse + Thermal Inertia

검증 항목:
  P6a-1: 온실 효과 (T_eq 254K → T_surface 288K)
  P6a-2: 대기 없음 (ε_a=0 → T_surface = T_eq)
  P6a-3: 광학 깊이 (τ) 조성 의존성
  P6a-4: 열적 관성 (thermal timescale ≈ 1–3 yr)
  P6a-5: 열평형 수렴 (cold start 200K → equilibrium)
  P6a-6: 대기압 + 물 상태 (liquid water check)
  P6a-7: 초기 지구 (faint Sun + high CO₂ → habitable)
  P6a-8: 기어 분리 (core 에너지 보존 무영향)
"""

import numpy as np
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from solar.atmosphere import (
    AtmosphereColumn,
    AtmosphereComposition,
    GreenhouseParams,
    optical_depth,
    effective_emissivity,
    equilibrium_surface_temp,
)
from solar.em import SolarLuminosity
from solar.core import EvolutionEngine, Body3D


PASS = "\u2705 PASS"
FAIL = "\u274c FAIL"


def check(name, condition, detail=""):
    tag = PASS if condition else FAIL
    print(f"  {tag}  {name}" + (f"  ({detail})" if detail else ""))
    return condition


def main():
    all_pass = True

    print("=" * 65)
    print(" Phase 6a: \uad81\ucc3d \u2014 Greenhouse + Thermal Inertia")
    print("=" * 65)

    sun = SolarLuminosity(mass_solar=1.0, alpha=4.0)
    F_earth = sun.irradiance_si(1.0)

    # ──── P6a-1: Greenhouse effect ────────────────────
    print("\n[P6a-1] \uc628\uc2e4 \ud6a8\uacfc: T_eq \u2192 T_surface")

    atm = AtmosphereColumn(
        body_name="Earth",
        surface_gravity=9.81,
        albedo=0.306,
        T_surface_init=288.0,
    )
    st = atm.state(F_earth)

    print(f"  T_eq (bare)   = {st.T_eq:.1f} K")
    print(f"  T_surface     = {st.T_surface:.1f} K")
    print(f"  Greenhouse \u0394T = +{st.greenhouse_dT:.1f} K")
    print(f"  \u03c4_IR          = {st.optical_depth:.3f}")
    print(f"  \u03b5_a           = {st.emissivity_atm:.3f}")

    all_pass &= check("T_eq \u2248 254 K", abs(st.T_eq - 254) < 2, f"{st.T_eq:.1f}")
    all_pass &= check("T_surface \u2248 288 K", abs(st.T_surface - 288) < 2, f"{st.T_surface:.1f}")
    all_pass &= check("\u0394T \u2248 33 K", abs(st.greenhouse_dT - 33) < 4, f"+{st.greenhouse_dT:.1f}")

    # ──── P6a-2: No atmosphere ────────────────────────
    print("\n[P6a-2] \ub300\uae30 \uc5c6\uc74c: T_surface = T_eq")

    no_atm = AtmosphereColumn(
        body_name="Bare_Rock",
        surface_gravity=9.81,
        albedo=0.306,
        composition=AtmosphereComposition(
            N2=0, O2=0, CO2=0, H2O=0, CH4=0, column_mass=0,
        ),
        greenhouse_params=GreenhouseParams(tau_base=0.0),
        T_surface_init=254.0,
    )
    st_no = no_atm.state(F_earth)

    all_pass &= check("\u03c4 = 0", st_no.optical_depth < 0.001, f"{st_no.optical_depth:.6f}")
    all_pass &= check("\u03b5_a \u2248 0", st_no.emissivity_atm < 0.001, f"{st_no.emissivity_atm:.6f}")
    all_pass &= check(
        "T_surface = T_eq",
        abs(st_no.T_surface - st_no.T_eq) < 1,
        f"T_s={st_no.T_surface:.1f}, T_eq={st_no.T_eq:.1f}",
    )

    # ──── P6a-3: Composition dependence ───────────────
    print("\n[P6a-3] \uad11\ud559 \uae4a\uc774 \uc870\uc131 \uc758\uc874\uc131")

    tau_pre = optical_depth(CO2=280e-6, H2O=0.01, CH4=0.7e-6)
    tau_cur = optical_depth(CO2=400e-6, H2O=0.01, CH4=1.8e-6)
    tau_10x = optical_depth(CO2=4000e-6, H2O=0.01, CH4=1.8e-6)
    tau_dry = optical_depth(CO2=400e-6, H2O=0.001, CH4=1.8e-6)

    print(f"  Pre-industrial : \u03c4 = {tau_pre:.3f}")
    print(f"  Current Earth  : \u03c4 = {tau_cur:.3f}")
    print(f"  10\u00d7 CO\u2082       : \u03c4 = {tau_10x:.3f}")
    print(f"  Dry (0.1% H\u2082O): \u03c4 = {tau_dry:.3f}")

    all_pass &= check(
        "\u03c4 increases with CO\u2082",
        tau_10x > tau_cur > tau_pre,
    )
    ratio_10x = (tau_10x - tau_cur) / (tau_cur - tau_pre + 1e-30)
    all_pass &= check(
        "CO2 sub-linear (log saturation)",
        ratio_10x < 10.0,
        f"10x CO2 gives {ratio_10x:.1f}x tau increase, not 10x",
    )
    all_pass &= check(
        "H\u2082O is dominant contributor",
        tau_dry < tau_cur,
        f"\u0394\u03c4(H\u2082O) = {tau_cur - tau_dry:.3f}",
    )

    # ──── P6a-4: Thermal timescale ────────────────────
    print("\n[P6a-4] \uc5f4\uc801 \uad00\uc131 (thermal timescale)")

    tau_th_yr = atm.thermal_timescale_s() / 3.15576e7
    print(f"  \u03c4_thermal = {tau_th_yr:.2f} yr (ocean-dominated)")

    all_pass &= check(
        "\u03c4_th \u2248 1\u20133 yr",
        0.5 < tau_th_yr < 5.0,
        f"{tau_th_yr:.2f} yr",
    )

    # ──── P6a-5: Cold start convergence ───────────────
    print("\n[P6a-5] \uc5f4\ud3c9\ud615 \uc218\ub834 (cold start 200K)")

    cold = AtmosphereColumn(
        body_name="Earth_cold",
        surface_gravity=9.81,
        albedo=0.306,
        T_surface_init=200.0,
    )
    T_target = cold.equilibrium_temp(F_earth)

    dt = 0.1
    for _ in range(300):
        cold.step(F_earth, dt)

    T_final = cold.T_surface
    err = abs(T_final - T_target)
    print(f"  Start: 200.0 K \u2192 Final: {T_final:.2f} K")
    print(f"  Equilibrium target: {T_target:.2f} K")
    print(f"  Error: {err:.4f} K after {cold.time_yr:.0f} yr")

    all_pass &= check(
        "Converges to equilibrium",
        err < 0.1,
        f"\u0394T = {err:.4f} K",
    )

    # also test hot start
    hot = AtmosphereColumn(
        body_name="Earth_hot",
        surface_gravity=9.81,
        albedo=0.306,
        T_surface_init=400.0,
    )
    for _ in range(300):
        hot.step(F_earth, 0.1)
    err_hot = abs(hot.T_surface - T_target)
    all_pass &= check(
        "Hot start also converges",
        err_hot < 0.1,
        f"400K \u2192 {hot.T_surface:.2f} K, \u0394={err_hot:.4f}",
    )

    # ──── P6a-6: Pressure + water phase ───────────────
    print("\n[P6a-6] \ub300\uae30\uc555 + \ubb3c \uc0c1\ud0dc")

    P = atm.surface_pressure()
    wp = atm.water_phase()
    hab = atm.habitable()

    print(f"  P_surface  = {P:.0f} Pa ({P / 101325:.3f} atm)")
    print(f"  Water phase: {wp}")
    print(f"  Habitable  : {hab}")

    all_pass &= check("P \u2248 101 kPa", abs(P - 101325) < 1000, f"{P:.0f} Pa")
    all_pass &= check("Water is liquid", wp == "liquid")
    all_pass &= check("Habitable = True", hab)

    # Mars comparison
    mars_atm = AtmosphereColumn(
        body_name="Mars",
        surface_gravity=3.72,
        albedo=0.25,
        composition=AtmosphereComposition(
            N2=0.027, O2=0.0, CO2=0.953, H2O=0.0003, CH4=0.0,
            column_mass=170.0,
        ),
        T_surface_init=210.0,
    )
    F_mars = sun.irradiance_si(1.524)
    mars_st = mars_atm.state(F_mars)
    print(f"\n  Mars comparison:")
    print(f"    P = {mars_st.P_surface:.0f} Pa, T = {mars_st.T_surface:.0f} K")
    print(f"    Water: {mars_st.water_phase}, Habitable: {mars_st.habitable}")
    all_pass &= check("Mars not habitable", not mars_st.habitable)

    # ──── P6a-7: Early Earth ──────────────────────────
    print("\n[P6a-7] \ucd08\uae30 \uc9c0\uad6c (Faint Young Sun)")

    faint_sun = SolarLuminosity(mass_solar=1.0, luminosity_override=0.7)
    F_early = faint_sun.irradiance_si(1.0)
    print(f"  F_solar (70% Sun) = {F_early:.0f} W/m\u00b2")

    early_comp = AtmosphereComposition(
        N2=0.90,
        O2=0.0,
        CO2=0.01,
        H2O=0.02,
        CH4=100e-6,
        column_mass=1.2e4,
    )
    early = AtmosphereColumn(
        body_name="Early_Earth",
        surface_gravity=9.81,
        albedo=0.15,
        composition=early_comp,
        T_surface_init=250.0,
    )
    for _ in range(300):
        early.step(F_early, 0.1)

    st_e = early.state(F_early)
    print(f"  T_eq (bare)   = {st_e.T_eq:.1f} K")
    print(f"  T_surface     = {st_e.T_surface:.1f} K")
    print(f"  \u03c4_IR          = {st_e.optical_depth:.3f}")
    print(f"  \u03b5_a           = {st_e.emissivity_atm:.3f}")
    print(f"  Greenhouse \u0394T = +{st_e.greenhouse_dT:.1f} K")
    print(f"  Water phase   = {st_e.water_phase}")
    print(f"  Habitable     = {st_e.habitable}")

    all_pass &= check(
        "Early Earth T > 273K (liquid water)",
        st_e.T_surface > 273,
        f"{st_e.T_surface:.1f} K",
    )
    all_pass &= check("Faint Young Sun paradox resolved", st_e.habitable)

    # ──── P6a-8: Gear separation ──────────────────────
    print("\n[P6a-8] \uae30\uc5b4 \ubd84\ub9ac \u2014 core \uc5d0\ub108\uc9c0 \ubcf4\uc874")

    engine = EvolutionEngine()
    engine.add_body(Body3D("Sun", mass=1.0, pos=np.zeros(3), vel=np.zeros(3)))
    engine.add_body(Body3D(
        "Earth",
        mass=3.003e-6,
        pos=np.array([1.0, 0.0, 0.0]),
        vel=np.array([0.0, 2 * np.pi, 0.0]),
        spin_axis=np.array([
            0.0,
            np.sin(np.radians(23.44)),
            np.cos(np.radians(23.44)),
        ]),
        spin_rate=2 * np.pi * 365.25,
        J2=1.08263e-3,
        radius=4.263e-5,
        obliquity=np.radians(23.44),
    ))

    test_atm = AtmosphereColumn(T_surface_init=288.0)
    E0 = engine.total_energy()

    for _ in range(100):
        engine.step(0.01)
        r_au = np.linalg.norm(engine.bodies[1].pos)
        F = sun.irradiance_si(r_au)
        test_atm.step(F, 0.01)

    E1 = engine.total_energy()
    dE = abs((E1 - E0) / (abs(E0) + 1e-30))
    print(f"  dE/E = {dE:.2e}")
    print(f"  T_surface after 1 yr = {test_atm.T_surface:.2f} K")

    all_pass &= check(
        "Core energy conserved (dE/E < 1e-8)",
        dE < 1e-8,
        f"{dE:.2e}",
    )

    # ──── Summary ─────────────────────────────────────
    print("\n" + "=" * 65)
    tag = "ALL PASS \u2705" if all_pass else "SOME FAILED \u274c"
    print(f" Phase 6a \uac80\uc99d: {tag}")
    print("=" * 65)

    # ──── State summary table ─────────────────────────
    print("\n-- 행성별 대기 상태 --")
    hdr = "{:<14} {:>7} {:>7} {:>6} {:>6} {:>10} {:>7} {:>5}".format(
        "Planet", "T_eq", "T_s", "dT", "tau", "P [Pa]", "Water", "Hab",
    )
    print(f"  {hdr}")
    print("  " + "-" * 65)

    planets = [
        ("Earth", 1.0, 0.306, 9.81, AtmosphereComposition(), 288.0),
        ("Mars", 1.524, 0.25, 3.72,
         AtmosphereComposition(N2=0.027, CO2=0.953, H2O=0.0003, CH4=0,
                               column_mass=170.0), 210.0),
        ("Venus", 0.723, 0.77, 8.87,
         AtmosphereComposition(N2=0.035, CO2=0.965, H2O=0.00003, CH4=0,
                               column_mass=1.035e6), 737.0),
    ]
    for name, r_au, alb, g, comp, T_init in planets:
        F = sun.irradiance_si(r_au)
        col = AtmosphereColumn(
            body_name=name,
            surface_gravity=g,
            albedo=alb,
            composition=comp,
            T_surface_init=T_init,
        )
        s = col.state(F)
        hab_str = "Y" if s.habitable else "N"
        row = "{:<14} {:>5.0f}K {:>5.0f}K {:>+5.0f} {:>6.2f} {:>10.0f} {:>7} {:>5}".format(
            name, s.T_eq, s.T_surface, s.greenhouse_dT,
            s.optical_depth, s.P_surface, s.water_phase, hab_str,
        )
        print(f"  {row}")

    return all_pass


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
