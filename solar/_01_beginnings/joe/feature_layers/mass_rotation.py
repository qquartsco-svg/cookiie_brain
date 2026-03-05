"""Feature Layer 01 — 질량·회전 안정성. (물리 → JOE 스냅샷 키)

g = GM/R², v_escape = √(2GM/R), centrifugal_ratio = (ω²R)/g → S_rot = clamp01(ratio).
"""
from __future__ import annotations

import math
from typing import Any, Dict

from ..snapshot_convention import S_rot_from_centrifugal_ratio

G_SI = 6.67430e-11
M_EARTH_KG = 5.972e24
R_EARTH_M = 6.371e6
G_EARTH = 9.81
V_ESCAPE_EARTH_M_S = 11_186.0
OMEGA_EARTH_RAD_S = 7.2921159e-5


def build(snapshot: Dict[str, Any]) -> Dict[str, Any]:
    """질량·반지름·자전 → g_norm, v_escape_norm, S_rot, rotation_stable."""
    M = snapshot.get("M_kg") or M_EARTH_KG
    R = snapshot.get("R_m") or R_EARTH_M
    omega = snapshot.get("omega_spin_rad_s")
    if omega is None:
        omega = OMEGA_EARTH_RAD_S

    if R <= 0:
        return {"g_surface_norm": 0.0, "v_escape_norm": 0.0, "S_rot": 1.0, "rotation_stable": False}

    g = G_SI * M / (R * R)
    v_escape = math.sqrt(2 * G_SI * M / R)
    centrifugal = omega * omega * R
    ratio = centrifugal / g if g > 0 else 1.0

    return {
        "g_m_s2": g,
        "v_escape_m_s": v_escape,
        "g_surface_norm": g / G_EARTH if G_EARTH > 0 else 0.0,
        "v_escape_norm": v_escape / V_ESCAPE_EARTH_M_S if V_ESCAPE_EARTH_M_S > 0 else 0.0,
        "centrifugal_ratio": ratio,
        "S_rot": S_rot_from_centrifugal_ratio(ratio),
        "rotation_stable": centrifugal < g,
        "M_kg": M,
        "R_m": R,
        "omega_spin_rad_s": omega,
    }


__all__ = ["build"]
