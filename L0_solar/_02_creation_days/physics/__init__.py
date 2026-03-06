"""
Phase 1: Physics — 행성 내부 물리 (Lucifer Core, planet_dynamics, rotation).
"""
from __future__ import annotations

PIPELINE_PHASE = "physics"

try:
    from L0_solar._02_creation_days.physics.lucifer_core import run as lucifer_run
except Exception:
    lucifer_run = None  # type: ignore

__all__ = ["lucifer_run", "PIPELINE_PHASE"]
