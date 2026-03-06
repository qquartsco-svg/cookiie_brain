# _04_firmament_era — 궁창 환경시대 (실제 패키지)
from __future__ import annotations

from L0_solar._03_eden_os_underworld.eden import firmament
from L0_solar._03_eden_os_underworld.eden import initial_conditions

from .engine import run_firmament_era_step

FirmamentLayer = firmament.FirmamentLayer
FirmamentState = getattr(firmament, "FirmamentState", None)
Layer0Snapshot = firmament.Layer0Snapshot
make_firmament = firmament.make_firmament
make_antediluvian = initial_conditions.make_antediluvian
make_postdiluvian = initial_conditions.make_postdiluvian
InitialConditions = initial_conditions.InitialConditions
EarthBandState = initial_conditions.EarthBandState

__all__ = [
    "run_firmament_era_step",
    "FirmamentLayer", "FirmamentState", "Layer0Snapshot", "make_firmament",
    "make_antediluvian", "make_postdiluvian", "InitialConditions", "EarthBandState",
]
