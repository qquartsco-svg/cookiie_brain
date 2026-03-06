"""Phase A: 자전 (Rotational Field)

ωJv 코리올리 회전 — 속도에 수직인 힘으로 에너지 보존하면서 방향을 꺾는다.
이것만 한다. 태양/달/조석은 solar/ 모듈 담당.
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

__all__ = [
    "create_skew_symmetric_matrix",
    "Pole",
    "create_minimal_rotational_field",
    "create_rotational_field",
    "create_combined_field",
    "compute_curl_2d",
    "verify_rotational_component",
    "Moon",
    "create_moon_gravity_field",
    "create_field_with_moon",
    "analyze_moon_effect",
]

__version__ = "0.7.1"
