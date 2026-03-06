"""Phase B 공전 검증 — 다중 우물 순환 궤도

검증 항목:
  1. 다중 우물 구조     (V(center) < V(saddle))
  2. 장벽 높이 양수     (barrier > 0)
  3. 전이 가능성        (E > V_saddle → 장벽 통과)
  4. 순환 궤도 (공전)   (A→B→C→A 주기적 순환)
  5. 에너지 보존        (Strang splitting, rel_drift < 0.1%)
  6. E < V_saddle 갇힘  (단일 우물 내, 전이 = 0)

핵심:
  우물 2개 직선 배치 → ωJv가 순환 방향을 만들지 못함 (왕복만)
  우물 3개 삼각형 배치 → ωJv가 한쪽 방향으로 꺾어줌 → 공전

수식:
  V(x) = -Σᵢ Aᵢ exp(-||x - cᵢ||² / (2σᵢ²))
  a = -∇V(x) + ωJv
  적분: Strang splitting (Phase A에서 검증 완료)

실행:
  python CookiieBrain/examples/phase_b_orbit_verification.py
"""

import numpy as np
import sys
from pathlib import Path

root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root / "CookiieBrain"))
sys.path.insert(0, str(root / "BrainCore" / "src"))
sys.path.append(str(root / "Brain_Disorder_Simulation_Engine"
                     / "Unsolved_Problems_Engines" / "PotentialFieldEngine"))

from brain_core.global_state import GlobalState
from potential_field_engine import PotentialFieldEngine
from L1_dynamics.Phase_B import MultiWellPotential, GaussianWell, create_symmetric_wells


def _count_transitions(well_sequence):
    return sum(
        1 for k in range(1, len(well_sequence))
        if well_sequence[k] != well_sequence[k - 1]
    )


def _detect_cycles(well_sequence, n_wells):
    """순환 패턴 검출: A→B→C→A 같은 패턴이 반복되는지"""
    transition_points = []
    for k in range(1, len(well_sequence)):
        if well_sequence[k] != well_sequence[k - 1]:
            transition_points.append((k, well_sequence[k]))

    if len(transition_points) < n_wells:
        return 0, []

    visited_sequence = [tp[1] for tp in transition_points]

    cycles = 0
    cycle_patterns = []
    i = 0
    while i + n_wells <= len(visited_sequence):
        window = visited_sequence[i:i + n_wells]
        if len(set(window)) == n_wells:
            cycles += 1
            cycle_patterns.append(window)
            i += n_wells
        else:
            i += 1

    return cycles, cycle_patterns


def _simulate(engine, state, mwp, n_steps, dim=2):
    x0 = state.state_vector[:dim]
    v0 = state.state_vector[dim:]
    E0 = 0.5 * np.dot(v0, v0) + mwp.potential(x0)

    energies = [E0]
    well_visits = [mwp.nearest_well(x0)]

    current = state
    for _ in range(n_steps):
        current = engine.update(current)
        x = current.state_vector[:dim]
        v = current.state_vector[dim:]
        E = 0.5 * np.dot(v, v) + mwp.potential(x)
        energies.append(E)
        well_visits.append(mwp.nearest_well(x))

    return np.array(energies), well_visits


