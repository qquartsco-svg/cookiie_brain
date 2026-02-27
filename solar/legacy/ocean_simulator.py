"""DEPRECATED — analysis/ocean_simulator.py 로 이동됨.

OceanSimulator는 시뮬레이션 도구이므로 L4(Analysis)에 배치.
from analysis.ocean_simulator import OceanSimulator 를 사용하세요.
"""
import warnings as _w
_w.warn(
    "solar.ocean_simulator는 deprecated. 'from analysis.ocean_simulator import OceanSimulator'를 사용하세요.",
    DeprecationWarning,
    stacklevel=2,
)
from analysis.ocean_simulator import OceanSimulator  # noqa: F401
__all__ = ["OceanSimulator"]
