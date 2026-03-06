"""Photosynthetic biosphere — GPP/NPP, biomass pools, seed, O2/CO2 feedback.

Active only when environment is “ready” (organic_layer or pioneer above threshold,
liquid water, T/F/CO2 in range). Produces O2, consumes CO2, transpiration → delta_H2O.
"""

import math
from ._constants import (
    P_MAX,
    F_HALF,
    K_C,
    T_OPT,
    SIGMA_T_PHOTO,
    K_RESP_LEAF,
    K_RESP_ROOT,
    K_RESP_WOOD,
    A_LEAF,
    A_ROOT,
    A_WOOD,
    A_SEED,
    M_LEAF,
    M_ROOT,
    M_WOOD,
    B_THRESHOLD_SEED,
    K_SEED,
    M_SEED,
    K_GERM,
    K_O2,
    O2_THRESHOLD,
    K_TRANS,
    L_V_REF,
    ORGANIC_THRESHOLD,
    PIONEER_THRESHOLD,
    EPS,
)


def f_I(F: float) -> float:
    """Light saturation."""
    return F / (F + F_HALF + EPS)


def f_C(CO2: float) -> float:
    """CO2 saturation."""
    return CO2 / (CO2 + K_C + EPS)


def f_T_photo(T: float) -> float:
    """Temperature optimum (narrower than pioneer)."""
    return math.exp(-0.5 * ((T - T_OPT) / max(SIGMA_T_PHOTO, EPS)) ** 2)


def f_O2(O2: float) -> float:
    """O2 limitation for successional/respiration plants (0~1)."""
    return O2 / (O2 + K_O2 + EPS)


def photo_ready(organic_layer: float, pioneer_biomass: float, water_phase: str) -> bool:
    """True if photosynthesis is allowed (soil prepared + liquid water)."""
    if water_phase != "liquid":
        return False
    return organic_layer >= ORGANIC_THRESHOLD or pioneer_biomass >= PIONEER_THRESHOLD


def gpp(F: float, CO2: float, T: float, f_W: float) -> float:
    """GPP [kg C/m²/yr]."""
    return P_MAX * f_I(F) * f_C(CO2) * f_T_photo(T) * max(0.0, min(1.0, f_W))


def respiration(B_leaf: float, B_root: float, B_wood: float) -> float:
    """Resp [kg C/m²/yr]."""
    return (
        K_RESP_LEAF * B_leaf
        + K_RESP_ROOT * B_root
        + K_RESP_WOOD * B_wood
    )


def transpiration_flux(B_leaf: float, F: float, f_W: float) -> float:
    """Transpiration [kg H2O/m²/yr]. Scales with leaf and light and water."""
    return K_TRANS * B_leaf * (F + EPS) * f_W


def latent_heat_W(E_kg_per_m2_yr: float) -> float:
    """Convert kg H2O/m²/yr to W/m² (annual mean)."""
    from ._constants import L_V_REF, YR_S
    return (E_kg_per_m2_yr * L_V_REF) / YR_S
