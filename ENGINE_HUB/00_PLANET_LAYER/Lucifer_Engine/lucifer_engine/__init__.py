# Lucifer Engine — 혜성/소행성 충돌 예상·탐색 독립 엔진. CookiieBrain 무의존.

from __future__ import annotations

from .impact_estimator import ImpactParams, ImpactResult, estimate_impact

__version__ = "0.1.0"

__all__ = [
    "ImpactParams",
    "ImpactResult",
    "estimate_impact",
    "__version__",
]
