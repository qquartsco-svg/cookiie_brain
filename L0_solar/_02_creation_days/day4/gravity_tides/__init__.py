"""gravity_tides/ — 중력-조석 주기 (넷째날 순환 3)

조석력 → 해양 혼합 → 영양염 upwelling → 식물플랑크톤 → 탄소 격리

설계 원칙:
  - TidalField: 달+태양 조석력 → 혼합 깊이 → 영양염 flux
  - OceanNutrients: 표층 영양염 + 식물플랑크톤 동역학 → 탄소 수출
  - CO2 격리 → GaiaLoopConnector.Loop A와 반대 방향 (음의 피드백)

구현 완료:
  tidal_mixing.py    — 달+태양 조석력, 혼합 깊이, 영양염 upwelling
  ocean_nutrients.py — 식물플랑크톤 동역학, 생물학적 탄소 펌프

구현 예정:
  carbon_pump.py     — 심층 탄소 격리 + 대기 CO₂ 피드백 완성
"""

from .tidal_mixing import (
    TidalField,
    TidalState,
    make_tidal_field,
    F_MOON_REF,
    K_MIX,
    K_UPWELLING,
)

from .ocean_nutrients import (
    OceanNutrients,
    OceanState,
    make_ocean_nutrients,
    K_PHYTO_GROWTH,
    K_EXPORT,
    CO2_PPM_PER_GT_CO2,
)

__all__ = [
    # tidal_mixing
    "TidalField",
    "TidalState",
    "make_tidal_field",
    "F_MOON_REF",
    "K_MIX",
    "K_UPWELLING",
    # ocean_nutrients
    "OceanNutrients",
    "OceanState",
    "make_ocean_nutrients",
    "K_PHYTO_GROWTH",
    "K_EXPORT",
    "CO2_PPM_PER_GT_CO2",
]

__version__ = "1.0.0"
