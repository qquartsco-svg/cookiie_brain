"""Layer 3: 게이지/기하학 (Gauge / Geometry)

Layer 2(다체) 위에 쌓이는 세 번째 가지.
균일 회전 → 위치 의존 회전(자기장형 힘)으로 확장한다.

구성:
  - gauge.py : MagneticForce, NBodyMagneticForce, GeometryAnalyzer
"""

from .gauge import (
    MagneticForce,
    NBodyMagneticForce,
    GeometryAnalyzer,
)
