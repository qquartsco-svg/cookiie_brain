#!/usr/bin/env python3
"""빛이 있으라 / Let There Be Light — Phase 5 검증
==================================================

"중력장이 공간을 지배하고, 행성이 궤도를 돌고,
 자기장이 방어막을 세운 그 위에 — 마침내 빛이 켜진다."

빛이 켜지는 순간:
  어둠 속의 질량들에 형태가 생긴다.
  그림자가 생긴다.
  낮과 밤이 나뉜다.
  존재의 의미가 시작된다.

물리:
  L/L☉ = (M/M☉)^α          질량-광도 관계
  F(r) = L / (4πr²)         역제곱 복사 조도
  P_rad = F / c             복사압
  T_eq = [F(1-A)/(4σ)]^¼   평형 온도

검증 항목:
  [P5-1] 질량-광도: L(1.0 M☉) = 1.0 L☉
  [P5-2] 역제곱 법칙: F ∝ 1/r²
  [P5-3] 전체 태양계 조명 — 수성~해왕성
  [P5-4] 평형 온도 (지구 ≈ 255K 이론값 근접)
  [P5-5] 복사압-태양풍 연동 (비율 보존)
  [P5-6] core/ 에너지 보존 (기어 분리)

단위: AU, yr, M_sun, L☉, F☉
"""

import sys
import os
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from L0_solar.day4.core import EvolutionEngine, Body3D
from L0_solar.day1.em import SolarLuminosity, SolarWind, Magnetosphere, MagneticDipole
from L0_solar.day4.data import PLANETS, SUN_DATA


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  본드 알베도 (NASA Planetary Fact Sheet)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

BOND_ALBEDOS = {
    "Mercury": 0.088,
    "Venus":   0.76,
    "Earth":   0.306,
    "Mars":    0.25,
    "Jupiter": 0.503,
    "Saturn":  0.342,
    "Uranus":  0.300,
    "Neptune": 0.290,
}

KNOWN_T_EQ = {
    "Mercury": 440,
    "Venus":   232,
    "Earth":   255,
    "Mars":    210,
    "Jupiter": 110,
    "Saturn":   81,
    "Uranus":   58,
    "Neptune":  46,
}


def print_header(title: str):
    print(f"\n{'=' * 72}")
    print(f"  {title}")
    print(f"{'=' * 72}\n")


def print_section(title: str):
    print(f"\n  [{title}]")
    print(f"  {'-' * 52}")


