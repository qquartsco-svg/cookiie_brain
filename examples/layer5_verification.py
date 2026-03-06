"""Layer 5 — 확률역학 검증 (Stochastic Mechanics)

5개 물리 검증:
  1. 정상 분포 = 볼츠만  : ρ(t→∞) ∝ exp(−V/T)
  2. 확률 보존           : ∫ρ dx = 1  (모든 t)
  3. 평형 확률류 = 0      : J_eq ≈ 0  (detailed balance)
  4. Nelson 삼투 속도     : v_osmotic ≈ D·∇ln ρ
  5. Langevin-FP 일치    : Langevin 히스토그램 ≈ FP 해

핵심 물리:
  Fokker-Planck와 Langevin은 동일한 물리의 두 관점이다.
  밀도 관점에서 정상 분포는 반드시 볼츠만으로 수렴해야 한다.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
for p in [str(ROOT)]:
    if p not in sys.path:
        sys.path.insert(0, p)

import numpy as np
from L4_analysis.Layer_5.stochastic_mechanics import (
    FokkerPlanckSolver1D,
    NelsonDecomposition,
    ProbabilityCurrent,
    double_well_potential,
    gaussian_initial,
    langevin_ensemble_histogram,
)


# ================================================================== #
#  공통 설정
# ================================================================== #

T = 1.0
GAMMA = 2.0
MASS = 1.0
D = T / (MASS * GAMMA)


def harmonic_V(x):
    return 0.5 * 2.0 * x**2


# ================================================================== #
#  Test 1: 정상 분포 = 볼츠만
# ================================================================== #

def test_stationary_boltzmann():
    print("=" * 60)
    print("Test 1: 정상 분포 = 볼츠만  ρ_eq ∝ exp(−V/T)")
    print("=" * 60)

    fp = FokkerPlanckSolver1D(
        x_min=-4.0, x_max=4.0, nx=201,
        V_func=harmonic_V, T=T, gamma=GAMMA, mass=MASS,
    )

    rho0 = gaussian_initial(fp.x, center=2.0, sigma=0.5)

    dt_fp = 0.0005
    n_steps = 40000
    rho_final = fp.evolve(rho0, dt_fp, n_steps)

    rho_boltz = fp.boltzmann()

    diff = np.abs(rho_final - rho_boltz)
    L1 = np.trapezoid(diff, fp.x)
    Linf = np.max(diff)

    print(f"  V(x) = x², T={T}, γ={GAMMA}")
    print(f"  초기: 가우시안 (center=2.0, σ=0.5)")
    print(f"  FP 진화: {n_steps} steps, dt={dt_fp}")
    print(f"  L1 오차: {L1:.6f}")
    print(f"  L∞ 오차: {Linf:.6f}")

    ok = L1 < 0.05 and Linf < 0.02
    print(f"  결과: {'PASS ✓' if ok else 'FAIL ✗'}")
    return ok


# ================================================================== #
#  Test 2: 확률 보존  ∫ρ dx = 1
# ================================================================== #

def test_probability_conservation():
    print("\n" + "=" * 60)
    print("Test 2: 확률 보존  ∫ρ dx = 1")
    print("=" * 60)

    fp = FokkerPlanckSolver1D(
        x_min=-5.0, x_max=5.0, nx=201,
        V_func=harmonic_V, T=T, gamma=GAMMA, mass=MASS,
    )

    rho = gaussian_initial(fp.x, center=1.0, sigma=0.3)
    dt_fp = 0.0005

    norms = [np.trapezoid(rho, fp.x)]
    for step in range(10000):
        rho = fp.step(rho, dt_fp)
        if (step + 1) % 2000 == 0:
            norms.append(np.trapezoid(rho, fp.x))

    max_dev = max(abs(n - 1.0) for n in norms)

    for i, n in enumerate(norms):
        print(f"  step {i * 2000:5d}: ∫ρ = {n:.10f}")

    print(f"  최대 편차: {max_dev:.2e}")

    ok = max_dev < 1e-6
    print(f"  결과: {'PASS ✓' if ok else 'FAIL ✗'}")
    return ok


# ================================================================== #
#  Test 3: 평형 확률류 = 0
# ================================================================== #

def test_equilibrium_current():
    print("\n" + "=" * 60)
    print("Test 3: 평형 확률류 J_eq ≈ 0  (detailed balance)")
    print("=" * 60)

    fp = FokkerPlanckSolver1D(
        x_min=-4.0, x_max=4.0, nx=201,
        V_func=harmonic_V, T=T, gamma=GAMMA, mass=MASS,
    )

    rho_eq = fp.boltzmann()
    J = fp.probability_current(rho_eq)
    J_max = ProbabilityCurrent.max_current(J)

    interior = J[10:-10]
    J_interior_max = np.max(np.abs(interior))

    print(f"  ρ_eq = 볼츠만 분포")
    print(f"  J_max (전체): {J_max:.2e}")
    print(f"  J_max (내부): {J_interior_max:.2e}")

    ok = J_interior_max < 5e-4
    print(f"  참고: 수치 미분 O(dx²) 오차로 J가 정확히 0이 아님")
    print(f"  결과: {'PASS ✓' if ok else 'FAIL ✗'}")
    return ok


# ================================================================== #
#  Test 4: Nelson 삼투 속도 검증
# ================================================================== #

def test_nelson_osmotic():
    print("\n" + "=" * 60)
    print("Test 4: Nelson 삼투 속도  v_osmotic = D·∇ln ρ")
    print("=" * 60)

    fp = FokkerPlanckSolver1D(
        x_min=-4.0, x_max=4.0, nx=201,
        V_func=harmonic_V, T=T, gamma=GAMMA, mass=MASS,
    )

    rho_eq = fp.boltzmann()

    v_osm = NelsonDecomposition.osmotic_velocity(rho_eq, fp.dx, D)

    k = 2.0
    v_osm_analytical = -D * k * fp.x / T

    mask = np.abs(fp.x) < 2.5
    diff = np.abs(v_osm[mask] - v_osm_analytical[mask])
    max_err = np.max(diff)
    mean_err = np.mean(diff)

    print(f"  V(x) = ½·{k}·x², D={D:.3f}")
    print(f"  해석적 v_osmotic = −Dkx/T = −{D*k/T:.3f}·x")
    print(f"  내부(|x|<2.5) 최대 오차: {max_err:.6f}")
    print(f"  내부(|x|<2.5) 평균 오차: {mean_err:.6f}")

    ok = max_err < 0.01
    print(f"  결과: {'PASS ✓' if ok else 'FAIL ✗'}")
    return ok


# ================================================================== #
#  Test 5: Langevin-FP 일치
# ================================================================== #

def test_langevin_fp_consistency():
    print("\n" + "=" * 60)
    print("Test 5: Langevin ↔ Fokker-Planck 일치")
    print("=" * 60)

    V_dw = double_well_potential(a=0.5, b=2.0)

    fp = FokkerPlanckSolver1D(
        x_min=-4.0, x_max=4.0, nx=201,
        V_func=V_dw, T=T, gamma=GAMMA, mass=MASS,
    )

    rho_fp = fp.boltzmann()

    rho_lang = langevin_ensemble_histogram(
        V_func=V_dw, T=T, gamma=GAMMA, mass=MASS,
        dt=0.005, n_steps=20000, n_particles=50000,
        x_grid=fp.x, seed=42,
    )

    mask = rho_fp > 0.01
    diff = np.abs(rho_fp[mask] - rho_lang[mask])
    L1 = np.trapezoid(np.abs(rho_fp - rho_lang), fp.x)
    Linf = np.max(diff) if np.any(mask) else 0.0

    print(f"  V(x) = 0.5x⁴ − 2x² (이중 우물)")
    print(f"  FP: 해석적 볼츠만")
    print(f"  Langevin: 50000 입자, 20000 steps")
    print(f"  L1 오차: {L1:.4f}")
    print(f"  L∞ 오차 (ρ>0.01): {Linf:.4f}")

    ok = L1 < 0.10
    print(f"  결과: {'PASS ✓' if ok else 'FAIL ✗'}")
    return ok


# ================================================================== #
#  Main
# ================================================================== #

if __name__ == "__main__":
    print("Layer 5 — 확률역학 검증")
    print("=" * 60)

    results = []
    results.append(("정상 분포 = 볼츠만", test_stationary_boltzmann()))
    results.append(("확률 보존 ∫ρ=1", test_probability_conservation()))
    results.append(("평형 확률류 J=0", test_equilibrium_current()))
    results.append(("Nelson 삼투 속도", test_nelson_osmotic()))
    results.append(("Langevin ↔ FP 일치", test_langevin_fp_consistency()))

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
        print("\n  ★ ALL PASS — Layer 5 물리적 정합성 확인 ★")
    else:
        print(f"\n  ✗ {len(results) - n_pass}개 실패")

    sys.exit(0 if n_pass == len(results) else 1)
