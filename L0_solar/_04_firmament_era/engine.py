"""궁창 환경시대 — 실행 단계. FirmamentLayer + antediluvian 초기조건으로 한 스텝 실행."""
from __future__ import annotations

from typing import Any, Optional, Tuple


def run_firmament_era_step(
    firmament: Any = None,
    ic: Any = None,
    dt_yr: float = 1.0,
    instability: float = 0.0,
) -> Tuple[Any, Any, float]:
    """궁창 환경시대 한 스텝. (firmament, layer0_snapshot, instability) 반환."""
    from L0_solar._03_eden_os_underworld.eden import firmament as _fm
    from L0_solar._03_eden_os_underworld.eden import initial_conditions as _ic_mod

    if firmament is None:
        firmament = _fm.make_firmament(phase="antediluvian")
    if ic is None:
        ic = _ic_mod.make_antediluvian()

    firmament.step(dt_yr=dt_yr, instability=instability)
    layer0 = firmament.get_layer0_snapshot() if hasattr(firmament, "get_layer0_snapshot") else None
    if layer0 is None and hasattr(firmament, "state"):
        from L0_solar._03_eden_os_underworld.eden.firmament import Layer0Snapshot
        state = firmament.state
        layer0 = Layer0Snapshot(
            shield_strength=getattr(state, "shield_strength", 1.0),
            env_load=getattr(state, "env_load", 0.0),
        )
    return (firmament, layer0, instability)


__all__ = ["run_firmament_era_step"]
