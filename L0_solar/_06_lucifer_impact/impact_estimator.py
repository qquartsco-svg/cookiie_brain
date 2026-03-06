from __future__ import annotations

"""impact_estimator — 혜성/소행성 충돌 에너지 → 환경 델타 추정기.

이 모듈은 **루시퍼 임팩트 레이어(_06_lucifer_impact)** 의 코어로,

    - 충돌체 파라미터(D, ρ, v, θ, h, 위치)를 받아
    - 전지구 평균 에너지 밀도(J/m²)를 추정하고
    - 궁창 캐노피, 대기압, 해수면, 극-적도 온도차에 대한
      오더 수준의 델타를 계산한다.

노아 플러드 레이어(`_05_noah_flood`)는 이 모듈을 읽어
effective_instability spike 및 postdiluvian IC 보정을 걸 수 있다.
"""

from dataclasses import dataclass
from math import pi, sin, radians


@dataclass
class ImpactParams:
    """충돌체 파라미터.

    단위:
      - D_km      : 직경 [km]
      - rho_gcm3  : 밀도 [g/cm³]
      - v_kms     : 속도 [km/s]
      - theta_deg : 입사각 [deg] (0=수평, 90=수직)
      - h_km      : 해수 깊이 [km]
      - lat_deg   : 위도 (에덴 좌표계)
      - lon_deg   : 경도 (에덴 좌표계)
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
    """충돌 에너지 및 환경 델타 추정."""

    E_total_J: float
    E_eff_J: float
    f_atm: float
    f_ocean: float
    f_crust: float
    delta_H2O_canopy: float
    delta_pressure_atm: float
    delta_sea_level_m: float
    delta_pole_eq_delta_K: float
    shock_strength: float  # 0~1, effective_instability spike 용


# 지구 물리 상수 (대략값)
R_EARTH_M = 6_371_000.0
AREA_EARTH_M2 = 4.0 * pi * R_EARTH_M**2


def _impact_energy(params: ImpactParams) -> tuple[float, float]:
    """충돌체의 총 운동에너지와 유효 에너지(J)를 계산."""

    D_m = params.D_km * 1_000.0
    rho_kgm3 = params.rho_gcm3 * 1_000.0  # 1 g/cm³ = 1000 kg/m³
    v_ms = params.v_kms * 1_000.0

    volume_m3 = (pi / 6.0) * D_m**3
    m_kg = volume_m3 * rho_kgm3
    E_total = 0.5 * m_kg * v_ms**2

    # 입사각에 따른 유효 에너지 (수직일수록 효율↑)
    theta_rad = radians(max(0.0, min(90.0, params.theta_deg)))
    E_eff = E_total * sin(theta_rad)
    return E_total, E_eff


def estimate_impact(params: ImpactParams) -> ImpactResult:
    """충돌 파라미터 → 행성 환경 델타 추정."""

    E_total, E_eff = _impact_energy(params)

    # 에너지 분배 비율 (단순 모델):
    #   - 깊은 바다일수록 해수/수증기 비중↑, 지각 비중↓.
    h = max(0.0, params.h_km)
    depth_factor = min(h / 5.0, 1.0)  # 0~1, 5km 이상이면 깊은 바다 취급
    f_ocean = 0.3 + 0.4 * depth_factor
    f_crust = 0.4 - 0.2 * depth_factor
    f_atm = 1.0 - f_ocean - f_crust

    # 전지구 평균 에너지 밀도 [J/m²]
    E_per_m2 = E_eff / AREA_EARTH_M2

    # 기준 스케일: 대략 Chicxulub 급(10km rock, 20km/s) 충돌을 1.0으로 정규화.
    # 이 스케일에서 canopy 완전 붕괴 + pressure 1.25→1.0 전환이 가능하다고 가정.
    CHICXULUB_EFF_PER_M2 = 1.0e8  # 대략적 오더 [J/m²]
    scale = min(1.0, E_per_m2 / CHICXULUB_EFF_PER_M2)

    # 궁창 캐노피/압력 델타 추정.
    delta_H2O_canopy = -0.05 * scale
    delta_pressure_atm = -0.25 * scale

    # 해수면 델타 (짧은 시간 스케일에서의 global 평균 수위 편차)
    delta_sea_level_m = 80.0 * scale

    # 극-적도 온도차 변화 (에덴→현재 지구 수준으로 가는 스케일).
    delta_pole_eq_delta_K = 30.0 * scale

    # shock_strength: effective_instability spike 에 쓸 0~1 값.
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

