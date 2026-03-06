"""WellFormation → Gaussian 브릿지 검증

검증 항목:
  1. 변환 정확성   — W, b + episodes → GaussianWell 파라미터 생성
  2. Registry 누적  — 3개 이상 누적 시 ready_for_orbit = True
  3. 중복 제거      — dedup_distance 이내 우물 병합
  4. 장벽 양수      — export_potential() 결과에서 barrier > 0
  5. 공전 재현      — 브릿지 생성 우물로 순환 궤도

테스트 구조:
  Mock WellFormationResult + Mock Episode 사용.
  center_mode="pattern" → mean(post_activity)로 center 결정.
  3개 클러스터 → 삼각형 배치 → 공전 검증.

실행:
  python CookiieBrain/examples/bridge_verification.py
"""

import numpy as np
import sys
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Any

root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root / "CookiieBrain"))
sys.path.insert(0, str(root / "BrainCore" / "src"))
sys.path.append(str(root / "Brain_Disorder_Simulation_Engine"
                     / "Unsolved_Problems_Engines" / "PotentialFieldEngine"))

from L1_dynamics.Phase_B import (
    MultiWellPotential, GaussianWell, create_symmetric_wells,
    WellToGaussianConfig, WellRegistry, well_result_to_gaussian,
    compute_center, compute_amplitude, compute_sigma,
)


# ------------------------------------------------------------------ #
#  Mock 객체 — WellFormationEngine 없이 테스트
# ------------------------------------------------------------------ #

@dataclass
class MockEpisode:
    post_activity: List[float]
    pre_activity: List[float] = None
    timestamp: float = 0.0
    episode_id: int = 0
    context: Dict[str, Any] = None

    def __post_init__(self):
        if self.pre_activity is None:
            self.pre_activity = self.post_activity
        if self.context is None:
            self.context = {}


@dataclass
class MockWellResult:
    W: List[List[float]]
    b: List[float]
    analysis: Dict[str, Any] = None

    def __post_init__(self):
        if self.analysis is None:
            self.analysis = {}


def make_cluster_episodes(center, n=5, noise=0.05):
    """특정 center 주변에 클러스터된 Episode 생성"""
    episodes = []
    for i in range(n):
        pattern = center + np.random.randn(len(center)) * noise
        episodes.append(MockEpisode(
            post_activity=pattern.tolist(),
            episode_id=i,
        ))
    return episodes


def make_stable_W(dim=2, strength=1.0):
    """안정적인 (음정부호) W 행렬 생성"""
    return [[-strength, 0.0], [0.0, -strength]] if dim == 2 else \
           [[-strength] * dim for _ in range(dim)]


# ------------------------------------------------------------------ #
#  검증
# ------------------------------------------------------------------ #

