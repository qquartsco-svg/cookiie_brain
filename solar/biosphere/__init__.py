"""solar/biosphere/ — 척박→선구→광합성→대기 변화→호흡 식생 (Phase 7b)

셋째날(땅/바다 분리) 이후, 환경이 아직 척박한 상태에서:
  1. 선구 생물(pioneer): 균사·이끼·지의류류 — 넓은 T·극소 물만으로 생존, organic_layer 축적
  2. organic_layer(또는 pioneer) 임계 초과 + 액체 물 → 광합성 활성화
  3. 광합성 → O₂ 상승, CO₂ 감소 → 대기 조성 변화
  4. O₂ 임계 이상 → 호흡형(후기) 식생(나무·씨/열매) 비중 증가

의존: atmosphere/(T, P, CO2, H2O, O2, water_phase), surface/(land_fraction), em/(F).
출력: delta_CO2, delta_O2, transpiration, latent_heat_biosphere, delta_albedo_land.
"""

from .state import BiosphereState
from .column import BiosphereColumn
from . import pioneer
from . import photo

__all__ = [
    "BiosphereState",
    "BiosphereColumn",
    "pioneer",
    "photo",
]
