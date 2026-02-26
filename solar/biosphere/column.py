"""BiosphereColumn — pioneer + photosynthetic + successional (O2-dependent) in one column.

Phase 7b: Harsh environment → pioneer colonizers → organic layer → photosynthesis on
→ O2 rise → respiration/successional plants (wood, seed).

Inputs: F_solar_si, T_surface, P_surface, CO2, H2O, O2, water_phase, land_fraction.
Outputs: delta_CO2, delta_O2, delta_H2O (or flux), latent_heat_biosphere, delta_albedo_land.
"""

import math
from dataclasses import dataclass, field
from typing import Dict, Any, Optional

from .state import BiosphereState
from . import pioneer
from . import photo
from ._constants import (
    A_LEAF,
    A_ROOT,
    A_WOOD,
    A_SEED,
    M_LEAF,
    M_ROOT,
    M_WOOD,
    M_SEED,
    K_GERM,
    B_THRESHOLD_SEED,
    K_SEED,
    ALBEDO_BARE_LAND,
    ALBEDO_VEG_MIN,
    VEG_COVER_SCALE,
    EPS,
)


@dataclass
class BiosphereColumn:
    """Single-column biosphere (0D global land average).

    State: pioneer_biomass, organic_layer, B_leaf, B_root, B_wood, B_seed.
    step(env, dt) updates state and returns feedback dict for atmosphere/surface.
    """

    body_name: str = "Earth"
    land_fraction: float = 0.29

    # Initial state
    pioneer_biomass_init: float = 0.01   # small seed to start
    organic_layer_init: float = 0.0
    B_leaf_init: float = 0.0
    B_root_init: float = 0.0
    B_wood_init: float = 0.0
    B_seed_init: float = 0.0

    # Internal state (evolving)
    pioneer_biomass: float = field(default=0.01)
    organic_layer: float = field(default=0.0)
    mineral_layer: float = field(default=0.0)
    B_leaf: float = field(default=0.0)
    B_root: float = field(default=0.0)
    B_wood: float = field(default=0.0)
    B_seed: float = field(default=0.0)

    time_yr: float = field(default=0.0)

    def __post_init__(self) -> None:
        self.pioneer_biomass = self.pioneer_biomass_init
        self.organic_layer = self.organic_layer_init
        self.B_leaf = self.B_leaf_init
        self.B_root = self.B_root_init
        self.B_wood = self.B_wood_init
        self.B_seed = self.B_seed_init

    def step(self, env: Dict[str, Any], dt_yr: float) -> Dict[str, Any]:
        """Advance biosphere by dt_yr. env: F_solar_si, T_surface, P_surface,
        CO2, H2O, O2, water_phase, (optional) soil_moisture.
        Returns feedback: delta_CO2, delta_O2, transpiration_kg, latent_heat_W, delta_albedo_land.
        """
        F = env.get("F_solar_si", 0.0)
        T = env.get("T_surface", 273.0)
        P = env.get("P_surface", 1e5)
        CO2 = env.get("CO2", 400e-6)
        H2O = env.get("H2O", 0.01)
        O2 = env.get("O2", 0.0)
        water_phase = env.get("water_phase", "gas")
        f_W = env.get("soil_moisture", 1.0 if water_phase == "liquid" else 0.2)

        # —— Pioneer (always active in harsh conditions) —————————————
        d_pioneer, d_organic, d_mineral = pioneer.d_pioneer_dt(
            self.pioneer_biomass,
            self.organic_layer,
            self.mineral_layer,
            T,
            water_phase,
            H2O,
        )
        self.pioneer_biomass = max(0.0, self.pioneer_biomass + d_pioneer * dt_yr)
        self.organic_layer = max(0.0, self.organic_layer + d_organic * dt_yr)
        self.mineral_layer = max(0.0, self.mineral_layer + d_mineral * dt_yr)

        GPP = 0.0
        Resp = 0.0
        trans_kg = 0.0
        delta_CO2 = 0.0
        delta_O2 = 0.0

        if photo.photo_ready(self.organic_layer, self.pioneer_biomass, water_phase):
            GPP = photo.gpp(F, CO2, T, f_W)
            Resp = photo.respiration(self.B_leaf, self.B_root, self.B_wood)
            NPP = GPP - Resp
            o2_fac = photo.f_O2(O2)

            # Allocation: O2 high → more wood/seed (successional)
            a_leaf = A_LEAF * (1.0 - 0.5 * o2_fac)
            a_root = A_ROOT
            a_wood = A_WOOD + 0.3 * o2_fac
            a_seed = A_SEED + 0.2 * o2_fac
            a_leaf = max(EPS, a_leaf)
            a_seed = max(EPS, a_seed)

            d_B_leaf = a_leaf * NPP - M_LEAF * self.B_leaf
            d_B_root = a_root * NPP - M_ROOT * self.B_root
            d_B_wood = a_wood * NPP - M_WOOD * self.B_wood

            # Seed production when biomass is high
            B_total = self.B_leaf + self.B_root + self.B_wood
            if B_total >= B_THRESHOLD_SEED:
                to_seed = K_SEED * (self.B_leaf + self.B_wood) * dt_yr
                d_B_leaf -= to_seed * 0.5
                d_B_wood -= to_seed * 0.5
                self.B_seed += to_seed
            # Germination
            germ = K_GERM * photo.f_T_photo(T) * f_W * self.B_seed * dt_yr
            self.B_seed = max(0.0, self.B_seed - germ)
            d_B_leaf += germ * 0.7
            d_B_root += germ * 0.3
            # Seed loss
            self.B_seed = max(0.0, self.B_seed - M_SEED * self.B_seed * dt_yr)

            self.B_leaf = max(0.0, self.B_leaf + d_B_leaf * dt_yr)
            self.B_root = max(0.0, self.B_root + d_B_root * dt_yr)
            self.B_wood = max(0.0, self.B_wood + d_B_wood * dt_yr)

            # Fluxes for atmosphere feedback (simplified: GPP in kg C/m²/yr → mol ratio change)
            # Scale: 1 kg C/m² = column_mass * (1/MU_AIR) * (12/44) approx for CO2
            # Per unit area, delta_CO2 per year: -GPP/M_C * area_factor; we give rate per land area
            area_land = max(EPS, self.land_fraction)
            delta_CO2 = -(GPP - Resp) / area_land   # net C flux [kg C/m²/yr] → caller converts to mixing ratio
            delta_O2 = (GPP - Resp) * (32.0 / 12.0) / area_land  # O2 mass flux [kg O2/m²/yr]

            trans_kg = photo.transpiration_flux(self.B_leaf, F, f_W) * dt_yr

        latent_W = photo.latent_heat_W(trans_kg / max(dt_yr, EPS)) if dt_yr > 0 else 0.0

        # Albedo: vegetation cover lowers land albedo
        veg = 1.0 - math.exp(-VEG_COVER_SCALE * max(0.0, self.B_leaf + self.B_wood))
        A_land_new = ALBEDO_VEG_MIN + (ALBEDO_BARE_LAND - ALBEDO_VEG_MIN) * (1.0 - veg)
        delta_albedo_land = A_land_new - ALBEDO_BARE_LAND  # negative when veg grows

        self.time_yr += dt_yr

        return {
            "delta_CO2": delta_CO2,
            "delta_O2": delta_O2,
            "transpiration_kg_per_m2_yr": trans_kg / max(dt_yr, EPS),
            "latent_heat_biosphere_W": latent_W,
            "delta_albedo_land": delta_albedo_land,
            "GPP": GPP,
            "Resp": Resp,
            "NPP": GPP - Resp,
            "photo_active": GPP > 0,
        }

    def state(self) -> BiosphereState:
        """Current state snapshot."""
        return BiosphereState(
            pioneer_biomass=self.pioneer_biomass,
            organic_layer=self.organic_layer,
            B_leaf=self.B_leaf,
            B_root=self.B_root,
            B_wood=self.B_wood,
            B_seed=self.B_seed,
            GPP=0.0,
            Resp=0.0,
            NPP=0.0,
            transpiration_flux=0.0,
            latent_heat_biosphere=0.0,
            photo_active=False,
            f_O2=photo.f_O2(0.0),
        )
