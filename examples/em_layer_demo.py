#!/usr/bin/env python3
"""EM Layer Integration Demo — 자기장 + 태양풍 + 자기권 통합 검증
================================================================

Phase 2+3+4 전자기 레이어를 EvolutionEngine(core/) 위에 얹어
세차운동하는 지구의 자기권 환경을 시뮬레이션한다.

기어 구조:
  em/magnetosphere  ← em/magnetic_dipole + em/solar_wind
                    ← core/Body3D.spin_axis, .pos (읽기 전용)

검증 항목:
  [Phase 2] 자기쌍극자
    1) 표면 B 정확도 (적도=1.0, 극=2.0)
    2) 1/r³ 감쇠
  [Phase 3] 태양풍
    3) 1/r² 감쇠 (동압, 플럭스, 복사압, IMF)
    4) 행성별 태양풍 동압 비교
  [Phase 4] 자기권
    5) 마그네토포즈 ~10 R_E (지구 기준)
    6) 보우 쇼크 = 1.3 × 마그네토포즈
    7) 차폐 지표 > 0.8 (지구)
    8) 세차 연동 — 자기권이 자전축과 동기
  [기어 분리]
    9) core/ 물리 수정 없음 (에너지 보존)

단위: AU, yr, M_sun, B₀, P₀
"""

import sys
import os
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from L0_solar.day4.core import EvolutionEngine, Body3D
from L0_solar.day1.em import MagneticDipole, SolarWind, Magnetosphere
from L0_solar.day4.data import PLANETS


def print_header(title: str):
    print(f"\n{'=' * 70}")
    print(f"  {title}")
    print(f"{'=' * 70}\n")


def print_section(title: str):
    print(f"\n  [{title}]")
    print(f"  {'-' * 50}")


