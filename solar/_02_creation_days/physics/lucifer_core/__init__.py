"""
Lucifer Core — 내핵·외핵·맨틀 대류, 자기장(Dynamo). day4.core + deep_monitor.
"""
from __future__ import annotations

from typing import Any, Optional

try:
    from solar._03_eden_os_underworld.underworld.deep_monitor import read_deep_snapshot, DeepSnapshot
    _ok = True
except Exception:
    _ok = False
    read_deep_snapshot = None  # type: ignore
    DeepSnapshot = None  # type: ignore


def run(tick: int, engine: Any = None, layer0_snapshot: Any = None) -> Optional[Any]:
    if not _ok or read_deep_snapshot is None:
        return None
    return read_deep_snapshot(tick=tick, engine=engine, layer0_snapshot=layer0_snapshot)


__all__ = ["run", "read_deep_snapshot", "DeepSnapshot"]
