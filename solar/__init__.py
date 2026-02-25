"""solar/ — L2 Field: 3계층 중력장

태양(1/r) + 달(조석) → 상태 공간에 작용하는 힘을 정의한다.
우물(지구)은 trunk/Phase_B에서 정의.

파일:
  central_body.py  → CentralBody   (태양: 1/r 장거리 중력)
  orbital_moon.py  → OrbitalMoon   (달: 공전+자전+조석력)
  tidal_field.py   → TidalField    (합성기: 태양+달 힘 합산)

OceanSimulator는 L4(Analysis)로 이동: analysis/ocean_simulator.py
"""

from .central_body import CentralBody
from .orbital_moon import OrbitalMoon
from .tidal_field import TidalField

__all__ = [
    "CentralBody",
    "OrbitalMoon",
    "TidalField",
]

__version__ = "0.7.2"
