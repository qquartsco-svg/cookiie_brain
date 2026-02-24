"""Layer 2: 다체/장론 (Many-body / Field Theory)

Layer 1(통계역학 토양) 위에 쌓이는 두 번째 가지.
단일 입자 → N 입자로 확장한다.

trunk(줄기)의 state_vector를 [x₁...xₙ, v₁...vₙ] 로 키우고,
N-body 전용 레이어를 꽂는다.

구성:
  - nbody.py : NBodyState, InteractionForce, ExternalForce, NBodyGauge
"""

from .nbody import (
    NBodyState,
    InteractionForce,
    ExternalForce,
    NBodyGauge,
)
