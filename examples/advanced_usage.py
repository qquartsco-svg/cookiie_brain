"""Cookiie Brain 통합 엔진 고급 사용 예제

이 예제는 WellFormationEngine, PotentialFieldEngine, CerebellumEngine을
모두 활성화하여 통합 시스템으로 작동하는 방법을 보여줍니다.

Author: GNJz (Qquarts)
Version: 0.1.1
"""

import numpy as np
import sys
from pathlib import Path

# 경로 설정
current_dir = Path(__file__).parent.parent
sys.path.insert(0, str(current_dir))

# BrainCore import
try:
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


def main():
    """고급 사용 예제"""
    
    print("=" * 60)
    print("Cookiie Brain 통합 엔진 고급 사용 예제")
    print("=" * 60)
    
    # 1. CookiieBrainEngine 생성 (모든 엔진 활성화)
    print("\n1. CookiieBrainEngine 생성 중...")
    brain = CookiieBrainEngine(
        enable_well_formation=True,
        enable_potential_field=True,
        enable_cerebellum=True,  # CerebellumEngine 활성화
        enable_hippo_memory=False,  # HippoMemoryEngine은 아직 구현 예정
        error_isolation=True,  # 에러 격리 모드
        enable_logging=True,
    )
    print("✅ CookiieBrainEngine 생성 완료")
    
    # 2. 상태 생성
    print("\n2. 상태 생성 중...")
    state = GlobalState(
        state_vector=np.concatenate([
            np.array([1.0, 0.0, 0.0, 0.0, 0.0]),  # 위치 [x, y, z, theta_a, theta_b]
            np.array([0.0, 0.0, 0.0, 0.0, 0.0]),  # 속도 [vx, vy, vz, vtheta_a, vtheta_b]
        ]),
        energy=0.0,
        risk=0.0,
    )
    print("✅ 상태 생성 완료")
    print(f"   상태 벡터: {state.state_vector}")
    
    # 3. episodes 추가 (WellFormationEngine용)
    print("\n3. episodes 데이터 추가 중...")
    episodes = [
        # 예시 episodes 데이터
        # 실제로는 WellFormationEngine이 요구하는 형식으로 제공해야 함
    ]
    state.set_extension("episodes", episodes)
    print("✅ episodes 데이터 추가 완료")
    
    # 4. 목표 상태 추가 (CerebellumEngine용)
    print("\n4. 목표 상태 추가 중...")
    target_state = np.array([2.0, 1.0, 0.0, 0.0, 0.0])  # 목표 위치
    state.set_extension("target_state", target_state)
    state.set_extension("context", {})  # 컨텍스트 정보
    print("✅ 목표 상태 추가 완료")
    print(f"   목표 상태: {target_state}")
    
    # 5. 통합 엔진 실행
    print("\n5. 통합 엔진 실행 중...")
    try:
        result = brain.update(state)
        print("✅ 통합 엔진 실행 완료")
        
        # 6. 결과 확인
        print("\n6. 결과 확인:")
        print(f"   상태 벡터: {result.state_vector}")
        print(f"   에너지: {result.energy}")
        
        # Extensions 확인
        if result.has_extension("well_formation"):
            well_data = result.get_extension("well_formation")
            print(f"\n   WellFormationEngine 결과:")
            print(f"     W shape = {well_data['W'].shape if 'W' in well_data else 'N/A'}")
        
        if result.has_extension("potential_field"):
            potential_data = result.get_extension("potential_field")
            print(f"\n   PotentialFieldEngine 결과:")
            print(f"     potential = {potential_data.get('potential', 'N/A')}")
        
        if result.has_extension("cerebellum"):
            cerebellum_data = result.get_extension("cerebellum")
            print(f"\n   CerebellumEngine 결과:")
            print(f"     correction = {cerebellum_data.get('correction', 'N/A')}")
            print(f"     target_state = {cerebellum_data.get('target_state', 'N/A')}")
        
        # 에너지 확인
        energy = brain.get_energy(result)
        print(f"\n   에너지 (get_energy): {energy}")
        
        # 엔진 상태 확인
        engine_state = brain.get_state()
        print(f"\n7. 엔진 상태:")
        for key, value in engine_state.items():
            print(f"   {key}: {value}")
    
    except Exception as e:
        print(f"❌ 통합 엔진 실행 실패: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("예제 실행 완료")
    print("=" * 60)


if __name__ == "__main__":
    main()