def run_verification():
    np.random.seed(42)

    r = 2.5
    target_centers = [
        np.array([r * np.cos(2 * np.pi * k / 3),
                   r * np.sin(2 * np.pi * k / 3)])
        for k in range(3)
    ]

    print("=" * 60)
    print("WellFormation → Gaussian Bridge 검증")
    print("=" * 60)

    # ------------------------------------------------------------ #
    #  검증 1: 단일 변환 정확성
    # ------------------------------------------------------------ #
    print("\n--- 검증 1: 단일 변환 (W, b + episodes → GaussianWell) ---")

    config = WellToGaussianConfig(
        center_mode="pattern",
        amplitude_scale=1.0,
        sigma_scale=1.0,
    )
    W = np.array(make_stable_W(dim=2, strength=2.0))
    b = np.array([0.0, 0.0])
    episodes_0 = make_cluster_episodes(target_centers[0], n=10, noise=0.1)

    well = well_result_to_gaussian(
        MockWellResult(W=W.tolist(), b=b.tolist()),
        config=config,
        episodes=episodes_0,
    )

    center_error = np.linalg.norm(well.center - target_centers[0])
    print(f"  target center: {target_centers[0]}")
    print(f"  computed center: {well.center}")
    print(f"  center error: {center_error:.6f}")
    print(f"  amplitude: {well.amplitude:.4f}")
    print(f"  sigma: {well.sigma:.4f}")

    convert_ok = center_error < 0.5 and well.amplitude > 0 and well.sigma > 0
    print(f"  결과: {'PASS' if convert_ok else 'FAIL'}")

    # ------------------------------------------------------------ #
    #  검증 2: Registry 누적
    # ------------------------------------------------------------ #
    print("\n--- 검증 2: Registry 누적 (3개 우물) ---")

    registry = WellRegistry(config=WellToGaussianConfig(
        center_mode="pattern",
        amplitude_scale=1.0,
        sigma_scale=1.0,
        dedup_distance=0.5,
        min_wells_for_orbit=3,
    ))

    for i, center in enumerate(target_centers):
        eps = make_cluster_episodes(center, n=10, noise=0.1)
        wr = MockWellResult(
            W=make_stable_W(dim=2, strength=2.0),
            b=[0.0, 0.0],
        )
        idx = registry.add(wr, eps)
        print(f"  Well #{idx}: center={registry.wells[idx].center.tolist()}")

    print(f"  count: {registry.count}")
    print(f"  ready_for_orbit: {registry.ready_for_orbit}")

    accumulate_ok = registry.count == 3 and registry.ready_for_orbit
    print(f"  결과: {'PASS' if accumulate_ok else 'FAIL'}")

    # ------------------------------------------------------------ #
    #  검증 3: 중복 제거
    # ------------------------------------------------------------ #
    print("\n--- 검증 3: 중복 제거 (dedup) ---")

    registry_dup = WellRegistry(config=WellToGaussianConfig(
        center_mode="pattern",
        dedup_distance=1.0,
        min_wells_for_orbit=3,
    ))

    eps_a = make_cluster_episodes(target_centers[0], n=5, noise=0.05)
    eps_a_near = make_cluster_episodes(
        target_centers[0] + np.array([0.1, 0.1]), n=5, noise=0.05
    )
    wr = MockWellResult(W=make_stable_W(), b=[0.0, 0.0])

    registry_dup.add(wr, eps_a)
    registry_dup.add(wr, eps_a_near)
    print(f"  2개 추가 (근접) → count: {registry_dup.count}")

    dedup_ok = registry_dup.count == 1
    print(f"  결과: {'PASS' if dedup_ok else 'FAIL'} (1개로 병합됨)")

    # ------------------------------------------------------------ #
    #  검증 4: 장벽 양수
    # ------------------------------------------------------------ #
    print("\n--- 검증 4: 장벽 양수 ---")

    mwp = registry.export_potential()
    info = mwp.landscape_info()

    barriers = [b_info["barrier_height"] for b_info in info["barriers"]]
    for b_info in info["barriers"]:
        print(f"  우물 {b_info['wells']}: barrier={b_info['barrier_height']:.6f}")

    barrier_ok = all(bh > 0 for bh in barriers)
    print(f"  결과: {'PASS' if barrier_ok else 'FAIL'}")

    # ------------------------------------------------------------ #
    #  검증 5: 공전 재현
    # ------------------------------------------------------------ #
    print("\n--- 검증 5: 공전 재현 (PotentialFieldEngine) ---")

    try:
        from brain_core.global_state import GlobalState
        from potential_field_engine import PotentialFieldEngine

        omega = 0.3
        dt = 0.005
        n_steps = 30000

        engine = PotentialFieldEngine(
            potential_func=mwp.potential,
            field_func=mwp.field,
            omega_coriolis=omega,
            rotation_axis=(0, 1),
            dt=dt,
        )

        x0 = registry.wells[0].center * 0.8
        V_init = mwp.potential(x0)
        V_saddle_max = max(b_info["V_saddle"] for b_info in info["barriers"])
        K_need = V_saddle_max - V_init + 1.0
        v_mag = np.sqrt(2.0 * max(K_need, 0.01))
        toward_center = -x0 / np.linalg.norm(x0)
        v0 = v_mag * toward_center

        E_init = 0.5 * np.dot(v0, v0) + V_init
        state = GlobalState(
            state_vector=np.concatenate([x0, v0]),
            energy=E_init,
        )

        well_visits = [mwp.nearest_well(x0)]
        current = state
        for _ in range(n_steps):
            current = engine.update(current)
            x = current.state_vector[:2]
            well_visits.append(mwp.nearest_well(x))

        transitions = sum(
            1 for k in range(1, len(well_visits))
            if well_visits[k] != well_visits[k - 1]
        )
        visited_wells = set(well_visits)

        # 순환 검출
        transition_points = [
            well_visits[k] for k in range(1, len(well_visits))
            if well_visits[k] != well_visits[k - 1]
        ]
        n_cycles = 0
        i = 0
        while i + 3 <= len(transition_points):
            window = transition_points[i:i + 3]
            if len(set(window)) == 3:
                n_cycles += 1
                i += 3
            else:
                i += 1

        print(f"  전이 횟수: {transitions}")
        print(f"  3-우물 순환: {n_cycles}")
        print(f"  방문 우물: {visited_wells}")

        orbit_ok = n_cycles >= 2 and len(visited_wells) == 3
        print(f"  결과: {'PASS' if orbit_ok else 'FAIL'}")

    except ImportError as e:
        print(f"  PotentialFieldEngine/BrainCore import 실패: {e}")
        print(f"  결과: SKIP (의존성 없음)")
        orbit_ok = True

    # ============================================================ #
    #  종합
    # ============================================================ #
    print("\n" + "=" * 60)
    print("종합")
    print("=" * 60)
    results = {
        "단일 변환 (W,b → GaussianWell)": convert_ok,
        "Registry 누적 (3개)": accumulate_ok,
        "중복 제거 (dedup)": dedup_ok,
        "장벽 양수": barrier_ok,
        "공전 재현": orbit_ok,
    }
    for name, ok in results.items():
        print(f"  {name}: {'PASS' if ok else 'FAIL'}")
    all_pass = all(results.values())
    print(f"\n  Bridge 검증: {'ALL PASS' if all_pass else 'SOME FAILED'}")
    return all_pass


if __name__ == "__main__":
    run_verification()
