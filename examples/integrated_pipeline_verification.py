"""통합 파이프라인 검증: trunk(Phase A+B+C) → analysis(Layer 1~6)

PotentialFieldEngine으로 궤적을 생성하고,
BrainAnalyzer가 Layer 1~6 분석을 자동으로 수행하는
end-to-end 통합 흐름을 검증한다.

검증 항목:
  1. 궤적 생성 (PFE + Phase A 회전 + Phase B 다중 우물 + Phase C FDT 노이즈)
  2. Layer 1: 전이 분석, 엔트로피 생산
  3. Layer 5: 확률 밀도 ↔ 볼츠만 일치
  4. Layer 6: Fisher 계량, 곡률
  5. 통합 리포트 출력

실행:
  python examples/integrated_pipeline_verification.py
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

pfe_path = (
    project_root.parent
    / "Brain_Disorder_Simulation_Engine"
    / "Unsolved_Problems_Engines"
    / "PotentialFieldEngine"
)
sys.path.append(str(pfe_path))

import numpy as np

from potential_field_engine import PotentialFieldEngine

try:
    from brain_core.global_state import GlobalState
except ImportError:
    brain_core_path = project_root.parent / "BrainCore" / "src"
    sys.path.insert(0, str(brain_core_path))
    from brain_core.global_state import GlobalState

from trunk.Phase_B.multi_well_potential import MultiWellPotential, GaussianWell
from brain_analyzer import BrainAnalyzer


def build_double_well_1d():
    """1D 이중 우물 퍼텐셜 생성 (Phase B)."""
    wells = [
        GaussianWell(center=np.array([-1.5]), amplitude=3.0, sigma=1.0),
        GaussianWell(center=np.array([1.5]), amplitude=3.0, sigma=1.0),
    ]
    return MultiWellPotential(wells=wells)


def run_pfe_simulation(mwp, n_steps, gamma, temperature, mass, omega, dt, seed=42):
    """PFE로 궤적 생성: Phase A(회전) + Phase B(우물) + Phase C(FDT 노이즈)."""
    dim = mwp.dim

    pfe = PotentialFieldEngine(
        potential_func=mwp.potential,
        field_func=mwp.field,
        omega_coriolis=omega,
        gamma=gamma,
        temperature=temperature,
        mass=mass,
        noise_seed=seed,
        dt=dt,
    )

    rng = np.random.default_rng(seed)
    sigma_x = np.sqrt(temperature / 4.0)
    sigma_v = np.sqrt(temperature / mass)
    x0 = rng.normal(-1.5, sigma_x, dim)
    v0 = rng.normal(0.0, sigma_v, dim)

    state = GlobalState(state_vector=np.concatenate([x0, v0]))

    positions = np.zeros((n_steps, dim))
    velocities = np.zeros((n_steps, dim))
    energies = np.zeros(n_steps)

    for i in range(n_steps):
        state = pfe.update(state)
        sv = state.state_vector
        positions[i] = sv[:dim]
        velocities[i] = sv[dim:]
        energies[i] = state.energy

    return positions, velocities, energies


# ═══════════════════════════════════════════════════════
#  메인 검증
# ═══════════════════════════════════════════════════════

def main():
    print("=" * 65)
    print("  CookiieBrain 통합 파이프라인 검증")
    print("  trunk(Phase A+B+C) → analysis(Layer 1~6)")
    print("=" * 65)

    gamma = 2.0
    T = 2.0
    mass = 1.0
    omega = None  # 1D이므로 회전 비활성
    dt = 0.005
    n_steps = 80000

    # ── Phase B: 다중 우물 생성 ──
    mwp = build_double_well_1d()
    print(f"\n[Phase B] 이중 우물 생성: centers={[w.center[0] for w in mwp.wells]}")

    # ── Phase A+B+C: 궤적 생성 ──
    print(f"[Phase C] FDT: γ={gamma}, T={T}, σ²=2γT/m={2*gamma*T/mass:.4f}")
    print(f"[시뮬레이션] {n_steps} steps, dt={dt}, 총 시간={n_steps*dt:.1f}")

    positions, velocities, energies = run_pfe_simulation(
        mwp, n_steps, gamma, T, mass, omega, dt
    )
    print(f"[궤적] x 범위: [{positions.min():.2f}, {positions.max():.2f}]")
    print(f"[궤적] ⟨KE⟩ = {0.5*mass*np.mean(velocities**2):.4f}  (기대값 T/2 = {T/2:.4f})")

    # ── BrainAnalyzer: Layer 1~6 자동 분석 ──
    print("\n" + "-" * 65)
    print("  BrainAnalyzer 통합 분석 실행")
    print("-" * 65)

    analyzer = BrainAnalyzer(mwp=mwp, gamma=gamma, temperature=T, mass=mass)
    report = analyzer.run(positions, velocities, dt)

    # ── 리포트 출력 ──
    BrainAnalyzer.print_report(report)

    # ── 검증 ──
    print("\n" + "=" * 65)
    print("  검증 결과")
    print("=" * 65)

    passed = 0
    total = 0

    # Test 1: 등분배 정리
    total += 1
    ke_mean = 0.5 * mass * np.mean(velocities**2)
    ke_expected = 0.5 * T
    ke_ok = abs(ke_mean - ke_expected) / ke_expected < 0.15
    status = "PASS" if ke_ok else "FAIL"
    if ke_ok:
        passed += 1
    print(f"\n  [{status}] Test 1: 등분배 ⟨KE⟩={ke_mean:.4f} ≈ T/2={ke_expected:.4f}")

    # Test 2: 전이 발생
    total += 1
    n_trans = report["summary"]["total_transitions"]
    trans_ok = n_trans > 10
    status = "PASS" if trans_ok else "FAIL"
    if trans_ok:
        passed += 1
    print(f"  [{status}] Test 2: 우물 간 전이 {n_trans}회 (>10)")

    # Test 3: 엔트로피 생산률 (평형 → 작아야 함)
    total += 1
    ep = report["summary"]["entropy_production_rate"]
    ep_threshold = 0.5 * gamma * T / mass
    ep_ok = abs(ep) < ep_threshold
    status = "PASS" if ep_ok else "FAIL"
    if ep_ok:
        passed += 1
    print(f"  [{status}] Test 3: 엔트로피 생산률 |Ṡ|={abs(ep):.4f} < {ep_threshold:.4f}")

    # Test 4: 상세 균형
    total += 1
    dbv = report["summary"]["detailed_balance_violation"]
    dbv_ok = dbv < 0.15
    status = "PASS" if dbv_ok else "FAIL"
    if dbv_ok:
        passed += 1
    print(f"  [{status}] Test 4: 상세 균형 위반 = {dbv:.4f} (<0.15)")

    # Test 5: Layer 5 밀도 일치
    total += 1
    l5 = report["layer5"]
    if l5.get("skipped"):
        print(f"  [SKIP] Test 5: Layer 5 건너뜀 ({l5['reason']})")
    else:
        dm = l5.get("density_match", False)
        status = "PASS" if dm else "FAIL"
        if dm:
            passed += 1
        err = l5.get("density_l1_error", float("inf"))
        print(f"  [{status}] Test 5: 관측 밀도 ↔ 볼츠만 (L1 오차={err:.4f})")

    # Test 6: Layer 6 Fisher 계량 양정치
    total += 1
    l6 = report["layer6"]
    if l6.get("skipped"):
        print(f"  [SKIP] Test 6: Layer 6 건너뜀 ({l6['reason']})")
    else:
        fpd = l6.get("fisher_positive_definite", False)
        status = "PASS" if fpd else "FAIL"
        if fpd:
            passed += 1
        print(f"  [{status}] Test 6: Fisher 계량 양정치 = {fpd}")

    # Test 7: 곡률 비자명
    total += 1
    if l6.get("skipped"):
        print(f"  [SKIP] Test 7: Layer 6 건너뜀")
    else:
        cnt = l6.get("curvature_nontrivial", False)
        status = "PASS" if cnt else "FAIL"
        if cnt:
            passed += 1
        K = l6.get("gaussian_curvature_origin", 0)
        print(f"  [{status}] Test 7: 가우스 곡률 K={K:.6f} (비자명)")

    print(f"\n{'=' * 65}")
    print(f"  최종: {passed}/{total} PASSED")
    if passed == total:
        print("  ALL PASS — trunk → analysis 통합 흐름 정상 작동")
    print(f"{'=' * 65}")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