def run_verification():
    # ============================================================ #
    #  삼각형 배치 — 공전의 핵심
    # ============================================================ #
    #  정삼각형 꼭짓점 (반지름 2.5)
    r = 2.5
    centers = [
        np.array([r * np.cos(2 * np.pi * k / 3),
                   r * np.sin(2 * np.pi * k / 3)])
        for k in range(3)
    ]
    amplitude = 2.0
    sigma = 1.2

    mwp = create_symmetric_wells(centers=centers, amplitude=amplitude, sigma=sigma)
    info = mwp.landscape_info()

    omega = 0.3
    dt = 0.005
    n_steps = 60000

    print("=" * 60)
    print("Phase B 공전 검증 — 삼각형 3-우물 순환")
    print("=" * 60)

    # ------------------------------------------------------------ #
    #  검증 1: 다중 우물 구조
    # ------------------------------------------------------------ #
    print("\n--- 검증 1: 다중 우물 구조 ---")
    for w in info["wells"]:
        print(f"  우물 {w['index']}: center=[{w['center'][0]:.3f}, {w['center'][1]:.3f}], "
              f"V={w['V_center']:.6f}")

    V_wells = [w["V_center"] for w in info["wells"]]
    V_saddles = [b["V_saddle"] for b in info["barriers"]]
    V_deepest = min(V_wells)
    V_highest_saddle = max(V_saddles)

    structure_ok = all(vw < vs for vw in V_wells for vs in V_saddles)
    print(f"  V_deepest={V_deepest:.6f}, V_highest_saddle={V_highest_saddle:.6f}")
    print(f"  결과: {'PASS' if structure_ok else 'FAIL'}")

    # ------------------------------------------------------------ #
    #  검증 2: 장벽 양수
    # ------------------------------------------------------------ #
    print("\n--- 검증 2: 장벽 높이 ---")
    barriers = [b["barrier_height"] for b in info["barriers"]]
    for b in info["barriers"]:
        print(f"  우물 {b['wells']}: barrier={b['barrier_height']:.6f}, "
              f"V_saddle={b['V_saddle']:.6f}")
    barrier_ok = all(bh > 0 for bh in barriers)
    print(f"  결과: {'PASS' if barrier_ok else 'FAIL'}")

    # ------------------------------------------------------------ #
    #  검증 3: 전이 가능성 (E > V_saddle)
    # ------------------------------------------------------------ #
    print("\n--- 검증 3: 전이 가능성 ---")

    x0 = centers[0] * 0.8
    V_init = mwp.potential(x0)
    K_needed = V_highest_saddle - V_init + 1.5
    v_mag = np.sqrt(2.0 * max(K_needed, 0.01))
    toward_center = -centers[0] / np.linalg.norm(centers[0])
    v0 = v_mag * toward_center
    E_init = 0.5 * np.dot(v0, v0) + V_init

    print(f"  E_init = {E_init:.6f}")
    print(f"  V_highest_saddle = {V_highest_saddle:.6f}")
    print(f"  E > V_saddle: {E_init > V_highest_saddle}")

    engine = PotentialFieldEngine(
        potential_func=mwp.potential,
        field_func=mwp.field,
        omega_coriolis=omega,
        rotation_axis=(0, 1),
        dt=dt,
    )
    state = GlobalState(
        state_vector=np.concatenate([x0, v0]),
        energy=E_init,
    )

    energies, well_visits = _simulate(engine, state, mwp, n_steps)
    transitions = _count_transitions(well_visits)

    visited_wells = set(well_visits)
    all_visited = len(visited_wells) == 3

    for wid in range(3):
        count = well_visits.count(wid)
        print(f"  우물 {wid} 체류: {count} steps ({100*count/len(well_visits):.1f}%)")
    print(f"  전이 횟수: {transitions}")
    print(f"  3개 우물 모두 방문: {all_visited}")
    transition_ok = transitions >= 4 and all_visited
    print(f"  결과: {'PASS' if transition_ok else 'FAIL'}")

    # ------------------------------------------------------------ #
    #  검증 4: 순환 궤도 (공전)
    # ------------------------------------------------------------ #
    print("\n--- 검증 4: 순환 궤도 (A→B→C→A 공전) ---")

    n_cycles, patterns = _detect_cycles(well_visits, 3)
    print(f"  3-우물 순환 횟수: {n_cycles}")
    if patterns:
        for idx, p in enumerate(patterns[:5]):
            print(f"    순환 {idx+1}: {p[0]}→{p[1]}→{p[2]}")
        if len(patterns) > 5:
            print(f"    ... 외 {len(patterns)-5}개")

    direction_counts = {}
    for p in patterns:
        key = tuple(p)
        direction_counts[key] = direction_counts.get(key, 0) + 1

    if direction_counts:
        dominant = max(direction_counts, key=direction_counts.get)
        dominant_ratio = direction_counts[dominant] / max(n_cycles, 1)
        print(f"  주 순환 방향: {'→'.join(str(x) for x in dominant)} "
              f"({direction_counts[dominant]}회, {100*dominant_ratio:.0f}%)")
        orbit_ok = n_cycles >= 3 and dominant_ratio > 0.5
    else:
        dominant_ratio = 0
        orbit_ok = False

    print(f"  결과: {'PASS' if orbit_ok else 'FAIL'} "
          f"(기준: ≥3 순환, 주방향 >50%)")

    # ------------------------------------------------------------ #
    #  검증 5: 에너지 보존
    # ------------------------------------------------------------ #
    print("\n--- 검증 5: 에너지 보존 ---")
    E_drift = abs(energies[-1] - energies[0])
    E_rel = E_drift / abs(energies[0]) if abs(energies[0]) > 1e-15 else E_drift
    print(f"  E_initial = {energies[0]:.12f}")
    print(f"  E_final   = {energies[-1]:.12f}")
    print(f"  drift     = {E_drift:.2e}")
    print(f"  rel_drift = {E_rel:.2e}")
    energy_ok = E_rel < 1e-3
    print(f"  결과: {'PASS' if energy_ok else 'FAIL'} (기준: < 0.1%)")

    # ------------------------------------------------------------ #
    #  검증 6: E < V_saddle → 갇힘
    # ------------------------------------------------------------ #
    print("\n--- 검증 6: E < V_saddle → 단일 우물 갇힘 ---")

    x0_trap = centers[0].copy()
    V_trap = mwp.potential(x0_trap)
    min_saddle = min(V_saddles)
    K_small = (min_saddle - V_trap) * 0.3
    v_small = np.sqrt(2.0 * max(K_small, 0.01))
    v0_trap = np.array([0.0, v_small])
    E_trap = 0.5 * np.dot(v0_trap, v0_trap) + V_trap

    print(f"  E_init = {E_trap:.6f}")
    print(f"  V_lowest_saddle = {min_saddle:.6f}")
    print(f"  E < V_saddle: {E_trap < min_saddle}")

    engine_trap = PotentialFieldEngine(
        potential_func=mwp.potential,
        field_func=mwp.field,
        omega_coriolis=omega,
        rotation_axis=(0, 1),
        dt=dt,
    )
    state_trap = GlobalState(
        state_vector=np.concatenate([x0_trap, v0_trap]),
        energy=E_trap,
    )

    _, trap_visits = _simulate(engine_trap, state_trap, mwp, n_steps)
    trap_transitions = _count_transitions(trap_visits)

    print(f"  전이 횟수: {trap_transitions}")
    trapped_ok = trap_transitions == 0
    print(f"  결과: {'PASS' if trapped_ok else 'FAIL'} (전이 없어야 함)")

    # ============================================================ #
    #  종합
    # ============================================================ #
    print("\n" + "=" * 60)
    print("종합")
    print("=" * 60)
    results = {
        "다중 우물 구조": structure_ok,
        "장벽 양수": barrier_ok,
        "전이 가능성 (3우물 방문)": transition_ok,
        "순환 궤도 (공전)": orbit_ok,
        "에너지 보존": energy_ok,
        "E<V_saddle 갇힘": trapped_ok,
    }
    for name, ok in results.items():
        print(f"  {name}: {'PASS' if ok else 'FAIL'}")
    all_pass = all(results.values())
    print(f"\n  Phase B 공전 검증: {'ALL PASS' if all_pass else 'SOME FAILED'}")
    return all_pass


if __name__ == "__main__":
    run_verification()
