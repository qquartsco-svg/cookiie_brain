"""solar/cognitive/ — 인지 레이어 (관성 기억 + 커플링)
====================================================

이 레이어는 core/만 참조한다. em/을 참조하지 않는다.
의존: numpy + solar.core
"""

from .ring_attractor import RingAttractorEngine, RingState
from .spin_ring_coupling import SpinRingCoupling, CouplingState

__all__ = [
    "RingAttractorEngine",
    "RingState",
    "SpinRingCoupling",
    "CouplingState",
]
