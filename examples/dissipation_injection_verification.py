"""에너지 주입/소산 검증

수식:
  ẍ = -∇V(x) + ωJv - γv + I(x,v,t)
  dE/dt = -γ||v||² + v·I

검증 항목:
  1. 하위 호환 (γ=0, I=None → 에너지 보존, 기존 공전 유지)
  2. 감쇠→갇힘 (γ>0 → 에너지 감소 → 단일 우물에 갇힘)
  3. 주입→전이 (E<V_saddle 상태에서 I(t) → 장벽 통과)
  4. 에너지 밸런스 (dE/dt ≈ -γ||v||² + v·I 수치 검증)

적분:
  Modified Strang splitting:
    D(dt/2) → S(dt/2) → K(dt/2) → R(dt) → K(dt/2) → S(dt/2) → D(dt/2)
  D = exp(-γdt/2), S = drift, K = kick(g+I), R = exact rotation

실행:
  python CookiieBrain/examples/dissipation_injection_verification.py
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
from L1_dynamics.Phase_B import create_symmetric_wells


def _make_triangle_system(omega=0.3, amplitude=2.0, sigma=1.2, r=2.5):
    """검증용 3-우물 삼각형 시스템 생성"""
    centers = [
        np.array([r * np.cos(2 * np.pi * k / 3),
                   r * np.sin(2 * np.pi * k / 3)])
        for k in range(3)
    ]
    mwp = create_symmetric_wells(centers=centers, amplitude=amplitude, sigma=sigma)
    info = mwp.landscape_info()
    V_saddle_max = max(b["V_saddle"] for b in info["barriers"])
    return mwp, info, V_saddle_max, centers


def _simulate(engine, state, mwp, n_steps, dim=2):
    """시뮬레이션 실행, 에너지/우물방문 기록"""
    x0 = state.state_vector[:dim]
    v0 = state.state_vector[dim:]
    E0 = 0.5 * np.dot(v0, v0) + mwp.potential(x0)

    energies = [E0]
    well_visits = [mwp.nearest_well(x0)]
    speeds = [np.linalg.norm(v0)]

    current = state
    for _ in range(n_steps):
        current = engine.update(current)
        x = current.state_vector[:dim]
        v = current.state_vector[dim:]
        E = 0.5 * np.dot(v, v) + mwp.potential(x)
        energies.append(E)
        well_visits.append(mwp.nearest_well(x))
        speeds.append(np.linalg.norm(v))

    return np.array(energies), well_visits, np.array(speeds), current


def _count_transitions(well_visits):
    return sum(1 for k in range(1, len(well_visits))
               if well_visits[k] != well_visits[k - 1])


def run_verification():
    np.random.seed(42)
    dt = 0.005

    mwp, info, V_saddle_max, centers = _make_triangle_system()

    print("=" * 60)
    print("에너지 주입/소산 검증")
    print("=" * 60)
    print(f"  V_well = {info['wells'][0]['V_center']:.6f}")
    print(f"  V_saddle_max = {V_saddle_max:.6f}")
    print(f"  barrier ≈ {info['barriers'][0]['barrier_height']:.6f}")

    # ============================================================ #
    #  검증 1: 하위 호환 (γ=0, I=None)
    # ============================================================ #
    print("\n--- 검증 1: 하위 호환 (γ=0, I=None → 에너지 보존) ---")

    x0 = centers[0] * 0.8
    V_init = mwp.potential(x0)
    K_need = V_saddle_max - V_init + 1.5
    v_mag = np.sqrt(2.0 * max(K_need, 0.01))
    toward_center = -centers[0] / np.linalg.norm(centers[0])
    v0 = v_mag * toward_center

    engine_0 = PotentialFieldEngine(
        potential_func=mwp.potential, field_func=mwp.field,
        omega_coriolis=0.3, rotation_axis=(0, 1), dt=dt,
        gamma=0.0, injection_func=None,
    )
    state_0 = GlobalState(
        state_vector=np.concatenate([x0, v0]),
        energy=0.5 * np.dot(v0, v0) + V_init,
    )

    energies_0, visits_0, _, _ = _simulate(engine_0, state_0, mwp, 20000)
    E_drift_0 = abs(energies_0[-1] - energies_0[0])
    E_rel_0 = E_drift_0 / abs(energies_0[0]) if abs(energies_0[0]) > 1e-15 else E_drift_0
    trans_0 = _count_transitions(visits_0)

    print(f"  E_rel_drift = {E_rel_0:.2e}")
    print(f"  transitions = {trans_0}")
    compat_ok = E_rel_0 < 1e-3 and trans_0 >= 4
    print(f"  결과: {'PASS' if compat_ok else 'FAIL'} (에너지 보존 + 공전 유지)")

    # ============================================================ #
    #  검증 2: 감쇠→갇힘 (γ>0 → 에너지 감소 → 갇힘)
    # ============================================================ #
    print("\n--- 검증 2: 감쇠→갇힘 (γ=0.02) ---")

    engine_damp = PotentialFieldEngine(
        potential_func=mwp.potential, field_func=mwp.field,
        omega_coriolis=0.3, rotation_axis=(0, 1), dt=dt,
        gamma=0.02, injection_func=None,
    )
    state_damp = GlobalState(
        state_vector=np.concatenate([x0, v0]),
        energy=0.5 * np.dot(v0, v0) + V_init,
    )

    energies_d, visits_d, speeds_d, final_damp = _simulate(
        engine_damp, state_damp, mwp, 40000
    )

    E_final = energies_d[-1]
    E_init = energies_d[0]
    energy_decreased = E_final < E_init
    trapped = E_final < V_saddle_max

    last_quarter = visits_d[len(visits_d) * 3 // 4:]
    trans_last = _count_transitions(last_quarter)
    speed_final = speeds_d[-100:].mean()

    print(f"  E_init = {E_init:.6f}")
    print(f"  E_final = {E_final:.6f} (Δ = {E_final - E_init:.6f})")
    print(f"  E < V_saddle: {trapped} (E={E_final:.4f}, V_s={V_saddle_max:.4f})")
    print(f"  후반 전이: {trans_last}")
    print(f"  최종 속력: {speed_final:.6f}")

    damp_ok = energy_decreased and trapped and trans_last == 0
    print(f"  결과: {'PASS' if damp_ok else 'FAIL'} (에너지↓ + 장벽 아래 + 후반 갇힘)")

    # ============================================================ #
    #  검증 3: 주입→전이 (E<V_saddle에서 시작, I(t)로 장벽 통과)
    # ============================================================ #
    print("\n--- 검증 3: 주입→전이 (E<V_saddle + pulse injection) ---")

    x0_trap = centers[0].copy()
    V_trap = mwp.potential(x0_trap)
    min_saddle = min(b["V_saddle"] for b in info["barriers"])
    K_small = (min_saddle - V_trap) * 0.3
    v_small = np.sqrt(2.0 * max(K_small, 0.01))
    v0_trap = np.array([0.0, v_small])
    E_trap_init = 0.5 * np.dot(v0_trap, v0_trap) + V_trap

    print(f"  E_init = {E_trap_init:.6f} (< V_saddle = {min_saddle:.6f})")

    pulse_start = 5.0
    pulse_end = 15.0
    pulse_strength = 0.8

    def injection_pulse(x, v, t):
        """시간 제한 펄스: pulse_start < t < pulse_end 동안 중심 방향으로 힘"""
        if pulse_start < t < pulse_end:
            direction = -x / (np.linalg.norm(x) + 1e-10)
            return pulse_strength * direction
        return np.zeros_like(x)

    engine_inj = PotentialFieldEngine(
        potential_func=mwp.potential, field_func=mwp.field,
        omega_coriolis=0.3, rotation_axis=(0, 1), dt=dt,
        gamma=0.0, injection_func=injection_pulse,
    )
    state_inj = GlobalState(
        state_vector=np.concatenate([x0_trap, v0_trap]),
        energy=E_trap_init,
    )

    energies_i, visits_i, _, _ = _simulate(engine_inj, state_inj, mwp, 30000)
    trans_i = _count_transitions(visits_i)
    visited_wells = set(visits_i)
    E_peak = max(energies_i)

    print(f"  E_peak = {E_peak:.6f} (pulse 동안)")
    print(f"  transitions = {trans_i}")
    print(f"  visited wells = {visited_wells}")

    inject_ok = trans_i >= 2 and len(visited_wells) >= 2
    print(f"  결과: {'PASS' if inject_ok else 'FAIL'} (펄스→장벽 통과→전이)")

    # ============================================================ #
    #  검증 4: 에너지 밸런스 (수치 dE/dt vs 해석적 -γ||v||²)
    # ============================================================ #
    print("\n--- 검증 4: 에너지 밸런스 (dE/dt ≈ -γ||v||²) ---")

    gamma_test = 0.05
    engine_bal = PotentialFieldEngine(
        potential_func=mwp.potential, field_func=mwp.field,
        omega_coriolis=0.3, rotation_axis=(0, 1), dt=dt,
        gamma=gamma_test, injection_func=None,
    )
    state_bal = GlobalState(
        state_vector=np.concatenate([x0, v0]),
        energy=0.5 * np.dot(v0, v0) + V_init,
    )

    n_bal = 5000
    energies_b, _, speeds_b, _ = _simulate(engine_bal, state_bal, mwp, n_bal)

    # 수치 dE/dt vs 해석적 -γ||v||²
    dE_numerical = np.diff(energies_b) / dt
    dissipation_analytical = -gamma_test * speeds_b[1:] ** 2

    # 중간 구간에서 비교 (초반 transient 제외)
    mid_start = n_bal // 4
    mid_end = n_bal * 3 // 4
    dE_mid = dE_numerical[mid_start:mid_end]
    diss_mid = dissipation_analytical[mid_start:mid_end]

    if np.std(dE_mid) > 1e-10:
        correlation = np.corrcoef(dE_mid, diss_mid)[0, 1]
    else:
        correlation = 1.0

    mean_ratio = np.mean(np.abs(dE_mid)) / (np.mean(np.abs(diss_mid)) + 1e-15)

    print(f"  correlation(dE/dt, -γ||v||²) = {correlation:.6f}")
    print(f"  mean |dE/dt| / mean |γ||v||²| = {mean_ratio:.4f}")

    balance_ok = correlation > 0.8 and 0.5 < mean_ratio < 2.0
    print(f"  결과: {'PASS' if balance_ok else 'FAIL'} (상관 >0.8, 비율 0.5~2.0)")

    # ============================================================ #
    #  종합
    # ============================================================ #
    print("\n" + "=" * 60)
    print("종합")
    print("=" * 60)
    results = {
        "하위 호환 (γ=0)": compat_ok,
        "감쇠→갇힘 (γ>0)": damp_ok,
        "주입→전이 (I pulse)": inject_ok,
        "에너지 밸런스": balance_ok,
    }
    for name, ok in results.items():
        print(f"  {name}: {'PASS' if ok else 'FAIL'}")
    all_pass = all(results.values())
    print(f"\n  에너지 주입/소산 검증: {'ALL PASS' if all_pass else 'SOME FAILED'}")
    return all_pass


if __name__ == "__main__":
    run_verification()