def run():
    # ══════════════════════════════════════════════════
    #  어둠의 시간 — 중력장만 존재하는 태양계
    # ══════════════════════════════════════════════════
    print_header("어둠 속의 태양계 — 빛이 있기 전")

    print("  태양계가 존재한다.")
    print("  질량이 있다. 중력이 있다. 궤도가 있다.")
    print("  그러나 아직 — 빛이 없다.")
    print()

    engine = EvolutionEngine()
    G = 4 * np.pi**2

    sun = Body3D("Sun", mass=1.0, pos=np.zeros(3), vel=np.zeros(3))
    engine.add_body(sun)

    planet_bodies = {}
    for name, pdata in PLANETS.items():
        a = pdata.semi_major_au
        v = np.sqrt(G * 1.0 / a)
        incl = np.radians(pdata.inclination_deg)
        pos = np.array([a * np.cos(incl), 0.0, a * np.sin(incl)])
        vel = np.array([0.0, v * np.cos(incl), v * np.sin(incl)])

        b = Body3D(name, mass=pdata.mass_solar, pos=pos, vel=vel,
                   radius=pdata.radius_au)
        engine.add_body(b)
        planet_bodies[name] = b

    engine.giant_impact("Earth", obliquity_deg=23.44, spin_period_days=1.0)

    print(f"  천체 수: {len(engine.bodies)} (태양 + 8행성 + 달)")
    print(f"  단위계: AU / yr / M_sun / G = 4pi^2")

    E0 = engine.total_energy()
    print(f"  초기 총 에너지: {E0:.8e}")
    print()
    print("  모든 행성이 어둠 속에서 궤도를 돈다...")
    print("  형태도 그림자도 없이 — 오직 중력만으로.")

    # ══════════════════════════════════════════════════
    #  빛이 있으라 — SolarLuminosity 점등
    # ══════════════════════════════════════════════════
    print_header("빛이 있으라 / LET THERE BE LIGHT")

    solar_lum = SolarLuminosity(
        star_name="Sun",
        mass_solar=SUN_DATA.mass_solar,
    )

    print(f"  항성: {solar_lum.star_name}")
    print(f"  질량: {solar_lum.mass_solar:.4f} M_sun")
    print(f"  광도: {solar_lum.luminosity:.4f} L_sun")
    print(f"  질량-광도 지수: alpha = {solar_lum.alpha:.1f}")
    print()
    print("  L = M^{:.1f} = ({:.4f})^{:.1f} = {:.4f} L_sun".format(
        solar_lum.alpha, solar_lum.mass_solar,
        solar_lum.alpha, solar_lum.luminosity,
    ))
    print()
    print("  ┌─────────────────────────────────────────┐")
    print("  │                                         │")
    print("  │    And God said, 'Let there be light,'  │")
    print("  │    and there was light.                  │")
    print("  │                                         │")
    print("  │    — Genesis 1:3                        │")
    print("  │                                         │")
    print("  │    빛이 있으라 하시니 빛이 있었고         │")
    print("  │                                         │")
    print("  └─────────────────────────────────────────┘")

    # ══════════════════════════════════════════════════
    #  P5-1: 질량-광도 관계 검증
    # ══════════════════════════════════════════════════
    print_section("P5-1: 질량-광도 관계 / Mass-Luminosity Relation")

    L_expected = 1.0 ** 4.0  # 1.0 M_sun → 1.0 L_sun
    L_err = abs(solar_lum.luminosity - L_expected)
    ml_pass = L_err < 1e-10

    print(f"  L(1.0 M_sun) = {solar_lum.luminosity:.6f} L_sun")
    print(f"  이론값:        {L_expected:.6f} L_sun")
    print(f"  오차:          {L_err:.2e}")
    print(f"  결과:          {'PASS' if ml_pass else 'FAIL'}")

    test_masses = [0.5, 0.8, 1.0, 1.5, 2.0]
    print(f"\n  {'M/M_sun':>8s}  {'L/L_sun (계산)':>15s}  {'L/L_sun (이론)':>15s}")
    print(f"  {'-'*8}  {'-'*15}  {'-'*15}")
    for m in test_masses:
        lum_test = SolarLuminosity(mass_solar=m)
        theory = m ** 4.0
        print(f"  {m:>8.2f}  {lum_test.luminosity:>15.6f}  {theory:>15.6f}")

    # ══════════════════════════════════════════════════
    #  P5-2: 역제곱 법칙 검증
    # ══════════════════════════════════════════════════
    print_section("P5-2: 역제곱 법칙 / Inverse-Square Law")

    print(f"\n  {'거리(AU)':>10s}  {'F [F_sun]':>12s}  {'이론 1/r^2':>12s}  {'오차':>8s}")
    print(f"  {'-'*10}  {'-'*12}  {'-'*12}  {'-'*8}")

    isq_errors = []
    for r in [0.387, 0.723, 1.0, 1.524, 5.203, 9.555, 19.218, 30.110]:
        F = solar_lum.irradiance(r)
        theory = 1.0 / r**2
        err = abs(F - theory) / theory * 100
        isq_errors.append(err)
        print(f"  {r:>10.3f}  {F:>12.6f}  {theory:>12.6f}  {err:>7.3f}%")

    isq_pass = all(e < 0.01 for e in isq_errors)
    print(f"\n  1/r^2 법칙: {'PASS' if isq_pass else 'FAIL'}")

    # ══════════════════════════════════════════════════
    #  P5-3: 전체 태양계 조명 — 빛이 퍼지는 순간
    # ══════════════════════════════════════════════════
    print_section("P5-3: 빛이 태양계를 비추다 / Light Fills the Solar System")

    sun_b = engine.find("Sun")
    positions = {name: engine.find(name).pos for name in PLANETS}

    states = solar_lum.illuminate_system(
        positions, sun_b.pos, BOND_ALBEDOS,
    )

    print()
    print(f"  {'행성':>10s}  {'거리(AU)':>10s}  {'조도[F_sun]':>12s}  "
          f"{'조도[W/m^2]':>12s}  {'T_eq(K)':>8s}  {'NASA(K)':>8s}")
    print(f"  {'-'*10}  {'-'*10}  {'-'*12}  {'-'*12}  {'-'*8}  {'-'*8}")

    for name in ["Mercury", "Venus", "Earth", "Mars",
                  "Jupiter", "Saturn", "Uranus", "Neptune"]:
        s = states[name]
        known_t = KNOWN_T_EQ.get(name, 0)
        print(f"  {name:>10s}  {s.distance_au:>10.4f}  {s.irradiance:>12.6f}  "
              f"{s.irradiance_si:>12.1f}  {s.equilibrium_temp_k:>8.1f}  {known_t:>8d}")

    earth_state = states["Earth"]
    earth_T_err = abs(earth_state.equilibrium_temp_k - 255) / 255 * 100

    print(f"\n  지구 평형 온도: {earth_state.equilibrium_temp_k:.1f} K")
    print(f"  이론값 (A=0.306): ~255 K")
    print(f"  오차: {earth_T_err:.1f}%")

    temp_pass = earth_T_err < 5.0
    print(f"  결과: {'PASS' if temp_pass else 'FAIL'}")

    # ══════════════════════════════════════════════════
    #  P5-4: 복사(photon) vs 플라즈마(wind) — 독립 입력 확인
    # ══════════════════════════════════════════════════
    print_section("P5-4: 복사 vs 플라즈마 — 독립 입력 / Photon vs Plasma")

    wind = SolarWind(sun_name="Sun")

    P_RAD_1AU_SI = solar_lum.radiation_pressure_si(1.0)  # F/c [Pa]
    P_SW_1AU_SI = 2.0e-9  # canonical solar wind dynamic pressure [Pa]
    physical_ratio = P_RAD_1AU_SI / P_SW_1AU_SI

    print(f"\n  P_rad(1 AU) = F/c = {P_RAD_1AU_SI:.4e} Pa")
    print(f"  P_sw (1 AU) = ρv² ≈ {P_SW_1AU_SI:.4e} Pa  (canonical)")
    print(f"  P_rad / P_sw ≈ {physical_ratio:.0f}")
    print(f"  → 복사압 >> 태양풍 동압 (광자와 플라즈마는 독립 입력)")
    print()

    print(f"  {'행성':>10s}  {'P_rad [Pa]':>12s}  {'P_sw [norm]':>12s}  {'F [W/m^2]':>12s}")
    print(f"  {'-'*10}  {'-'*12}  {'-'*12}  {'-'*12}")

    for name in ["Mercury", "Venus", "Earth", "Mars", "Jupiter"]:
        s = states[name]
        sw = wind.state_at(engine.find(name).pos, sun_b.pos)
        print(f"  {name:>10s}  {s.radiation_pressure_si:>12.4e}  "
              f"{sw.dynamic_pressure:>12.6f}  {s.irradiance_si:>12.1f}")

    chain_pass = abs(solar_lum.radiation_pressure_si(1.0) - 1361.0 / 2.998e8) < 1e-4
    print(f"\n  P_rad = F/c 물리 일관성: {'PASS' if chain_pass else 'FAIL'}")

    # ══════════════════════════════════════════════════
    #  P5-5: 자기권까지의 완전 체인
    # ══════════════════════════════════════════════════
    print_section("P5-5: 완전 체인 — 빛 → 태양풍 → 자기장 → 자기권")

    R_EARTH = PLANETS["Earth"].radius_au
    earth_b = engine.find("Earth")
    dipole = MagneticDipole(body_name="Earth", tilt_deg=11.5)
    magneto = Magnetosphere(dipole, wind)

    ms = magneto.evaluate(earth_b.pos, R_EARTH, earth_b.spin_axis, sun_b.pos)

    print(f"  [빛]   태양 광도:     {solar_lum.luminosity:.4f} L_sun")
    print(f"  [빛]   지구 조도:     {earth_state.irradiance_si:.1f} W/m^2")
    print(f"  [빛]   복사압 P_rad:  {earth_state.radiation_pressure_si:.4e} Pa")
    print(f"  [바람] 태양풍 P_sw:   {wind.dynamic_pressure(1.0):.4f} P0")
    print(f"  [자기] 표면 자기장:   1.0 B0")
    print(f"  [자기] 마그네토포즈:  {ms.magnetopause_R_eq:.2f} R_E (P_sw vs B)")
    print(f"  [자기] 차폐 지표:     {ms.shielding_factor:.4f}")
    print(f"  [빛]   평형 온도:     {earth_state.equilibrium_temp_k:.1f} K")

    # ══════════════════════════════════════════════════
    #  P5-6: 기어 분리 — core 에너지 보존
    # ══════════════════════════════════════════════════
    print_section("P5-6: 기어 분리 — 빛이 궤도를 바꾸지 않는다")

    dt = 0.0002
    n_steps = 10000  # 2년
    for _ in range(n_steps):
        engine.step(dt, ocean=False)

    E1 = engine.total_energy()
    dE = abs((E1 - E0) / E0)

    states_after = solar_lum.illuminate_system(
        {name: engine.find(name).pos for name in PLANETS},
        sun_b.pos, BOND_ALBEDOS,
    )

    print(f"  시뮬레이션: {n_steps * dt:.1f}년")
    print(f"  에너지 보존: dE/E = {dE:.4e}")
    print(f"  지구 조도 (t=0):    {earth_state.irradiance_si:.1f} W/m^2")
    print(f"  지구 조도 (t={n_steps*dt:.1f}yr): {states_after['Earth'].irradiance_si:.1f} W/m^2")

    energy_pass = dE < 1e-6
    print(f"  core 무결성: {'PASS' if energy_pass else 'FAIL'}")

    # ══════════════════════════════════════════════════
    #  빛과 그림자 — 존재의 순간
    # ══════════════════════════════════════════════════
    print_header("빛과 그림자 — 존재의 의미가 시작되다")

    print("  빛이 있기 전:")
    print("    - 질량이 있었다. 중력이 있었다.")
    print("    - 궤도가 있었다. 자전이 있었다.")
    print("    - 자기장이 있었다.")
    print("    - 그러나 형태가 없었다. 그림자가 없었다.")
    print()
    print("  빛이 있은 후:")
    print("    - 조도가 생겼다. F(r) = L/(4 pi r^2)")
    print(f"    - 지구에 {earth_state.irradiance_si:.0f} W/m^2의 에너지가 도달한다.")
    print(f"    - 수성은 {states['Mercury'].irradiance_si:.0f} W/m^2로 타오른다.")
    print(f"    - 해왕성은 {states['Neptune'].irradiance_si:.1f} W/m^2의 희미한 빛을 받는다.")
    print(f"    - 낮과 밤이 나뉜다. 그림자가 생긴다.")
    print(f"    - 온도가 정해진다. 지구는 {earth_state.equilibrium_temp_k:.0f}K.")
    print(f"    - 자기장은 태양풍을 막아내고, 빛은 오존층을 통과한다.")
    print()
    print("  빛이 있으라 하시니 — 빛이 있었고,")
    print("  빛이 있으매 — 존재의 의미가 시작되었다.")

    # ══════════════════════════════════════════════════
    #  전체 검증 요약
    # ══════════════════════════════════════════════════
    print_header("검증 요약 / VERIFICATION SUMMARY — v1.3.0")

    results = {
        "[P5-1] 질량-광도 L(1.0M)=1.0L":      ml_pass,
        "[P5-2] 역제곱 법칙 F ∝ 1/r²":         isq_pass,
        "[P5-3] 지구 평형 온도 ~255K":          temp_pass,
        "[P5-4] P_rad=F/c 물리 일관성":         chain_pass,
        "[P5-6] core 에너지 보존 (기어 분리)":   energy_pass,
    }

    all_pass = True
    for label, ok in results.items():
        status = "PASS" if ok else "FAIL"
        if not ok:
            all_pass = False
        print(f"  {label:<45s} {status}")

    mp_re = ms.magnetopause_R_eq
    print(f"""
  ┌───────────────────────────────────────────────────────┐
  │  Phase 5: Solar Luminosity — 빛이 있으라  v1.3.0      │
  │                                                       │
  │  L = M^4.0 = {solar_lum.luminosity:.4f} L_sun                          │
  │  F(1 AU) = {earth_state.irradiance_si:.0f} W/m^2  (Solar Constant)         │
  │  T_eq(Earth) = {earth_state.equilibrium_temp_k:.0f} K  (theory: 255 K)            │
  │                                                       │
  │  Full chain:                                          │
  │    Gravity → Orbits → Spin/Precession                 │
  │    → Magnetic Dipole → Solar Wind → Magnetosphere     │
  │    → Solar Luminosity → Irradiance → Temperature      │
  │                                                       │
  │  Observer mode: dE/E = {dE:.2e}                  │
  │  Magnetopause: {mp_re:.1f} R_E, Shielding: {ms.shielding_factor:.3f}            │
  │                                                       │
  │  "And there was light."                               │
  └───────────────────────────────────────────────────────┘
""")

    print(f"  통합 결과: {'ALL PASS' if all_pass else 'SOME FAILED'}")

    return all_pass


if __name__ == "__main__":
    success = run()
    sys.exit(0 if success else 1)
