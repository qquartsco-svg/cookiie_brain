"""solar/ — L2 Field: 중력장 + 3D 진화 엔진 + 관성 기억
=======================================================

태양(1/r) + 달(조석) → 상태 공간에 작용하는 힘을 정의한다.
우물(지구)은 trunk/Phase_B에서 정의.

파일:
  central_body.py      → CentralBody       (태양: 1/r 장거리 중력)
  orbital_moon.py      → OrbitalMoon       (달: 공전+자전+조석력)
  tidal_field.py       → TidalField        (합성기: 태양+달 힘 합산)
  evolution_engine.py  → EvolutionEngine   (3D N-body + 세차 + 해양)
  ring_attractor.py    → RingAttractorEngine (관성 기억: 위상 보존)
  spin_ring_coupling.py→ SpinRingCoupling  (물리↔인지 필드 연결)

OceanSimulator는 L4(Analysis)로 이동: analysis/ocean_simulator.py
"""

from .central_body import CentralBody
from .orbital_moon import OrbitalMoon
from .tidal_field import TidalField
from .evolution_engine import EvolutionEngine, Body3D, SurfaceOcean
from .ring_attractor import RingAttractorEngine, RingState
from .spin_ring_coupling import SpinRingCoupling, CouplingState

__all__ = [
    "CentralBody",
    "OrbitalMoon",
    "TidalField",
    "EvolutionEngine",
    "Body3D",
    "SurfaceOcean",
    "RingAttractorEngine",
    "RingState",
    "SpinRingCoupling",
    "CouplingState",
]

__version__ = "0.9.0"
