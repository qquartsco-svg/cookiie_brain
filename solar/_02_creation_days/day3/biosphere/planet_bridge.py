"""Biosphere ↔ Atmosphere unit conversion for feedback application.

Biosphere outputs: kg C/m²/yr, kg O2/m²/yr, kg H2O/m²/yr (per land area).
Atmosphere expects: composition mixing ratio [mol/mol] increment per dt_yr.

규약: column_mass [kg/m²], MU_* [kg/mol]. n_air = column_mass / MU_AIR [mol/m²].
"""

from typing import Dict, Any

# Use atmosphere constants for consistency
from solar._02_creation_days.day2.atmosphere._constants import MU_AIR, YR_S

M_C = 12.010e-3   # kg/mol carbon
M_O2 = 31.998e-3  # kg/mol O2
M_H2O = 18.015e-3 # kg/mol H2O


def biosphere_feedback_to_atmosphere(
    feedback: Dict[str, Any],
    dt_yr: float,
    land_fraction: float,
    column_mass: float,
) -> Dict[str, Any]:
    """Convert biosphere step() output to atmosphere composition deltas and extra latent.

    feedback: from BiosphereColumn.step(env, dt_yr)
    dt_yr: time step [yr]
    land_fraction: land area fraction (e.g. 0.29)
    column_mass: atmospheric column mass [kg/m²] (e.g. 1.0332e4)

    Returns
    -------
    dict with:
      delta_CO2_mixing, delta_O2_mixing, delta_H2O_mixing: to add to composition
      extra_latent_heat_Wm2: [W/m²] to pass to atmosphere.step(..., extra_latent_heat_Wm2=)
      delta_albedo_land: to combine with surface_schema for albedo
    """
    n_air = column_mass / MU_AIR  # mol/m²
    delta_CO2 = feedback.get("delta_CO2", 0.0)  # kg C/m²/yr (per land)
    delta_O2 = feedback.get("delta_O2", 0.0)    # kg O2/m²/yr (per land)
    trans_kg = feedback.get("transpiration_kg_per_m2_yr", 0.0)
    latent_W = feedback.get("latent_heat_biosphere_W", 0.0)
    delta_albedo = feedback.get("delta_albedo_land", 0.0)

    # Global average: flux_global = flux_land * land_fraction
    mol_C_per_m2 = (delta_CO2 * dt_yr * land_fraction) / M_C
    mol_O2_per_m2 = (delta_O2 * dt_yr * land_fraction) / M_O2
    mol_H2O_per_m2 = (trans_kg * dt_yr * land_fraction) / M_H2O

    delta_CO2_mixing = mol_C_per_m2 / n_air if n_air > 0 else 0.0
    delta_O2_mixing = mol_O2_per_m2 / n_air if n_air > 0 else 0.0
    delta_H2O_mixing = mol_H2O_per_m2 / n_air if n_air > 0 else 0.0

    return {
        "delta_CO2_mixing": delta_CO2_mixing,
        "delta_O2_mixing": delta_O2_mixing,
        "delta_H2O_mixing": delta_H2O_mixing,
        "extra_latent_heat_Wm2": latent_W,
        "delta_albedo_land": delta_albedo,
    }
