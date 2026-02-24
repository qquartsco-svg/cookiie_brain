"""Layer 4 — 비평형 일 정리 검증 (Non-equilibrium Work Theorems)

5개 물리 검증:
  1. Jarzynski 등식 (이동 트랩)    : ⟨e^{-W/T}⟩ ≈ 1  (ΔF = 0)
  2. 제2법칙                       : ⟨W⟩ ≥ ΔF
  3. Jarzynski (강성 변화)          : ΔF_Jarzynski ≈ T·ln(k₂/k₁)
  4. 준정적 극한                    : 느린 프로토콜 → ⟨W⟩ → ΔF
  5. Crooks 대칭                   : 정방향/역방향 ΔF 일치

핵심 물리:
  Jarzynski 등식은 임의의 비평형 과정에서 정확하다.
  이 검증은 Langevin 동역학 위에서 수치적으로 확인한다.
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
from layers import LangevinThermo, CoriolisGauge
from Layer_4.fluctuation_theorems import (
    Protocol,
    ProtocolForce,
    WorkAccumulator,
    JarzynskiEstimator,
    CrooksAnalyzer,
    moving_trap,
    stiffness_change,
    equilibrium_sample,
)


DIM = 2
MASS = 1.0


def make_state(sv):
    return GlobalState(state_vector=sv.copy(), energy=0.0)


def run_ensemble(protocol, k_init, T, gamma, dt, n_steps, n_traj, base_seed=0):
    """프로토콜 앙상블 실행 → 일(W) 목록 반환."""
    works = []
    for i in range(n_traj):
        seed = base_seed + i
        rng = np.random.default_rng(seed)
        sv = equilibrium_sample(k_init, T, MASS, DIM, rng)

        pf = ProtocolForce(protocol)
        engine = PotentialFieldEngine(
            force_layers=[pf],
            gauge_layer=CoriolisGauge(0.0),
            thermo_layer=LangevinThermo(gamma=gamma, temperature=T, mass=MASS),
            dt=dt,
            noise_seed=seed,
        )

        wa = WorkAccumulator(protocol, dt)
        state = make_state(sv)

        for _ in range(n_steps):
            x = state.state_vector[:DIM]
            wa.step(x)
            state = engine.update(state)

        works.append(wa.W)

    return np.array(works)


# ================================================================== #
#  Test 1: Jarzynski 등식 — 이동 트랩 (ΔF = 0)
# ================================================================== #

def test_jarzynski_moving_trap():
    """이동 트랩 Jarzynski: 느린 프로토콜에서 수렴 확인.

    Jarzynski 지수 평균 ⟨e^{-W/T}⟩은 rare event에 민감하여
    빠른 프로토콜에서 수렴이 느리다 (알려진 한계).
    느린 프로토콜(τ 큼)에서 확인한다.
    """
    print("=" * 60)
    print("Test 1: Jarzynski 등식 — 이동 트랩 (ΔF = 0)")
    print("=" * 60)

    k, L, tau = 2.0, 1.0, 20.0
    T, gamma, dt = 1.0, 2.0, 0.01
    n_steps = int(tau / dt)
    n_traj = 500

    protocol = moving_trap(k, L, tau, DIM)

    print(f"  k={k}, L={L}, τ={tau}, T={T}, γ={gamma}")
    print(f"  {n_traj} trajectories, {n_steps} steps each")

    works = run_ensemble(protocol, k, T, gamma, dt, n_steps, n_traj, base_seed=100)

    J_avg = JarzynskiEstimator.jarzynski_average(works, T)
    dF = JarzynskiEstimator.free_energy(works, T)

    print(f"  ⟨W⟩ = {np.mean(works):.4f}  (ΔF=0이므로 ⟨W⟩≥0)")
    print(f"  ⟨e^{{-W/T}}⟩ = {J_avg:.4f}  (이론: 1.0)")
    print(f"  ΔF_Jarzynski = {dF:.4f}  (이론: 0.0)")

    ok = abs(dF) < 0.25
    print(f"  |ΔF| < 0.25: {ok}")
    print(f"  참고: 지수 평균은 rare event에 민감 (Jarzynski bias)")
    print(f"  결과: {'PASS ✓' if ok else 'FAIL ✗'}")
    return ok


# ================================================================== #
#  Test 2: 제2법칙 — ⟨W⟩ ≥ ΔF
# ================================================================== #

def test_second_law():
    print("\n" + "=" * 60)
    print("Test 2: 제2법칙 — ⟨W⟩ ≥ ΔF")
    print("=" * 60)

    k, L, tau = 2.0, 3.0, 3.0
    T, gamma, dt = 1.0, 2.0, 0.01
    n_steps = int(tau / dt)
    n_traj = 200

    protocol = moving_trap(k, L, tau, DIM)
    works = run_ensemble(protocol, k, T, gamma, dt, n_steps, n_traj, base_seed=200)

    W_mean = np.mean(works)
    dF = 0.0
    W_diss = JarzynskiEstimator.dissipated_work(works, dF)

    print(f"  ⟨W⟩ = {W_mean:.4f}")
    print(f"  ΔF = {dF:.4f}")
    print(f"  ⟨W_diss⟩ = ⟨W⟩ − ΔF = {W_diss:.4f}  (≥ 0 이어야)")

    ok = W_diss >= -0.05
    print(f"  결과: {'PASS ✓' if ok else 'FAIL ✗'}")
    return ok


# ================================================================== #
#  Test 3: Jarzynski — 강성 변화 (알려진 ΔF)
# ================================================================== #

def test_jarzynski_stiffness():
    print("\n" + "=" * 60)
    print("Test 3: Jarzynski — 강성 변화 (ΔF = T·ln(k₂/k₁))")
    print("=" * 60)

    k1, k2, tau = 1.0, 2.0, 10.0
    T, gamma, dt = 1.0, 2.0, 0.01
    n_steps = int(tau / dt)
    n_traj = 400

    protocol, analytical_dF = stiffness_change(k1, k2, tau, DIM)
    dF_exact = analytical_dF(T)

    print(f"  k₁={k1}, k₂={k2}, τ={tau}, T={T}")
    print(f"  ΔF (해석적) = (d/2)·T·ln(k₂/k₁) = {dF_exact:.4f}")

    works = run_ensemble(protocol, k1, T, gamma, dt, n_steps, n_traj, base_seed=300)

    dF_jarzynski = JarzynskiEstimator.free_energy(works, T)
    W_mean = np.mean(works)

    print(f"  ⟨W⟩ = {W_mean:.4f}")
    print(f"  ΔF_Jarzynski = {dF_jarzynski:.4f}")
    print(f"  |ΔF_J − ΔF_exact| = {abs(dF_jarzynski - dF_exact):.4f}")

    rel_err = abs(dF_jarzynski - dF_exact) / abs(dF_exact)
    print(f"  상대 오차: {rel_err:.1%}")

    ok = rel_err < 0.25
    print(f"  결과: {'PASS ✓' if ok else 'FAIL ✗'}")
    return ok


# ================================================================== #
#  Test 4: 준정적 극한 — ⟨W⟩ → ΔF as τ → ∞
# ================================================================== #

def test_quasistatic():
    print("\n" + "=" * 60)
    print("Test 4: 준정적 극한 — 느린 프로토콜 → ⟨W⟩ → ΔF")
    print("=" * 60)

    k, L = 2.0, 2.0
    T, gamma, dt = 1.0, 2.0, 0.01
    n_traj = 150

    taus = [2.0, 10.0, 50.0]
    W_means = []

    for tau in taus:
        n_steps = int(tau / dt)
        protocol = moving_trap(k, L, tau, DIM)
        works = run_ensemble(protocol, k, T, gamma, dt, n_steps, n_traj, base_seed=400)
        W_means.append(np.mean(works))

    for tau, wm in zip(taus, W_means):
        print(f"  τ={tau:5.1f}: ⟨W⟩ = {wm:.4f}")

    monotone = all(W_means[i] >= W_means[i + 1] - 0.05 for i in range(len(W_means) - 1))
    approaching_zero = abs(W_means[-1]) < abs(W_means[0]) or W_means[-1] < 0.3

    print(f"  단조 감소 (느릴수록 ⟨W⟩ 감소): {monotone}")
    print(f"  ΔF=0 수렴 (최느림 ⟨W⟩ < 0.3): {approaching_zero}")

    ok = monotone and approaching_zero
    print(f"  결과: {'PASS ✓' if ok else 'FAIL ✗'}")
    return ok


# ================================================================== #
#  Test 5: Crooks 대칭 — 정방향/역방향 ΔF 일치
# ================================================================== #

def test_crooks_symmetry():
    print("\n" + "=" * 60)
    print("Test 5: Crooks 대칭 — 정방향/역방향 ΔF 일치")
    print("=" * 60)

    k1, k2, tau = 1.0, 2.0, 10.0
    T, gamma, dt = 1.0, 2.0, 0.01
    n_steps = int(tau / dt)
    n_traj = 400

    protocol_f, analytical_dF = stiffness_change(k1, k2, tau, DIM)
    protocol_r, _ = stiffness_change(k2, k1, tau, DIM)
    dF_exact = analytical_dF(T)

    works_f = run_ensemble(protocol_f, k1, T, gamma, dt, n_steps, n_traj, base_seed=500)
    works_r = run_ensemble(protocol_r, k2, T, gamma, dt, n_steps, n_traj, base_seed=600)

    dF_f, dF_r = CrooksAnalyzer.verify_symmetry(works_f, works_r, T)

    print(f"  ΔF (해석적):     {dF_exact:.4f}")
    print(f"  ΔF (정방향 J):   {dF_f:.4f}")
    print(f"  ΔF (역방향 J):   {dF_r:.4f}")
    print(f"  −ΔF (역방향):    {-dF_r:.4f}")
    print(f"  |ΔF_f − (−ΔF_r)|: {abs(dF_f + dF_r):.4f}")

    ok = abs(dF_f + dF_r) < 0.40
    print(f"  결과: {'PASS ✓' if ok else 'FAIL ✗'}")
    return ok


# ================================================================== #
#  Main
# ================================================================== #

if __name__ == "__main__":
    print("Layer 4 — 비평형 일 정리 검증")
    print("=" * 60)

    results = []
    results.append(("Jarzynski 등식 — 이동 트랩 (ΔF=0)", test_jarzynski_moving_trap()))
    results.append(("제2법칙 — ⟨W⟩ ≥ ΔF", test_second_law()))
    results.append(("Jarzynski — 강성 변화 (알려진 ΔF)", test_jarzynski_stiffness()))
    results.append(("준정적 극한 — ⟨W⟩ → ΔF", test_quasistatic()))
    results.append(("Crooks 대칭 — 정방향/역방향 일치", test_crooks_symmetry()))

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
        print("\n  ★ ALL PASS — Layer 4 물리적 정합성 확인 ★")
    else:
        print(f"\n  ✗ {len(results) - n_pass}개 실패")

    sys.exit(0 if n_pass == len(results) else 1)
