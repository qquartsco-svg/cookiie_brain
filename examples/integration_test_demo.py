"""Cookiie Brain 통합 엔진 - 통합 테스트 데모

이 데모는 WellFormationEngine에서 생성된 기억 우물에 따라
PotentialFieldEngine이 실시간으로 변하고 상태가 수렴하는지 확인합니다.

시나리오:
1. WellFormationEngine이 episodes로부터 기억 우물(W, b) 생성
2. PotentialFieldEngine이 우물을 퍼텐셜 필드로 변환
3. 상태가 우물(에너지 최소점)로 수렴하는지 확인
4. 여러 시뮬레이션 스텝을 통해 동역학 검증

Author: GNJz (Qquarts)
Version: 0.1.1
"""

import numpy as np
import sys
from pathlib import Path
import matplotlib.pyplot as plt
from typing import List, Tuple

# 경로 설정
current_dir = Path(__file__).parent.parent
sys.path.insert(0, str(current_dir))

# BrainCore import (메인 폴더 기준)
try:
    from brain_core.global_state import GlobalState
except ImportError:
    try:
        # 메인 폴더 기준: CookiieBrain/ -> 00_BRAIN/
        brain_core_path = current_dir.parent / "BrainCore" / "src"
        sys.path.insert(0, str(brain_core_path))
        from brain_core.global_state import GlobalState
    except ImportError:
        print("BrainCore가 필요합니다. BrainCore를 설치하거나 PYTHONPATH에 추가하세요.")
        sys.exit(1)

# CookiieBrainEngine import
try:
    from cookiie_brain_engine import CookiieBrainEngine
except ImportError as e:
    print(f"CookiieBrainEngine을 import할 수 없습니다: {e}")
    sys.exit(1)

# WellFormationEngine models import
try:
    from well_formation_engine.models import Episode
except ImportError:
    try:
        # 메인 폴더 기준: CookiieBrain/ -> Brain_Disorder_Simulation_Engine/Unsolved_Problems_Engines/WellFormationEngine/
        well_formation_path = current_dir.parent / "Brain_Disorder_Simulation_Engine" / "Unsolved_Problems_Engines" / "WellFormationEngine" / "src"
        sys.path.insert(0, str(well_formation_path))
        from well_formation_engine.models import Episode
    except ImportError:
        print("WellFormationEngine이 필요합니다.")
        sys.exit(1)


def create_test_episodes(n_episodes: int = 10, n_dim: int = 2) -> List[Episode]:
    """테스트용 episodes 생성
    
    간단한 패턴: 두 개의 기억 우물을 형성
    - 우물 1: [1.0, 1.0] 근처
    - 우물 2: [-1.0, -1.0] 근처
    """
    episodes = []
    np.random.seed(42)  # 재현 가능한 결과
    
    for i in range(n_episodes):
        # 우물 1 또는 우물 2 중 하나 선택
        well_center = np.array([1.0, 1.0]) if i % 2 == 0 else np.array([-1.0, -1.0])
        
        # 노이즈 추가
        pre_activity = well_center + np.random.normal(0, 0.2, n_dim)
        post_activity = well_center + np.random.normal(0, 0.1, n_dim)
        
        episode = Episode(
            pre_activity=pre_activity.tolist(),
            post_activity=post_activity.tolist(),
            timestamp=float(i),
            episode_id=i,
            context={"well_id": i % 2},
        )
        episodes.append(episode)
    
    return episodes


def simulate_convergence(
    brain: CookiieBrainEngine,
    initial_state: GlobalState,
    n_steps: int = 100,
    dt: float = 0.01,
) -> Tuple[List[np.ndarray], List[float]]:
    """수렴 시뮬레이션
    
    상태가 기억 우물로 수렴하는지 확인
    """
    states = []
    energies = []
    
    current_state = initial_state
    
    for step in range(n_steps):
        # CookiieBrainEngine 업데이트
        current_state = brain.update(current_state)
        
        # 상태 추출
        state_vector = current_state.state_vector
        n_dim = len(state_vector) // 2
        position = state_vector[:n_dim]
        
        # 에너지 추출
        energy = brain.get_energy(current_state)
        
        states.append(position.copy())
        energies.append(energy)
        
        # 로그 출력 (10스텝마다)
        if step % 10 == 0:
            print(f"Step {step:3d}: position = {position}, energy = {energy:.6f}")
    
    return states, energies


