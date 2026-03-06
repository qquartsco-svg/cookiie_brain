"""
Phase 7: Monitoring — 자원·저장소·경고. Underworld, Siren → Edge AI 피드백.
"""
from __future__ import annotations

PIPELINE_PHASE = "monitoring"

try:
    from L0_solar._03_eden_os_underworld.underworld.siren import Siren
except Exception:
    Siren = None  # type: ignore

__all__ = ["PIPELINE_PHASE", "Siren"]
