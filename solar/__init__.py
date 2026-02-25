"""solar/ — 3계층 중력 동역학 모듈 (태양계 구조)

태양이 장을 만들고, 우물(지구)이 상태를 가두고, 달이 조석 리듬을 만든다.

구조:
  central_body.py    → CentralBody   (Tier 1: 태양, 1/r 중력)
  orbital_moon.py    → OrbitalMoon   (Tier 3: 달, 공전+자전+조석)
  tidal_field.py     → TidalField    (합성기: 태양+달 힘 합산)
  ocean_simulator.py → OceanSimulator (바다: 우물 안 유속 시뮬레이션)

Tier 2(우물/지구)는 hippo/memory_store.py + trunk/Phase_B가 담당.

Version: 0.7.1
"""

from .central_body import CentralBody
from .orbital_moon import OrbitalMoon
from .tidal_field import TidalField
from .ocean_simulator import OceanSimulator

__all__ = [
    "CentralBody",
    "OrbitalMoon",
    "TidalField",
    "OceanSimulator",
]

__version__ = "0.7.1"
