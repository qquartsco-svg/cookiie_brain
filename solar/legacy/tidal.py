"""하위 호환 re-export.

새 코드에서는 'from solar import CentralBody, ...'를 사용하세요.
OceanSimulator는 analysis/ocean_simulator.py로 이동됨.
"""
from .central_body import CentralBody
from .orbital_moon import OrbitalMoon
from .tidal_field import TidalField

__all__ = ["CentralBody", "OrbitalMoon", "TidalField"]
