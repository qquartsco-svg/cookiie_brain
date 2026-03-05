# 루시퍼 임팩트 레이어 — 공개 API
#
# 독립 엔진(lucifer_engine)이 설치되어 있으면 해당 패키지를 사용하고,
# 없으면 이 패키지 내 impact_estimator를 사용한다.

from __future__ import annotations

try:
    from lucifer_engine import ImpactParams, ImpactResult, estimate_impact
except ImportError:
    from .impact_estimator import ImpactParams, ImpactResult, estimate_impact

__all__ = ["ImpactParams", "ImpactResult", "estimate_impact"]
