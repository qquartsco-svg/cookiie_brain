"""
Firmament — 2일차 궁창. 하늘과 물의 분리, 환경 경계. eden.firmament 구현.
"""
from __future__ import annotations

from typing import Any, Optional

try:
    from solar._03_eden_os_underworld.eden.firmament import FirmamentLayer, Layer0Snapshot
    _ok = True
except Exception:
    _ok = False
    FirmamentLayer = None  # type: ignore
    Layer0Snapshot = None  # type: ignore


def step(firmament: Any, dt_yr: float = 1.0, instability: float = 0.0) -> None:
    if firmament is not None and hasattr(firmament, "step"):
        firmament.step(dt_yr=dt_yr, instability=instability)


def get_layer0(firmament: Any) -> Optional[Any]:
    if firmament is None or not hasattr(firmament, "get_layer0_snapshot"):
        return None
    return firmament.get_layer0_snapshot()


__all__ = ["step", "get_layer0", "FirmamentLayer", "Layer0Snapshot"]
