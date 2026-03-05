"""
Phase 0: Pre-Genesis — 기초 물리 & 탐색.
행성이 만들어지기 전, 궤도·질량 등 거시적 물리 조건 탐색 (Joe).
"""
from __future__ import annotations

PIPELINE_PHASE = "precreation"

from solar.code.precreation.joe import run as joe_run

__all__ = ["joe_run", "PIPELINE_PHASE"]
