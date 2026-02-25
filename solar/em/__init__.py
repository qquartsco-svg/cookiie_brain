"""solar/em/ — 전자기 레이어 (자기장 + 태양풍 + 자기권)
====================================================

이 레이어는 core/만 참조한다.
cognitive/를 참조하지 않는다. data/를 직접 참조하지 않는다.
의존: numpy + solar.core (Body3D의 spin_axis, pos 등)
"""

from .magnetic_dipole import MagneticDipole, DipoleFieldPoint

__all__ = [
    "MagneticDipole",
    "DipoleFieldPoint",
]
