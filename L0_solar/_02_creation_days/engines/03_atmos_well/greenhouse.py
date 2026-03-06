"""Greenhouse — infrared optical depth and radiative transfer.

1-layer radiative model:

  Atmosphere absorbs fraction ε_a of outgoing longwave IR,
  re-emits equally upward (to space) and downward (to surface).

  ε_a = 1 - exp(-τ_IR)

  τ_IR = optical depth from atmospheric composition:
    CO₂: logarithmic (saturation at high concentration)
    H₂O: square-root (pressure/self-broadening)
    CH₄: square-root

  Equilibrium surface temperature:
    T_s = [F·(1-A) / (f·σ·(1 - ε_a/2))]^(1/4)

    ε_a=0 → T_s = T_eq (bare rock)
    ε_a>0 → T_s > T_eq (greenhouse warming)

  Calibration (current Earth):
    CO₂=400ppm, H₂O=1%, CH₄=1.8ppm
    → τ=1.56, ε_a=0.79, T_s=288K (F=1361, A=0.306, f=4)

Units: SI (K, W/m², Pa)
"""

import numpy as np
from dataclasses import dataclass
from typing import Optional

from ._constants import SIGMA_SB, EPS


@dataclass
class GreenhouseParams:
    """Radiative coefficients for greenhouse gas → τ mapping.

    Default values calibrated so:
      Current Earth (CO₂=400ppm, H₂O=1%, CH₄=1.8ppm) → τ≈1.56
      Pre-industrial (CO₂=280ppm, CH₄=0.7ppm) → τ≈1.44
    """
    alpha_CO2: float = 0.462
    CO2_ref: float = 280e-6       # pre-industrial [mol/mol]

    alpha_H2O: float = 0.940
    H2O_ref: float = 0.01

    alpha_CH4: float = 0.056
    CH4_ref: float = 0.7e-6       # pre-industrial [mol/mol]

    tau_base: float = 0.12        # N₂O, O₃, minor gases


def optical_depth(
    CO2: float = 400e-6,
    H2O: float = 0.01,
    CH4: float = 1.8e-6,
    params: Optional[GreenhouseParams] = None,
) -> float:
    """Infrared optical depth from atmospheric composition.

    τ = τ_base
        + α_CO₂ · ln(1 + CO₂/ref)     — logarithmic (saturation)
        + α_H₂O · √(H₂O/ref)          — square-root (self-broadening)
        + α_CH₄ · √(CH₄/ref)           — square-root

    Parameters
    ----------
    CO2, H2O, CH4 : float
        Volume mixing ratios [mol/mol]. CO₂ 400 ppm = 400e-6.
    params : GreenhouseParams or None
        Radiative coefficients. None → Earth-calibrated defaults.
    """
    if params is None:
        params = GreenhouseParams()

    tau = params.tau_base

    if CO2 > EPS:
        tau += params.alpha_CO2 * np.log(1.0 + CO2 / (params.CO2_ref + EPS))

    if H2O > EPS:
        tau += params.alpha_H2O * np.sqrt(H2O / (params.H2O_ref + EPS))

    if CH4 > EPS:
        tau += params.alpha_CH4 * np.sqrt(CH4 / (params.CH4_ref + EPS))

    return max(tau, 0.0)


def effective_emissivity(tau: float) -> float:
    """Atmospheric longwave emissivity from optical depth.

    ε_a = 1 - exp(-τ)

    τ=0 → ε_a=0 (transparent, no greenhouse)
    τ→∞ → ε_a→1 (opaque)
    """
    return 1.0 - np.exp(-max(tau, 0.0))


def equilibrium_surface_temp(
    F_solar_si: float,
    albedo: float = 0.306,
    redistribution: float = 4.0,
    emissivity_atm: float = 0.0,
) -> float:
    """Equilibrium surface temperature (1-layer greenhouse).

    T_s = [F·(1-A) / (f·σ·(1 - ε_a/2))]^(1/4)

    Parameters
    ----------
    F_solar_si : float
        Incoming stellar flux at planet distance [W/m²].
    albedo : float
        Bond albedo (0–1).
    redistribution : float
        Heat redistribution factor. 4.0 = uniform sphere.
    emissivity_atm : float
        Effective atmospheric longwave emissivity ε_a (0–1).
        0 = no atmosphere → returns bare T_eq.
    """
    absorbed = F_solar_si * (1.0 - albedo)
    denom_factor = max(1.0 - emissivity_atm / 2.0, EPS)
    denom = redistribution * SIGMA_SB * denom_factor
    if denom < EPS:
        return 0.0
    return (absorbed / denom) ** 0.25


def bare_equilibrium_temp(
    F_solar_si: float,
    albedo: float = 0.306,
    redistribution: float = 4.0,
) -> float:
    """Bare equilibrium temperature (no atmosphere).

    T_eq = [F·(1-A) / (f·σ)]^(1/4)
    """
    return equilibrium_surface_temp(F_solar_si, albedo, redistribution, 0.0)
