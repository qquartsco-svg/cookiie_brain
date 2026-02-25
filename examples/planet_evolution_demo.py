#!/usr/bin/env python3
"""Planet Evolution Demo — 점 객체 탄생 → 세차운동하는 행성

Phase 0: 탄생 — 태양 중력장에 점 객체 생성
Phase 1: 바다 — 우물에 물이 고여 바다 형성
Phase 2: 충돌 — 거대 충돌로 달 생성 + 자전축 기울어짐
Phase 3: 조석 — 달의 조석력으로 우물 타원 변형
Phase 4: 세차 — 기울어진 자전축이 팽이처럼 회전
Phase 5: 해류 — 자전+조석+세차가 만드는 복잡한 해류

Usage:
    python examples/planet_evolution_demo.py
"""

import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
from solar.evolution_engine import EvolutionEngine, Body3D

# ─── Constants (AU, yr, M_sun) ──────────────────────────
M_SUN = 1.0
M_EARTH = 3.003e-6
R_EARTH_AU = 4.259e-5
G4PI2 = 4 * np.pi**2


def sep(title: str):
    print(f"\n{'─' * 60}")
    print(f"  {title}")
    print(f"{'─' * 60}")


def main():
    wall_t0 = time.time()

    print("=" * 60)
    print("  PLANET EVOLUTION SIMULATOR")
    print("  점 객체 탄생  →  세차운동하는 행성")
    print("=" * 60)

    engine = EvolutionEngine(softening=1e-8)

    # ═══════════════════════════════════════════════════════
    #  Phase 0: 탄생 — Birth
    # ═══════════════════════════════════════════════════════
    sep("Phase 0: 탄생 — 태양 중력장에 점 객체 생성")

    sun = Body3D(
        name="Sun",
        mass=M_SUN,
        pos=np.zeros(3),
        vel=np.zeros(3),
        radius=0.00465,
    )
    earth = Body3D(
        name="Earth",
        mass=M_EARTH,
        pos=np.array([1.0, 0.0, 0.0]),
        vel=np.array([0.0, 2 * np.pi, 0.0]),
        radius=R_EARTH_AU,
    )
    engine.add_body(sun)
    engine.add_body(earth)

    print(f"  태양: {M_SUN} M☉ at origin")
    print(f"  지구: {M_EARTH:.3e} M☉ at 1.000 AU")
    print(f"  자전: 없음 | 기울기: 0° | 달: 없음")

    E0 = engine.total_energy()
    L0 = engine.total_angular_momentum()

    print(f"\n  Verifying orbit (2 cycles)...")
    for _ in range(2000):
        engine.step(0.001, ocean=False)

    E1 = engine.total_energy()
    dE = abs((E1 - E0) / E0)
    dL = np.linalg.norm(engine.total_angular_momentum() - L0) / np.linalg.norm(L0)
    r_now = np.linalg.norm(earth.pos)

    print(f"  궤도 반지름: {r_now:.6f} AU")
    print(f"  에너지 보존: dE/E = {dE:.2e}  {'PASS' if dE < 1e-8 else 'FAIL'}")
    print(f"  각운동량:    dL/L = {dL:.2e}  {'PASS' if dL < 1e-8 else 'FAIL'}")

    # ═══════════════════════════════════════════════════════
    #  Phase 1: 바다 형성 — Ocean
    # ═══════════════════════════════════════════════════════
    sep("Phase 1: 바다 형성 — 우물에 물이 고임")

    engine.form_ocean("Earth", n_wells=12)
    oc = engine.oceans["Earth"]

    print(f"  {oc.n_wells}개 우물이 지표면에 형성됨")
    print(f"  깊이: {np.mean(oc.depths):.2f} (균일)")
    print(f"  폭:   {np.mean(oc.widths):.2f} (균일)")
    print(f"  조석 변형: 0.000 (달 없음 → 원형 우물)")
    print()
    print(f"  >> 바다가 고였지만 아직 조석이 없습니다")

    # ═══════════════════════════════════════════════════════
    #  Phase 2: 충돌 — Giant Impact
    # ═══════════════════════════════════════════════════════
    sep("Phase 2: 충돌 — 거대 충돌 (Giant Impact)")

    print(f"  BEFORE impact:")
    print(f"    자전: {earth.spin_rate:.1f} rad/yr")
    print(f"    기울기: {np.degrees(earth.obliquity):.1f}°")
    print(f"    달: 없음")

    moon = engine.giant_impact(
        "Earth",
        obliquity_deg=23.44,
        spin_period_days=1.0,
        moon_mass_frac=0.0123,
        moon_distance_au=0.00257,
        J2=0.00108263,
        C_MR2=0.3307,
    )

    print(f"\n  AFTER impact:")
    print(f"    자전: {earth.spin_rate:.1f} rad/yr  (1 rotation/day)")
    print(f"    기울기: {np.degrees(earth.obliquity):.2f}°")
    print(
        f"    자전축: ({earth.spin_axis[0]:+.4f},"
        f" {earth.spin_axis[1]:+.4f},"
        f" {earth.spin_axis[2]:+.4f})"
    )
    print(f"    J2: {earth.J2:.8f}  |  C/(MR²): {earth.C_MR2:.4f}")
    print(f"    달: {moon.mass:.3e} M☉ at {np.linalg.norm(moon.pos - earth.pos):.5f} AU")
    print()
    print(f"  >> 점 객체가 기울어진 자전을 시작했습니다")

    # ═══════════════════════════════════════════════════════
    #  Phase 3: 조석 진화 — Tidal Evolution
    # ═══════════════════════════════════════════════════════
    sep("Phase 3: 조석 진화 — 달의 조석력으로 우물 변형")

    E_pre = engine.total_energy()
    print(f"  Running 5 orbits (Sun + Earth + Moon, dt=0.0002)...")

    moon_dists = []
    n3 = 25000
    for s in range(n3):
        engine.step(0.0002, ocean=(s % 50 == 0))
        if s % 10 == 0:
            moon_dists.append(np.linalg.norm(moon.pos - earth.pos))

    E_post = engine.total_energy()
    dE_3 = abs((E_post - E_pre) / E_pre)

    print(f"\n  Moon orbit:")
    print(f"    평균 거리: {np.mean(moon_dists):.5f} AU")
    print(f"    거리 변동: {np.std(moon_dists) / np.mean(moon_dists) * 100:.2f}%")
    print(f"    에너지 보존: dE/E = {dE_3:.2e}  {'PASS' if dE_3 < 1e-3 else 'FAIL'}")

    oc = engine.oceans["Earth"]
    print(f"\n  Ocean deformation:")
    print(f"    최대 조석 변형: {np.max(np.abs(oc.tidal_stretch)):.6f}")
    print(f"    깊은 우물 (Moon 방향): {np.max(oc.depths):.6f}")
    print(f"    얕은 우물 (수직 방향): {np.min(oc.depths):.6f}")
    print()
    print(f"  >> 우물이 타원형으로 변형되기 시작했습니다")

    # ═══════════════════════════════════════════════════════
    #  Phase 4: 세차운동 — Precession
    # ═══════════════════════════════════════════════════════
    sep("Phase 4: 세차운동 — 기울어진 자전축 회전")

    axis_0 = earth.spin_axis.copy()
    obl_0 = np.degrees(earth.obliquity)

    N_YEARS = 50
    dt_p = 0.0002
    steps_per_year = int(1.0 / dt_p)

    checkpoints = {10: None, 25: None, 50: None}

    print(f"  Running {N_YEARS} orbits (dt={dt_p})...")
    t4_start = time.time()

    for yr in range(1, N_YEARS + 1):
        for _ in range(steps_per_year):
            engine.step(dt_p, ocean=False)
        if yr in checkpoints:
            checkpoints[yr] = earth.spin_axis.copy()

    t4_elapsed = time.time() - t4_start
    print(f"  ({t4_elapsed:.1f}s elapsed)")

    axis_N = earth.spin_axis.copy()

    print(f"\n  Spin axis evolution:")
    print(
        f"    t=0 yr:  ({axis_0[0]:+.4f}, {axis_0[1]:+.4f}, {axis_0[2]:+.4f})"
        f"  obliquity={obl_0:.2f}°"
    )
    for yr, ax in sorted(checkpoints.items()):
        if ax is not None:
            o = np.degrees(np.arccos(np.clip(ax[2], -1, 1)))
            print(
                f"    t={yr} yr: ({ax[0]:+.4f}, {ax[1]:+.4f}, {ax[2]:+.4f})"
                f"  obliquity={o:.2f}°"
            )

    psi_0 = np.arctan2(axis_0[1], axis_0[0])
    psi_N = np.arctan2(axis_N[1], axis_N[0])
    delta_psi = psi_N - psi_0

    prec_rate = abs(delta_psi) / N_YEARS
    prec_period = 2 * np.pi / prec_rate if prec_rate > 0 else float("inf")
    prec_theory = 25772
    error_pct = abs(prec_period - prec_theory) / prec_theory * 100
    direction = "역행(retrograde)" if delta_psi < 0 else "순행(prograde)"

    print(f"\n  세차운동 측정:")
    print(f"    세차 각도 ({N_YEARS}yr): {np.degrees(abs(delta_psi)):.4f}°")
    print(f"    세차 방향:        {direction}")
    print(f"    세차 속도:        {prec_rate:.4e} rad/yr")
    print(f"    예상 주기:        {prec_period:,.0f} yr")
    print(f"    실제 주기:        {prec_theory:,} yr")
    print(f"    오차:             {error_pct:.1f}%  {'PASS' if error_pct < 5 else 'CHECK'}")
    print()
    print(f"  >> 세차운동이 시작되었습니다 — 자전축이 원을 그리며 회전합니다")

    # ═══════════════════════════════════════════════════════
    #  Phase 5: 해류 변화 — Ocean Dynamics
    # ═══════════════════════════════════════════════════════
    sep("Phase 5: 해류 변화 — 자전 + 조석 + 세차")

    print(f"  Running 0.5 orbit with ocean dynamics...")
    for _ in range(2500):
        engine.step(0.0002, ocean=True)

    oc = engine.oceans["Earth"]
    curr_speeds = np.linalg.norm(oc.current_vel, axis=1)

    print(f"\n  Ocean state after {engine.time:.1f} years of evolution:")
    print(f"    평균 깊이:       {np.mean(oc.depths):.4f}")
    print(f"    최대 조석 변형:  {np.max(np.abs(oc.tidal_stretch)):.6f}")
    print(f"    최대 해류 속도:  {np.max(curr_speeds):.6e} AU/yr")
    print(f"    최대 와도:       {np.max(np.abs(oc.vorticity)):.2f} rad/yr")
    print(f"    활성 해류:       {np.sum(curr_speeds > 1e-12)}/{oc.n_wells}")

    deep_i = np.argmax(oc.depths)
    shallow_i = np.argmin(oc.depths)
    print(f"\n    가장 깊은 우물: #{deep_i} (depth={oc.depths[deep_i]:.6f})")
    print(f"    가장 얕은 우물: #{shallow_i} (depth={oc.depths[shallow_i]:.6f})")
    print()
    print(f"  >> 코리올리 효과로 해류 패턴이 형성되었습니다")

    # ═══════════════════════════════════════════════════════
    #  Summary
    # ═══════════════════════════════════════════════════════
    print()
    print("=" * 60)
    print("  EVOLUTION COMPLETE — 전체 진화 요약")
    print("=" * 60)

    E_final = engine.total_energy()
    dE_total = abs((E_final - E0) / E0)

    print(
        f"""
  탄생  →  우물 속 점 객체 (자전 없음, 기울기 없음)
    |
  바다  →  우물에 물이 고여 {oc.n_wells}개 우물 형성
    |
  충돌  →  달 생성, 자전축 {np.degrees(earth.obliquity):.2f}° 기울어짐
    |
  조석  →  달의 중력으로 우물 타원 변형
    |
  세차  →  자전축이 {prec_period:,.0f}년 주기로 {direction}
    |
  해류  →  코리올리 + 조석 → 해류 패턴 형성
"""
    )

    wall_elapsed = time.time() - wall_t0
    print(f"  Simulation time: {engine.time:.1f} yr")
    print(f"  Wall-clock time: {wall_elapsed:.1f} s")
    print("=" * 60)


if __name__ == "__main__":
    main()
