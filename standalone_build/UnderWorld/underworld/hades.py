"""underworld.hades — 거시 감시자 + listen() API

Hades ONLY measures. Hades NEVER acts.
"""

from __future__ import annotations

from typing import Any, List, Optional

from .consciousness import ConsciousnessSignal
from .deep_monitor import read_deep_snapshot
from .rules import evaluate_rules_all


class HadesObserver:
    """지하(Hades) 감시자 — 거시 룰 위반 시 ConsciousnessSignal 방출."""

    def __init__(self, tick: int = 0):
        self._tick = tick
        self._last_signal: Optional[ConsciousnessSignal] = None

    def listen(
        self,
        tick: int,
        world_snapshot: Any = None,
        deep_engine: Any = None,
    ) -> List[ConsciousnessSignal]:
        """현재 틱 기준 목소리(신호) 리스트 반환."""
        self._tick = tick
        deep = read_deep_snapshot(tick=tick, engine=deep_engine)

        if not deep.core_available:
            sig = ConsciousnessSignal.quiet(tick=tick)
            self._last_signal = sig
            return [sig]

        violations = evaluate_rules_all(deep)
        if not violations:
            sig = ConsciousnessSignal.quiet(tick=tick)
            self._last_signal = sig
            return [sig]

        signals: List[ConsciousnessSignal] = []
        for severity, signal_type, message in violations:
            signals.append(
                ConsciousnessSignal(
                    source="underworld.hades",
                    severity=severity,
                    signal_type=signal_type,
                    message=message,
                    tick=tick,
                )
            )
        self._last_signal = signals[0]
        return signals

    @property
    def last_signal(self) -> Optional[ConsciousnessSignal]:
        return self._last_signal


def make_hades_observer(tick: int = 0) -> HadesObserver:
    """HadesObserver 생성."""
    return HadesObserver(tick=tick)
