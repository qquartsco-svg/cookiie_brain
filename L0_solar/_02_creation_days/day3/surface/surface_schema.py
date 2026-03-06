"""SurfaceSchema — 땅과 바다 분리, 유효 알베도

Phase 7 / 셋째날: 땅이 드러남.

물리:
  A_eff = f_land * A_land + (1 - f_land) * A_ocean
  f_land: 대륙 비율 (지구 ≈ 0.29)
  A_land: 육지 평균 알베도 (~0.2–0.4)
  A_ocean: 해양 알베도 (~0.06–0.1)

단위: 무차원 [0, 1]
"""

from dataclasses import dataclass

# 기본값 (지구 근사)
A_LAND_DEFAULT = 0.30
A_OCEAN_DEFAULT = 0.08
F_LAND_EARTH = 0.29


@dataclass
class SurfaceSchema:
    """표면 타입별 알베도, 대륙 비율."""
    land_fraction: float = F_LAND_EARTH
    albedo_land: float = A_LAND_DEFAULT
    albedo_ocean: float = A_OCEAN_DEFAULT

    def effective_albedo(self) -> float:
        """유효 전지구 알베도 [0, 1]."""
        return (
            self.land_fraction * self.albedo_land
            + (1.0 - self.land_fraction) * self.albedo_ocean
        )


def effective_albedo(
    land_fraction: float = F_LAND_EARTH,
    albedo_land: float = A_LAND_DEFAULT,
    albedo_ocean: float = A_OCEAN_DEFAULT,
) -> float:
    """유효 알베도 계산."""
    return (
        land_fraction * albedo_land
        + (1.0 - land_fraction) * albedo_ocean
    )
