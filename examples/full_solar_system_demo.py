#!/usr/bin/env python3
"""Full Solar System N-body Demo — 8행성 + 태양 + 달
====================================================

Phase 1: 다행성 중력장 확장 검증.
NASA 실측 데이터(solar/data/)를 EvolutionEngine에 투입.
기존 엔진 코드 수정 없이 전체 태양계를 구성한다.

검증 항목:
  1) 에너지 보존 (dE/E)  — 장기 안정성
  2) 각운동량 보존 (dL/L)
  3) 지구 세차운동 — 기존 정밀도 유지 확인
  4) 궤도 안정성 — 행성이 이탈하지 않는가
  5) 목성 섭동 효과 — 지구 세차에 대한 영향

단위: AU, yr, M_sun  (G = 4π²)
"""

import sys
import os
import time
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from L0_solar import EvolutionEngine, Body3D, build_solar_system, PLANETS


def print_header(title: str):
    print(f"\n{'=' * 70}")
    print(f"  {title}")
    print(f"{'=' * 70}\n")


def print_section(title: str):
    print(f"\n  [{title}]")
    print(f"  {'-' * 50}")


def build_engine(include_planets=None, with_moon=True):
    """데이터에서 엔진 구축. 엔진 코드 변경 없음."""
    engine = EvolutionEngine()
    bodies_data = build_solar_system(
        include=include_planets,
        with_moon=with_moon,
    )

    moon_config = None
    for d in bodies_data:
        if "_moon_config" in d:
            moon_config = d["_moon_config"]
            continue
        body = Body3D(
            name=d["name"],
            mass=d["mass"],
            pos=d["pos"].copy(),
            vel=d["vel"].copy(),
            spin_axis=d["spin_axis"].copy(),
            spin_rate=d["spin_rate"],
            obliquity=d["obliquity"],
            J2=d["J2"],
            radius=d["radius"],
            C_MR2=d["C_MR2"],
        )
        engine.add_body(body)

    if moon_config:
        engine.giant_impact(
            target_name=moon_config["target"],
            obliquity_deg=moon_config["obliquity_deg"],
            spin_period_days=moon_config["spin_period_days"],
            moon_mass_frac=moon_config["moon_mass_frac"],
            moon_distance_au=moon_config["moon_distance_au"],
            J2=moon_config["J2"],
            C_MR2=moon_config["C_MR2"],
        )

    return engine