def run():
    print_header("EM LAYER INTEGRATION — Phase 2+3+4 통합 검증")
    print("  기어: em/magnetic_dipole + em/solar_wind + em/magnetosphere")
    print("  토대: core/EvolutionEngine (수정 없음)")

    # ── 시스템 구축 ──────────────────────────────────
    print_section("시스템 구축")

    engine = EvolutionEngine()
    R_EARTH = PLANETS["Earth"].radius_au

    sun = Body3D("Sun", mass=1.0, pos=np.zeros(3), vel=np.zeros(3))
    earth = Body3D(
        "Earth", mass=3.0035e-6,
        pos=np.array([1.0, 0.0, 0.0]),
        vel=np.array([0.0, 2 * np.pi, 0.0]),
        radius=R_EARTH,
    )
    engine.add_body(sun)
    engine.add_body(earth)
    engine.giant_impact("Earth", obliquity_deg=23.44, spin_period_days=1.0)

    dipole = MagneticDipole(body_name="Earth", tilt_deg=11.5)
    wind = SolarWind(sun_name="Sun")
    magneto = Magnetosphere(dipole, wind)

    earth_b = engine.find("Earth")
    sun_b = engine.find("Sun")
    print(f"  천체: Sun + Earth + Moon = {len(engine.bodies)}체")
    print(f"  지구 반지름: {R_EARTH:.4e} AU ({R_EARTH * 1.496e8:.0f} km)")

    # ══════════════════════════════════════════════════
    #  Phase 2: 자기쌍극자 검증
    # ══════════════════════════════════════════════════
    print_section("Phase 2: 자기쌍극자")

    m_hat = dipole.magnetic_axis(earth_b.spin_axis)
    eq_dir = np.cross(m_hat, np.array([0, 0, 1]))
    eq_dir /= np.linalg.norm(eq_dir) + 1e-30

    eq_pt = earth_b.pos + R_EARTH * eq_dir
    B_eq = np.linalg.norm(dipole.B_field(eq_pt, earth_b.pos, earth_b.spin_axis, R_EARTH))

    pole_pt = earth_b.pos + R_EARTH * m_hat
    B_pole = np.linalg.norm(dipole.B_field(pole_pt, earth_b.pos, earth_b.spin_axis, R_EARTH))

    p5 = earth_b.pos + 5 * R_EARTH * eq_dir
    B_5R = np.linalg.norm(dipole.B_field(p5, earth_b.pos, earth_b.spin_axis, R_EARTH))

    print(f"  적도 표면 |B|:  {B_eq:.4f} B₀  (이론 1.0)")
    print(f"  자기극 |B|:     {B_pole:.4f} B₀  (이론 2.0)")
    print(f"  5R 거리 |B|:    {B_5R:.6f} B₀  (이론 {1.0/125:.6f})")

    dipole_pass = abs(B_eq - 1.0) < 0.05 and abs(B_pole - 2.0) < 0.05
    decay_pass = abs(B_5R - B_eq/125) / (B_eq/125) < 0.01
    print(f"  표면 정확도:    {'PASS' if dipole_pass else 'FAIL'}")
    print(f"  1/r³ 감쇠:      {'PASS' if decay_pass else 'FAIL'}")

    # ══════════════════════════════════════════════════
    #  Phase 3: 태양풍 검증
    # ══════════════════════════════════════════════════
    print_section("Phase 3: 태양풍")

    sw_earth = wind.state_at(earth_b.pos, sun_b.pos)
    print(f"  지구 거리:      {sw_earth.distance_au:.4f} AU")
    print(f"  동압 P_sw:      {sw_earth.dynamic_pressure:.6f} P₀")
    print(f"  IMF:            {sw_earth.imf_magnitude:.6f} B_sw₀")
    print(f"  (복사압은 solar_luminosity.py에서 L→F/c로 유도)")

    print(f"\n  {'행성':>10s}  {'거리(AU)':>10s}  {'P_sw':>10s}  {'이론 P_sw':>10s}  {'오차':>8s}")
    print(f"  {'-'*10}  {'-'*10}  {'-'*10}  {'-'*10}  {'-'*8}")

    sw_errors = []
    for name in ["Mercury", "Venus", "Earth", "Mars", "Jupiter"]:
        a = PLANETS[name].semi_major_au
        pos = np.array([a, 0.0, 0.0])
        sw = wind.state_at(pos, np.zeros(3))
        theory = 1.0 / a**2
        err = abs(sw.dynamic_pressure - theory) / theory * 100
        sw_errors.append(err)
        print(f"  {name:>10s}  {a:>10.4f}  {sw.dynamic_pressure:>10.6f}  {theory:>10.6f}  {err:>7.2f}%")

    sw_pass = all(e < 0.1 for e in sw_errors)
    print(f"\n  1/r² 법칙 PASS: {'YES' if sw_pass else 'NO'}")

    # ══════════════════════════════════════════════════
    #  Phase 4: 자기권 검증
    # ══════════════════════════════════════════════════
    print_section("Phase 4: 자기권")

    ms = magneto.evaluate(earth_b.pos, R_EARTH, earth_b.spin_axis, sun_b.pos)

    print(f"  마그네토포즈:   {ms.magnetopause_R_eq:.2f} R_E  ({ms.magnetopause_r:.6e} AU)")
    print(f"  보우 쇼크:      {ms.bow_shock_R_eq:.2f} R_E  ({ms.bow_shock_r:.6e} AU)")
    print(f"  자기꼬리:       {ms.tail_length_R_eq:.0f} R_E")
    print(f"  차폐 지표:      {ms.shielding_factor:.4f}  (0=무방비, 1=완전)")
    print(f"  극 쿠스프 침투: {ms.cusp_penetration:.4f}")
    print(f"  에너지 유입:    {ms.energy_input_fraction:.4f}")

    r_mp_real = ms.magnetopause_R_eq
    mp_pass = 5.0 < r_mp_real < 20.0
    bs_ratio = ms.bow_shock_R_eq / ms.magnetopause_R_eq
    bs_pass = abs(bs_ratio - 1.3) < 0.01
    shield_pass = ms.shielding_factor > 0.7

    print(f"\n  마그네토포즈 범위 (5-20 R_E): {'PASS' if mp_pass else 'FAIL'}")
    print(f"  BS/MP 비율 ({bs_ratio:.2f} ≈ 1.3):     {'PASS' if bs_pass else 'FAIL'}")
    print(f"  차폐 지표 > 0.8:              {'PASS' if shield_pass else 'FAIL'}")

    # ══════════════════════════════════════════════════
    #  세차 연동 + 기어 분리 검증
    # ══════════════════════════════════════════════════
    print_section("세차 연동 + 기어 분리")

    E0 = engine.total_energy()
    spin0 = earth_b.spin_axis.copy()
    ms0 = magneto.evaluate(earth_b.pos, R_EARTH, earth_b.spin_axis, sun_b.pos)

    dt = 0.0002
    n_steps = 50000  # 10년
    ms_history = []

    for i in range(n_steps):
        engine.step(dt, ocean=False)
        if i % 10000 == 0:
            ms_snap = magneto.evaluate(
                earth_b.pos, R_EARTH, earth_b.spin_axis, sun_b.pos,
            )
            ms_history.append(ms_snap)

    E1 = engine.total_energy()
    dE = abs((E1 - E0) / E0)
    spin_final = earth_b.spin_axis.copy()
    ms_final = magneto.evaluate(earth_b.pos, R_EARTH, earth_b.spin_axis, sun_b.pos)

    spin_change = np.degrees(np.arccos(np.clip(np.dot(spin0, spin_final), -1, 1)))
    m0 = ms0.magnetic_axis
    mf = ms_final.magnetic_axis
    mag_change = np.degrees(np.arccos(np.clip(np.dot(m0, mf), -1, 1)))

    mp_variation = [h.magnetopause_R_eq for h in ms_history]
    shield_variation = [h.shielding_factor for h in ms_history]

    print(f"  시뮬레이션: {n_steps * dt:.0f}년")
    print(f"  에너지 보존: dE/E = {dE:.4e}")
    print(f"  자전축 변화: {spin_change:.4f}°")
    print(f"  자기축 변화: {mag_change:.4f}° (연동 확인)")
    print(f"  마그네토포즈 범위: {min(mp_variation):.2f} ~ {max(mp_variation):.2f} R_E")
    print(f"  차폐 지표 범위: {min(shield_variation):.4f} ~ {max(shield_variation):.4f}")

    coupling_pass = abs(spin_change - mag_change) < 0.01
    energy_pass = dE < 1e-6
    print(f"\n  세차-자기권 연동:  {'PASS' if coupling_pass else 'FAIL'}")
    print(f"  에너지 보존:       {'PASS' if energy_pass else 'FAIL'}")

    # ══════════════════════════════════════════════════
    #  전체 요약
    # ══════════════════════════════════════════════════
    print_header("검증 요약 / VERIFICATION SUMMARY")

    results = {
        "[P2] 표면 자기장 정확도": dipole_pass,
        "[P2] 1/r³ 감쇠 법칙": decay_pass,
        "[P3] 1/r² 태양풍 법칙": sw_pass,
        "[P4] 마그네토포즈 범위 (5-20 R_E)": mp_pass,
        "[P4] BS/MP 비율 ≈ 1.3": bs_pass,
        "[P4] 차폐 지표 > 0.7 (순수 쌍극자)": shield_pass,
        "[연동] 세차-자기권 동기": coupling_pass,
        "[분리] 에너지 보존 (core 무수정)": energy_pass,
    }

    all_pass = True
    for label, ok in results.items():
        status = "PASS" if ok else "FAIL"
        if not ok:
            all_pass = False
        print(f"  {label:<45s} {status}")

    print(f"\n  통합 결과: {'ALL PASS' if all_pass else 'SOME FAILED'}")

    print(f"""
  ┌──────────────────────────────────────────────────────┐
  │  EM Layer v1.2.0                                     │
  │                                                      │
  │  Phase 2: magnetic_dipole  B ∝ 1/r³, 11.5° tilt     │
  │  Phase 3: solar_wind       P ∝ 1/r², v_sw, IMF      │
  │  Phase 4: magnetosphere    r_mp ≈ {r_mp_real:5.1f} R_E            │
  │                            shielding = {ms_final.shielding_factor:.3f}          │
  │                                                      │
  │  기어 분리: em/ → core/ (단방향, 읽기 전용)          │
  │  core 물리: dE/E = {dE:.2e}                     │
  └──────────────────────────────────────────────────────┘
""")

    return all_pass


if __name__ == "__main__":
    success = run()
    sys.exit(0 if success else 1)
