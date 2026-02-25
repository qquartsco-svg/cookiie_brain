"""solar/core/ — 물리 코어 (N-body + 스핀-궤도 + 해양)
====================================================

이 레이어는 절대 상위 레이어(cognitive/, em/)를 import하지 않는다.
의존: numpy만.
"""

from .evolution_engine import EvolutionEngine, Body3D, SurfaceOcean
from .central_body import CentralBody
from .orbital_moon import OrbitalMoon
from .tidal_field import TidalField

__all__ = [
    "EvolutionEngine",
    "Body3D",
    "SurfaceOcean",
    "CentralBody",
    "OrbitalMoon",
    "TidalField",
]
