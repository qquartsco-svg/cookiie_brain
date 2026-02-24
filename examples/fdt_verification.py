"""Phase C v2: 요동-소산 정리 (FDT) 검증 스크립트

검증 항목:
  1. 하위 호환: temperature=None → σ=0, 기존 결정론적 결과 동일
  2. σ 자동 계산: temperature=T, γ>0 → σ = √(2γT/m)
  3. Manual override: noise_sigma > 0이면 temperature 무시
  4. Boltzmann 등분배: 조화 퍼텐셜 + FDT → ⟨½v²⟩ ≈ T/2 (per DoF, m=1)
  5. γ=0 안전장치: temperature>0이어도 γ=0이면 σ=0 (FDT 요구)

실행:
  python examples/fdt_verification.py
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
sys.path.insert(0, str(pfe_path))

import numpy as np
from potential_field_engine import PotentialFieldEngine

try:
    from brain_core.global_state import GlobalState
except ImportError:
    brain_core_path = project_root.parent / "BrainCore" / "src"
    sys.path.insert(0, str(brain_core_path))
    from brain_core.global_state import GlobalState


# ─────────────────────────────────────────────────── #
#  검증 1: 하위 호환 (temperature=None → 결정론적)
# ─────────────────────────────────────────────────── #

def test_backward_compat():
    """temperature 미설정 시 기존 동작과 동일해야 한다."""
    V = lambda x: 0.5 * np.dot(x, x)
    g = lambda x: -x

    eng_old = PotentialFieldEngine(
        potential_func=V, field_func=g,
        omega_coriolis=0.3, gamma=0.0,
        noise_sigma=0.0, noise_seed=1, dt=0.01,
    )
    eng_new = PotentialFieldEngine(
        potential_func=V, field_func=g,
        omega_coriolis=0.3, gamma=0.0,
        temperature=None, mass=1.0,
        noise_seed=1, dt=0.01,
    )

    assert eng_old.noise_sigma == 0.0
    assert eng_new.noise_sigma == 0.0
    assert eng_new.noise_mode == "off"

    sv = np.array([1.0, 0.5, 0.2, -0.1])
    s1 = GlobalState(state_vector=sv.copy(), energy=0.0)
    s2 = GlobalState(state_vector=sv.copy(), energy=0.0)

    for _ in range(500):
        s1 = eng_old.update(s1)
        s2 = eng_new.update(s2)

    match = np.allclose(s1.state_vector, s2.state_vector, atol=1e-12)
    ok = match and eng_new.noise_mode == "off"
    print(f"[1] 하위 호환 (temperature=None): {'PASS' if ok else 'FAIL'}")
    print(f"    mode={eng_new.noise_mode}, σ={eng_new.noise_sigma:.6f}, match={match}")
    return ok


# ─────────────────────────────────────────────────── #
#  검증 2: σ 자동 계산 (FDT: σ² = 2γT/m)
# ─────────────────────────────────────────────────── #

def test_fdt_sigma():
    """temperature와 gamma로부터 σ가 정확히 계산되는지 확인."""
    V = lambda x: 0.0
    g = lambda x: np.zeros_like(x)

    T, gamma, m = 2.0, 0.5, 1.5
    expected_sigma = np.sqrt(2.0 * gamma * T / m)

    eng = PotentialFieldEngine(
        potential_func=V, field_func=g,
        gamma=gamma, temperature=T, mass=m, dt=0.01,
    )

    actual = eng.noise_sigma
    rel_err = abs(actual - expected_sigma) / expected_sigma
    mode_ok = eng.noise_mode == "fdt"
    ok = rel_err < 1e-10 and mode_ok
    print(f"[2] FDT σ 계산: {'PASS' if ok else 'FAIL'}")
    print(f"    expected={expected_sigma:.8f}, actual={actual:.8f}, "
          f"rel_err={rel_err:.2e}, mode={eng.noise_mode}")
    return ok


# ─────────────────────────────────────────────────── #
#  검증 3: Manual override (noise_sigma > 0 → FDT 무시)
# ─────────────────────────────────────────────────── #

def test_manual_override():
    """noise_sigma를 직접 설정하면 temperature가 있어도 무시."""
    V = lambda x: 0.0
    g = lambda x: np.zeros_like(x)

    manual_sigma = 0.42
    eng = PotentialFieldEngine(
        potential_func=V, field_func=g,
        gamma=0.5, temperature=100.0, mass=1.0,
        noise_sigma=manual_sigma, dt=0.01,
    )

    ok = (
        abs(eng.noise_sigma - manual_sigma) < 1e-12
        and eng.noise_mode == "manual"
    )
    print(f"[3] Manual override: {'PASS' if ok else 'FAIL'}")
    print(f"    σ={eng.noise_sigma:.4f} (expected {manual_sigma}), mode={eng.noise_mode}")
    return ok


# ─────────────────────────────────────────────────── #
#  검증 4: Boltzmann 등분배 ⟨½v²⟩ ≈ T/2 per DoF
# ─────────────────────────────────────────────────── #

def test_equipartition():
    """조화 퍼텐셜 V=½kx² + FDT → 등분배 정리 검증.

    이론: ⟨½m v_i²⟩ = T/2  (kB=1, per degree of freedom)
    m=1이면 ⟨½v_i²⟩ = T/2, 즉 ⟨v_i²⟩ = T.
    """
    k = 1.0
    V = lambda x: 0.5 * k * np.dot(x, x)
    g = lambda x: -k * x

    T = 1.0
    gamma = 0.5
    m = 1.0
    dt = 0.005

    n_runs = 30
    n_steps = 80000
    burn_in = 20000

    v_sq_samples = []
    for run in range(n_runs):
        eng = PotentialFieldEngine(
            potential_func=V, field_func=g,
            omega_coriolis=None, gamma=gamma,
            temperature=T, mass=m,
            noise_seed=run, dt=dt,
        )
        state = GlobalState(
            state_vector=np.array([0.5, -0.3, 0.1, 0.2]),
            energy=0.0,
        )
        for step in range(n_steps):
            state = eng.update(state)
            if step >= burn_in:
                vx, vy = state.state_vector[2], state.state_vector[3]
                v_sq_samples.append(vx**2 + vy**2)

    mean_v_sq = np.mean(v_sq_samples)
    expected_v_sq = 2.0 * T / m  # 2 DoF → ⟨|v|²⟩ = 2T/m
    rel_err = abs(mean_v_sq - expected_v_sq) / expected_v_sq

    ok = rel_err < 0.15
    print(f"[4] Boltzmann 등분배: {'PASS' if ok else 'FAIL'}")
    print(f"    ⟨|v|²⟩ = {mean_v_sq:.4f} (이론값 2T/m = {expected_v_sq:.4f})")
    print(f"    상대 오차: {rel_err*100:.1f}%")
    return ok


# ─────────────────────────────────────────────────── #
#  검증 5: γ=0 안전장치 (FDT 비활성)
# ─────────────────────────────────────────────────── #

def test_gamma_zero_guard():
    """γ=0이면 temperature가 설정되어 있어도 σ=0."""
    V = lambda x: 0.0
    g = lambda x: np.zeros_like(x)

    eng = PotentialFieldEngine(
        potential_func=V, field_func=g,
        gamma=0.0, temperature=5.0, mass=1.0, dt=0.01,
    )
    ok = eng.noise_sigma == 0.0 and eng.noise_mode == "off"
    print(f"[5] γ=0 안전장치: {'PASS' if ok else 'FAIL'}")
    print(f"    σ={eng.noise_sigma}, mode={eng.noise_mode}")
    return ok


# ─────────────────────────────────────────────────── #
#  실행
# ─────────────────────────────────────────────────── #

if __name__ == "__main__":
    print("=" * 60)
    print("Phase C v2: FDT (요동-소산 정리) 검증")
    print("=" * 60)
    print()

    results = []
    results.append(test_backward_compat())
    print()
    results.append(test_fdt_sigma())
    print()
    results.append(test_manual_override())
    print()
    results.append(test_equipartition())
    print()
    results.append(test_gamma_zero_guard())
    print()

    print("=" * 60)
    passed = sum(results)
    total = len(results)
    if passed == total:
        print(f"ALL PASS ({passed}/{total})")
    else:
        print(f"PARTIAL: {passed}/{total} PASS")
    print("=" * 60)
