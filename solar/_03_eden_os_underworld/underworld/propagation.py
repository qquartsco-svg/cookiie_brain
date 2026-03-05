"""underworld.propagation — 전파 계층 DTO (WavePacket, PerceptionSignal)

Hades 원신호(Raw) → WaveBus 전파(WavePacket) → Siren 지역 변환(PerceptionSignal).
consciousness.ConsciousnessSignal 는 건드리지 않음.

Layer: L1.5 (Propagation DTO). Allowed deps: TYPE_CHECKING only consciousness (no runtime import). Forbidden: hades, wave_bus, siren, deep_monitor, rules, solar.eden.
See LAYERS.md.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .consciousness import ConsciousnessSignal


@dataclass(frozen=True)
class WavePacket:
    """WaveBus가 만드는 전파 패킷. 원신호 + 감쇠 메타.

    WaveBus ONLY propagates/attenuates. Never decides/acts.
    """

    signal: "ConsciousnessSignal"
    attenuated_severity: float  # severity' = f(severity, distance, medium, time)
    distance: float
    medium: str
    tick: int

    @property
    def is_quiet(self) -> bool:
        return self.attenuated_severity <= 0.0 or (
            getattr(self.signal, "signal_type", "") == "QUIET"
        )


@dataclass(frozen=True)
class PerceptionSignal:
    """Siren이 만드는 지역 의미론적 이벤트. 수신측(Homeostasis/FSM)이 사용.

    Sirens ONLY propagate/transform. Never decide/act.
    """

    region_id: str
    severity: float
    signal_type: str
    message: str
    tick: int
    source_signal_tick: int  # 원신호 tick (추적용)
    source_signal_type: str  # 원신호 타입 (RULE_VIOLATION 등)

    @property
    def is_quiet(self) -> bool:
        return self.severity <= 0.0

    def to_consumable_severity(self) -> float:
        """Homeostasis/FSM 등에서 쓸 severity (0~1)."""
        return max(0.0, min(1.0, self.severity))
