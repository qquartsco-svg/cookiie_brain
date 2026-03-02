"""eden_os.homeostasis_engine — 항상성 엔진 (stress / integrity 매 틱)

관리자 = 항상성 유지 컨트롤러.
매 틱 stress_index·integrity 를 계산하여 IntegrityFSM 에 전달.
선악과 이벤트 = 대량 stress_injection 으로 통합 (동역학 안에서 즉각 붕괴).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional, Sequence, Union

# 지상 world 스냅샷 타입 (순환 방지)
EdenWorldEnv = Any


@dataclass
class HomeostasisSnapshot:
    """한 틱의 항상성 스냅샷."""
    tick:            int
    stress_index:    float   # 0.0 = 무스트레스, 1.0 = 최대
    integrity:       float   # 0.0 = 붕괴, 1.0 = 완전
    stress_injected: float   # 해당 틱에 주입된 일회성 스트레스 (선악과 등)


class HomeostasisEngine:
    """매 틱 stress · integrity 계산.

    입력: world(에덴 지수 등), hades_signal(선택), stress_injection(선악과 시 대량 주입).
    출력: stress_index, integrity — IntegrityFSM 이 사용.
    """

    def __init__(
        self,
        theta1: float = 0.75,
        theta2: float = 0.40,
    ):
        self.theta1 = theta1  # 이하 N tick → DEGRADED
        self.theta2 = theta2  # 이하 N tick → MORTAL
        self._last: Optional[HomeostasisSnapshot] = None

    def update(
        self,
        tick: int,
        world: EdenWorldEnv,
        hades_signal: Optional[Union[Any, Sequence[Any]]] = None,
        stress_injection: float = 0.0,
    ) -> HomeostasisSnapshot:
        """한 틱 갱신.

        Parameters
        ----------
        tick : int
            현재 틱.
        world : EdenWorldEnv (또는 layer/eden_index 있는 객체)
            지상 환경 스냅샷.
        hades_signal : optional
            ConsciousnessSignal 1개 또는 List[ConsciousnessSignal]. severity 가 있으면 stress 에 가산. 리스트면 최대 severity 사용.
        stress_injection : float
            일회성 스트레스 (선악과 = 대량, 예: 0.9).
        """
        eden_index = getattr(world, "eden_index", 0.9)
        if hasattr(world, "layer") and isinstance(getattr(world, "layer", None), dict):
            sc = world.layer.get("SCENARIO", {})
            eden_index = float(sc.get("eden_index", eden_index))

        # stress: 에덴 지수 역수 + 지하 경고 + 일회 주입
        base_stress = 1.0 - eden_index  # 0~1
        hades_severity = 0.0
        if hades_signal is not None:
            if isinstance(hades_signal, (list, tuple)):
                for s in hades_signal:
                    sev = getattr(s, "severity", None)
                    if sev is not None:
                        hades_severity = max(hades_severity, float(sev))
            else:
                if getattr(hades_signal, "severity", None) is not None:
                    hades_severity = float(hades_signal.severity)
        stress_index = min(1.0, base_stress * 0.7 + hades_severity * 0.3 + stress_injection)
        integrity = max(0.0, 1.0 - stress_index)

        snap = HomeostasisSnapshot(
            tick=tick,
            stress_index=round(stress_index, 4),
            integrity=round(integrity, 4),
            stress_injected=stress_injection,
        )
        self._last = snap
        return snap

    @property
    def last_snapshot(self) -> Optional[HomeostasisSnapshot]:
        return self._last


def make_homeostasis_engine(theta1: float = 0.75, theta2: float = 0.40) -> HomeostasisEngine:
    """HomeostasisEngine 생성."""
    return HomeostasisEngine(theta1=theta1, theta2=theta2)
