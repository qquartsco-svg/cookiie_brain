"""
Phase 2: Fields — 궁창(Firmament), 대기, 자기권, 복사. 2일차 환경 경계.
"""
from __future__ import annotations

PIPELINE_PHASE = "fields"

from L0_solar._02_creation_days.fields.firmament import step as firmament_step, get_layer0 as firmament_get_layer0

__all__ = ["firmament_step", "firmament_get_layer0", "PIPELINE_PHASE"]
