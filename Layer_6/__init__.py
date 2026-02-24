"""Layer 6: 정보 기하학 + 기하학적 위상 (Information Geometry)

매개변수 공간의 기하학적 구조를 Fisher 정보 계량으로 분석한다.
Layer 3(물리 공간 게이지)의 매개변수 공간 확장.

핵심:
  - Fisher 계량: g_μν = (1/T²) Cov(∂_μV, ∂_νV)
  - 가우스 곡률: K (비자명, 매개변수 공간의 내재적 기하)
  - 측지선 거리: 분포 변화의 통계적 거리

1D 고전계에서 naive Berry phase = 0인 이유:
  A = ∇_λ⟨x⟩ → curl(∇f) = 0 (항상)
Fisher 계량은 이와 독립적으로 비자명한 기하학을 제공한다.
"""

from .geometric_phase import (
    ParameterSpace,
    FisherMetricCalculator,
    tilted_double_well,
    circular_path,
)

__all__ = [
    "ParameterSpace",
    "FisherMetricCalculator",
    "tilted_double_well",
    "circular_path",
]
