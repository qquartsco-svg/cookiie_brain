"""polar_ice.stefan_ice — 결빙 성장 역학 (Stefan's law)

해빙 두께 성장의 열역학적 모델.

Stefan's Law (1891):
  dh/dt = k_ice · (T_freeze - T_surface) / (ρ_ice · L_f · h)

  적분 해:
  h(t) = √(2 · k_ice · ΔT · t / (ρ_ice · L_f))
       = √(A · t)     여기서 A = 2·k·ΔT / (ρ·Lf)  [m²/s]

  → h는 시간의 제곱근으로 성장: 초기에 빠르고 점점 느려짐

추가 물리:
  - 적설 단열 효과: 눈이 쌓이면 열전도 저하 → 성장 느려짐
  - 담수 vs 해수 결빙 온도 차이
  - 역학적 두께 한계 (표류, 압력 능선)

참조:
  Stefan (1891), Ann. Phys., 278:269
  Maykut (1986), The Geophysics of Sea Ice, Ch. 2
"""

from __future__ import annotations

import numpy as np
from dataclasses import dataclass
from math import sqrt, exp
from typing import Optional


# ── 물리 상수 ─────────────────────────────────────────────────────────────────
K_ICE        = 2.1      # W/(m·K)   얼음 열전도도
K_SNOW       = 0.31     # W/(m·K)   적설 열전도도
RHO_ICE      = 917.0    # kg/m³     얼음 밀도
RHO_SNOW     = 300.0    # kg/m³     신설 밀도
L_FUSION     = 334000.0 # J/kg      융해 잠열
T_FREEZE_SW  = 271.35   # K         해수 결빙 온도 (-1.8°C)
T_FREEZE_FW  = 273.15   # K         담수 결빙 온도 (0°C)

# 현실적 두께 한계
H_MAX_FIRST_YEAR = 2.5  # m  1년차 최대 해빙 두께
H_MAX_MULTI_YEAR = 5.0  # m  다년빙 최대 두께


@dataclass
class IceState:
    """얼음층 상태."""
    t_days:       float   # 결빙 시작 후 경과 시간 [일]
    h_ice_m:      float   # 얼음 두께 [m]
    h_snow_m:     float   # 적설 두께 [m]
    T_surface_K:  float   # 표면 온도 [K]
    T_bottom_K:   float   # 얼음 하부(결빙면) 온도 [K]
    growth_rate:  float   # 순간 성장 속도 [m/day]
    is_growing:   bool    # 현재 성장 중 여부


def stefan_thickness(
    delta_T_K:   float,
    t_days:      float,
    snow_m:      float = 0.0,
) -> float:
    """Stefan 법칙 얼음 두께 계산.

    눈 적설 보정 포함:
    유효 열저항: R_eff = h_ice/k_ice + h_snow/k_snow
    Stefan 적분: h² = A·t  단, A = 2·k_eff·ΔT / (ρ_ice·L_f)

    Parameters
    ----------
    delta_T_K : T_freeze - T_surface  [K]  (양수여야 성장)
    t_days    : 결빙 시작 후 시간 [일]
    snow_m    : 적설 두께 [m]

    Returns
    -------
    h_ice [m]
    """
    if delta_T_K <= 0:
        return 0.0

    t_sec = t_days * 86400.0

    if snow_m <= 0:
        # 순수 Stefan
        A = 2.0 * K_ICE * delta_T_K / (RHO_ICE * L_FUSION)
        h = sqrt(A * t_sec)
    else:
        # 눈 단열 보정 (Maykut 1986)
        # h_ice·(h_ice/k_ice + h_snow/k_snow) = A₀·t
        # 이차방정식: h² + (k_ice·h_snow/k_snow)·h - k_ice·A₀·t/RHO = 0
        A0   = 2.0 * delta_T_K / (RHO_ICE * L_FUSION)
        b    = K_ICE * snow_m / K_SNOW
        disc = b**2 + 4.0 * K_ICE * A0 * t_sec
        h    = (-b + sqrt(disc)) / 2.0

    return min(h, H_MAX_MULTI_YEAR)


