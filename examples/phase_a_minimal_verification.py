"""Phase A 최소 자전 검증 — Strang splitting + exact rotation

검증 항목:
1. v · R(x,v) = 0  (코리올리 직교성)
2. 궤도 회전       (자전 효과 존재)
3. 에너지 보존     (Strang splitting → 정확 보존)
4. 궤도 유계       (발산하지 않음)

수식:
  a = -∇V(x) + ωJv
  적분: Strang splitting = half kick + exact rotation + stream + half kick
  exact rotation: exp(ωJdt) v — |v| 정확 보존

  에너지 보존 증명 (연속):
    dE/dt = v·a + ∇V·v = v·(-∇V + ωJv) + ∇V·v = ω(v'Jv) = 0
    (J 반대칭 → v'Jv = 0 항상)

실행:
  python CookiieBrain/examples/phase_a_minimal_verification.py
"""

import numpy as np
import sys
from pathlib import Path

root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root / "CookiieBrain"))
sys.path.insert(0, str(root / "BrainCore" / "src"))
sys.path.append(str(root / "Brain_Disorder_Simulation_Engine" / "Unsolved_Problems_Engines" / "PotentialFieldEngine"))

from brain_core.global_state import GlobalState
from potential_field_engine import PotentialFieldEngine
from trunk.Phase_A import create_minimal_rotational_field


def run_verification():
    omega = 1.0
    dt = 0.005
    n_steps = 4000
    n_dim = 2

    def potential(x):
        return 0.5 * np.dot(x, x)

    def gradient_field(x):
        return -x

    R_func = create_minimal_rotational_field(omega=omega, n_dim=n_dim)

    engine = PotentialFieldEngine(
        potential_func=potential,
        field_func=gradient_field,
        omega_coriolis=omega,
        rotation_axis=(0, 1),
        dt=dt,
    )

    x0 = np.array([1.0, 0.0])
    v0 = np.array([0.0, 0.5])
    state = GlobalState(
        state_vector=np.concatenate([x0, v0]),
        energy=0.0,
    )

    # --- 검증 1: v · R(x,v) = 0 ---
    print("=" * 60)
    print("검증 1: v · R(x,v) = 0 (코리올리 직교)")
    print("=" * 60)
    test_cases = [
        (np.array([1.0, 0.0]), np.array([0.0, 1.0])),
        (np.array([0.3, -0.7]), np.array([1.2, 0.4])),
        (np.array([-2.0, 1.5]), np.array([-0.5, -0.8])),
        (np.array([0.0, 0.0]), np.array([3.0, -1.0])),
    ]
    all_ortho = True
    for x_test, v_test in test_cases:
        Rv = R_func(x_test, v_test)
        dot = np.dot(v_test, Rv)
        ok = abs(dot) < 1e-12
        if not ok:
            all_ortho = False
        print(f"  v={v_test}  R={Rv}  v·R={dot:.2e}  {'OK' if ok else 'FAIL'}")
    print(f"  결과: {'PASS' if all_ortho else 'FAIL'}\n")

    # --- 시뮬레이션 ---
    energies = []
    positions = []
    E0 = 0.5 * np.dot(v0, v0) + potential(x0)
    energies.append(E0)
    positions.append(x0.copy())

    current_state = state
    for _ in range(n_steps):
        current_state = engine.update(current_state)
        x = current_state.state_vector[:n_dim]
        v = current_state.state_vector[n_dim:]
        E = 0.5 * np.dot(v, v) + potential(x)
        energies.append(E)
        positions.append(x.copy())

    energies = np.array(energies)
    positions = np.array(positions)

    # --- 검증 2: 궤도 회전 ---
    print("=" * 60)
    print("검증 2: 궤도 회전 (자전 효과)")
    print("=" * 60)
    angles = np.arctan2(positions[:, 1], positions[:, 0])
    total_angle = np.sum(np.diff(np.unwrap(angles)))
    n_rotations = total_angle / (2 * np.pi)
    print(f"  총 회전: {np.degrees(total_angle):.1f}° ({n_rotations:.2f} 바퀴)")
    rotation_exists = abs(n_rotations) > 0.5
    print(f"  결과: {'PASS' if rotation_exists else 'FAIL'}\n")

    # --- 검증 3: 에너지 보존 ---
    print("=" * 60)
    print("검증 3: 에너지 보존")
    print("=" * 60)
    E_drift = abs(energies[-1] - energies[0])
    E_rel = E_drift / abs(energies[0]) if abs(energies[0]) > 1e-15 else E_drift
    print(f"  E_initial = {energies[0]:.12f}")
    print(f"  E_final   = {energies[-1]:.12f}")
    print(f"  E_max     = {energies.max():.12f}")
    print(f"  E_min     = {energies.min():.12f}")
    print(f"  drift     = {E_drift:.2e}")
    print(f"  rel_drift = {E_rel:.2e}")
    energy_ok = E_rel < 1e-4  # 0.01% 이내
    print(f"  결과: {'PASS' if energy_ok else 'FAIL'} (기준: < 0.01%)\n")

    # --- 검증 4: 궤도 유계 ---
    print("=" * 60)
    print("검증 4: 궤도 유계")
    print("=" * 60)
    r_all = np.linalg.norm(positions, axis=1)
    print(f"  궤도 반지름: min={r_all.min():.6f}  max={r_all.max():.6f}")
    orbit_bounded = r_all.max() < 3.0
    print(f"  결과: {'PASS' if orbit_bounded else 'FAIL'}\n")

    # --- 종합 ---
    print("=" * 60)
    print("종합")
    print("=" * 60)
    results = {
        "v·R=0 (직교)": all_ortho,
        "궤도 회전": rotation_exists,
        "에너지 보존": energy_ok,
        "궤도 유계": orbit_bounded,
    }
    for name, ok in results.items():
        print(f"  {name}: {'PASS' if ok else 'FAIL'}")
    all_pass = all(results.values())
    print(f"\n  Phase A 자전 검증: {'ALL PASS' if all_pass else 'SOME FAILED'}")
    return all_pass


if __name__ == "__main__":
    run_verification()
