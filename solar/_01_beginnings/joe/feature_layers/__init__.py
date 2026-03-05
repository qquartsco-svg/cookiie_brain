"""JOE Feature Layers — 물리 → 표준 스냅샷 키 변환.

순서: 00_cosmic → 01_mass_rotation → 02_retention → 03_water_plate_proxy.
각 레이어는 "스냅샷 생성기"만 담당; Aggregator(_core)는 합성만 수행.
"""
from __future__ import annotations

from typing import Any, Dict

from . import cosmic, mass_rotation, retention, water_plate_proxy


def build_joe_snapshot(raw: Dict[str, Any]) -> Dict[str, Any]:
    """원시 물리/스냅샷 → JOE 표준 스냅샷 (Feature Layer 순차 병합)."""
    out = dict(raw)
    for layer in (cosmic, mass_rotation, retention, water_plate_proxy):
        add = layer.build(out)
        for k, v in add.items():
            if k not in out or out[k] is None:
                out[k] = v
    return out


__all__ = ["build_joe_snapshot", "cosmic", "mass_rotation", "retention", "water_plate_proxy"]
