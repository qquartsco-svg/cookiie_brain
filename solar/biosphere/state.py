"""Biosphere state variables — pioneer, organic layer, photosynthetic pools.

Phase 7b: Harsh → pioneer → photosynthesis → O2 → successional.
All biomass in [kg C/m²] (global average per land area).
"""

from dataclasses import dataclass, field


@dataclass
class BiosphereState:
    """Snapshot of biosphere state for observation / coupling."""

    # Pioneer (Phase 7b-1)
    pioneer_biomass: float = 0.0      # [kg C/m²]
    organic_layer: float = 0.0        # [kg C/m²]

    # Photosynthetic (Phase 7b-2)
    B_leaf: float = 0.0
    B_root: float = 0.0
    B_wood: float = 0.0
    B_seed: float = 0.0

    # Fluxes (last step)
    GPP: float = 0.0                 # [kg C/m²/yr]
    Resp: float = 0.0
    NPP: float = 0.0
    transpiration_flux: float = 0.0   # [kg H2O/m²/yr] for delta_H2O
    latent_heat_biosphere: float = 0.0  # [W/m²]

    # Conditions (for debugging / coupling)
    photo_active: bool = False        # True if GPP > 0 this step
    f_O2: float = 0.0                # O2 limitation factor for successional

    @property
    def total_biomass(self) -> float:
        return self.B_leaf + self.B_root + self.B_wood + self.B_seed + self.pioneer_biomass

    @property
    def veg_cover_fraction(self) -> float:
        """0~1 proxy for vegetation cover (for albedo feedback)."""
        from ._constants import VEG_COVER_SCALE
        import math
        b = self.B_leaf + self.B_wood
        return 1.0 - math.exp(-VEG_COVER_SCALE * max(0.0, b))
