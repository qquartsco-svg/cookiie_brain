"""혜성/소행성 충돌 파라미터 → 행성 환경 델타 오더 추정.

이 모듈은 CookiieBrain·solar에 의존하지 않는 독립 코어다.
충돌체 직경·밀도·속도·입사각·수심·위치를 받아
총/유효 운동에너지, 대기/해수/지각 분배, 그리고
대기·수권·극-적도 온도차에 대한 델타를 오더 수준으로 추정한다.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import pi, radians, sin


@dataclass
class ImpactParams:
    """충돌체 파라미터.

    단위:
      - D_km      : 직경 [km]
      - rho_gcm3  : 밀도 [g/cm³]
      - v_kms     : 속도 [km/s]
      - theta_deg : 입사각 [deg] (0=수평, 90=수직)
      - h_km      : 충돌점 해수 깊이 [km]
      - lat_deg   : 위도
      - lon_deg   : 경도
    """

    D_km: float
    rho_gcm3: float
    v_kms: float
    theta_deg: float
    h_km: float
    lat_deg: float
    lon_deg: float


@dataclass
class ImpactResult:
    """충돌 에너지 및 행성 환경 델타 추정."""

    E_total_J: float
    E_eff_J: float
    f_atm: float
    f_ocean: float
    f_crust: float
    delta_H2O_canopy: float
    delta_pressure_atm: float
    delta_sea_level_m: float
    delta_pole_eq_delta_K: float
    shock_strength: float  # [0,1] 정규화 충격 강도


# 지구 물리 상수 (대략값, 다른 행성으로 확장 시 교체 가능)
R_EARTH_M = 6_371_000.0
AREA_EARTH_M2 = 4.0 * pi * R_EARTH_M**2


def _impact_energy(params: ImpactParams) -> tuple[float, float]:
    """충돌체의 총 운동에너지와 유효 에너지(J)."""
    D_m = params.D_km * 1_000.0
    rho_kgm3 = params.rho_gcm3 * 1_000.0
    v_ms = params.v_kms * 1_000.0

    volume_m3 = (pi / 6.0) * D_m**3
    m_kg = volume_m3 * rho_kgm3
    E_total = 0.5 * m_kg * v_ms**2

    theta_rad = radians(max(0.0, min(90.0, params.theta_deg)))
    E_eff = E_total * sin(theta_rad)
    return E_total, E_eff


def estimate_impact(params: ImpactParams) -> ImpactResult:
    """충돌 파라미터 → 행성 환경 델타 추정."""
    E_total, E_eff = _impact_energy(params)

    h = max(0.0, params.h_km)
    depth_factor = min(h / 5.0, 1.0)
    f_ocean = 0.3 + 0.4 * depth_factor
    f_crust = 0.4 - 0.2 * depth_factor
    f_atm = 1.0 - f_ocean - f_crust

    E_per_m2 = E_eff / AREA_EARTH_M2
    CHICXULUB_EFF_PER_M2 = 1.0e8
    scale = min(1.0, E_per_m2 / CHICXULUB_EFF_PER_M2)

    delta_H2O_canopy = -0.05 * scale
    delta_pressure_atm = -0.25 * scale
    delta_sea_level_m = 80.0 * scale
    delta_pole_eq_delta_K = 30.0 * scale
    shock_strength = max(0.0, min(1.0, scale))

    return ImpactResult(
        E_total_J=E_total,
        E_eff_J=E_eff,
        f_atm=f_atm,
        f_ocean=f_ocean,
        f_crust=f_crust,
        delta_H2O_canopy=delta_H2O_canopy,
        delta_pressure_atm=delta_pressure_atm,
        delta_sea_level_m=delta_sea_level_m,
        delta_pole_eq_delta_K=delta_pole_eq_delta_K,
        shock_strength=shock_strength,
    )


__all__ = [
    "ImpactParams",
    "ImpactResult",
    "estimate_impact",
]
