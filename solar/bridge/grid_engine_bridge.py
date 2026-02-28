"""
grid_engine_bridge.py — Grid Engine ↔ Solar 12 위도밴드 연결

데스크탑 00_BRAIN 내 Grid Engine(Archive/Integrated/3.Grid_Engine)을 불러와
solar의 12 위도밴드와 연결한다.

- Grid Engine 경로: 00_BRAIN/Archive/Integrated/3.Grid_Engine/package
- 12밴드: 위도 인덱스 0..11 ↔ Grid 2D의 X축 위상 (2π = 12밴드)
- 확장: 링 어트랙터 2D~7D까지 동일 패키지에 있으면 차원별 로드 후 사용 (get_max_grid_dimension, create_grid_engine_nd).
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# CookiieBrain 기준 00_BRAIN 경로 (상위 두 단계)
_COOKIIE_ROOT = Path(__file__).resolve().parent.parent.parent
_00_BRAIN = _COOKIIE_ROOT.parent
_GRID_ENGINE_PACKAGE = _00_BRAIN / "Archive" / "Integrated" / "3.Grid_Engine" / "package"
# Ring Attractor Engine (Grid 2D 의존성): 같은 00_BRAIN 아래 2.Ring_Attractor_Engine
_RING_ATTRACTOR_PACKAGE = _00_BRAIN / "Archive" / "Integrated" / "2.Ring_Attractor_Engine" / "package"
# Shim: 2.Ring_Attractor_Engine 미설치/의존성 실패 시 solar 경량 Ring Attractor로 대체
_RING_ATTRACTOR_SHIM = Path(__file__).resolve().parent / "ring_attractor_shim"

GRID_ENGINE_AVAILABLE = False
_Grid2DEngine = None
_Grid2DConfig = None
_GridInput = None
_grid_engine_error = None  # last import error for diagnostics

# 확장: 2D~7D 중 로드된 차원 (링 어트랙터 7D까지 확장 반영)
_GRID_ENGINES_ND: Dict[int, Any] = {}
_GRID_CONFIGS_ND: Dict[int, Any] = {}
_GRID_INPUTS_ND: Dict[int, Any] = {}
_MAX_GRID_DIMENSION = 0

if _GRID_ENGINE_PACKAGE.is_dir():
    _added = str(_GRID_ENGINE_PACKAGE)
    if _added not in sys.path:
        sys.path.insert(0, _added)
    if _RING_ATTRACTOR_PACKAGE.is_dir():
        _ring_added = str(_RING_ATTRACTOR_PACKAGE)
        if _ring_added not in sys.path:
            sys.path.insert(0, _ring_added)
    # Shim을 맨 앞에: hippo_memory.ring_engine을 solar 경량 엔진으로 제공 (2.Ring_Attractor_Engine 의존성 없이 동작)
    _shim = str(_RING_ATTRACTOR_SHIM)
    if _RING_ATTRACTOR_SHIM.is_dir() and _shim not in sys.path:
        sys.path.insert(0, _shim)
    try:
        from grid_engine import Grid2DEngine, Grid2DConfig, GridInput
        _Grid2DEngine = Grid2DEngine
        _Grid2DConfig = Grid2DConfig
        _GridInput = GridInput
        GRID_ENGINE_AVAILABLE = True
        _GRID_ENGINES_ND[2] = Grid2DEngine
        _GRID_CONFIGS_ND[2] = Grid2DConfig
        _GRID_INPUTS_ND[2] = GridInput
        _MAX_GRID_DIMENSION = 2
    except Exception as _e:
        _grid_engine_error = _e  # for diagnostics
        pass

    # 확장: 3D~7D 링 어트랙터 로드 (같은 패키지 내 dim3d~dim7d)
    for _dim in (3, 4, 5, 6, 7):
        try:
            _mod = __import__(f"grid_engine.dimensions.dim{_dim}d", fromlist=[f"Grid{_dim}DEngine", f"Grid{_dim}DConfig", f"Grid{_dim}DInput"])
            _eng = getattr(_mod, f"Grid{_dim}DEngine", None)
            _cfg = getattr(_mod, f"Grid{_dim}DConfig", None)
            _inp = getattr(_mod, f"Grid{_dim}DInput", None)
            if _eng is not None:
                _GRID_ENGINES_ND[_dim] = _eng
                if _cfg is not None:
                    _GRID_CONFIGS_ND[_dim] = _cfg
                if _inp is not None:
                    _GRID_INPUTS_ND[_dim] = _inp
                if _dim > _MAX_GRID_DIMENSION:
                    _MAX_GRID_DIMENSION = _dim
        except Exception:
            pass


def get_grid_engine_path() -> Path:
    """Grid Engine 패키지 경로 (있으면)."""
    return _GRID_ENGINE_PACKAGE


def is_available() -> bool:
    """Grid Engine 사용 가능 여부."""
    return GRID_ENGINE_AVAILABLE


def get_import_error() -> Optional[Exception]:
    """Grid Engine import 실패 시 오류 (진단용)."""
    return _grid_engine_error


def get_max_grid_dimension() -> int:
    """로드된 Grid Engine 최대 차원 (2~7). 링 어트랙터 7D까지 확장 시 7 반환."""
    return _MAX_GRID_DIMENSION


def get_grid_dimensions_available() -> List[int]:
    """로드된 차원 목록 (예: [2, 3, 4, 5, 6, 7])."""
    return sorted(_GRID_ENGINES_ND.keys())


def create_grid_engine_nd(
    dimension: int,
    config: Any = None,
    **kwargs: Any,
) -> Optional[Any]:
    """
    지정 차원의 Grid Engine 인스턴스 생성 (2D~7D 확장).

    dimension=2 시 Grid2DEngine, dimension=7 시 Grid7DEngine 등.
    위도 12밴드 전용은 create_latitude_grid_agent() 사용.
    """
    if dimension not in _GRID_ENGINES_ND:
        return None
    eng_class = _GRID_ENGINES_ND[dimension]
    cfg_class = _GRID_CONFIGS_ND.get(dimension)
    try:
        if config is None and cfg_class is not None:
            config = cfg_class()
        return eng_class(config=config, **kwargs)
    except Exception:
        return None


# ── 12 위도밴드 ↔ Grid 2D (X축 = 밴드 인덱스) ─────────────────────────────

BAND_COUNT = 12


def phase_to_band_index(phi_x: float) -> int:
    """위상 [0, 2π) → 밴드 인덱스 0..11."""
    import math
    wrap = 2.0 * math.pi
    x = (phi_x % wrap) / wrap * BAND_COUNT
    return int(x) % BAND_COUNT


def band_index_to_phase(band_idx: int) -> float:
    """밴드 인덱스 0..11 → 위상 [0, 2π)."""
    import math
    return (band_idx % BAND_COUNT) / BAND_COUNT * (2.0 * math.pi)


class LatitudeGridAdapter:
    """
    Grid 2D 엔진을 12 위도밴드 축(1D)으로 쓰는 어댑터.

    - X축: 위도 밴드 인덱스 0..11 (spatial_scale_x=12)
    - Y축: 고정 0 (1D만 사용)
    - 용도: 에이전트/관측점이 위도축 위에서 경로통합으로 이동하는 상태를 Grid Engine이 유지.
    """

    def __init__(
        self,
        initial_band: int = 0,
        ring_size: int = 15,
        dt_ms: float = 5.0,   # dt_ms < tau_ms * max_dt_ratio (10) 필요
        tau_ms: float = 100.0,
    ):
        if not GRID_ENGINE_AVAILABLE or _Grid2DEngine is None or _Grid2DConfig is None:
            raise RuntimeError(
                "Grid Engine not available. "
                "Ensure 00_BRAIN/Archive/Integrated/3.Grid_Engine/package exists and is importable."
            )
        # X: 0..12 (밴드 인덱스), Y: 0
        self.config = _Grid2DConfig(
            ring_size=ring_size,
            dt_ms=dt_ms,
            tau_ms=tau_ms,
            spatial_scale_x=float(BAND_COUNT),
            spatial_scale_y=1.0,
            diagnostics_enabled=False,
            energy_check_enabled=False,
        )
        x0 = initial_band + 0.5  # 밴드 중심
        self._engine = _Grid2DEngine(config=self.config, initial_x=x0, initial_y=0.0)

    def step(self, velocity_lat: float) -> int:
        """
        한 스텝 진행. velocity_lat = 위도축 방향 속도 (밴드/스텝 단위).

        Returns
        -------
        int  현재 밴드 인덱스 0..11
        """
        inp = _GridInput(v_x=velocity_lat, v_y=0.0)
        out = self._engine.step(inp)
        return phase_to_band_index(out.phi_x)

    def get_band_index(self) -> int:
        """현재 상태의 밴드 인덱스."""
        state = self._engine.get_state()
        return phase_to_band_index(state.phi_x)

    def reset(self, band: int = 0) -> None:
        """밴드 위치 리셋."""
        self._engine.reset(x=band + 0.5, y=0.0)


def create_latitude_grid_agent(
    initial_band: int = 0,
    ring_size: int = 15,
) -> Optional[LatitudeGridAdapter]:
    """
    Grid Engine 기반 위도축 에이전트 생성.
    Grid Engine 없으면 None.
    """
    if not GRID_ENGINE_AVAILABLE:
        return None
    return LatitudeGridAdapter(initial_band=initial_band, ring_size=ring_size)


__all__ = [
    "GRID_ENGINE_AVAILABLE",
    "get_grid_engine_path",
    "is_available",
    "get_import_error",
    "get_max_grid_dimension",
    "get_grid_dimensions_available",
    "create_grid_engine_nd",
    "phase_to_band_index",
    "band_index_to_phase",
    "LatitudeGridAdapter",
    "create_latitude_grid_agent",
    "BAND_COUNT",
]
