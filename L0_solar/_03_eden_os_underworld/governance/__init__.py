"""
Phase 6: Governance — 법칙·룰·통제. Hades, rules.
"""
from __future__ import annotations

PIPELINE_PHASE = "governance"

from L0_solar._03_eden_os_underworld.governance.hades import listen as hades_listen
from L0_solar._03_eden_os_underworld.governance.hades import HadesObserver, make_hades_observer, ConsciousnessSignal

__all__ = ["hades_listen", "HadesObserver", "make_hades_observer", "ConsciousnessSignal", "PIPELINE_PHASE"]