def ice_growth_rate(
    h_ice_m:     float,
    delta_T_K:   float,
    snow_m:      float = 0.0,
) -> float:
    """순간 결빙 성장 속도 dh/dt [m/day].

    dh/dt = k_eff · ΔT / (ρ_ice · L_f · h_total)
    h_total = h_ice + h_snow·(k_ice/k_snow)  [유효 두께]
    """
    if delta_T_K <= 0 or h_ice_m <= 0:
        return 0.0

    h_eff = h_ice_m + snow_m * (K_ICE / K_SNOW)
    dhdt  = K_ICE * delta_T_K / (RHO_ICE * L_FUSION * max(h_eff, 1e-6))
    return dhdt * 86400.0   # m/s → m/day


def snow_accumulation(
    H2O_canopy_kg_now: float,
    tau_decay_yr:      float = 1.0,
) -> float:
    """수증기 캐노피 현재값 → 순간 강설률 [m/yr].

    Fix: 이전 구현은 simulation 루프의 clim.H2O_canopy_kg (이미 지수 감쇠된 값)을
    받으면서 내부에서 또 (1 - exp(-t/τ)) 적분을 하여 이중 적산 오류 발생.

    수정: 현재 시각의 잔여 수증기 H2O_canopy_kg_now 로부터
          순간 강설 플럭스 [m/yr]를 반환. simulation.py 루프에서 dt_yr 를 곱해 누적.

    물리 모델:
      H2O_canopy_kg_now: 현재 대기 중 잉여 수증기 [kg]
      강설률 = H2O_canopy_now * f_polar / (A_polar * ρ_snow * τ_h2o)
               [kg ÷ (m² · kg/m³ · yr)] = [m/yr]

    Parameters
    ----------
    H2O_canopy_kg_now : 현재 잔여 수증기 [kg]  (clim.H2O_canopy_kg 직접 전달)
    tau_decay_yr      : 수증기 감쇠 시상수 [yr]

    Returns
    -------
    snow_rate [m/yr]  (시뮬레이션 루프에서 h_snow += snow_rate * dt_yr 로 누적)
    """
    POLAR_FRACTION = 0.05    # 전지구 수증기 중 극지방 분배 비율
    POLAR_AREA_M2  = 2.0e13  # 북극권 면적 [m²] (~북위 70° 이상)
    tau_s          = tau_decay_yr * 365.25 * 86400.0  # [s]

    # 순간 강설률: dH/dt = H2O_now / (τ · A_polar · ρ_snow) * f_polar
    snow_rate_m_s = (H2O_canopy_kg_now * POLAR_FRACTION
                     / (tau_s * POLAR_AREA_M2 * RHO_SNOW))
    return float(snow_rate_m_s * 365.25 * 86400.0)  # m/yr


def ice_state_at(
    t_days:       float,
    T_surface_K:  float,
    H2O_canopy_kg: float = 0.0,
    lat_deg:      float  = 85.0,
    t_freeze_K:   float  = T_FREEZE_SW,
) -> IceState:
    """시각 t_days에서의 얼음 상태 계산.

    Parameters
    ----------
    t_days       : 결빙 시작 후 경과 시간 [일]  (이미 T < T_freeze인 상태)
    T_surface_K  : 현재 표면 온도 [K]
    H2O_canopy_kg: 잔여 수증기 [kg]  (적설 계산용)
    lat_deg      : 위도 [°]
    t_freeze_K   : 결빙 온도 [K]
    """
    delta_T = t_freeze_K - T_surface_K   # 양수: 결빙 조건

    h_snow  = snow_accumulation(t_days, H2O_canopy_kg, lat_deg)
    h_ice   = stefan_thickness(delta_T, t_days, h_snow) if delta_T > 0 else 0.0
    dh_dt   = ice_growth_rate(h_ice, delta_T, h_snow)  if delta_T > 0 else 0.0

    return IceState(
        t_days=t_days,
        h_ice_m=h_ice,
        h_snow_m=h_snow,
        T_surface_K=T_surface_K,
        T_bottom_K=t_freeze_K,
        growth_rate=dh_dt,
        is_growing=delta_T > 0 and h_ice < H_MAX_MULTI_YEAR,
    )


__all__ = [
    "IceState",
    "stefan_thickness", "ice_growth_rate",
    "snow_accumulation", "ice_state_at",
    "K_ICE", "K_SNOW", "RHO_ICE", "L_FUSION",
    "T_FREEZE_SW", "T_FREEZE_FW",
]
