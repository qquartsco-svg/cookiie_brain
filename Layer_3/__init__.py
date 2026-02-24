"""Layer 3: 게이지/기하학 (Gauge / Geometry)

Layer 2(다체) 위에 쌓이는 세 번째 가지.
균일 회전 Ω = ωJ → 위치 의존 반대칭 연산자 Ω(x)로 확장한다.

게이지 ≠ 보존력:
  - 퍼텐셜에서 유도되지 않는다 (G ≠ −∇V)
  - 반대칭 연산자: Ω(x)ᵀ = −Ω(x), v·Ω(x)v = 0
  - Hamiltonian의 symplectic 구조 내 회전 항 (geometric phase term)

구성:
  gauge.py : GaugeForce, NBodyGaugeForce, GeometryAnalyzer
             + 편의 함수 (uniform_field, gaussian_field, ...)
"""

from .gauge import (
    GaugeForce,
    NBodyGaugeForce,
    GeometryAnalyzer,
    MagneticForce,
    NBodyMagneticForce,
    uniform_field,
    gaussian_field,
    dipole_field,
    multi_well_field,
)

__all__ = [
    "GaugeForce",
    "NBodyGaugeForce",
    "GeometryAnalyzer",
    "MagneticForce",
    "NBodyMagneticForce",
    "uniform_field",
    "gaussian_field",
    "dipole_field",
    "multi_well_field",
]
