"""underworld.deep_monitor — 물리 코어 스냅샷 읽기 (독립 엔진용)

행성 거시 룰 감시를 위한 읽기 전용 스냅샷.
독립 패키지: solar/day4 미참조. engine 은 덕 타이핑으로만 사용.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


@dataclass(frozen=True)
class DeepSnapshot:
    """지하/코어 물리 스냅샷 (읽기 전용).

    자기장, 지열, 중력 등 — Hades가 거시 룰 위반 여부 판단에 사용.
    """
    tick:           int
    core_available: bool
    magnetic_ok:    bool
    thermal_ok:     bool
    gravity_ok:     bool
    extra:          Dict[str, Any]

    @classmethod
    def stub(cls, tick: int = 0) -> DeepSnapshot:
        """엔진 없을 때 스텁."""
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

    독립 패키지: engine 이 None 이면 항상 스텁.
    engine 이 있으면 getattr(engine, "magnetic_ok", True) 등 덕 타이핑으로 읽음.
    """
    if engine is None:
        return DeepSnapshot.stub(tick=tick)
    try:
        return DeepSnapshot(
            tick=tick,
            core_available=True,
            magnetic_ok=getattr(engine, "magnetic_ok", True),
            thermal_ok=getattr(engine, "thermal_ok", True),
            gravity_ok=getattr(engine, "gravity_ok", True),
            extra={"engine_tick": getattr(engine, "_tick", tick)},
        )
    except Exception:
        return DeepSnapshot.stub(tick=tick)
