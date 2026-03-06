"""Phase B: 공전 (Orbit)

다중 우물 사이의 상태 순환 — 기억 간 전이.

Phase A(자전)가 우물 내부에 리듬을 만들었다면,
Phase B(공전)는 우물 사이를 주기적으로 순환하는 궤도를 만든다.

구조:
  삼각형 배치된 3개 우물 + 코리올리 자전(ωJv)
  → 상태가 한 방향으로 우물들을 순환 (공전)

조건:
  V(x) = -Σᵢ Aᵢ exp(-||x - cᵢ||² / (2σᵢ²))
  E > V_saddle → 장벽 통과 → 순환 가능
  ωJv → 순환 방향 생성

Modules:
- multi_well_potential: 가우시안 합성 다중 우물 퍼텐셜
- well_to_gaussian: WellFormation → Gaussian 브릿지 (변환 + 누적 저장소)
"""

from .multi_well_potential import (
    GaussianWell,
    MultiWellPotential,
    create_symmetric_wells,
)

from .well_to_gaussian import (
    WellToGaussianConfig,
    WellRegistry,
    well_result_to_gaussian,
    compute_center,
    compute_amplitude,
    compute_sigma,
)

__all__ = [
    "GaussianWell",
    "MultiWellPotential",
    "create_symmetric_wells",
    "WellToGaussianConfig",
    "WellRegistry",
    "well_result_to_gaussian",
    "compute_center",
    "compute_amplitude",
    "compute_sigma",
]

__version__ = "0.3.0-dev"
