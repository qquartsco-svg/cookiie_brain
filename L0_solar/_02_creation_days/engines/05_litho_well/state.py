"""Biosphere state variables — pioneer, organic layer, photosynthetic pools.

Phase 7b: Harsh → pioneer → photosynthesis → O2 → successional.
Phase 7c: seed → sprout → stem → wood → fruit (Phase Gate ODE)

All biomass in [kg C/m²] (global average per land area).
모든 전이는 율(d/dt)로 정의, dt는 적분에서 한 번만 적용.
"""

from dataclasses import dataclass, field


@dataclass
class BiosphereState:
    """Snapshot of biosphere state for observation / coupling.

    상태변수 계층:
      Pioneer  : pioneer_biomass, organic_layer, mineral_layer
      광합성   : B_leaf, B_root (기관 reservoir)
      Phase Gate: B_sprout → B_stem → B_wood → B_fruit → B_seed (생애주기)
    """

    # Pioneer (Phase 7b-1)
    pioneer_biomass: float = 0.0      # [kg C/m²]
    organic_layer: float = 0.0        # [kg C/m²] humus
    mineral_layer: float = 0.0        # [kg/m²]   풍화 광물

    # 광합성 기관 reservoir (Phase 7b-2)
    B_leaf: float = 0.0               # [kg C/m²] 잎
    B_root: float = 0.0               # [kg C/m²] 뿌리

    # Phase Gate 생애주기 (Phase 7c) — 씨→싹→줄기→나무→열매
    B_sprout: float = 0.0             # [kg C/m²] 싹 (발아 직후 유묘)
    B_stem: float = 0.0               # [kg C/m²] 줄기 (초본/관목 단계)
    B_wood: float = 0.0               # [kg C/m²] 목본 (나무 단계)
    B_fruit: float = 0.0              # [kg C/m²] 열매 (결실)
    B_seed: float = 0.0               # [kg C/m²] 씨 (번식/저장 풀)

    # Fluxes (last step)
    GPP: float = 0.0                  # [kg C/m²/yr]
    Resp: float = 0.0
    NPP: float = 0.0
    transpiration_flux: float = 0.0   # [kg H2O/m²/yr]
    latent_heat_biosphere: float = 0.0  # [W/m²]

    # Phase 진행 상태 (edge AI 요약 출력)
    photo_active: bool = False         # True if GPP > 0 this step
    f_O2: float = 0.0                  # O2 limitation factor (0~1)
    succession_phase: float = 0.0      # 0=pioneer, 1=sprout, 2=stem, 3=wood, 4=fruit

    @property
    def total_biomass(self) -> float:
        return (self.B_leaf + self.B_root + self.B_sprout + self.B_stem
                + self.B_wood + self.B_fruit + self.B_seed + self.pioneer_biomass)

    @property
    def plant_biomass(self) -> float:
        """Pioneer 제외 식물 생체량."""
        return (self.B_leaf + self.B_root + self.B_sprout
                + self.B_stem + self.B_wood + self.B_fruit + self.B_seed)

    @property
    def veg_cover_fraction(self) -> float:
        """0~1 proxy for vegetation cover (for albedo feedback)."""
        from ._constants import VEG_COVER_SCALE
        import math
        b = self.B_leaf + self.B_stem + self.B_wood
        return 1.0 - math.exp(-VEG_COVER_SCALE * max(0.0, b))
