"""day1/ — 첫째날 레이어 집합 (빛이 있으라 / EM)

개념:
    첫째날은 "빛이 있으라" — 태양 광도와 복사 환경이 켜지는 단계.
    구현은 `solar/em/` 레이어에 있고, 여기서는 그 핵심 기어들을
    한 곳에서 import/export 하여 Day 1 뷰를 제공한다.

포함 모듈:
    - solar_luminosity: 태양 광도 L=M^α, 복사 조도 F(r), 평형 온도
    - magnetic_dipole: 자기쌍극자장 B ∝ 1/r³
    - solar_wind: 태양풍 동압·플럭스·IMF (1/r²)
    - magnetosphere: 자기권 경계 r_mp, 차폐율

참고 문서:
    - solar/em/README.md
    - docs/CREATION_DAYS_AND_PHASES.md (첫째날 정리)
"""

from __future__ import annotations

from ..em import (
    SolarLuminosity,
    IrradianceState,
    MagneticDipole,
    DipoleFieldPoint,
    SolarWind,
    SolarWindState,
    Magnetosphere,
    MagnetosphereState,
)

__all__ = [
    "SolarLuminosity",
    "IrradianceState",
    "MagneticDipole",
    "DipoleFieldPoint",
    "SolarWind",
    "SolarWindState",
    "Magnetosphere",
    "MagnetosphereState",
]

__version__ = "1.0.0"

