"""day3/ — 셋째날 레이어 집합 (땅·바다 + 식생 + 산불 + Gaia 루프)

개념:
    셋째날은 "땅과 바다"가 분리되고, 그 위에
    풀·씨·열매·나무(식생)와 산불 항상성이 올라오는 단계.

포함 모듈:
    - surface/: SurfaceSchema, effective_albedo (land_fraction, A_eff)
    - biosphere/: BiosphereColumn, BiosphereState, LatitudeBands
    - fire/: FireEngine, FireEnvSnapshot
    - gaia_loop_connector: GaiaLoopConnector, LoopState

이 모듈은 실제 구현을 옮기지 않고, 셋째날 관련 엔진 기어들을
한 곳에서 import/export 하는 집합 패키지 역할만 한다.
"""

from __future__ import annotations

from .surface import SurfaceSchema, effective_albedo

from .biosphere import (
    BiosphereColumn,
    BiosphereState,
    LatitudeBands,
    BAND_CENTERS_DEG,
    BAND_WEIGHTS,
)

from .gaia_fire import FireEngine, FireEnvSnapshot

__all__ = [
    # surface
    "SurfaceSchema",
    "effective_albedo",
    # biosphere
    "BiosphereColumn",
    "BiosphereState",
    "LatitudeBands",
    "BAND_CENTERS_DEG",
    "BAND_WEIGHTS",
    # fire
    "FireEngine",
    "FireEnvSnapshot",
]

__version__ = "1.0.0"

