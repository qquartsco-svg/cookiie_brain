"""day4/ — 넷째날 순환 레이어 집합 (nitrogen + cycles + gravity_tides)

개념:
    셋째날까지 만든 biosphere/ + atmosphere/ + surface/ + fire/ 위에
    넷째날 3개 순환(질소·장주기·조석)을 한곳에서 바라볼 수 있도록
    얇은 집합 패키지를 둔다.

    - 순환 1: nitrogen/       — 질소 고정 + 탈질 + N_soil 항상성
    - 순환 2: cycles/         — Milankovitch 3주기 + 일사량/빙하기 드라이버
    - 순환 3: gravity_tides/  — 달·태양 조석 → 해양 혼합 → 탄소 펌프

설계 원칙:
    - 실제 구현은 원래 폴더(nitrogen/, cycles/, gravity_tides/)에 그대로 둔다.
    - day4/ 는 "어디에 뭐가 있는지"를 한 번에 보는 관문 역할만 한다.
    - solar/__init__.py 에서 이미 각각을 export 하고 있으므로,
      이 모듈은 import 경로를 정리해 주는 얇은 집합 레이어이다.

참고 문서:
    - docs/DAY4_DESIGN.md     — 넷째날 설계 개요
    - docs/VERSION_LOG.md     — v2.5.0~v2.7.0 (cycles / nitrogen / gravity_tides)
"""

from __future__ import annotations

# 순환 1 — 질소 루프 (nitrogen/)
from ..nitrogen import (
    NitrogenFixation,
    FixationResult,
    make_fixation_engine,
    NitrogenCycle,
    NitrogenState,
    make_nitrogen_cycle,
)

# 순환 2 — 장주기 Milankovitch 드라이버 (cycles/)
from ..cycles import (
    MilankovitchCycle,
    MilankovitchState,
    make_earth_cycle,
    make_custom_cycle,
    insolation_at,
    insolation_grid,
    MilankovitchDriver,
    DriverOutput,
    make_earth_driver,
)

# 순환 3 — 조석-해양 탄소 펌프 (gravity_tides/)
from ..gravity_tides import (
    TidalField,
    TidalState,
    make_tidal_field,
    OceanNutrients,
    OceanState,
    make_ocean_nutrients,
)

# 셋째날 Gaia 루프와의 연결점 (참고용 re-export)
from ..gaia_loop_connector import GaiaLoopConnector, LoopState, make_connector

__all__ = [
    # nitrogen — 순환 1
    "NitrogenFixation",
    "FixationResult",
    "make_fixation_engine",
    "NitrogenCycle",
    "NitrogenState",
    "make_nitrogen_cycle",
    # cycles — 순환 2
    "MilankovitchCycle",
    "MilankovitchState",
    "make_earth_cycle",
    "make_custom_cycle",
    "insolation_at",
    "insolation_grid",
    "MilankovitchDriver",
    "DriverOutput",
    "make_earth_driver",
    # gravity_tides — 순환 3
    "TidalField",
    "TidalState",
    "make_tidal_field",
    "OceanNutrients",
    "OceanState",
    "make_ocean_nutrients",
    # GaiaLoopConnector — 넷째날 루프가 연결되는 지점
    "GaiaLoopConnector",
    "LoopState",
    "make_connector",
]

__version__ = "1.0.0"

