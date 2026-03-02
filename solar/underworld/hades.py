"""underworld.hades — 거시 감시자 + listen() API

행성 전체 스케일 룰 위반 감시.
입력: deep_monitor(물리 코어), 선택적으로 지상 스냅샷.
출력: ConsciousnessSignal — 지상 observe()에 포함할 "목소리".

설계 규칙 (불가침)
──────────────────
  Hades ONLY measures.  Hades NEVER acts.
  - Hades는 관측·신호 생성만 함. 결정(decide)·처벌(punish)·의도(want) 없음.
  - 행동/전이는 항상 Dynamics(IntegrityFSM 등) 쪽에서만 발생.
  - 이 규칙이 깨지면 physics layer → narrative agent 로 붕괴.
"""

from __future__ import annotations

from typing import Any, Optional

from .consciousness import ConsciousnessSignal
from .deep_monitor import DeepSnapshot, read_deep_snapshot
from .rules import evaluate_rules


class HadesObserver:
    """지하(Hades) 감시자 — 거시 룰 위반 시 ConsciousnessSignal 방출.

    지상 에이전트(아담) observe() 시 hades.listen(tick, ...) 호출하여
    경고/압력 신호를 함께 수신할 수 있음.
    """

    def __init__(self, tick: int = 0):
        self._tick = tick
        self._last_signal: Optional[ConsciousnessSignal] = None

    def listen(
        self,
        tick: int,
        world_snapshot: Any = None,
        deep_engine: Any = None,
    ) -> ConsciousnessSignal:
        """현재 틱 기준 목소리(신호) 수신.

        Parameters
        ----------
        tick : int
            현재 시뮬레이션 틱.
        world_snapshot : optional
            지상 환경 스냅샷 (EdenWorldEnv 등). 있으면 에덴 지수 등으로 severity 보정 가능.
        deep_engine : optional
            물리 코어 엔진 (EvolutionEngine 등). 없으면 deep_monitor 스텁 사용.

        Returns
        -------
        ConsciousnessSignal
            조용(QUIET)이거나 경고/위반/패닉 중 하나.
        """
        self._tick = tick
        deep = read_deep_snapshot(tick=tick, engine=deep_engine)

        if not deep.core_available:
            sig = ConsciousnessSignal.quiet(tick=tick)
            self._last_signal = sig
            return sig

        severity, signal_type, message = evaluate_rules(deep)
        if severity <= 0.0:
            sig = ConsciousnessSignal.quiet(tick=tick)
        else:
            sig = ConsciousnessSignal(
                source="underworld.hades",
                severity=severity,
                signal_type=signal_type,
                message=message,
                tick=tick,
            )
        self._last_signal = sig
        return sig

    @property
    def last_signal(self) -> Optional[ConsciousnessSignal]:
        return self._last_signal


def make_hades_observer(tick: int = 0) -> HadesObserver:
    """HadesObserver 생성."""
    return HadesObserver(tick=tick)
