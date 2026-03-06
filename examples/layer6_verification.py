"""Layer 6 — 정보 기하학 검증 (Information Geometry)

5개 물리 검증:
  1. Fisher 계량 양정치   : g_μν ≻ 0 (positive definite)
  2. 해석적 대조          : V = λ₁x + λ₂x² → g 해석해 일치
  3. 가우스 곡률 비자명    : K ≠ 0 (비평탄 기하)
  4. 측지선 거리 ≥ 유클리드 : Fisher 거리가 유클리드보다 항상 길다
  5. 대칭점 특성          : λ₁=0에서 g₁₂ = 0 (대칭 퍼텐셜)

핵심 물리:
  Fisher 정보 계량은 매개변수 공간 위의 Riemannian 기하를 정의한다.
  이것은 양자 Fubini-Study 계량의 고전 극한이다.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
for p in [str(ROOT)]:
    if p not in sys.path:
        sys.path.insert(0, p)

import numpy as np
from L4_analysis.Layer_6.geometric_phase import (
    ParameterSpace,
    FisherMetricCalculator,
    tilted_double_well,
    circular_path,
)


x_grid = np.linspace(-5.0, 5.0, 501)
T = 0.5


def make_calc():
    return FisherMetricCalculator(x_grid, tilted_double_well, T)


# ================================================================== #
#  Test 1: Fisher 계량 양정치
# ================================================================== #

def test_positive_definite():
    print("=" * 60)
    print("Test 1: Fisher 계량 양정치  g_μν ≻ 0")
    print("=" * 60)

    calc = make_calc()

    test_points = [(0.0, 0.0), (0.5, 0.0), (0.0, 1.0),
                   (-0.5, -1.0), (1.0, 1.0)]

    all_pd = True
    for lam1, lam2 in test_points:
        g = calc.metric_tensor(lam1, lam2)
        eigvals = np.linalg.eigvalsh(g)
        pd = np.all(eigvals > 0)
        det = eigvals[0] * eigvals[1]
        print(f"  λ=({lam1:5.1f}, {lam2:5.1f}): "
              f"eigenvalues=[{eigvals[0]:.4f}, {eigvals[1]:.4f}], "
              f"det={det:.4f}, pd={pd}")
        if not pd:
            all_pd = False

    print(f"  결과: {'PASS ✓' if all_pd else 'FAIL ✗'}")
    return all_pd


# ================================================================== #
#  Test 2: 해석적 대조 — 가우시안 분포에서 Fisher 계량
# ================================================================== #

def test_analytical_gaussian():
    """단순 퍼텐셜 V = ½k·x² (k=λ₂, no tilt) 에서 해석적 검증.

    ρ ∝ exp(−kx²/(2T)), Var(x) = T/k

    g₂₂ = (1/T²) Var(∂V/∂k) = (1/T²) Var(½x²)
         = (1/T²) [⟨x⁴/4⟩ − ⟨x²/2⟩²]

    ⟨x²⟩ = T/k, ⟨x⁴⟩ = 3(T/k)² (가우시안)
    g₂₂ = (1/T²)[3T²/(4k²) − T²/(4k²)] = 1/(2k²)
    """
    print("\n" + "=" * 60)
    print("Test 2: 해석적 대조 — 가우시안 분포")
    print("=" * 60)

    def harmonic_V(x, lam1, lam2):
        return 0.5 * (4.0 + lam2) * x**2 + lam1 * x

    calc = FisherMetricCalculator(x_grid, harmonic_V, T)

    k = 4.0
    g = calc.metric_tensor(0.0, 0.0)

    g11_exact = 1.0 / (T * k)
    g22_exact = 1.0 / (2.0 * k**2)

    print(f"  V = ½(4+λ₂)x² + λ₁x, T={T}, k=4")
    print(f"  g₁₁: 수치={g[0,0]:.6f}, 해석={g11_exact:.6f}, "
          f"오차={abs(g[0,0]-g11_exact):.2e}")
    print(f"  g₂₂: 수치={g[1,1]:.6f}, 해석={g22_exact:.6f}, "
          f"오차={abs(g[1,1]-g22_exact):.2e}")
    print(f"  g₁₂: 수치={g[0,1]:.6f}, 해석=0.0000, "
          f"오차={abs(g[0,1]):.2e}")

    ok = (abs(g[0, 0] - g11_exact) < 1e-3 and
          abs(g[1, 1] - g22_exact) < 1e-3 and
          abs(g[0, 1]) < 1e-3)
    print(f"  결과: {'PASS ✓' if ok else 'FAIL ✗'}")
    return ok


# ================================================================== #
#  Test 3: 가우스 곡률 비자명 — K ≠ 0
# ================================================================== #

def test_nonzero_curvature():
    print("\n" + "=" * 60)
    print("Test 3: 가우스 곡률 비자명 — K ≠ 0")
    print("=" * 60)

    calc = make_calc()

    test_points = [(0.3, 0.0), (0.5, -0.5), (0.8, 0.5)]
    K_values = []

    for lam1, lam2 in test_points:
        K = calc.gaussian_curvature(lam1, lam2)
        K_values.append(K)
        print(f"  K({lam1}, {lam2}) = {K:.6f}")

    K_max = max(abs(k) for k in K_values)
    n_nonzero = sum(1 for k in K_values if abs(k) > 1e-4)

    print(f"  |K|_max = {K_max:.6f}")
    print(f"  |K| > 1e-4: {n_nonzero}/{len(test_points)}")

    ok = K_max > 1e-3
    print(f"  결과: {'PASS ✓' if ok else 'FAIL ✗'}")
    return ok


# ================================================================== #
#  Test 4: Fisher 거리 ≠ 유클리드 — metric 비자명
# ================================================================== #

def test_fisher_nontrivial():
    """Fisher 거리가 유클리드 거리와 다름을 확인.

    L_Fisher ≥ L_Euclid는 보편 부등식이 아니라
    metric scale에 의존한다 (g_μν > δ_μν일 때만 성립).
    여기서는 Fisher metric이 비자명하게 유클리드와 다른 것만 확인.
    """
    print("\n" + "=" * 60)
    print("Test 4: Fisher 거리 ≠ 유클리드 — metric 비자명")
    print("=" * 60)

    calc = make_calc()

    paths = [
        ("직선 (0,0)→(1,0)", np.column_stack([np.linspace(0, 1, 50),
                                                np.zeros(50)])),
        ("원호 r=0.5", circular_path((0.3, 0.0), 0.5, 100)),
    ]

    all_ok = True
    for name, path in paths:
        d_fisher = calc.geodesic_distance(path)
        d_euclid = np.sum(np.sqrt(np.sum(np.diff(path, axis=0)**2, axis=1)))

        ratio = d_fisher / d_euclid if d_euclid > 0 else float('inf')
        print(f"  {name}:")
        print(f"    Fisher = {d_fisher:.4f}, Euclid = {d_euclid:.4f}, "
              f"비율 = {ratio:.4f}")

        if abs(ratio - 1.0) < 0.01:
            all_ok = False
            print(f"    ⚠ Fisher ≈ Euclid → metric이 trivial")

    ok = all_ok
    print(f"  Fisher ≠ Euclid (비자명 metric 확인)")
    print(f"  결과: {'PASS ✓' if ok else 'FAIL ✗'}")
    return ok


# ================================================================== #
#  Test 5: 대칭점에서 g₁₂ = 0
# ================================================================== #

def test_symmetry_metric():
    print("\n" + "=" * 60)
    print("Test 5: 대칭점 λ₁=0에서 g₁₂ = 0")
    print("=" * 60)

    calc = make_calc()

    g_sym = calc.metric_tensor(0.0, 0.0)
    g_asym = calc.metric_tensor(0.5, 0.0)

    print(f"  V(x;0,0) = x⁴ − 4x² (대칭)")
    print(f"  g₁₂(0,0) = {g_sym[0,1]:.6f}  (대칭 → 0 기대)")
    print(f"  g₁₂(0.5,0) = {g_asym[0,1]:.6f}  (비대칭 → ≠0)")

    ok = abs(g_sym[0, 1]) < 1e-6 and abs(g_asym[0, 1]) > 1e-4
    print(f"  |g₁₂(sym)| < 1e-6: {abs(g_sym[0,1]) < 1e-6}")
    print(f"  |g₁₂(asym)| > 1e-4: {abs(g_asym[0,1]) > 1e-4}")
    print(f"  결과: {'PASS ✓' if ok else 'FAIL ✗'}")
    return ok


# ================================================================== #
#  Main
# ================================================================== #

if __name__ == "__main__":
    print("Layer 6 — 정보 기하학 검증")
    print("=" * 60)

    results = []
    results.append(("Fisher 계량 양정치", test_positive_definite()))
    results.append(("해석적 대조 (가우시안)", test_analytical_gaussian()))
    results.append(("가우스 곡률 비자명 K≠0", test_nonzero_curvature()))
    results.append(("Fisher ≠ 유클리드 (비자명)", test_fisher_nontrivial()))
    results.append(("대칭점 g₁₂=0", test_symmetry_metric()))

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
        print("\n  ★ ALL PASS — Layer 6 물리적 정합성 확인 ★")
    else:
        print(f"\n  ✗ {len(results) - n_pass}개 실패")

    sys.exit(0 if n_pass == len(results) else 1)
