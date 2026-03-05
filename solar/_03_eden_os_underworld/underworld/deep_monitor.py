"""underworld.deep_monitor — 물리 코어(day4/core) 값 읽기

행성 거시 룰 감시를 위한 읽기 전용 스냅샷.
day4/core 가 없거나 사용하지 않으면 스텁 값을 반환.

Layer: L0' (Adapter). Allowed deps: stdlib, optional solar.day4.core. Forbidden: consciousness, rules, hades, propagation, wave_bus, siren, solar.eden.
See LAYERS.md.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

# day4.core 는 선택 의존 — 없으면 None
try:
    from solar._02_creation_days.day4.core import EvolutionEngine, CentralBody  # type: ignore
    _CORE_AVAILABLE = True
except Exception:
    _CORE_AVAILABLE = False
    EvolutionEngine = None  # type: ignore
    CentralBody = None  # type: ignore


@dataclass(frozen=True)
class DeepSnapshot:
    """지하/코어 물리 스냅샷 (읽기 전용).

    자기장, 지열, 중력 등 — Hades가 거시 룰 위반 여부 판단에 사용.
    궁창/환경: shield_strength(S(t)), env_load(L_env) 는 Layer0 주입 시 채움. None=미제공.
    """
    tick:           int
    core_available: bool
    magnetic_ok:    bool
    thermal_ok:     bool
    gravity_ok:     bool
    shield_strength: Optional[float] = None   # S(t) in [0,1]. 1=궁창 완전, 0=붕괴
    env_load:       Optional[float] = None    # L_env(t) >= 0
    extra:          Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def stub(cls, tick: int = 0) -> DeepSnapshot:
        """core 없을 때 스텁."""
        return cls(
            tick=tick,
            core_available=False,
            magnetic_ok=True,
            thermal_ok=True,
            gravity_ok=True,
            shield_strength=None,
            env_load=None,
        )


def read_deep_snapshot(tick: int = 0, engine: Any = None, layer0_snapshot: Any = None) -> DeepSnapshot:
    """물리 코어에서 현재 스냅샷 읽기.

    Parameters
    ----------
    tick : int
        현재 틱.
    engine : optional
        EvolutionEngine 등 — 주어지면 해당 엔진 상태를 읽음.
    layer0_snapshot : optional
        Layer0 환경(궁창) 스냅샷. shield_strength, env_load 속성이 있으면 채움 (덕 타이핑).

    Returns
    -------
    DeepSnapshot
        코어 사용 불가면 스텁(모두 ok=True). shield_strength/env_load 는 layer0_snapshot 제공 시에만 채워짐.
    """
    if not _CORE_AVAILABLE or engine is None:
        snap = DeepSnapshot.stub(tick=tick)
    else:
        try:
            snap = DeepSnapshot(
                tick=tick,
                core_available=True,
                magnetic_ok=True,
                thermal_ok=True,
                gravity_ok=True,
                shield_strength=None,
                env_load=None,
                extra={"engine_tick": getattr(engine, "_tick", tick)},
            )
        except Exception:
            snap = DeepSnapshot.stub(tick=tick)

    if layer0_snapshot is not None:
        s = getattr(layer0_snapshot, "shield_strength", None)
        e = getattr(layer0_snapshot, "env_load", None)
        if s is not None or e is not None:
            snap = DeepSnapshot(
                tick=snap.tick,
                core_available=snap.core_available,
                magnetic_ok=snap.magnetic_ok,
                thermal_ok=snap.thermal_ok,
                gravity_ok=snap.gravity_ok,
                shield_strength=s if s is not None else snap.shield_strength,
                env_load=e if e is not None else snap.env_load,
                extra=dict(snap.extra),
            )
    return snap
