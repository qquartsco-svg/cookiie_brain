"""Feature Layer 00 — 우주 필드장. (물리 → JOE 스냅샷 키)

산출: F_star_norm, cosmic_ray_flux_norm, stellar_wind_pressure_norm, in_habitable_zone.
"""
from __future__ import annotations

import math
from typing import Any, Dict

# 참조: 지구 궤도 복사 ~1361 W/m²
F_STAR_EARTH_W_M2 = 1361.0


def build(snapshot: Dict[str, Any]) -> Dict[str, Any]:
    """우주 필드 입력 → JOE 표준 키. 기존 스냅샷에 병합할 추가분만 반환."""
    out: Dict[str, Any] = {}
    L = snapshot.get("L_star_watt")
    r_au = snapshot.get("r_au")
    if L is not None and r_au is not None and r_au > 0:
        r_m = r_au * 1.495978707e11
        F_star = L / (4 * math.pi * r_m * r_m)
        out["F_star_W_m2"] = F_star
        out["F_star_norm"] = F_star / F_STAR_EARTH_W_M2 if F_STAR_EARTH_W_M2 > 0 else 0.0
        out["in_habitable_zone"] = 500 <= F_star <= 2500
    for k in ("cosmic_ray_flux_norm", "stellar_wind_pressure_norm"):
        if snapshot.get(k) is not None:
            out[k] = snapshot[k]
    return out


__all__ = ["build", "F_STAR_EARTH_W_M2"]
