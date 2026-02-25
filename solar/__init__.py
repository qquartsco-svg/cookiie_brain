"""Solar — 3계층 중력 동역학 모듈

태양(CentralBody) + 달(OrbitalMoon) + 합성(TidalField) + 바다(OceanSimulator)

상태 공간의 거대질량 코어.
CookiieBrainEngine의 enable_tidal=True로 활성화하면
매 update() 스텝마다 태양+달 힘이 상태 벡터에 작용한다.

Version: 0.7.1
"""

from .tidal import CentralBody, OrbitalMoon, TidalField, OceanSimulator

__all__ = [
    "CentralBody",
    "OrbitalMoon",
    "TidalField",
    "OceanSimulator",
]

__version__ = "0.7.1"
