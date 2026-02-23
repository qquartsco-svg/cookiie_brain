"""Cookiie Brain 통합 엔진 기본 사용 예제

이 예제는 WellFormationEngine과 PotentialFieldEngine을 통합하여
하나의 시스템으로 작동하는 방법을 보여줍니다.

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
    """기본 사용 예제"""
    
    print("=" * 60)
    print("Cookiie Brain 통합 엔진 기본 사용 예제")
    print("=" * 60)
    
    # 1. CookiieBrainEngine 생성
    print("\n1. CookiieBrainEngine 생성 중...")
    brain = CookiieBrainEngine(
        enable_well_formation=True,
        enable_potential_field=True,
        enable_logging=True,
    )
    print("✅ CookiieBrainEngine 생성 완료")
    
    # 2. 상태 생성
    print("\n2. 상태 생성 중...")
    state = GlobalState(
        state_vector=np.concatenate([
            np.array([1.0, 0.0]),  # 위치 [x1, x2]
            np.array([0.0, 0.0]),  # 속도 [v1, v2]
        ]),
        energy=0.0,
        risk=0.0,
    )
    print("✅ 상태 생성 완료")
    print(f"   상태 벡터: {state.state_vector}")
    
    # 3. episodes 추가 (WellFormationEngine용)
    # 실제로는 WellFormationEngine의 generate_well() 메서드에 전달할 episodes 데이터
    print("\n3. episodes 데이터 추가 중...")
    episodes = [
        # 예시 episodes 데이터
        # 실제로는 WellFormationEngine이 요구하는 형식으로 제공해야 함
    ]
    state.set_extension("episodes", episodes)
    print("✅ episodes 데이터 추가 완료")
    
    # 4. 통합 엔진 실행
    print("\n4. 통합 엔진 실행 중...")
    try:
        result = brain.update(state)
        print("✅ 통합 엔진 실행 완료")
        
        # 5. 결과 확인
        print("\n5. 결과 확인:")
        print(f"   상태 벡터: {result.state_vector}")
        print(f"   에너지: {result.energy}")
        
        # Extensions 확인
        if result.has_extension("well_formation"):
            well_data = result.get_extension("well_formation")
            print(f"   WellFormationEngine 결과: W shape = {well_data['W'].shape if 'W' in well_data else 'N/A'}")
        
        if result.has_extension("potential_field"):
            potential_data = result.get_extension("potential_field")
            print(f"   PotentialFieldEngine 결과: potential = {potential_data.get('potential', 'N/A')}")
        
        # 에너지 확인
        energy = brain.get_energy(result)
        print(f"   에너지 (get_energy): {energy}")
        
        # 엔진 상태 확인
        engine_state = brain.get_state()
        print(f"\n6. 엔진 상태:")
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

