"""Feature Layer 03 — 수권·판 proxy. (물리 → JOE 스냅샷 키)

T_eq_norm, liquid_window_score, sigma_plate, P_w 등. 정밀 기후 시뮬 금지 — 가능/불가/빡셈 정도만.
"""
from __future__ import annotations

from typing import Any, Dict


def build(snapshot: Dict[str, Any]) -> Dict[str, Any]:
    """온도·압력 proxy → liquid_window_score; tectonics_score → sigma_plate. 기존 키 있으면 유지."""
    out: Dict[str, Any] = {}
    T = snapshot.get("T_eq_K") or snapshot.get("T_surface_K")
    if T is not None:
        # 273~373 K 창 → 1, 벗어나면 0에 가깝게
        if 273 <= T <= 373:
            out["liquid_window_score"] = 1.0
        else:
            delta = min(abs(T - 273), abs(T - 373)) if T < 273 or T > 373 else 0
            out["liquid_window_score"] = max(0.0, 1.0 - delta / 100.0)
    if snapshot.get("tectonics_score") is not None:
        out["sigma_plate"] = snapshot["tectonics_score"]
    if snapshot.get("P_w") is not None:
        out["P_w"] = snapshot["P_w"]
    return out


__all__ = ["build"]
