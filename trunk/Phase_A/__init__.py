"""Phase A: 위상 생성 (Rotational Field)

회전 성분을 생성하여 순환 운동(자전)을 가능하게 만듭니다.

Modules:
- rotational_field: Rotational field 생성 (ωJv 코리올리)
- moon: 달/위성 중력장 (정적, 레거시)
- tidal: solar/ 모듈의 re-export (하위 호환)

3계층 중력 실제 구현: solar/ 모듈 (CentralBody, OrbitalMoon, TidalField, OceanSimulator)
"""

from .rotational_field import (
    create_skew_symmetric_matrix,
    Pole,
    create_minimal_rotational_field,
    create_rotational_field,
    create_combined_field,
    compute_curl_2d,
    verify_rotational_component,
)

from .moon import (
    Moon,
    create_moon_gravity_field,
    create_field_with_moon,
    analyze_moon_effect,
)

from .tidal import (
    CentralBody,
    OrbitalMoon,
    TidalField,
    OceanSimulator,
)

__all__ = [
    # Rotational field
    "create_skew_symmetric_matrix",
    "Pole",
    "create_minimal_rotational_field",
    "create_rotational_field",
    "create_combined_field",
    "compute_curl_2d",
    "verify_rotational_component",
    # Moon (static)
    "Moon",
    "create_moon_gravity_field",
    "create_field_with_moon",
    "analyze_moon_effect",
    # Tidal dynamics (v0.7.0)
    "CentralBody",
    "OrbitalMoon",
    "TidalField",
    "OceanSimulator",
]

__version__ = "0.7.1"
