"""
00_precreation — Phase 0: 조(JOE) 탐색, 행성 스트레스.
행성이 만들어지기 전 거시 물리 조건 탐색.
"""
from __future__ import annotations

PIPELINE_PHASE = "precreation"

from L0_solar._01_beginnings.joe import run as joe_run

__all__ = ["joe_run", "PIPELINE_PHASE"]
