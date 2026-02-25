"""solar/em/ — 전자기 레이어 (자기장 + 태양풍 + 자기권)
====================================================

이 레이어는 core/만 참조한다.
cognitive/를 참조하지 않는다. data/를 직접 참조하지 않는다.
의존: numpy + solar.core (Body3D의 spin_axis, pos 등)

Phase 2: magnetic_dipole  — 자기쌍극자장 B(x,t)
Phase 3: solar_wind       — 태양풍 동압 + 복사압 (1/r²)
Phase 4: magnetosphere    — dipole vs P_sw 균형 → 자기권 경계
"""

from .magnetic_dipole import MagneticDipole, DipoleFieldPoint
from .solar_wind import SolarWind, SolarWindState
from .magnetosphere import Magnetosphere, MagnetosphereState

__all__ = [
    "MagneticDipole",
    "DipoleFieldPoint",
    "SolarWind",
    "SolarWindState",
    "Magnetosphere",
    "MagnetosphereState",
]
