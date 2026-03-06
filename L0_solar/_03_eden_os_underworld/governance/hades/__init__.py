"""
Hades — 법칙·룰 설정. 물리 상수, 엔트로피 등 행성 상수 에디팅. underworld.hades 구현.
"""
from __future__ import annotations

from typing import Any, List, Optional

try:
    from L0_solar.underworld import HadesObserver, make_hades_observer, ConsciousnessSignal
    _ok = True
except Exception:
    _ok = False
    HadesObserver = None  # type: ignore
    make_hades_observer = None  # type: ignore
    ConsciousnessSignal = None  # type: ignore


def listen(
    hades_observer: Any,
    tick: int,
    world_snapshot: Any,
    deep_engine: Any = None,
    layer0_snapshot: Any = None,
) -> Optional[List[Any]]:
    if hades_observer is None or not _ok:
        return None
    return hades_observer.listen(
        tick, world_snapshot,
        deep_engine=deep_engine,
        layer0_snapshot=layer0_snapshot,
    )


__all__ = ["listen", "HadesObserver", "make_hades_observer", "ConsciousnessSignal"]
