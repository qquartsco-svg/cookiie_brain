"""underworld.deep_monitor — 물리 코어(day4/core) 값 읽기

행성 거시 룰 감시를 위한 읽기 전용 스냅샷.
day4/core 가 없거나 사용하지 않으면 스텁 값을 반환.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

# day4.core 는 선택 의존 — 없으면 None
try:
    from solar.day4.core import EvolutionEngine, CentralBody  # type: ignore
    _CORE_AVAILABLE = True
except Exception:
    _CORE_AVAILABLE = False
    EvolutionEngine = None  # type: ignore
    CentralBody = None  # type: ignore


@dataclass(frozen=True)
class DeepSnapshot:
    """지하/코어 물리 스냅샷 (읽기 전용).

    자기장, 지열, 중력 등 — Hades가 거시 룰 위반 여부 판단에 사용.
    """
    tick:           int
    core_available: bool
    # 스텁 또는 실제 값
    magnetic_ok:    bool   # 자기장 정상 여부
    thermal_ok:     bool   # 열류/맨틀 정상
    gravity_ok:     bool   # 중력장 정상
    extra:          Dict[str, Any]  # 확장용

    @classmethod
    def stub(cls, tick: int = 0) -> DeepSnapshot:
        """core 없을 때 스텁."""
        return cls(
            tick=tick,
            core_available=False,
            magnetic_ok=True,
            thermal_ok=True,
            gravity_ok=True,
            extra={},
        )


def read_deep_snapshot(tick: int = 0, engine: Any = None) -> DeepSnapshot:
    """물리 코어에서 현재 스냅샷 읽기.

    Parameters
    ----------
    tick : int
        현재 틱.
    engine : optional
        EvolutionEngine 등 — 주어지면 해당 엔진 상태를 읽음.

    Returns
    -------
    DeepSnapshot
        코어 사용 불가면 스텁(모두 ok=True).
    """
    if not _CORE_AVAILABLE or engine is None:
        return DeepSnapshot.stub(tick=tick)

    try:
        # 실제 엔진에서 읽을 수 있는 값이 있으면 여기서 채움
        # 예: engine.get_earth_body() → magnetic_dipole, spin, ...
        return DeepSnapshot(
            tick=tick,
            core_available=True,
            magnetic_ok=True,
            thermal_ok=True,
            gravity_ok=True,
            extra={"engine_tick": getattr(engine, "_tick", tick)},
        )
    except Exception:
        return DeepSnapshot.stub(tick=tick)
