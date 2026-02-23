"""Phase B: 공전 (Orbit)

다중 우물 사이의 상태 전이 — 기억 간 순환.

Phase A(자전)가 우물 내부에 리듬을 만들었다면,
Phase B(공전)는 우물 사이를 넘나드는 전이를 만든다.

핵심 구조:
  V(x) = -Σᵢ Aᵢ exp(-||x - cᵢ||² / (2σᵢ²))
  E > V_saddle → 전이 가능

Modules:
- multi_well_potential: 가우시안 합성 다중 우물 퍼텐셜
"""

from .multi_well_potential import (
    GaussianWell,
    MultiWellPotential,
    create_symmetric_wells,
)

__all__ = [
    "GaussianWell",
    "MultiWellPotential",
    "create_symmetric_wells",
]

__version__ = "0.3.0-dev"
