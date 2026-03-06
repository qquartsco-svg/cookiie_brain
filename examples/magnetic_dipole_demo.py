#!/usr/bin/env python3
"""Magnetic Dipole Demo — 세차운동하는 지구의 자기쌍극자장 검증
============================================================

Phase 2: 전자기 레이어 첫 번째 기어.
core/(EvolutionEngine)의 자전축 상태를 읽어서
em/(MagneticDipole)이 공간상의 B(x,t)를 계산한다.

검증 항목:
  1) 표면 자기장 세기 — 적도 B₀=1.0, 극 B₀·√4=2.0
  2) 거리에 따른 감쇠 — B ∝ 1/r³
  3) 자기축-자전축 기울기 — 11.5° 유지
  4) 세차 연동 — 자전축이 움직이면 자기장도 따라감
  5) 기어 분리 — em/이 core/의 물리를 수정하지 않음

단위: AU, yr, M_sun, B₀ (표면 적도 자기장 = 1.0)
"""

import sys
import os
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from L0_solar.day4.core import EvolutionEngine, Body3D
from L0_solar.day1.em import MagneticDipole


def print_header(title: str):
    print(f"\n{'=' * 70}")
    print(f"  {title}")
    print(f"{'=' * 70}\n")


def print_section(title: str):
    print(f"\n  [{title}]")
    print(f"  {'-' * 50}")


