"""Phase A: 위상 생성 (Rotational Field)

회전 성분을 생성하여 순환 운동(자전)을 가능하게 만듭니다.

Modules:
- rotational_field: Rotational field 생성
- moon: 달/위성 중력장
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
    # Rotational field
    "create_skew_symmetric_matrix",
    "Pole",
    "create_minimal_rotational_field",
    "create_rotational_field",
    "create_combined_field",
    "compute_curl_2d",
    "verify_rotational_component",
    # Moon
    "Moon",
    "create_moon_gravity_field",
    "create_field_with_moon",
    "analyze_moon_effect",
]

__version__ = "0.2.0"
