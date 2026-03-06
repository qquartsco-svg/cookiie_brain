"""Feature Layer 02 — 대기 유지. (물리 → JOE 스냅샷 키)

v_escape > 6×v_thermal 등 → atm_retention_score [0~1].
"""
from __future__ import annotations

from typing import Any, Dict


def build(snapshot: Dict[str, Any]) -> Dict[str, Any]:
    """v_escape, T 등 → atm_retention_score. 이미 있으면 유지."""
    out: Dict[str, Any] = {}
    v_esc = snapshot.get("v_escape_m_s")
    if v_esc is not None and v_esc > 0:
        # v_thermal proxy: 지구 대기 평균 분자량 기준 대략 350 m/s
        v_thermal_proxy = 350.0
        ratio = v_esc / (6.0 * v_thermal_proxy)
        out["atm_retention_score"] = min(1.0, max(0.0, ratio))
    elif snapshot.get("atm_retention_score") is not None:
        out["atm_retention_score"] = snapshot["atm_retention_score"]
    return out


__all__ = ["build"]
