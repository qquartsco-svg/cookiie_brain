"""행성 탐사 한 스텝 실행 — joe.run(ic, water_snapshot)."""
from __future__ import annotations

from typing import Any, Optional, Tuple

from .observer import compute_planet_stress_and_instability


def run(ic: Any, water_snapshot: Optional[dict] = None) -> Tuple[float, float]:
    """1일 이전 거시 탐색. (planet_stress, instability) 반환."""
    return compute_planet_stress_and_instability(ic, water_snapshot=water_snapshot)


__all__ = ["run"]
