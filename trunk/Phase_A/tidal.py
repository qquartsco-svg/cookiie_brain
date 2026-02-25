"""하위 호환 re-export — 실제 구현은 solar/tidal.py로 이동"""
from solar.tidal import CentralBody, OrbitalMoon, TidalField, OceanSimulator

__all__ = ["CentralBody", "OrbitalMoon", "TidalField", "OceanSimulator"]
