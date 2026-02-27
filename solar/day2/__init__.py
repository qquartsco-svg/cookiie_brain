"""day2/ — 둘째날 레이어 집합 (궁창 / 대기권)

개념:
    둘째날은 "궁창" — 바다와 하늘이 PT(압력-온도) 공간에서
    분리되는 단계. 구현은 `solar/atmosphere/` 레이어에 있고,
    여기서는 그 핵심 기어들을 둘째날 관점에서 한 곳에 모아 보여준다.

포함 모듈:
    - AtmosphereColumn, AtmosphereState, AtmosphereComposition
    - GreenhouseParams (온실 파라미터)

참고 문서:
    - solar/atmosphere/README.md
    - docs/CREATION_DAYS_AND_PHASES.md (둘째날 정리)
"""

from __future__ import annotations

from ..atmosphere import (
    AtmosphereColumn,
    AtmosphereState,
    AtmosphereComposition,
    GreenhouseParams,
)

__all__ = [
    "AtmosphereColumn",
    "AtmosphereState",
    "AtmosphereComposition",
    "GreenhouseParams",
]

__version__ = "1.0.0"

