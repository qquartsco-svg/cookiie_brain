"""Layer 3 — 게이지/기하학 검증 (Gauge / Geometry Verification)

5개 물리 검증:
  1. 에너지 보존    : F·v = 0 → B-field 하에서도 E = const
  2. 사이클로트론   : 균일 B, 자유 입자 → 원 궤도 (ω_c = B/m)
  3. B=0 극한      : B-field 없으면 궤적이 자유 입자와 동일
  4. E×B drift     : 선형 퍼텐셜 + 균일 B → gradient에 수직 표류
  5. Berry 위상    : 닫힌 원형 경로의 선속 = 해석적 면적분과 일치

극한 일관성:
  - B(x) = const → CoriolisGauge와 동일
  - B(x) = 0 → 자유 입자
  - F·v = 0 → 에너지 보존 (구조적)
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
from layers import LangevinThermo, NullGauge, CoriolisGauge, GradientForce
from Layer_3.gauge import (
    MagneticForce,
    GeometryAnalyzer,
    uniform_field,
    gaussian_field,
)


def make_state(sv):
    return GlobalState(state_vector=sv.copy(), energy=0.0)


# ================================================================== #
#  Test 1: 에너지 보존 — F·v = 0 구조적 보장
# ================================================================== #

def test_energy_conservation():
    """조화 퍼텐셜 + 위치 의존 B-field, γ=0, σ=0 → E = const

    CoriolisGauge(0.0)을 넣어 Strang splitting을 강제한다.
    MagneticForce는 v-의존 힘이라 Euler에서는 에너지 drift가 심함.
    Strang O-S-K-R-K-S-O 에서는 bounded error.
    """
    print("=" * 60)
    print("Test 1: 에너지 보존 — B-field 하에서 (Strang)")
    print("=" * 60)

    def V(x): return 0.5 * np.dot(x, x)
    def g(x): return -x

    B_func = gaussian_field(B0=2.0, center=np.array([0.0, 0.0]), sigma=2.0)
    magnetic = MagneticForce(B_func=B_func, dim=2)
    gradient = GradientForce(V, g)

    engine = PotentialFieldEngine(
        force_layers=[gradient, magnetic],
        gauge_layer=CoriolisGauge(0.0),
        thermo_layer=LangevinThermo(gamma=0.0, temperature=None, mass=1.0),
        dt=0.002,
        noise_seed=0,
    )

    sv = np.array([1.5, 0.0, 0.0, 1.0])
    state = make_state(sv)

    state = engine.update(state)
    E0 = state.energy

    energies = [E0]
    n_steps = 5000
    for _ in range(n_steps):
        state = engine.update(state)
        energies.append(state.energy)

    E_final = energies[-1]
    dE_max = max(abs(e - E0) for e in energies) / max(abs(E0), 1e-15)

    print(f"  초기 E = {E0:.8f}")
    print(f"  최종 E = {E_final:.8f}")
    print(f"  최대 상대 drift: {dE_max:.2e}")
    print(f"  참고: v-의존 힘의 Strang error는 bounded O(dt²)")

    ok = dE_max < 0.05
    print(f"  결과: {'PASS ✓' if ok else 'FAIL ✗'}")
    return ok


# ================================================================== #
#  Test 2: 사이클로트론 운동 — 균일 B → 원 궤도
# ================================================================== #

def test_cyclotron():
    """균일 B, 퍼텐셜 없음 → 원형 궤도. 주기 T = 2πm/B."""
    print("\n" + "=" * 60)
    print("Test 2: 사이클로트론 운동 — 균일 B → 원 궤도")
    print("=" * 60)

    B0 = 1.0
    mass = 1.0
    v0 = 1.0

    omega_c = GeometryAnalyzer.cyclotron_frequency(B0, mass)
    r_c = GeometryAnalyzer.cyclotron_radius(v0, B0, mass)
    T_c = 2.0 * np.pi / omega_c

    print(f"  이론: ω_c = {omega_c:.4f}, r_c = {r_c:.4f}, T_c = {T_c:.4f}")

    magnetic = MagneticForce(B_func=uniform_field(B0), dim=2)

    dt = 0.005
    engine = PotentialFieldEngine(
        force_layers=[magnetic],
        gauge_layer=CoriolisGauge(0.0),
        thermo_layer=LangevinThermo(gamma=0.0, temperature=None, mass=mass),
        dt=dt,
        noise_seed=0,
    )

    sv = np.array([r_c, 0.0, 0.0, v0])
    state = make_state(sv)
    state = engine.update(state)

    positions = []
    n_steps = int(2 * T_c / dt)
    for _ in range(n_steps):
        state = engine.update(state)
        positions.append(state.state_vector[:2].copy())

    positions = np.array(positions)
    center = np.mean(positions, axis=0)
    radii = np.sqrt(np.sum((positions - center) ** 2, axis=1))
    r_mean = np.mean(radii)
    r_std = np.std(radii)
    r_rel_std = r_std / r_mean

    print(f"  궤도 반경: {r_mean:.4f} ± {r_std:.4f}")
    print(f"  이론 반경: {r_c:.4f}")
    print(f"  상대 편차: {abs(r_mean - r_c) / r_c:.2e}")
    print(f"  원형도 (r_std/r_mean): {r_rel_std:.2e}")

    ok = r_rel_std < 0.05 and abs(r_mean - r_c) / r_c < 0.1
    print(f"  결과: {'PASS ✓' if ok else 'FAIL ✗'}")
    return ok


# ================================================================== #
#  Test 3: B=0 극한 — 자유 입자와 동일
# ================================================================== #

def test_b_zero_limit():
    """B(x)=0이면 MagneticForce 없는 것과 동일한 궤적"""
    print("\n" + "=" * 60)
    print("Test 3: B=0 극한 — 자유 입자와 동일")
    print("=" * 60)

    def V(x): return 0.5 * np.dot(x, x)
    def g(x): return -x

    magnetic_zero = MagneticForce(B_func=uniform_field(0.0), dim=2)

    engine_with_B = PotentialFieldEngine(
        force_layers=[GradientForce(V, g), magnetic_zero],
        gauge_layer=NullGauge(),
        thermo_layer=LangevinThermo(gamma=0.5, temperature=0.3, mass=1.0),
        noise_seed=42, dt=0.01,
    )
    engine_no_B = PotentialFieldEngine(
        force_layers=[GradientForce(V, g)],
        gauge_layer=NullGauge(),
        thermo_layer=LangevinThermo(gamma=0.5, temperature=0.3, mass=1.0),
        noise_seed=42, dt=0.01,
    )

    sv = np.array([1.0, -0.5, 0.2, 0.3])
    state_B = make_state(sv)
    state_0 = make_state(sv)

    for _ in range(1000):
        state_B = engine_with_B.update(state_B)
        state_0 = engine_no_B.update(state_0)

    diff = np.linalg.norm(state_B.state_vector - state_0.state_vector)
    print(f"  B=0 궤적 차이: {diff:.2e}")

    ok = diff < 1e-10
    print(f"  결과: {'PASS ✓' if ok else 'FAIL ✗'}")
    return ok


# ================================================================== #
#  Test 4: E×B drift — 수직 표류
# ================================================================== #

def test_exb_drift():
    """선형 퍼텐셜(일정 기울기) + 균일 B → gradient에 수직 drift (collisionless)

    V(x) = a·x₁  →  ∇V = (a, 0), 힘 F = (-a, 0)
    MagneticForce 규약: F_mag = B·(-v_y, v_x)

    정상 상태 drift:
      0 = -a - B·v_y  →  v_y = -a/B
      0 = B·v_x       →  v_x = 0

    γ=0, σ=0 (collisionless) 해석해.
    정수 사이클로트론 주기 동안 평균을 내면 진동 부분이 상쇄된다.
    """
    print("\n" + "=" * 60)
    print("Test 4: E×B drift — 수직 표류 (collisionless)")
    print("=" * 60)

    a = 0.5
    B0 = 10.0
    mass = 1.0

    v_drift_theory = np.array([0.0, -a / B0])
    omega_c = B0 / mass
    T_c = 2.0 * np.pi / omega_c

    print(f"  이론 drift: ({v_drift_theory[0]:.4f}, {v_drift_theory[1]:.4f})")
    print(f"  사이클로트론: ω_c={omega_c:.2f}, T_c={T_c:.4f}")

    def V(x): return a * x[0]
    def g(x): return np.array([-a, 0.0])

    magnetic = MagneticForce(B_func=uniform_field(B0), dim=2)

    dt = 0.001
    engine = PotentialFieldEngine(
        force_layers=[GradientForce(V, g), magnetic],
        gauge_layer=CoriolisGauge(0.0),
        thermo_layer=LangevinThermo(gamma=0.0, temperature=None, mass=mass),
        dt=dt,
        noise_seed=0,
    )

    sv = np.array([0.0, 0.0, 0.0, 0.0])
    state = make_state(sv)
    x_init = state.state_vector[:2].copy()

    n_periods = 40
    n_steps = int(n_periods * T_c / dt)
    t_total = n_steps * dt

    for _ in range(n_steps):
        state = engine.update(state)

    x_final = state.state_vector[:2]
    v_drift_measured = (x_final - x_init) / t_total

    print(f"  실측 drift: ({v_drift_measured[0]:.6f}, {v_drift_measured[1]:.6f})")

    err_y = abs(v_drift_measured[1] - v_drift_theory[1])
    drift_rel = err_y / abs(v_drift_theory[1])

    print(f"  v_y 상대 오차: {drift_rel:.2%}")
    print(f"  |v_x| (0이어야): {abs(v_drift_measured[0]):.2e}")

    ok = drift_rel < 0.15 and abs(v_drift_measured[0]) < 0.01
    print(f"  결과: {'PASS ✓' if ok else 'FAIL ✗'}")
    return ok


# ================================================================== #
#  Test 5: Berry 위상 — 면적분 정합
# ================================================================== #

def test_berry_phase():
    """가우시안 B-field의 원형 경로 선속 ≈ 수치 면적분"""
    print("\n" + "=" * 60)
    print("Test 5: Berry 위상 — 면적분 정합")
    print("=" * 60)

    B0 = 1.0
    sigma = 2.0
    center = np.array([0.0, 0.0])
    B_func = gaussian_field(B0=B0, center=center, sigma=sigma)

    radius = 3.0
    n_path = 200

    theta = np.linspace(0, 2 * np.pi, n_path, endpoint=False)
    path = np.column_stack([radius * np.cos(theta), radius * np.sin(theta)])

    flux_berry = GeometryAnalyzer.berry_phase_loop(B_func, path)
    flux_area = GeometryAnalyzer.magnetic_flux(B_func, center, radius, n_points=500)

    flux_exact = B0 * 2 * np.pi * sigma ** 2 * (1 - np.exp(-radius ** 2 / (2 * sigma ** 2)))

    print(f"  Berry 위상 (경로):  {flux_berry:.6f}")
    print(f"  면적분 (수치):      {flux_area:.6f}")
    print(f"  해석적:            {flux_exact:.6f}")

    err_berry = abs(flux_berry - flux_exact) / abs(flux_exact)
    err_area = abs(flux_area - flux_exact) / abs(flux_exact)

    print(f"  Berry 상대 오차: {err_berry:.2e}")
    print(f"  면적분 상대 오차: {err_area:.2e}")

    ok = err_berry < 0.05 and err_area < 0.05
    print(f"  결과: {'PASS ✓' if ok else 'FAIL ✗'}")
    return ok


# ================================================================== #
#  Main
# ================================================================== #

if __name__ == "__main__":
    print("Layer 3 — 게이지/기하학 검증")
    print("=" * 60)

    results = []
    results.append(("에너지 보존 — B-field 하에서", test_energy_conservation()))
    results.append(("사이클로트론 운동 — 원 궤도", test_cyclotron()))
    results.append(("B=0 극한 — 자유 입자와 동일", test_b_zero_limit()))
    results.append(("E×B drift — 수직 표류", test_exb_drift()))
    results.append(("Berry 위상 — 면적분 정합", test_berry_phase()))

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
        print("\n  ★ ALL PASS — Layer 3 물리적 정합성 확인 ★")
    else:
        print(f"\n  ✗ {len(results) - n_pass}개 실패")

    sys.exit(0 if n_pass == len(results) else 1)
