"""UnderWorld — 거시 감시·의식 경고 독립 엔진

Hades ONLY measures. Hades NEVER acts.
solar/cookiie_brain 에서 분리된 완전 독립 패키지.
"""

from .consciousness import ConsciousnessSignal, SignalType
from .hades import HadesObserver, make_hades_observer

__all__ = [
    "ConsciousnessSignal",
    "SignalType",
    "HadesObserver",
    "make_hades_observer",
]
