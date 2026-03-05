# _05_noah_flood — 노아 대홍수 이벤트 (실제 패키지)
from __future__ import annotations

from solar._03_eden_os_underworld.eden import flood
from solar._03_eden_os_underworld.eden import firmament
from solar._03_eden_os_underworld.eden import initial_conditions

from .engine import run_flood_step, run_trigger_flood

FloodEngine = flood.FloodEngine
FloodSnapshot = flood.FloodSnapshot
make_flood_engine = flood.make_flood_engine
FLOOD_PHASES = flood.FLOOD_PHASES
FirmamentLayer = firmament.FirmamentLayer
make_antediluvian = initial_conditions.make_antediluvian
make_postdiluvian = initial_conditions.make_postdiluvian
make_flood_peak = getattr(initial_conditions, "make_flood_peak", None)

__all__ = [
    "run_flood_step", "run_trigger_flood",
    "FloodEngine", "FloodSnapshot", "make_flood_engine", "FLOOD_PHASES",
    "FirmamentLayer", "make_antediluvian", "make_postdiluvian", "make_flood_peak",
]
