"""underworld.siren — 지역 공명 노드 (Siren)

WavePacket을 지역 컨텍스트로 변환/재방송만 수행. 판단·행동 없음.
raw telemetry → semantic perception.

Layer: L2 (Transform). Allowed deps: propagation only. Forbidden: consciousness, hades, wave_bus, deep_monitor, rules, solar.eden.
See LAYERS.md.
"""

from __future__ import annotations

from typing import Any, Callable, List, Optional

from .propagation import PerceptionSignal, WavePacket


def _default_message(packet: WavePacket, _region: Any) -> str:
    """기본: 원신호 메시지 그대로."""
    return getattr(packet.signal, "message", "") or ""


class Siren:
    """지역 공명 장치. WavePacket → PerceptionSignal 변환만.

    Sirens ONLY propagate/transform. Sirens NEVER decide/act.
    """

    def __init__(
        self,
        region_id: str,
        message_template: Optional[
            Callable[[WavePacket, Any], str]
        ] = None,
    ):
        self.region_id = region_id
        self._message_fn = message_template or _default_message

    def broadcast(
        self,
        wave_packets: List[WavePacket],
        region_state: Any = None,
        tick: int = 0,
    ) -> List[PerceptionSignal]:
        """전파 패킷을 지역 의미론적 신호로 변환해 반환.

        Parameters
        ----------
        wave_packets : List[WavePacket]
            WaveBus.propagate() 반환값.
        region_state : optional
            지역 상태 (덕 타이핑). 메시지 변환 시 전달.
        tick : int
            현재 틱.

        Returns
        -------
        List[PerceptionSignal]
            이 region 에 도달한 “들리는” 신호. 판단/전이는 수신측(FSM 등) 책임.
        """
        out: List[PerceptionSignal] = []
        for p in wave_packets:
            if p.is_quiet:
                continue
            sig = p.signal
            msg = self._message_fn(p, region_state)
            out.append(
                PerceptionSignal(
                    region_id=self.region_id,
                    severity=p.attenuated_severity,
                    signal_type=getattr(sig, "signal_type", "RULE_VIOLATION"),
                    message=msg,
                    tick=tick,
                    source_signal_tick=sig.tick,
                    source_signal_type=getattr(sig, "signal_type", "RULE_VIOLATION"),
                )
            )
        return out


def make_siren(region_id: str, message_template: Optional[Callable[[WavePacket, Any], str]] = None) -> Siren:
    """Siren 생성."""
    return Siren(region_id=region_id, message_template=message_template)
