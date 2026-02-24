"""Phase A 통합 테스트: 우물 + 회전항(자전)

- 단일 우물 + enable_phase_a=True 로 CookiieBrain 실행
- curl 확인 (2D, 합성 필드 g = -∇E + R)
- 궤도 수 step 돌려서 위치 이력 출력

실행: CookiieBrain/examples/ 에서
  python phase_a_integration_test.py

또는 00_BRAIN 기준:
  python CookiieBrain/examples/phase_a_integration_test.py
"""

import numpy as np
import sys
from pathlib import Path

current_dir = Path(__file__).parent.parent
sys.path.insert(0, str(current_dir))
parent = current_dir.parent
sys.path.insert(0, str(parent))

# BrainCore
try:
    from brain_core.global_state import GlobalState
except ImportError:
    brain_core_path = parent / "BrainCore" / "src"
    sys.path.insert(0, str(brain_core_path))
    from brain_core.global_state import GlobalState

# CookiieBrain
from cookiie_brain_engine import CookiieBrainEngine

# WellFormation
try:
    from well_formation_engine.models import Episode
except ImportError:
    well_path = parent / "Brain_Disorder_Simulation_Engine" / "Unsolved_Problems_Engines" / "WellFormationEngine" / "src"
    sys.path.insert(0, str(well_path))
    from well_formation_engine.models import Episode

# Phase_A (curl 검증용)
try:
    from trunk.Phase_A import Pole, create_rotational_field, create_combined_field, compute_curl_2d
except ImportError:
    Pole = None
    create_rotational_field = None
    create_combined_field = None
    compute_curl_2d = None


def single_well_episodes(n_episodes: int = 15, n_dim: int = 2, center=None):
    """단일 우물 하나만 형성하는 episodes."""
    center = center if center is not None else np.zeros(2)
    center = np.array(center)[:n_dim]
    episodes = []
    np.random.seed(42)
    for i in range(n_episodes):
        pre = center + np.random.normal(0, 0.25, n_dim)
        post = center + np.random.normal(0, 0.15, n_dim)
        episodes.append(Episode(
            pre_activity=pre.tolist(),
            post_activity=post.tolist(),
            timestamp=float(i),
            episode_id=i,
            context={},
        ))
    return episodes


def main():
    n_dim = 2
    n_steps = 200
    dt = 0.01

    print("Phase A 통합 테스트 (단일 우물 + 자전)")
    print("  n_dim=%d, n_steps=%d, dt=%s" % (n_dim, n_steps, dt))

    episodes = single_well_episodes(n_episodes=15, n_dim=n_dim)
    state = GlobalState(
        state_vector=np.concatenate([
            np.array([0.5, 0.5]),
            np.array([0.0, 0.0]),
        ]),
        energy=0.0,
    )
    state.set_extension("episodes", episodes)

    brain = CookiieBrainEngine(
        enable_well_formation=True,
        enable_potential_field=True,
        enable_cerebellum=False,
        well_formation_config={},
        potential_field_config={
            "enable_phase_a": True,
            "phase_a_pole_position": [0.0, 0.0],
            "phase_a_strength": 0.8,
            "phase_a_rotation_direction": 1,
        },
        enable_logging=False,
    )

    state = GlobalState(
        state_vector=np.concatenate([
            np.array([0.5, 0.5]),
            np.array([0.0, 0.0]),
        ]),
        energy=0.0,
    )
    state.set_extension("episodes", episodes)

    # 한 번 update로 well 생성
    for _ in range(3):
        state = brain.update(state)

    well_result = state.get_extension("well_formation")
    if not well_result or "well_result" not in well_result:
        print("Well 생성 실패")
        return

    # curl 검증 (Phase_A로 합성 필드 직접 구성)
    if create_rotational_field is not None and compute_curl_2d is not None:
        pfe_path = parent / "Brain_Disorder_Simulation_Engine" / "Unsolved_Problems_Engines" / "PotentialFieldEngine"
        if str(pfe_path) not in sys.path:
            sys.path.append(str(pfe_path))
        from well_formation_integration import create_field_from_wells
        well_result_obj = well_result["well_result"]
        field_func = create_field_from_wells(well_result_obj)
        pole = Pole(position=np.array([0.0, 0.0]), rotation_direction=1, strength=0.8)
        R = create_rotational_field(pole, use_simple_form=True)
        combined = create_combined_field(field_func, R)
        test_pt = np.array([0.5, 0.3])
        curl_val = compute_curl_2d(combined, test_pt)
        print("  curl(합성 필드) at [0.5, 0.3]: %s (≠0 이면 회전 성분 있음)" % curl_val)
    else:
        print("  Phase_A 미사용 또는 curl 검증 스킵")

    # 궤도 수 step
    positions = []
    for _ in range(n_steps):
        state = brain.update(state)
        x = state.state_vector[:n_dim]
        positions.append(x.copy())

    positions = np.array(positions)
    print("  궤도: 처음 3점 %s" % positions[:3].tolist())
    print("  궤도: 마지막 3점 %s" % positions[-3:].tolist())
    r = np.linalg.norm(positions, axis=1)
    print("  원점으로부터 거리: min=%.4f max=%.4f" % (r.min(), r.max()))
    print("Phase A 통합 테스트 끝.")


if __name__ == "__main__":
    main()