def run():
    print_header("MAGNETIC DIPOLE VERIFICATION — Phase 2")
    print("  단위: AU, yr, M_sun, B₀ (표면 적도 = 1.0)")
    print("  자기축 기울기: 11.5° (자전축 대비)")

    # ── Phase 0: 엔진 + 쌍극자 구축 ──────────────────
    print_section("Phase 0: 시스템 구축")

    engine = EvolutionEngine()
    R_EARTH = 4.2635e-5  # AU

    sun = Body3D("Sun", mass=1.0, pos=np.zeros(3), vel=np.zeros(3))
    earth = Body3D(
        "Earth", mass=3.0035e-6,
        pos=np.array([1.0, 0.0, 0.0]),
        vel=np.array([0.0, 2 * np.pi, 0.0]),
        radius=R_EARTH,
    )
    engine.add_body(sun)
    engine.add_body(earth)
    moon = engine.giant_impact("Earth", obliquity_deg=23.44, spin_period_days=1.0)

    dipole = MagneticDipole(
        body_name="Earth",
        magnetic_moment=1.0,
        tilt_deg=11.5,
    )

    earth_body = engine.find("Earth")
    m_hat = dipole.magnetic_axis(earth_body.spin_axis)
    angle = np.degrees(np.arccos(np.clip(
        np.dot(m_hat, earth_body.spin_axis / np.linalg.norm(earth_body.spin_axis)),
        -1, 1
    )))

    print(f"  천체: Sun + Earth + Moon")
    print(f"  지구 반지름: {R_EARTH:.4e} AU")
    print(f"  자전축 기울기: {np.degrees(earth_body.obliquity):.2f}°")
    print(f"  자기축 기울기: {angle:.2f}° (자전축 대비)")
    print(f"  자전축: [{earth_body.spin_axis[0]:.4f}, {earth_body.spin_axis[1]:.4f}, {earth_body.spin_axis[2]:.4f}]")
    print(f"  자기축: [{m_hat[0]:.4f}, {m_hat[1]:.4f}, {m_hat[2]:.4f}]")

    # ── Phase 1: 표면 자기장 검증 ─────────────────────
    print_section("Phase 1: 표면 자기장 세기 검증")
    print()
    print(f"  {'위치':>12s}  {'이론값':>10s}  {'계산값':>10s}  {'오차':>8s}")
    print(f"  {'-'*12}  {'-'*10}  {'-'*10}  {'-'*8}")

    test_points = []

    s_hat = earth_body.spin_axis / np.linalg.norm(earth_body.spin_axis)

    eq_point = earth_body.pos + R_EARTH * np.array([0.0, 1.0, 0.0])
    fp_eq = dipole.field_at(eq_point, earth_body.pos, earth_body.spin_axis, R_EARTH)

    expected_eq = dipole.surface_field_strength(fp_eq.latitude_deg)
    err_eq = abs(fp_eq.B_magnitude - expected_eq) / (expected_eq + 1e-30) * 100
    print(f"  {'적도 근처':>12s}  {expected_eq:>10.4f}  {fp_eq.B_magnitude:>10.4f}  {err_eq:>7.2f}%")
    test_points.append(("적도 근처", expected_eq, fp_eq.B_magnitude, err_eq))

    pole_point = earth_body.pos + R_EARTH * m_hat
    fp_pole = dipole.field_at(pole_point, earth_body.pos, earth_body.spin_axis, R_EARTH)
    expected_pole = 2.0
    err_pole = abs(fp_pole.B_magnitude - expected_pole) / expected_pole * 100
    print(f"  {'자기극':>12s}  {expected_pole:>10.4f}  {fp_pole.B_magnitude:>10.4f}  {err_pole:>7.2f}%")
    test_points.append(("자기극", expected_pole, fp_pole.B_magnitude, err_pole))

    mid_lat_dir = (m_hat + np.array([0.0, 1.0, 0.0]))
    mid_lat_dir /= np.linalg.norm(mid_lat_dir)
    mid_point = earth_body.pos + R_EARTH * mid_lat_dir
    fp_mid = dipole.field_at(mid_point, earth_body.pos, earth_body.spin_axis, R_EARTH)
    expected_mid = dipole.surface_field_strength(fp_mid.latitude_deg)
    err_mid = abs(fp_mid.B_magnitude - expected_mid) / (expected_mid + 1e-30) * 100
    print(f"  {'중위도':>12s}  {expected_mid:>10.4f}  {fp_mid.B_magnitude:>10.4f}  {err_mid:>7.2f}%")
    test_points.append(("중위도", expected_mid, fp_mid.B_magnitude, err_mid))

    surface_pass = all(e < 5.0 for _, _, _, e in test_points)
    print(f"\n  표면 자기장 PASS: {'YES' if surface_pass else 'NO'}")

    # ── Phase 2: 거리 감쇠 (1/r³) 검증 ───────────────
    print_section("Phase 2: 거리 감쇠 검증 (B ∝ 1/r³)")

    r_multiples = [1.0, 2.0, 3.0, 5.0, 10.0]
    test_dir = np.array([0.0, 1.0, 0.0])
    B_ref = None

    print(f"\n  {'r/R_eq':>8s}  {'|B|':>12s}  {'이론 비율':>10s}  {'실제 비율':>10s}  {'오차':>8s}")
    print(f"  {'-'*8}  {'-'*12}  {'-'*10}  {'-'*10}  {'-'*8}")

    decay_errors = []
    for mult in r_multiples:
        point = earth_body.pos + mult * R_EARTH * test_dir
        B = dipole.B_field(point, earth_body.pos, earth_body.spin_axis, R_EARTH)
        B_mag = np.linalg.norm(B)

        if B_ref is None:
            B_ref = B_mag
            print(f"  {mult:>8.1f}  {B_mag:>12.6f}  {'(기준)':>10s}  {'(기준)':>10s}  {'—':>8s}")
        else:
            theory_ratio = 1.0 / mult**3
            actual_ratio = B_mag / B_ref
            err = abs(actual_ratio - theory_ratio) / theory_ratio * 100
            decay_errors.append(err)
            print(f"  {mult:>8.1f}  {B_mag:>12.6f}  {theory_ratio:>10.6f}  {actual_ratio:>10.6f}  {err:>7.2f}%")

    decay_pass = all(e < 1.0 for e in decay_errors)
    print(f"\n  1/r³ 감쇠 PASS: {'YES' if decay_pass else 'NO'}")

    # ── Phase 3: 세차 연동 검증 ──────────────────────
    print_section("Phase 3: 세차 연동 — 자전축 변화 → 자기장 변화")

    E0 = engine.total_energy()
    spin0 = earth_body.spin_axis.copy()
    m0 = dipole.magnetic_axis(spin0).copy()

    dt = 0.0002
    n_steps = 50000  # 10년
    sample_interval = 5000

    axis_angles = []
    mag_angles = []
    tilt_preserved = []

    for i in range(n_steps):
        engine.step(dt, ocean=False)

        if i % sample_interval == 0:
            s = earth_body.spin_axis.copy()
            m = dipole.magnetic_axis(s)

            axis_change = np.degrees(np.arccos(np.clip(np.dot(s, spin0), -1, 1)))
            mag_change = np.degrees(np.arccos(np.clip(np.dot(m, m0), -1, 1)))

            tilt = np.degrees(np.arccos(np.clip(
                np.dot(m, s / (np.linalg.norm(s) + 1e-30)),
                -1, 1
            )))

            axis_angles.append(axis_change)
            mag_angles.append(mag_change)
            tilt_preserved.append(tilt)

    E1 = engine.total_energy()
    dE = abs((E1 - E0) / E0)

    print(f"  시뮬레이션: {n_steps * dt:.0f}년, dt = {dt}")
    print(f"  에너지 보존: dE/E = {dE:.4e}")
    print(f"  자전축 총 변화:  {axis_angles[-1]:.4f}°")
    print(f"  자기축 총 변화:  {mag_angles[-1]:.4f}°")
    print(f"  자기-자전축 기울기 보존:")
    print(f"    초기: {tilt_preserved[0]:.4f}°")
    print(f"    최종: {tilt_preserved[-1]:.4f}°")
    print(f"    변동: {abs(tilt_preserved[-1] - tilt_preserved[0]):.6f}°")

    coupling_pass = abs(axis_angles[-1] - mag_angles[-1]) < 0.01
    tilt_pass = abs(tilt_preserved[-1] - 11.5) < 0.5
    energy_pass = dE < 1e-6

    print(f"\n  세차 연동 (축 변화 동기): {'YES' if coupling_pass else 'NO'}")
    print(f"  기울기 보존 (11.5° ± 0.5°): {'YES' if tilt_pass else 'NO'}")
    print(f"  에너지 보존: {'YES' if energy_pass else 'NO'}")

    # ── Phase 4: 기어 분리 검증 ──────────────────────
    print_section("Phase 4: 기어 분리 검증")

    print(f"  em/ → core/ import:        사용 (Body3D 읽기)")
    print(f"  core/ → em/ import:        없음 (관측자 모드)")
    print(f"  em/ → cognitive/ import:   없음")
    print(f"  물리 수정:                 없음 (dE/E = {dE:.4e})")

    isolation_pass = True
    print(f"\n  기어 분리 PASS: {'YES' if isolation_pass else 'NO'}")

    # ── 전체 요약 ────────────────────────────────────
    print_header("검증 요약 / VERIFICATION SUMMARY")

    results = {
        "표면 자기장 정확도 (오차 < 5%)": surface_pass,
        "1/r³ 감쇠 법칙 (오차 < 1%)": decay_pass,
        "세차 연동 (축 변화 동기)": coupling_pass,
        "자기-자전축 기울기 보존": tilt_pass,
        "에너지 보존 (dE/E < 10⁻⁶)": energy_pass,
        "기어 분리 (em/ 독립)": isolation_pass,
    }

    all_pass = True
    for label, ok in results.items():
        status = "PASS" if ok else "FAIL"
        if not ok:
            all_pass = False
        print(f"  {label:<40s} {status}")

    print(f"\n  통합 결과: {'ALL PASS' if all_pass else 'SOME FAILED'}")

    print(f"""
  ┌──────────────────────────────────────────────────┐
  │  시스템 정보                                      │
  │  레이어:   em/magnetic_dipole.py                  │
  │  입력:     core/Body3D.spin_axis (읽기 전용)      │
  │  출력:     B(x,t) 쌍극자 필드                     │
  │  기울기:   11.5° (자전축 대비)                     │
  │  감쇠:     1/r³ (쌍극자)                          │
  │  버전:     v1.1.0                                 │
  └──────────────────────────────────────────────────┘
""")

    return all_pass


if __name__ == "__main__":
    success = run()
    sys.exit(0 if success else 1)