def plot_convergence(
    states: List[np.ndarray],
    energies: List[float],
    save_path: Path,
):
    """수렴 시각화"""
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    
    # 1. 궤적 플롯
    ax1 = axes[0]
    positions = np.array(states)
    
    # 초기 위치
    ax1.plot(positions[0, 0], positions[0, 1], 'go', markersize=10, label='Start')
    # 최종 위치
    ax1.plot(positions[-1, 0], positions[-1, 1], 'ro', markersize=10, label='End')
    # 궤적
    ax1.plot(positions[:, 0], positions[:, 1], 'b-', alpha=0.5, linewidth=1)
    
    # 예상 우물 위치 표시
    ax1.plot(1.0, 1.0, 'k*', markersize=15, label='Well 1 (expected)')
    ax1.plot(-1.0, -1.0, 'k*', markersize=15, label='Well 2 (expected)')
    
    ax1.set_xlabel('x1')
    ax1.set_ylabel('x2')
    ax1.set_title('State Trajectory (Convergence to Memory Wells)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_aspect('equal', adjustable='box')
    
    # 2. 에너지 플롯
    ax2 = axes[1]
    steps = np.arange(len(energies))
    ax2.plot(steps, energies, 'b-', linewidth=2)
    ax2.set_xlabel('Step')
    ax2.set_ylabel('Energy')
    ax2.set_title('Energy Convergence')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    print(f"\n시각화 저장: {save_path}")
    plt.close()


def main():
    """통합 테스트 데모 메인 함수"""
    
    print("=" * 70)
    print("Cookiie Brain 통합 엔진 - 통합 테스트 데모")
    print("=" * 70)
    print("\n목표: WellFormationEngine → PotentialFieldEngine → 상태 수렴 검증")
    print("-" * 70)
    
    # 1. CookiieBrainEngine 생성
    print("\n[1/5] CookiieBrainEngine 생성 중...")
    brain = CookiieBrainEngine(
        enable_well_formation=True,
        enable_potential_field=True,
        enable_cerebellum=False,  # 이 데모에서는 Cerebellum 비활성화
        enable_hippo_memory=False,
        error_isolation=False,
        enable_logging=True,
    )
    print("✅ CookiieBrainEngine 생성 완료")
    
    # 2. 테스트 episodes 생성
    print("\n[2/5] 테스트 episodes 생성 중...")
    n_dim = 2  # 2D 상태 공간
    episodes = create_test_episodes(n_episodes=20, n_dim=n_dim)
    print(f"✅ {len(episodes)}개의 episodes 생성 완료")
    print(f"   예상 우물 위치: [1.0, 1.0], [-1.0, -1.0]")
    
    # 3. 초기 상태 생성
    print("\n[3/5] 초기 상태 생성 중...")
    initial_position = np.array([0.5, 0.5])  # 우물 사이의 위치
    initial_velocity = np.array([0.0, 0.0])
    
    initial_state = GlobalState(
        state_vector=np.concatenate([initial_position, initial_velocity]),
        energy=0.0,
        risk=0.0,
    )
    
    # episodes 추가
    initial_state.set_extension("episodes", episodes)
    print(f"✅ 초기 상태 생성 완료")
    print(f"   초기 위치: {initial_position}")
    
    # 4. WellFormationEngine 실행 (첫 번째 업데이트)
    print("\n[4/5] WellFormationEngine 실행 (첫 번째 업데이트)...")
    state_after_well = brain.update(initial_state)
    
    # Well 결과 확인
    well_data = state_after_well.get_extension("well_formation")
    if well_data is not None:
        W = well_data.get("W")
        b = well_data.get("b")
        if W is not None:
            # numpy 배열로 변환 (리스트인 경우)
            if isinstance(W, list):
                W = np.array(W)
            if isinstance(b, list):
                b = np.array(b)
            print(f"✅ WellFormationEngine 실행 완료")
            print(f"   W shape: {W.shape}")
            print(f"   b shape: {b.shape if b is not None else 'N/A'}")
        else:
            print("⚠️  WellFormationEngine 결과가 없습니다.")
    else:
        print("⚠️  WellFormationEngine extension이 없습니다.")
    
    # 5. 수렴 시뮬레이션
    print("\n[5/5] 수렴 시뮬레이션 실행 중...")
    print("-" * 70)
    
    # 시뮬레이션 파라미터 (필요시 조정 가능)
    n_steps = 100  # 더 빠른 수렴을 원하면 500-1000으로 증가
    dt = 0.01  # 더 빠른 수렴을 원하면 0.02-0.05로 증가 (단, 안정성 주의)
    
    states, energies = simulate_convergence(
        brain=brain,
        initial_state=state_after_well,
        n_steps=n_steps,
        dt=dt,
    )
    
    print("-" * 70)
    print(f"✅ 시뮬레이션 완료 ({n_steps} 스텝)")
    
    # 최종 상태 확인
    final_position = states[-1]
    final_energy = energies[-1]
    initial_energy = energies[0]
    
    print(f"\n📊 결과 요약:")
    print(f"   초기 위치: {states[0]}")
    print(f"   최종 위치: {final_position}")
    print(f"   초기 에너지: {initial_energy:.6f}")
    print(f"   최종 에너지: {final_energy:.6f}")
    
    # 에너지 변화 계산 (올바른 방향)
    energy_change = final_energy - initial_energy
    if energy_change < 0:
        print(f"   에너지 감소: {abs(energy_change):.6f}")
    else:
        print(f"   에너지 증가: {energy_change:.6f} (과도기 현상: 운동 에너지 증가)")
    
    # 우물까지의 거리 계산
    well1_dist = np.linalg.norm(final_position - np.array([1.0, 1.0]))
    well2_dist = np.linalg.norm(final_position - np.array([-1.0, -1.0]))
    min_dist = min(well1_dist, well2_dist)
    
    print(f"\n🎯 수렴 분석:")
    print(f"   우물 1까지 거리: {well1_dist:.4f}")
    print(f"   우물 2까지 거리: {well2_dist:.4f}")
    print(f"   가장 가까운 우물까지 거리: {min_dist:.4f}")
    
    if min_dist < 0.5:
        print(f"   ✅ 수렴 성공! (거리 < 0.5)")
    elif min_dist < 0.6:
        print(f"   ⚠️  수렴 경계 케이스 (거리: {min_dist:.4f}, 목표: < 0.5)")
        print(f"      → 더 많은 스텝 필요 (현재: {n_steps} 스텝)")
    else:
        print(f"   ⚠️  수렴 미완료 (거리 >= 0.6)")
        print(f"      → 스텝 수 증가 또는 dt 조정 필요")
    
    # 6. 시각화
    print("\n[6/6] 시각화 생성 중...")
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)
    
    plot_convergence(
        states=states,
        energies=energies,
        save_path=output_dir / "integration_test_convergence.png",
    )
    
    print("\n" + "=" * 70)
    print("통합 테스트 데모 완료!")
    print("=" * 70)
    print(f"\n📁 결과 파일: {output_dir / 'integration_test_convergence.png'}")


if __name__ == "__main__":
    main()

