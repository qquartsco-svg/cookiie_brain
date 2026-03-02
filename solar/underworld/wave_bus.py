"""underworld.wave_bus — 전파 매질 (WaveBus)

Hades 원신호를 감쇠/라우팅만 수행. 판단·행동 없음.
severity' = f(severity, distance, medium, time) 결정론적.

Layer: L2 (Propagate). Allowed deps: consciousness, propagation. Forbidden: hades, siren, deep_monitor, rules, solar.eden.
See LAYERS.md.
"""

from __future__ import annotations

from typing import Any, List

from .consciousness import ConsciousnessSignal
from .propagation import WavePacket


def _attenuate(severity: float, distance: float, medium: str, _tick: int = 0) -> float:
    """감쇠 함수. 결정론적.

    severity' = severity / (1 + distance) * medium_factor
    medium: "default"=1.0, "dense"=0.8, "void"=0.95 등 확장 가능.
    """
    if severity <= 0.0:
        return 0.0
    medium_factor = {"default": 1.0, "dense": 0.8, "void": 0.95}.get(
        medium, 1.0
    )
    return severity * (1.0 / (1.0 + max(0.0, distance))) * medium_factor


class WaveBus:
    """전파 매질. Raw 신호 리스트 → WavePacket 리스트로만 변환.

    WaveBus NEVER decides/acts. Pure propagation/attenuation.
    """

    def __init__(
        self,
        default_distance: float = 0.0,
        default_medium: str = "default",
    ):
        self.default_distance = default_distance
        self.default_medium = default_medium

    def propagate(
        self,
        signals: List[ConsciousnessSignal],
        context: Any = None,
        distance: float | None = None,
        medium: str | None = None,
        tick: int = 0,
    ) -> List[WavePacket]:
        """원신호를 전파(감쇠)만 적용해 WavePacket 리스트로 반환.

        Parameters
        ----------
        signals : List[ConsciousnessSignal]
            Hades.listen() 반환값 등.
        context : optional
            추후 거리/매질 보정용 (덕 타이핑). 현재 미사용.
        distance : optional
            전파 거리. None 이면 default_distance 사용.
        medium : optional
            매질. None 이면 default_medium 사용.
        tick : int
            현재 틱.

        Returns
        -------
        List[WavePacket]
            감쇠된 전파 패킷. QUIET 신호는 그대로 severity=0 유지.
        """
        if not signals:
            return []
        dist = distance if distance is not None else self.default_distance
        med = medium if medium is not None else self.default_medium
        out: List[WavePacket] = []
        for sig in signals:
            if sig.is_quiet:
                sev = 0.0
            else:
                sev = _attenuate(sig.severity, dist, med, tick)
            out.append(
                WavePacket(
                    signal=sig,
                    attenuated_severity=sev,
                    distance=dist,
                    medium=med,
                    tick=tick,
                )
            )
        return out


def propagate(
    signals: List[ConsciousnessSignal],
    context: Any = None,
    distance: float = 0.0,
    medium: str = "default",
    tick: int = 0,
) -> List[WavePacket]:
    """편의 함수. 기본 WaveBus로 한 번 전파."""
    bus = WaveBus(default_distance=distance, default_medium=medium)
    return bus.propagate(signals, context=context, tick=tick)
