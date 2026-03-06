"""DEPRECATED — solar/ 모듈로 이동됨.

새 코드에서는 solar/를 직접 import하세요:
  from L0_solar import CentralBody, OrbitalMoon, TidalField
  from L4_analysis.ocean_simulator import OceanSimulator
"""
import warnings as _w
_w.warn(
    "trunk.Phase_A.tidal은 deprecated. 'from L0_solar import ...'를 사용하세요.",
    DeprecationWarning,
    stacklevel=2,
)
from L0_solar import CentralBody, OrbitalMoon, TidalField  # noqa

__all__ = ["CentralBody", "OrbitalMoon", "TidalField"]
