"""solar.underworld — 지하(Hades) 레이어 + 전파(WaveBus / Siren)

지상(EdenOS)과 물리 코어(day4/core) 사이의 거시 감시자.
Hades = 인격화된 악역이 아닌, 행성 규모 룰 집행·의식의 목소리(ConsciousnessSignal) 전달.

- hades.listen() → 지상 observe()에 포함할 신호
- (확장) wave_bus.propagate() → siren.broadcast() → PerceptionSignal → Homeostasis/FSM
- deep_monitor: day4/core 물리값 읽기 (선택 의존)

Layer: 진입점 (re-export only). 의존성 순서는 LAYERS.md 준수. 수정 시 레이어 꼬임 방지.
설계 규칙: Hades ONLY measures, NEVER acts. WaveBus/Siren ONLY propagate/transform, NEVER decide/act.
"""

from .consciousness import ConsciousnessSignal, SignalType
from .hades import HadesObserver, make_hades_observer
from .propagation import PerceptionSignal, WavePacket
from .siren import Siren, make_siren
from .wave_bus import WaveBus, propagate

__all__ = [
    "ConsciousnessSignal",
    "SignalType",
    "HadesObserver",
    "make_hades_observer",
    "WavePacket",
    "PerceptionSignal",
    "WaveBus",
    "propagate",
    "Siren",
    "make_siren",
]
