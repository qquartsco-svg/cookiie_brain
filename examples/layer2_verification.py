"""Layer 2 — 다체/장론 검증 (Many-body Verification)

5개 물리 검증:
  1. Newton 제3법칙: F_ij = -F_ji → 총 운동량 보존
  2. 에너지 보존    : γ=0, σ=0 → E = const
  3. N=1 극한      : 단일 입자 ↔ Layer 2 N=1 동일
  4. 등분배 정리    : N 입자 열평형 → ⟨½mv²⟩ = dT/2 per DOF
  5. 2체 순환      : 중력 궤도 → 각운동량 보존

극한 일관성 검증:
  - N=1 → 단일 입자 trunk과 수치적으로 동일
  - γ=0, σ=0 → 보존계
  - FDT + N 입자 → 등분배 수렴
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PFE_DIR = ROOT.parent / "Brain_Disorder_Simulation_Engine" / "Unsolved_Problems_Engines" / "PotentialFieldEngine"
BRAINCORE = ROOT.parent / "BrainCore" / "src"

for p in [str(ROOT), str(PFE_DIR), str(BRAINCORE)]:
    if p not in sys.path:
        sys.path.insert(0, p)

import numpy as np
from brain_core.global_state import GlobalState
from potential_field_engine import PotentialFieldEngine
from layers import LangevinThermo, NullGauge, GradientForce
from analysis.Layer_2.nbody import (
    NBodyState,
    InteractionForce,
    ExternalForce,
    NBodyGauge,
    gravitational_interaction,
    spring_interaction,
)


def make_state(state_vector: np.ndarray) -> GlobalState:
    return GlobalState(state_vector=state_vector.copy(), energy=0.0)


# ================================================================== #
#  Test 1: Newton 제3법칙 — 운동량 보존
# ================================================================== #

def test_momentum_conservation():
    """γ=0, σ=0, 스프링 상호작용 → 총 운동량 보존"""
    print("=" * 60)
    print("Test 1: Newton 제3법칙 — 운동량 보존")
    print("=" * 60)

    N, d = 4, 2
    nbs = NBodyState(N, d)

    rng = np.random.default_rng(42)
    X0 = rng.uniform(-3, 3, (N, d))
    V0 = rng.uniform(-1, 1, (N, d))
    sv = nbs.make_state_vector(X0, V0)

    interaction = spring_interaction(N, d, k=2.0, r0=1.5)

    engine = PotentialFieldEngine(
        force_layers=[interaction],
        gauge_layer=NullGauge(),
        thermo_layer=LangevinThermo(gamma=0.0, temperature=None, mass=1.0),
        dt=0.001,
        noise_seed=0,
    )

    state = make_state(sv)
    p0 = nbs.total_momentum(state.state_vector, mass=1.0)
    print(f"  초기 운동량: [{p0[0]:.8f}, {p0[1]:.8f}]")

    n_steps = 10000
    for _ in range(n_steps):
        state = engine.update(state)

    p_final = nbs.total_momentum(state.state_vector, mass=1.0)
    dp = np.linalg.norm(p_final - p0) / max(np.linalg.norm(p0), 1e-15)

    print(f"  최종 운동량: [{p_final[0]:.8f}, {p_final[1]:.8f}]")
    print(f"  상대 변화: {dp:.2e}")

    ok = dp < 1e-4
    print(f"  결과: {'PASS ✓' if ok else 'FAIL ✗'}")
    return ok


# ================================================================== #
#  Test 2: 에너지 보존 — 보존계
# ================================================================== #

def test_energy_conservation():
    """γ=0, σ=0, 스프링 상호작용 → 총 에너지 보존"""
    print("\n" + "=" * 60)
    print("Test 2: 에너지 보존 — 보존계")
    print("=" * 60)

    N, d = 3, 2
    nbs = NBodyState(N, d)

    rng = np.random.default_rng(99)
    X0 = rng.uniform(-2, 2, (N, d))
    V0 = rng.uniform(-0.5, 0.5, (N, d))
    sv = nbs.make_state_vector(X0, V0)

    interaction = spring_interaction(N, d, k=1.0, r0=2.0)

    engine = PotentialFieldEngine(
        force_layers=[interaction],
        gauge_layer=NullGauge(),
        thermo_layer=LangevinThermo(gamma=0.0, temperature=None, mass=1.0),
        dt=0.002,
        noise_seed=0,
    )

    state = make_state(sv)
    K0 = nbs.kinetic_energy(state.state_vector)
    V0_pot = interaction.potential(state.state_vector[:N * d])
    E0 = K0 + V0_pot
    print(f"  초기 E = {E0:.8f}  (K={K0:.8f}, V={V0_pot:.8f})")

    energies = [E0]
    n_steps = 5000
    for _ in range(n_steps):
        state = engine.update(state)
        K = nbs.kinetic_energy(state.state_vector)
        V_pot = interaction.potential(state.state_vector[:N * d])
        energies.append(K + V_pot)

    E_final = energies[-1]
    dE_rel = abs(E_final - E0) / max(abs(E0), 1e-15)
    E_max_drift = max(abs(e - E0) for e in energies) / max(abs(E0), 1e-15)

    print(f"  최종 E = {E_final:.8f}")
    print(f"  상대 에너지 변화: {dE_rel:.2e}")
    print(f"  최대 에너지 drift: {E_max_drift:.2e}")

    ok = E_max_drift < 0.01
    print(f"  결과: {'PASS ✓' if ok else 'FAIL ✗'}")
    return ok


# ================================================================== #
#  Test 3: N=1 극한 — 단일 입자와 동일
# ================================================================== #

def test_n1_limit():
    """N=1 Layer 2 경로 = 단일 입자 Classic API 경로 (수치적 동일)"""
    print("\n" + "=" * 60)
    print("Test 3: N=1 극한 — 단일 입자와 동일")
    print("=" * 60)

    d = 2

    def V_func(x):
        return 0.5 * np.dot(x, x)

    def field_func(x):
        return -x

    x0 = np.array([1.5, -0.8])
    v0 = np.array([0.3, 0.5])
    sv = np.concatenate([x0, v0])

    engine_classic = PotentialFieldEngine(
        potential_func=V_func,
        field_func=field_func,
        gamma=0.5,
        temperature=0.3,
        mass=1.0,
        noise_seed=42,
        dt=0.01,
    )

    ext_force = ExternalForce(
        n_particles=1, dim=d,
        potential_func=V_func, field_func=field_func,
    )
    engine_nbody = PotentialFieldEngine(
        force_layers=[ext_force],
        gauge_layer=NullGauge(),
        thermo_layer=LangevinThermo(gamma=0.5, temperature=0.3, mass=1.0),
        noise_seed=42,
        dt=0.01,
    )

    state_c = make_state(sv)
    state_n = make_state(sv)

    n_steps = 1000
    for _ in range(n_steps):
        state_c = engine_classic.update(state_c)
        state_n = engine_nbody.update(state_n)

    diff = np.linalg.norm(state_c.state_vector - state_n.state_vector)
    print(f"  Classic 최종: {state_c.state_vector[:2]}")
    print(f"  N-body 최종:  {state_n.state_vector[:2]}")
    print(f"  차이 (L2 norm): {diff:.2e}")

    ok = diff < 1e-10
    print(f"  결과: {'PASS ✓' if ok else 'FAIL ✗'}")
    return ok


# ================================================================== #
#  Test 4: 등분배 정리 — 열평형
# ================================================================== #

def test_equipartition():
    """N 입자 + Langevin → ⟨½mv²_α⟩ = T/2 per DOF"""
    print("\n" + "=" * 60)
    print("Test 4: 등분배 정리 — 열평형")
    print("=" * 60)

    N, d = 5, 2
    T = 0.5
    gamma = 2.0
    mass = 1.0
    nbs = NBodyState(N, d)

    rng = np.random.default_rng(77)
    X0 = rng.uniform(-2, 2, (N, d))
    V0 = rng.standard_normal((N, d)) * np.sqrt(T / mass)
    sv = nbs.make_state_vector(X0, V0)

    interaction = spring_interaction(N, d, k=1.0, r0=2.0)

    def trap(xi):
        return float(0.1 * np.dot(xi, xi))

    def trap_field(xi):
        return -0.2 * xi

    ext = ExternalForce(N, d, trap, trap_field)

    engine = PotentialFieldEngine(
        force_layers=[interaction, ext],
        gauge_layer=NullGauge(),
        thermo_layer=LangevinThermo(gamma=gamma, temperature=T, mass=mass),
        noise_seed=123,
        dt=0.005,
    )

    state = make_state(sv)

    n_equil = 10000
    for _ in range(n_equil):
        state = engine.update(state)

    n_sample = 50000
    v2_sum = np.zeros(N * d)
    for _ in range(n_sample):
        state = engine.update(state)
        v = state.state_vector[N * d:]
        v2_sum += v ** 2

    v2_mean = v2_sum / n_sample
    ke_per_dof = 0.5 * mass * v2_mean
    expected = T / 2.0

    mean_ke = np.mean(ke_per_dof)
    std_ke = np.std(ke_per_dof)

    print(f"  설정: N={N}, d={d}, T={T}, γ={gamma}")
    print(f"  ⟨½mv²⟩ per DOF = {mean_ke:.4f} ± {std_ke:.4f}")
    print(f"  이론값 T/2 = {expected:.4f}")
    print(f"  상대 오차: {abs(mean_ke - expected) / expected:.2%}")

    ok = abs(mean_ke - expected) / expected < 0.05
    print(f"  결과: {'PASS ✓' if ok else 'FAIL ✗'}")
    return ok


# ================================================================== #
#  Test 5: 2체 순환 — 각운동량 보존
# ================================================================== #

def test_angular_momentum():
    """2체 중력 궤도 → L = Σ m(x × v) 보존"""
    print("\n" + "=" * 60)
    print("Test 5: 2체 순환 — 각운동량 보존")
    print("=" * 60)

    N, d = 2, 2
    nbs = NBodyState(N, d)

    r0 = 2.0
    v_circ = np.sqrt(0.5 / r0)

    X0 = np.array([[-r0 / 2, 0.0], [r0 / 2, 0.0]])
    V0 = np.array([[0.0, -v_circ], [0.0, v_circ]])
    sv = nbs.make_state_vector(X0, V0)

    gravity = gravitational_interaction(N, d, G=1.0, softening=1e-4)

    engine = PotentialFieldEngine(
        force_layers=[gravity],
        gauge_layer=NullGauge(),
        thermo_layer=LangevinThermo(gamma=0.0, temperature=None, mass=1.0),
        dt=0.001,
        noise_seed=0,
    )

    def angular_momentum(sv_vec):
        X = nbs.positions(sv_vec)
        V = nbs.velocities(sv_vec)
        L = 0.0
        for i in range(N):
            L += X[i, 0] * V[i, 1] - X[i, 1] * V[i, 0]
        return L

    state = make_state(sv)
    L0 = angular_momentum(state.state_vector)
    print(f"  초기 각운동량: {L0:.8f}")

    L_vals = [L0]
    n_steps = 10000
    for _ in range(n_steps):
        state = engine.update(state)
        L_vals.append(angular_momentum(state.state_vector))

    L_final = L_vals[-1]
    dL_max = max(abs(L - L0) for L in L_vals) / max(abs(L0), 1e-15)

    print(f"  최종 각운동량: {L_final:.8f}")
    print(f"  최대 상대 변화: {dL_max:.2e}")

    ok = dL_max < 0.01
    print(f"  결과: {'PASS ✓' if ok else 'FAIL ✗'}")
    return ok


# ================================================================== #
#  Main
# ================================================================== #

if __name__ == "__main__":
    print("Layer 2 — 다체/장론 검증")
    print("=" * 60)

    results = []
    results.append(("Newton 제3법칙 — 운동량 보존", test_momentum_conservation()))
    results.append(("에너지 보존 — 보존계", test_energy_conservation()))
    results.append(("N=1 극한 — 단일 입자와 동일", test_n1_limit()))
    results.append(("등분배 정리 — 열평형", test_equipartition()))
    results.append(("2체 순환 — 각운동량 보존", test_angular_momentum()))

    print("\n" + "=" * 60)
    print("종합 결과")
    print("=" * 60)
    n_pass = 0
    for name, ok in results:
        status = "PASS ✓" if ok else "FAIL ✗"
        print(f"  [{status}]  {name}")
        if ok:
            n_pass += 1

    print(f"\n  총 {n_pass}/{len(results)} PASS")

    if n_pass == len(results):
        print("\n  ★ ALL PASS — Layer 2 물리적 정합성 확인 ★")
    else:
        print(f"\n  ✗ {len(results) - n_pass}개 실패")

    sys.exit(0 if n_pass == len(results) else 1)
