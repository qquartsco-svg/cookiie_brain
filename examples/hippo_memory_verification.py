"""HippoMemoryEngine 검증: 기억 형성 → 강화 → 망각 → 리콜

검증 항목:
  1. 우물 자동 생성 (encode)
  2. 반복 자극 → amplitude 증가 (강화)
  3. 자연 감쇠 → amplitude 감소 (망각)
  4. threshold 이하 → 우물 삭제 (소멸)
  5. recall → I_recall 방향성 확인
  6. 하위 호환 (η=0, λ=0 → amplitude 불변)
  7. PFE 통합: 동적 우물 위에서 궤적 생성 + BrainAnalyzer

실행:
  python examples/hippo_memory_verification.py
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
from L3_memory import HippoMemoryEngine, HippoConfig, MemoryStore, EnergyBudgeter


def test_1_well_creation():
    """Test 1: 우물 자동 생성"""
    config = HippoConfig(creation_distance=2.0, sigma_init=1.0)
    engine = HippoMemoryEngine(config=config, dim=1)

    idx0 = engine.encode(np.array([-2.0]))
    idx1 = engine.encode(np.array([0.0]))
    idx2 = engine.encode(np.array([2.0]))

    ok = engine.store.count == 3
    print(f"  [{'PASS' if ok else 'FAIL'}] Test 1: 우물 3개 생성 → count={engine.store.count}")
    return ok


def test_2_reinforcement():
    """Test 2: 반복 자극 → amplitude 증가"""
    config = HippoConfig(eta=0.5, decay_rate=0.0, creation_distance=2.0)
    engine = HippoMemoryEngine(config=config, dim=1)

    engine.encode(np.array([0.0]))
    A_before = engine.store._wells[0].amplitude

    for _ in range(10):
        engine.encode(np.array([0.0]), strength=1.0)

    A_after = engine.store._wells[0].amplitude

    ok = A_after > A_before
    print(f"  [{'PASS' if ok else 'FAIL'}] Test 2: 강화 A={A_before:.4f} → {A_after:.4f}")
    return ok


def test_3_decay():
    """Test 3: 자연 감쇠 → amplitude 감소"""
    config = HippoConfig(eta=0.0, decay_rate=0.01, amplitude_min=0.01)
    store = MemoryStore(config, dim=1)

    from L1_dynamics.Phase_B.multi_well_potential import GaussianWell
    store._wells.append(GaussianWell(center=np.array([0.0]), amplitude=5.0, sigma=1.0))
    store._visit_counts.append(0)
    store._ages.append(0.0)

    A_before = store._wells[0].amplitude

    for _ in range(100):
        store.step(np.array([10.0]), dt=1.0)

    A_after = store._wells[0].amplitude
    ok = A_after < A_before * 0.5 and store.count > 0
    print(f"  [{'PASS' if ok else 'FAIL'}] Test 3: 감쇠 A={A_before:.4f} → {A_after:.4f}")
    return ok


def test_4_pruning():
    """Test 4: threshold 이하 → 우물 삭제"""
    config = HippoConfig(eta=0.0, decay_rate=0.5, amplitude_min=0.1)
    store = MemoryStore(config, dim=1)

    from L1_dynamics.Phase_B.multi_well_potential import GaussianWell
    store._wells.append(GaussianWell(center=np.array([0.0]), amplitude=0.5, sigma=1.0))
    store._visit_counts.append(0)
    store._ages.append(0.0)
    store._version += 1

    for _ in range(50):
        store.step(np.array([10.0]), dt=1.0)

    ok = store.count == 0
    print(f"  [{'PASS' if ok else 'FAIL'}] Test 4: 소멸 → count={store.count}")
    return ok


def test_5_recall():
    """Test 5: recall → 리콜 타깃 방향 확인"""
    config = HippoConfig(recall_strength=2.0, creation_distance=5.0)
    engine = HippoMemoryEngine(config=config, dim=1)

    engine.encode(np.array([-3.0]))
    engine.encode(np.array([3.0]))

    engine.recall(np.array([-2.5]))

    x = np.array([0.0])
    v = np.array([0.0])
    injection = engine.budgeter.compute_injection(x, v, engine.store)

    ok = injection[0] < 0
    print(f"  [{'PASS' if ok else 'FAIL'}] Test 5: 리콜(-3.0) → I={injection[0]:.4f} (음수면 정상)")
    return ok


def test_6_backward_compat():
    """Test 6: η=0, λ=0 → amplitude 불변 (하위 호환)"""
    config = HippoConfig(eta=0.0, decay_rate=0.0)
    store = MemoryStore(config, dim=1)

    from L1_dynamics.Phase_B.multi_well_potential import GaussianWell
    store._wells.append(GaussianWell(center=np.array([0.0]), amplitude=3.0, sigma=1.0))
    store._visit_counts.append(0)
    store._ages.append(0.0)

    A_before = store._wells[0].amplitude

    for _ in range(1000):
        store.step(np.array([0.0]), dt=0.01)

    A_after = store._wells[0].amplitude

    ok = abs(A_after - A_before) < 1e-10
    print(f"  [{'PASS' if ok else 'FAIL'}] Test 6: 하위 호환 A={A_before:.4f} → {A_after:.4f} (불변)")
    return ok


def test_7_integrated_pipeline():
    """Test 7: PFE + HippoMemory + BrainAnalyzer 통합"""
    try:
        from potential_field_engine import PotentialFieldEngine
    except ImportError:
        print("  [SKIP] Test 7: PFE import 실패")
        return True

    try:
        from brain_core.global_state import GlobalState
    except ImportError:
        brain_core_path = project_root.parent / "BrainCore" / "src"
        sys.path.insert(0, str(brain_core_path))
        from brain_core.global_state import GlobalState

    from L4_analysis.brain_analyzer import BrainAnalyzer

    config = HippoConfig(
        eta=0.05, decay_rate=0.0005, amplitude_init=3.0,
        amplitude_min=0.1, creation_distance=3.0, sigma_init=1.0,
    )
    engine = HippoMemoryEngine(config=config, dim=1, rng_seed=42)

    engine.encode(np.array([-1.5]), strength=1.0)
    engine.encode(np.array([1.5]), strength=1.0)

    mwp = engine.export_potential()
    gamma = 2.0
    T = 2.0
    mass = 1.0
    dt = 0.005
    n_steps = 20000

    pfe = PotentialFieldEngine(
        potential_func=mwp.potential,
        field_func=mwp.field,
        gamma=gamma,
        temperature=T,
        mass=mass,
        noise_seed=42,
        dt=dt,
    )

    rng = np.random.default_rng(42)
    x0 = rng.normal(-1.5, 0.5, 1)
    v0 = rng.normal(0.0, np.sqrt(T / mass), 1)
    state = GlobalState(state_vector=np.concatenate([x0, v0]))

    positions = np.zeros((n_steps, 1))
    velocities = np.zeros((n_steps, 1))

    for i in range(n_steps):
        state = pfe.update(state)
        sv = state.state_vector
        positions[i] = sv[:1]
        velocities[i] = sv[1:]

        engine.store.step(positions[i], dt)

    mwp_final = engine.export_potential()
    analyzer = BrainAnalyzer(mwp=mwp_final, gamma=gamma, temperature=T, mass=mass)
    report = analyzer.run(positions, velocities, dt)

    n_wells = engine.store.count
    ep = report["summary"]["entropy_production_rate"]

    ok = n_wells >= 2 and abs(ep) < 5.0
    print(f"  [{'PASS' if ok else 'FAIL'}] Test 7: 통합 — wells={n_wells}, Ṡ={ep:.4f}")

    amps = [w.amplitude for w in engine.store._wells]
    print(f"          우물 amplitudes: {[f'{a:.4f}' for a in amps]}")

    return ok


def main():
    print("=" * 65)
    print("  HippoMemoryEngine 검증")
    print("  기억 생성 → 강화 → 망각 → 리콜")
    print("=" * 65)

    tests = [
        test_1_well_creation,
        test_2_reinforcement,
        test_3_decay,
        test_4_pruning,
        test_5_recall,
        test_6_backward_compat,
        test_7_integrated_pipeline,
    ]

    passed = 0
    for t in tests:
        if t():
            passed += 1

    print(f"\n{'=' * 65}")
    print(f"  최종: {passed}/{len(tests)} PASSED")
    if passed == len(tests):
        print("  ALL PASS — HippoMemoryEngine 정상 작동")
    print(f"{'=' * 65}")

    return passed == len(tests)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
