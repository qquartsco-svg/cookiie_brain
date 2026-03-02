"""underworld.consciousness — 의식의 목소리 (ConsciousnessSignal)

지하(Hades)에서 지상 에이전트로 전달되는 신호.
경고, 압력, 임박 붕괴 등 — 에이전트 observe() 루프에서 수신 가능.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class SignalType(str, Enum):
    """목소리 유형."""
    ENTROPY_WARNING = "ENTROPY_WARNING"
    RULE_VIOLATION  = "RULE_VIOLATION"
    SYSTEM_PANIC    = "SYSTEM_PANIC"
    QUIET           = "QUIET"


@dataclass(frozen=True)
class ConsciousnessSignal:
    """지하 → 지상 전달 신호 (불변)."""

    source:       str
    severity:     float
    signal_type:  str
    message:      str
    tick:         int

    @classmethod
    def quiet(cls, tick: int = 0) -> ConsciousnessSignal:
        """신호 없음 (조용)."""
        return cls(
            source="underworld.hades",
            severity=0.0,
            signal_type=SignalType.QUIET.value,
            message="",
            tick=tick,
        )

    @property
    def is_quiet(self) -> bool:
        return self.signal_type == SignalType.QUIET.value or self.severity <= 0.0