def run_simulation():
    print_header("FULL SOLAR SYSTEM N-BODY SIMULATION v1.0.0")
    print("  단위: AU, yr, M_sun  (G = 4π²)")
    print("  데이터: NASA Planetary Fact Sheet / JPL Horizons")
    print()

    # ── Phase 0: 전체 태양계 구축 ─────────────────────
    print_section("Phase 0: 전체 태양계 구축")

    engine = build_engine()
    engine.form_ocean("Earth", n_wells=12)

    print(f"  천체 수: {len(engine.bodies)}")
    print(f"  {'이름':>10s}  {'질량(M☉)':>14s}  {'거리(AU)':>10s}")
    print(f"  {'-'*10}  {'-'*14}  {'-'*10}")

    sun = engine.find("Sun")
    for b in engine.bodies:
        dist = np.linalg.norm(b.pos - sun.pos) if b.name != "Sun" else 0.0
        print(f"  {b.name:>10s}  {b.mass:>14.6e}  {dist:>10.4f}")

    # ── Phase 1: 시뮬레이션 실행 ─────────────────────
    print_section("Phase 1: N-body 시뮬레이션 실행")

    dt = 0.0002          # yr (~1.75 hours)
    t_total = 100.0      # 100년
    n_steps = int(t_total / dt)
    sample_interval = n_steps // 200

    E0 = engine.total_energy()
    L0 = engine.total_angular_momentum()
    L0_mag = np.linalg.norm(L0)

    earth = engine.find("Earth")
    spin0 = earth.spin_axis.copy()
    obl0 = np.degrees(earth.obliquity)

    print(f"  시뮬레이션 시간: {t_total} yr")
    print(f"  timestep:        {dt} yr ({dt*365.25*24:.1f} hours)")
    print(f"  총 스텝 수:      {n_steps:,}")
    print(f"  초기 에너지:     {E0:.10e}")
    print(f"  초기 |L|:        {L0_mag:.10e}")
    print(f"  지구 초기 경사각: {obl0:.4f}°")
    print()

    energy_history = []
    angular_momentum_history = []
    earth_obliquity_history = []
    earth_spin_azimuth_history = []
    orbit_distances = {b.name: [] for b in engine.bodies if b.name != "Sun"}

    t_start = time.time()
    progress_marks = set(range(10, 101, 10))

    for i in range(n_steps):
        engine.step(dt, ocean=(i % 50 == 0))

        if i % sample_interval == 0:
            E = engine.total_energy()
            L = engine.total_angular_momentum()
            energy_history.append(E)
            angular_momentum_history.append(np.linalg.norm(L))

            earth_obliquity_history.append(np.degrees(earth.obliquity))

            az = np.degrees(np.arctan2(earth.spin_axis[1], earth.spin_axis[0]))
            earth_spin_azimuth_history.append(az)

            for b in engine.bodies:
                if b.name != "Sun" and b.name in orbit_distances:
                    orbit_distances[b.name].append(
                        np.linalg.norm(b.pos - sun.pos)
                    )

        pct = int(100 * (i + 1) / n_steps)
        if pct in progress_marks:
            progress_marks.discard(pct)
            elapsed = time.time() - t_start
            print(f"    {pct:3d}%  t = {engine.time:7.1f} yr  "
                  f"elapsed = {elapsed:.1f}s", flush=True)

    wall_time = time.time() - t_start
    print(f"\n  완료: {wall_time:.1f}s ({n_steps/wall_time:.0f} steps/s)")

    # ── Phase 2: 보존 법칙 검증 ─────────────────────
    print_section("Phase 2: 보존 법칙 검증")

    E_final = engine.total_energy()
    L_final = engine.total_angular_momentum()
    L_final_mag = np.linalg.norm(L_final)

    dE = abs((E_final - E0) / E0)
    dL = abs((L_final_mag - L0_mag) / L0_mag)

    energy_arr = np.array(energy_history)
    dE_max = np.max(np.abs((energy_arr - E0) / E0))

    print(f"  에너지 보존:      dE/E = {dE:.4e}  (최대 {dE_max:.4e})")
    print(f"  각운동량 보존:    dL/L = {dL:.4e}")

    E_pass = dE < 1e-6
    L_pass = dL < 1e-6

    print(f"  에너지 PASS:      {'YES' if E_pass else 'NO — WARNING'}")
    print(f"  각운동량 PASS:    {'YES' if L_pass else 'NO — WARNING'}")

    # ── Phase 3: 지구 세차운동 검증 ─────────────────────
    print_section("Phase 3: 지구 세차운동 검증")

    spin_final = earth.spin_axis.copy()
    obl_final = np.degrees(earth.obliquity)
    obl_arr = np.array(earth_obliquity_history)
    obl_drift = abs(obl_arr[-1] - obl_arr[0])

    az_arr = np.array(earth_spin_azimuth_history)
    total_az_change = az_arr[-1] - az_arr[0]

    if abs(total_az_change) > 0.001:
        precession_period = 360.0 / abs(total_az_change) * t_total
    else:
        precession_period = float('inf')

    precession_dir = "역행(retrograde)" if total_az_change < 0 else "순행(prograde)"

    print(f"  최종 경사각:       {obl_final:.4f}°")
    print(f"  경사각 변동:       {obl_drift:.6f}°")
    print(f"  방위각 총 변화:    {total_az_change:.4f}°")
    print(f"  세차 주기 (추정):  {precession_period:,.0f} yr")
    print(f"  세차 방향:         {precession_dir}")

    P_pass = 15000 < precession_period < 40000
    D_pass = total_az_change < 0  # retrograde
    print(f"  주기 범위 PASS:    {'YES' if P_pass else 'NO'}")
    print(f"  역행 방향 PASS:    {'YES' if D_pass else 'NO'}")

    # ── Phase 4: 궤도 안정성 검증 ─────────────────────
    print_section("Phase 4: 궤도 안정성 검증")

    print(f"  {'행성':>10s}  {'평균 거리(AU)':>14s}  {'min':>8s}  "
          f"{'max':>8s}  {'NASA a':>8s}  {'|편차|':>8s}")
    print(f"  {'-'*10}  {'-'*14}  {'-'*8}  {'-'*8}  {'-'*8}  {'-'*8}")

    orbit_stable = True
    for name in ["Mercury", "Venus", "Earth", "Mars",
                  "Jupiter", "Saturn", "Uranus", "Neptune"]:
        if name not in orbit_distances or len(orbit_distances[name]) == 0:
            continue
        darr = np.array(orbit_distances[name])
        mean_d = np.mean(darr)
        min_d = np.min(darr)
        max_d = np.max(darr)
        nasa_a = PLANETS[name].semi_major_au
        dev = abs(mean_d - nasa_a) / nasa_a * 100

        if name == "Moon":
            continue

        ok = dev < 10.0
        if not ok:
            orbit_stable = False

        print(f"  {name:>10s}  {mean_d:>14.4f}  {min_d:>8.4f}  "
              f"{max_d:>8.4f}  {nasa_a:>8.4f}  {dev:>7.2f}%")

    print(f"\n  궤도 안정성 PASS:  {'YES' if orbit_stable else 'NO — WARNING'}")

    # ── Phase 5: 목성 섭동 분석 ─────────────────────
    print_section("Phase 5: 목성 섭동 효과 분석")

    jup = engine.find("Jupiter")
    jup_dist = np.linalg.norm(jup.pos - earth.pos)
    jup_grav = EvolutionEngine.G * jup.mass / jup_dist**2
    sun_grav = EvolutionEngine.G * sun.mass / np.linalg.norm(earth.pos - sun.pos)**2
    ratio = jup_grav / sun_grav

    print(f"  목성-지구 현재 거리:  {jup_dist:.4f} AU")
    print(f"  목성 중력 / 태양 중력: {ratio:.6e}")
    print(f"  목성 질량 (M☉):       {jup.mass:.6e}")
    print(f"  세차 섭동 기여:        ~{ratio*100:.4f}%")

    # ── 전체 요약 ─────────────────────────────────
    print_header("검증 요약 / VERIFICATION SUMMARY")

    results = {
        "에너지 보존 (dE/E < 10⁻⁶)": E_pass,
        "각운동량 보존 (dL/L < 10⁻⁶)": L_pass,
        "세차 주기 범위 (15k-40k yr)": P_pass,
        "세차 역행 방향": D_pass,
        "궤도 안정성 (편차 < 10%)": orbit_stable,
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
  │  천체 수:        {len(engine.bodies):>3d}                            │
  │  시뮬레이션:     {t_total:.0f} yr / dt = {dt} yr            │
  │  벽시계 시간:    {wall_time:.1f}s                           │
  │  엔진 버전:      v1.0.0                           │
  │  데이터 소스:    NASA/JPL                          │
  └──────────────────────────────────────────────────┘
""")

    return all_pass


if __name__ == "__main__":
    success = run_simulation()
    sys.exit(0 if success else 1)
