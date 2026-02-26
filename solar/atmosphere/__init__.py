"""solar/atmosphere/ — 대기권 환경 레이어 (궁창 / Firmament)
=========================================================

Phase 6: 바다(SurfaceOcean)와 하늘의 분리.

에너지 입력(solar_luminosity)과 자기권 차폐(magnetosphere) 위에
대기 열역학 레이어를 얹어 표면 온도·압력·물 상태를 결정한다.

Phase 6a: 온실 효과 + 대기압 + 열적 관성 (thermal inertia)

의존: numpy + solar.em (solar_luminosity)
이 레이어는 core/를 수정하지 않는다. 관측자 모드.
"""

from .column import AtmosphereColumn, AtmosphereState, AtmosphereComposition
from .greenhouse import (
    optical_depth,
    effective_emissivity,
    equilibrium_surface_temp,
    bare_equilibrium_temp,
    GreenhouseParams,
)

__all__ = [
    "AtmosphereColumn",
    "AtmosphereState",
    "AtmosphereComposition",
    "optical_depth",
    "effective_emissivity",
    "equilibrium_surface_temp",
    "bare_equilibrium_temp",
    "GreenhouseParams",
]
