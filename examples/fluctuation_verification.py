"""Phase C 요동 (Fluctuation) 검증 스크립트

검증 항목:
  1. 하위 호환: σ=0이면 기존 결정론적 결과와 동일
  2. Kramers 탈출: σ>0이면 우물에 갇힌 입자가 확률적으로 탈출
  3. 통계적 비편향: 노이즈가 평균 속도를 한 방향으로 치우치게 하지 않음
  4. 감쇠+노이즈 정상 상태: γ>0, σ>0이면 에너지가 유한한 정상 상태에 도달

실행:
  python examples/fluctuation_verification.py
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

pfe_path = project_root.parent / "Brain_Disorder_Simulation_Engine" / "Unsolved_Problems_Engines" / "PotentialFieldEngine"
sys.path.append(str(pfe_path))

import numpy as np
from trunk.Phase_B.multi_well_potential import MultiWellPotential, GaussianWell, create_symmetric_wells
from potential_field_engine import PotentialFieldEngine


# ─────────────────────────────────────────────────── #
#  공통 설정
# ─────────────────────────────────────────────────── #

def _make_triangle_system():
    """3-우물 삼각형 (Phase B 검증과 동일)"""
    r = 2.5
    centers = [
        np.array([r * np.cos(2 * np.pi * k / 3),
                   r * np.sin(2 * np.pi * k / 3)])
        for k in range(3)
    ]
    return create_symmetric_wells(centers=centers, amplitude=2.0, sigma=1.2)


def _simulate(mwp, x0, v0, n_steps, omega, dt, gamma=0.0,
              noise_sigma=0.0, seed=None, injection_func=None):
    """시뮬레이션 실행 → (에너지 배열, 최종 x, 최종 v, 전이 로그)"""
    try:
        from brain_core.global_state import GlobalState
    except ImportError:
        brain_core_path = project_root.parent / "BrainCore" / "src"
        sys.path.insert(0, str(brain_core_path))
        from brain_core.global_state import GlobalState

    engine = PotentialFieldEngine(
        potential_func=mwp.potential,
        field_func=mwp.field,
        omega_coriolis=omega,
        gamma=gamma,
        injection_func=injection_func,
        noise_sigma=noise_sigma,
        noise_seed=seed,
        dt=dt,
    )

    state = GlobalState(
        state_vector=np.concatenate([x0, v0]),
        energy=0.5 * np.dot(v0, v0) + mwp.potential(x0),
    )

    energies = [state.energy]
    positions = [x0.copy()]
    wells_visited = [mwp.nearest_well(x0)]

    for _ in range(n_steps):
        state = engine.update(state)
        x_cur = state.state_vector[:2]
        energies.append(state.energy)
        positions.append(x_cur.copy())
        w = mwp.nearest_well(x_cur)
        if w != wells_visited[-1]:
            wells_visited.append(w)

    x_final = state.state_vector[:2]
    v_final = state.state_vector[2:]
    return np.array(energies), x_final, v_final, wells_visited, np.array(positions)


# ─────────────────────────────────────────────────── #
#  검증 1: 하위 호환 (σ=0 → 결정론적)
# ─────────────────────────────────────────────────── #

def test_backward_compatibility():
    """σ=0이면 시드와 무관하게 동일한 결과"""
    mwp = _make_triangle_system()
    x0 = np.array([2.0, 1.0])
    v0 = np.array([0.5, -0.3])
    n_steps = 5000
    omega = 0.3
    dt = 0.005

    E1, xf1, vf1, _, _ = _simulate(mwp, x0, v0, n_steps, omega, dt,
                                     noise_sigma=0.0, seed=42)
    E2, xf2, vf2, _, _ = _simulate(mwp, x0, v0, n_steps, omega, dt,
                                     noise_sigma=0.0, seed=99)

    pos_match = np.allclose(xf1, xf2, atol=1e-12)
    vel_match = np.allclose(vf1, vf2, atol=1e-12)
    e_drift = abs(E1[-1] - E1[0]) / abs(E1[0]) if abs(E1[0]) > 1e-10 else abs(E1[-1] - E1[0])

    ok = pos_match and vel_match and e_drift < 1e-4
    print(f"[1] 하위 호환 (σ=0 결정론): {'PASS' if ok else 'FAIL'}")
    print(f"    위치 일치: {pos_match}, 속도 일치: {vel_match}, E drift: {e_drift:.2e}")
    return ok


# ─────────────────────────────────────────────────── #
#  검증 2: Kramers 탈출 (노이즈로 장벽 넘기)
# ─────────────────────────────────────────────────── #

def test_kramers_escape():
    """갇힌 상태(E < V_saddle) + 노이즈 → 확률적 탈출"""
    mwp = _make_triangle_system()
    center0 = mwp.wells[0].center
    V_saddle = mwp.min_energy_for_orbit(0, 1)

    x0 = center0 + np.array([0.05, 0.0])
    v0 = np.array([0.1, 0.05])
    E0 = 0.5 * np.dot(v0, v0) + mwp.potential(x0)
    assert E0 < V_saddle, f"초기 E={E0:.4f} > V_saddle={V_saddle:.4f}"

    n_runs = 10
    escape_count = 0
    for run in range(n_runs):
        _, _, _, wells, _ = _simulate(
            mwp, x0, v0, n_steps=80000, omega=0.3, dt=0.005,
            gamma=0.01, noise_sigma=0.25, seed=run * 7 + 1,
        )
        unique_wells = set(wells)
        if len(unique_wells) >= 2:
            escape_count += 1

    escape_rate = escape_count / n_runs
    ok = escape_rate > 0.3
    print(f"[2] Kramers 탈출 (σ=0.25, γ=0.01): {'PASS' if ok else 'FAIL'}")
    print(f"    탈출 횟수: {escape_count}/{n_runs} ({escape_rate*100:.0f}%)")
    return ok


# ─────────────────────────────────────────────────── #
#  검증 3: 통계적 비편향 (노이즈 평균 drift = 0)
# ─────────────────────────────────────────────────── #

def test_unbiased_noise():
    """자유 입자(V=0) + 노이즈 → 평균 속도 ≈ 0"""
    zero_potential = lambda x: 0.0
    zero_field = lambda x: np.zeros_like(x)

    n_runs = 200
    final_velocities = []
    for run in range(n_runs):
        engine = PotentialFieldEngine(
            potential_func=zero_potential,
            field_func=zero_field,
            omega_coriolis=0.0,
            gamma=0.0,
            noise_sigma=0.5,
            noise_seed=run,
            dt=0.01,
        )

        try:
            from brain_core.global_state import GlobalState
        except ImportError:
            brain_core_path = project_root.parent / "BrainCore" / "src"
            sys.path.insert(0, str(brain_core_path))
            from brain_core.global_state import GlobalState

        state = GlobalState(
            state_vector=np.array([0.0, 0.0, 0.0, 0.0]),
            energy=0.0,
        )
        for _ in range(500):
            state = engine.update(state)
        final_velocities.append(state.state_vector[2:].copy())

    mean_v = np.mean(final_velocities, axis=0)
    std_v = np.std(final_velocities, axis=0)
    bias = np.linalg.norm(mean_v) / (np.mean(std_v) + 1e-10)

    ok = bias < 0.3
    print(f"[3] 통계적 비편향: {'PASS' if ok else 'FAIL'}")
    print(f"    mean(v): [{mean_v[0]:.4f}, {mean_v[1]:.4f}], "
          f"std(v): [{std_v[0]:.4f}, {std_v[1]:.4f}], bias ratio: {bias:.4f}")
    return ok


# ─────────────────────────────────────────────────── #
#  검증 4: 감쇠+노이즈 정상 상태 (에너지 수렴)
# ─────────────────────────────────────────────────── #

def test_steady_state():
    """γ>0, σ>0 → 에너지가 유한한 정상 상태에 도달 (폭발하지 않음)"""
    mwp = _make_triangle_system()
    center0 = mwp.wells[0].center

    x0 = center0 + np.array([0.1, 0.0])
    v0 = np.array([0.5, 0.3])
    n_steps = 60000

    energies, _, _, _, _ = _simulate(
        mwp, x0, v0, n_steps=n_steps, omega=0.3, dt=0.005,
        gamma=0.05, noise_sigma=0.15, seed=42,
    )

    E_first_quarter = np.mean(energies[:n_steps // 4])
    E_last_quarter = np.mean(energies[3 * n_steps // 4:])
    E_std_last = np.std(energies[3 * n_steps // 4:])

    not_divergent = abs(E_last_quarter) < 100.0
    fluctuating = E_std_last > 0.001
    bounded = E_std_last < 10.0

    ok = not_divergent and fluctuating and bounded
    print(f"[4] 감쇠+노이즈 정상 상태: {'PASS' if ok else 'FAIL'}")
    print(f"    E mean (1st quarter): {E_first_quarter:.4f}")
    print(f"    E mean (last quarter): {E_last_quarter:.4f}")
    print(f"    E std (last quarter): {E_std_last:.4f}")
    print(f"    not divergent: {not_divergent}, fluctuating: {fluctuating}, bounded: {bounded}")
    return ok


# ─────────────────────────────────────────────────── #
#  실행
# ─────────────────────────────────────────────────── #

if __name__ == "__main__":
    print("=" * 60)
    print("Phase C: 요동 (Fluctuation) 검증")
    print("=" * 60)
    print()

    results = []
    results.append(test_backward_compatibility())
    print()
    results.append(test_kramers_escape())
    print()
    results.append(test_unbiased_noise())
    print()
    results.append(test_steady_state())
    print()

    print("=" * 60)
    passed = sum(results)
    total = len(results)
    if passed == total:
        print(f"ALL PASS ({passed}/{total})")
    else:
        print(f"PARTIAL: {passed}/{total} PASS")
    print("=" * 60)
