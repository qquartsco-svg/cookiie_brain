"""solar/biosphere/ — 셋째날: 선구→토양→생애주기→항상성→공간 분포 (Phase 7b/c/d/e)

셋째날(땅/바다 분리) 이후 완성 흐름:
  Phase 7b: 선구 ODE → 2739년 원시토양 (이끼·지의류·균사)
  Phase 7c: Phase Gate ODE → 씨→싹→줄기→나무→열매 생애주기
  Phase 7d: Gaia Attractor → 루프A(분해→CO₂)·루프B(토양환류)·루프C(대기↔생물)
  Phase 7e: LatitudeBands → ε(자전축)·φ(위도) → 척박/비옥 공간 분포 창발

설계 철학 (세차운동과 동일):
  입력: 물리 법칙/관측값 → 결과(2739년 토양, 항상성, viability field)가 자연스럽게 나온다

의존: atmosphere/(T,P,CO2,H2O,O2,water_phase), surface/(land_fraction), em/(F).
출력: delta_CO2, delta_O2, transpiration, latent_heat_biosphere, delta_albedo_land.
"""

from .state import BiosphereState
from .column import BiosphereColumn
from .latitude_bands import LatitudeBands, BAND_CENTERS_DEG, BAND_WEIGHTS
from . import pioneer
from . import photo

__all__ = [
    "BiosphereState",
    "BiosphereColumn",
    "LatitudeBands",
    "BAND_CENTERS_DEG",
    "BAND_WEIGHTS",
    "pioneer",
    "photo",
]
