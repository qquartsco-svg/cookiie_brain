"""Water Cycle — 증발, 응결, 잠열, Clausius-Clapeyron (Phase 6b)

수순환(Water Cycle)의 물리 기반:
  - Clausius-Clapeyron: 포화 수증기압 e_sat(T)
  - 증발율 E ∝ (e_sat - e_actual) × wind_factor
  - 잠열 L_v ≈ 2.5×10⁶ J/kg (0°C 근방)

단위: SI (Pa, K, kg/m²/s, W/m²)
"""

import numpy as np
from typing import Optional

from ._constants import EPS, WATER_TRIPLE_T, WATER_TRIPLE_P


# 잠열 (latent heat of vaporization) [J/kg]
# T=273K: ~2.50e6, T=373K: ~2.26e6
L_V_REF = 2.501e6   # at 0°C
L_V_SLOPE = -2.37e3  # dL/dT [J/(kg·K)] approx
R_V = 461.5          # gas constant for water vapor [J/(kg·K)]


def latent_heat_vaporization(T_k: float) -> float:
    """Latent heat of vaporization L_v(T) [J/kg].
    L_v ≈ L_v0 + slope*(T - 273)
    """
    return max(L_V_REF + L_V_SLOPE * (T_k - 273.16), 1e6)


def saturation_vapor_pressure(T_k: float) -> float:
    """Clausius-Clapeyron: saturation vapor pressure e_sat(T) [Pa].

    Magnus formula (empirical, 0–50°C accurate):
    e_sat = 611.2 × exp(17.67 × (T-273.15)/(T-29.65))

    Or Bolton (1980): e_sat = 611.2 exp(17.67(T-273.15)/(T-29.65))
    """
    if T_k < 200:
        return 0.0
    T_c = T_k - 273.15
    return 611.2 * np.exp(17.67 * T_c / (T_c + 243.5))


def saturation_mixing_ratio(T_k: float, P_pa: float) -> float:
    """Saturation mass mixing ratio q_sat [kg/kg] ≈ 0.622 × e_sat/P.

    For mol/mol: w_sat ≈ e_sat/P (ideal gas, approximate).
    """
    if P_pa < EPS:
        return 0.0
    e_sat = saturation_vapor_pressure(T_k)
    return 0.622 * e_sat / P_pa  # kg_vapor / kg_air


def evaporation_rate(
    T_surface: float,
    P_surface: float,
    q_actual: float,
    wind_factor: float = 1.0,
    exchange_coeff: float = 1.2e-3,
    U_ref: float = 5.0,
) -> float:
    """Bulk evaporation rate E [kg/(m²·s)].

    E = C_E × ρ × U × (q_sat - q_actual)
    ρ ≈ P/(R_d T), q_sat = 0.622 × e_sat/P

    q_actual: current mass mixing ratio [kg/kg].
    wind_factor: 0–2, 1 = normal.
    """
    if T_surface < WATER_TRIPLE_T:
        return 0.0
    q_sat = saturation_mixing_ratio(T_surface, P_surface)
    deficit = max(q_sat - q_actual, 0.0)
    rho = P_surface / (287.0 * T_surface)
    return exchange_coeff * wind_factor * U_ref * rho * deficit


def latent_heat_flux(E_kg_ms2: float, T_k: float) -> float:
    """Latent heat flux Q_latent = L_v × E [W/m²].

    Positive = energy leaving surface (cooling).
    """
    return L_V_REF * E_kg_ms2  # use constant L_v for simplicity
