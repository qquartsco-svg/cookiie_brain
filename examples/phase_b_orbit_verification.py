"""Phase B 공전 최소 검증 — 다중 우물 순환

검증 항목:
  1. 다중 우물 구조     (V(center) < V(saddle))
  2. 장벽 높이 양수     (barrier > 0)
  3. E > V_saddle 순환  (우물 전이 ≥ 2회)
  4. 에너지 보존        (Strang splitting, rel_drift < 0.1%)
  5. E < V_saddle 갇힘  (단일 우물 내, 전이 = 0)

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
sys.path.insert(0, str(root / "Brain_Disorder_Simulation_Engine"
                        / "Unsolved_Problems_Engines" / "PotentialFieldEngine"))

from brain_core.global_state import GlobalState
from potential_field_engine import PotentialFieldEngine
from Phase_B import MultiWellPotential, GaussianWell, create_symmetric_wells


def _count_transitions(well_sequence):
    """우물 전이 횟수 (연속 동일 우물 제외)"""
    return sum(
        1 for k in range(1, len(well_sequence))
        if well_sequence[k] != well_sequence[k - 1]
    )


def _simulate(engine, state, mwp, n_steps, dim=2):
    """시뮬레이션 실행, (energies, well_visits) 반환"""
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
    omega = 0.5
    dt = 0.005
    n_steps = 20000

    # ============================================================ #
    #  다중 우물 생성
    # ============================================================ #
    mwp = create_symmetric_wells(
        centers=[np.array([-2.0, 0.0]), np.array([2.0, 0.0])],
        amplitude=2.0,
        sigma=1.0,
    )
    info = mwp.landscape_info()

    print("=" * 60)
    print("Phase B 공전 검증")
    print("=" * 60)

    # ------------------------------------------------------------ #
    #  검증 1: 다중 우물 구조
    # ------------------------------------------------------------ #
    print("\n--- 검증 1: 다중 우물 구조 ---")
    for w in info["wells"]:
        print(f"  우물 {w['index']}: center={w['center']}, "
              f"V={w['V_center']:.6f}, A={w['amplitude']}, σ={w['sigma']}")

    b_info = info["barriers"][0]
    V_well = info["wells"][0]["V_center"]
    V_saddle = b_info["V_saddle"]

    print(f"  안장점: pos={[f'{x:.4f}' for x in b_info['saddle_position']]}, "
          f"V_saddle={V_saddle:.6f}")
    structure_ok = V_well < V_saddle
    print(f"  V_well({V_well:.6f}) < V_saddle({V_saddle:.6f}) → "
          f"{'PASS' if structure_ok else 'FAIL'}")

    # ------------------------------------------------------------ #
    #  검증 2: 장벽 양수
    # ------------------------------------------------------------ #
    print("\n--- 검증 2: 장벽 높이 ---")
    barrier = b_info["barrier_height"]
    barrier_ok = barrier > 0
    print(f"  barrier_height = {barrier:.6f}")
    print(f"  결과: {'PASS' if barrier_ok else 'FAIL'}")

    # ------------------------------------------------------------ #
    #  검증 3: E > V_saddle → 순환
    # ------------------------------------------------------------ #
    print("\n--- 검증 3: E > V_saddle → 우물 전이 ---")

    x0 = np.array([-1.8, 0.0])
    V_init = mwp.potential(x0)
    K_needed = V_saddle - V_init + 0.5
    v_mag = np.sqrt(2.0 * max(K_needed, 0.01))
    v0 = np.array([v_mag * 0.7, v_mag * 0.7])
    E_init = 0.5 * np.dot(v0, v0) + V_init

    print(f"  E_init = {E_init:.6f}")
    print(f"  V_saddle = {V_saddle:.6f}")
    print(f"  E > V_saddle: {E_init > V_saddle}")

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

    well_0_count = well_visits.count(0)
    well_1_count = well_visits.count(1)
    print(f"  우물 0 체류: {well_0_count} steps")
    print(f"  우물 1 체류: {well_1_count} steps")
    print(f"  전이 횟수: {transitions}")
    orbit_ok = transitions >= 2
    print(f"  결과: {'PASS' if orbit_ok else 'FAIL'} (기준: ≥ 2회 전이)")

    # ------------------------------------------------------------ #
    #  검증 4: 에너지 보존
    # ------------------------------------------------------------ #
    print("\n--- 검증 4: 에너지 보존 ---")
    E_drift = abs(energies[-1] - energies[0])
    E_rel = E_drift / abs(energies[0]) if abs(energies[0]) > 1e-15 else E_drift
    print(f"  E_initial = {energies[0]:.12f}")
    print(f"  E_final   = {energies[-1]:.12f}")
    print(f"  E_max     = {energies.max():.12f}")
    print(f"  E_min     = {energies.min():.12f}")
    print(f"  drift     = {E_drift:.2e}")
    print(f"  rel_drift = {E_rel:.2e}")
    energy_ok = E_rel < 1e-3
    print(f"  결과: {'PASS' if energy_ok else 'FAIL'} (기준: < 0.1%)")

    # ------------------------------------------------------------ #
    #  검증 5: E < V_saddle → 갇힘
    # ------------------------------------------------------------ #
    print("\n--- 검증 5: E < V_saddle → 단일 우물 갇힘 ---")

    x0_trap = np.array([-2.0, 0.0])
    V_trap = mwp.potential(x0_trap)
    K_small = (V_saddle - V_trap) * 0.3
    v_small = np.sqrt(2.0 * max(K_small, 0.01))
    v0_trap = np.array([0.0, v_small])
    E_trap = 0.5 * np.dot(v0_trap, v0_trap) + V_trap

    print(f"  E_init = {E_trap:.6f}")
    print(f"  V_saddle = {V_saddle:.6f}")
    print(f"  E < V_saddle: {E_trap < V_saddle}")

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
        "E>V_saddle 순환": orbit_ok,
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
