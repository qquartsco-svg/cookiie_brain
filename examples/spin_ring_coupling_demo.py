#!/usr/bin/env python3
"""Spin-Ring Coupling Demo — 물리 엔진 ↔ 관성 기억 엔진 통합 검증
================================================================

EvolutionEngine(물리: 중력+토크)과 RingAttractor(인지: 관성 기억)를
SpinRingCoupling으로 연결하여, 세차운동 중 자전축 방위각을
Ring Attractor가 추적·기억하는 과정을 검증한다.

구조:
  [RingAttractor]  ← 관성 기억 (위상 보존)
       ↑ 읽기: 자전축 방위각 φ(t)
       ↓ 필드: coupling_strength로 간접 결합
  [EvolutionEngine] ← 물리 계산 (중력 + 토크)

검증 항목:
  1. Ring이 물리적 방위각을 정확히 추적하는가 (phase_error)
  2. Ring의 안정성이 유지되는가 (stability)
  3. 세차운동의 방향을 Ring이 올바르게 기억하는가
  4. 물리 정확도가 커플링에 의해 훼손되지 않는가 (에너지 보존)
"""

import sys
import os
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from solar import EvolutionEngine, Body3D, SpinRingCoupling


def main():
    print("=" * 70)
    print("  Spin-Ring Coupling Demo")
    print("  물리 엔진(세차운동) ↔ 관성 기억 엔진(Ring Attractor) 통합")
    print("=" * 70)

    # ── Phase 0: 시스템 구성 ──────────────────────────────
    print("\n[Phase 0] 시스템 구성")

    engine = EvolutionEngine(softening=1e-8)

    sun = Body3D(
        name="Sun", mass=1.0,
        pos=np.array([0.0, 0.0, 0.0]),
        vel=np.array([0.0, 0.0, 0.0]),
    )
    earth = Body3D(
        name="Earth", mass=3.003e-6,
        pos=np.array([1.0, 0.0, 0.0]),
        vel=np.array([0.0, 2 * np.pi, 0.0]),
        radius=4.26352e-5,
    )
    engine.add_body(sun)
    engine.add_body(earth)

    moon = engine.giant_impact(
        "Earth",
        obliquity_deg=23.44,
        spin_period_days=1.0,
    )

    E0 = engine.total_energy()
    print(f"  태양 + 지구 + 달 배치 완료")
    print(f"  초기 에너지: {E0:.10e}")
    print(f"  초기 자전축: {earth.spin_axis}")
    print(f"  초기 경사각: {np.degrees(earth.obliquity):.2f}°")

    az0 = np.arctan2(earth.spin_axis[1], earth.spin_axis[0])
    print(f"  초기 방위각: {np.degrees(az0):.2f}°")

    # ── Phase 1: 커플링 연결 ──────────────────────────────
    print("\n[Phase 1] 커플링 연결")
    print("  EvolutionEngine ↔ RingAttractor 필드 결합")

    coupling = SpinRingCoupling(
        engine=engine,
        target_body="Earth",
        n_neurons=64,
        coupling_strength=0.5,
    )

    print(f"  Ring 해상도: 64 뉴런")
    print(f"  결합 강도: 0.5 (관측자 모드)")
    print(f"  Ring → 물리 영향: 없음 (물리 보존)")

    # ── Phase 2: 세차운동 + Ring 추적 ─────────────────────
    print("\n[Phase 2] 세차운동 + Ring Attractor 추적 시작")
    print("-" * 70)

    dt = 0.0002
    N_STEPS = 250_000
    LOG_INTERVAL = 50_000

    print(f"  dt = {dt} yr, 총 {N_STEPS} 스텝 = {N_STEPS * dt:.1f} yr")
    print(f"  로그 간격: {LOG_INTERVAL} 스텝마다\n")

    states = coupling.run(
        n_steps=N_STEPS,
        dt=dt,
        ocean=False,
        log_interval=LOG_INTERVAL,
    )

    # ── Phase 3: 검증 결과 ────────────────────────────────
    print("\n" + "-" * 70)
    print("[Phase 3] 검증 결과\n")

    summary = coupling.summary()

    E1 = engine.total_energy()
    dE = abs((E1 - E0) / E0) if abs(E0) > 1e-30 else 0.0

    first = states[0]
    last = states[-1]
    precession_deg = np.degrees(last.spin_azimuth - first.spin_azimuth)

    if abs(precession_deg) > 1e-5:
        years_per_deg = summary["total_time_yr"] / abs(precession_deg)
        precession_period = years_per_deg * 360
    else:
        precession_period = float("inf")

    print(f"  [물리 층]")
    print(f"    시뮬레이션 시간:     {summary['total_time_yr']:.1f} yr")
    print(f"    에너지 보존:         dE/E = {dE:.2e}")
    print(f"    최종 경사각:         {last.obliquity_deg:.2f}°")
    print(f"    세차 진행량:         {precession_deg:.4f}°")
    print(f"    세차 주기 (추정):    {precession_period:,.0f} yr")
    print(f"    세차 방향:           {'역행(retrograde)' if precession_deg < 0 else '순행(prograde)'}")

    print(f"\n  [인지 층 — Ring Attractor]")
    print(f"    평균 위상 오차:      {summary['mean_phase_error_deg']:.4f}°")
    print(f"    최대 위상 오차:      {summary['max_phase_error_deg']:.4f}°")
    print(f"    평균 안정성:         {summary['mean_stability']:.4f}")
    print(f"    동기화 비율:         {summary['sync_ratio'] * 100:.1f}%")
    print(f"    Ring 추적 드리프트:  {summary['ring_tracked_drift_deg']:.4f}°")

    print(f"\n  [커플링 층]")
    print(f"    결합 강도:           {coupling.coupling_strength}")
    print(f"    물리 → Ring:         필드 입력 (간접)")
    print(f"    Ring → 물리:         없음 (관측자 모드)")

    # ── Phase 4: 관성 기억 검증 ───────────────────────────
    print(f"\n[Phase 4] 관성 기억 검증")
    print(f"  Ring Attractor가 자전축 방위각을 기억하고 있는가?")

    ring_state = coupling.ring.get_state()
    physics_az = coupling._get_azimuth()

    print(f"    물리 방위각:  {np.degrees(physics_az):.4f}°")
    print(f"    Ring 기억:    {np.degrees(ring_state.phase):.4f}°")
    print(f"    차이:         {np.degrees(abs(physics_az - ring_state.phase)):.4f}°")
    print(f"    기억 유지:    {'YES' if ring_state.sustained else 'NO'}")
    print(f"    안정성:       {ring_state.stability:.4f}")

    # ── 요약 ──────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("  요약")
    print("=" * 70)

    physics_ok = dE < 1e-10
    tracking_ok = summary["mean_phase_error_deg"] < 5.0
    stability_ok = summary["mean_stability"] > 0.3
    memory_ok = ring_state.sustained

    print(f"\n  물리 보존 (dE/E < 10⁻¹⁰):           {'PASS' if physics_ok else 'FAIL'}")
    print(f"  위상 추적 (오차 < 5°):               {'PASS' if tracking_ok else 'FAIL'}")
    print(f"  Ring 안정성 (stability > 0.3):       {'PASS' if stability_ok else 'FAIL'}")
    print(f"  관성 기억 (sustained = True):        {'PASS' if memory_ok else 'FAIL'}")

    all_pass = physics_ok and tracking_ok and stability_ok and memory_ok
    print(f"\n  통합 결과: {'ALL PASS' if all_pass else 'SOME FAILED'}")

    if all_pass:
        print("\n  물리 엔진과 관성 기억 엔진이 필드를 통해 동기화되었다.")
        print("  세차운동의 자전축 변화를 Ring Attractor가 정확히 추적·기억한다.")
        print("  물리 정확도는 커플링에 의해 훼손되지 않았다.")

    print("\n" + "=" * 70)
    print("  Layer 구조:")
    print("    [RingAttractor]   ← 관성 기억 (위상 보존)")
    print("         ↑ 필드 결합")
    print("    [EvolutionEngine] ← 물리 (중력 + 토크)")
    print("=" * 70)


if __name__ == "__main__":
    main()
