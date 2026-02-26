"""Pioneer biosphere — harsh-environment colonizers (lichen, moss, mycelium-like).

Grows under minimal conditions (broad T, some moisture), builds organic_layer.
No strong photosynthesis; NPP_pioneer is small and T/water limited only.
"""

import math
from ._constants import (
    T_MID_PIONEER,
    SIGMA_T_PIONEER,
    R_PIONEER,
    M_PIONEER,
    ETA_ORGANIC,
    LAMBDA_DECAY,
    EPS,
)


def f_T_pioneer(T: float) -> float:
    """Broad temperature tolerance for pioneer."""
    return math.exp(-0.5 * ((T - T_MID_PIONEER) / max(SIGMA_T_PIONEER, EPS)) ** 2)


def f_W_pioneer(water_phase: str, H2O: float, organic_layer: float) -> float:
    """Moisture availability 0~1. Liquid water or high humidity + organic helps."""
    if water_phase == "liquid":
        return 1.0
    # Vapor + organic retention: simple blend
    w_vap = min(1.0, H2O * 50.0)  # scale so ~0.02 H2O → ~1
    w_org = min(1.0, organic_layer * 2.0)
    return max(0.0, min(1.0, 0.3 * w_vap + 0.7 * w_org))


def npp_pioneer(T: float, water_phase: str, H2O: float, organic_layer: float) -> float:
    """Pioneer NPP [kg C/m²/yr]. No light/CO2 dependence."""
    return R_PIONEER * f_T_pioneer(T) * f_W_pioneer(water_phase, H2O, organic_layer)


def d_pioneer_dt(
    pioneer_biomass: float,
    organic_layer: float,
    T: float,
    water_phase: str,
    H2O: float,
) -> tuple:
    """d(pioneer)/dt and d(organic_layer)/dt."""
    npp = npp_pioneer(T, water_phase, H2O, organic_layer)
    d_pioneer = npp - M_PIONEER * pioneer_biomass
    # Organic from dead pioneer
    d_organic = ETA_ORGANIC * M_PIONEER * pioneer_biomass - LAMBDA_DECAY * organic_layer
    return d_pioneer, d_organic
