"""조(JOE) 물리 확장 단계 — Physics-First Planet Evaluation.

9단계 확장 방향: Cosmic Field → Mass/Rotation → Formation → Atmosphere
→ Hydrology → Magnetosphere → Climate → Biosphere → Terraforming.
상세: _meta/20_CONCEPT/maps/JOE_PHYSICS_EXPANSION.md
"""
from __future__ import annotations

import math
from typing import Any, Dict

# 단계 이름 (확장 시 일관된 키 사용)
STAGE_1_COSMIC_FIELD = "cosmic_field"
STAGE_2_MASS_ROTATION = "mass_rotation"
STAGE_3_PLANET_FORMATION = "planet_formation"
STAGE_4_ATMOSPHERE = "atmosphere"
STAGE_5_HYDROLOGY = "hydrology"
STAGE_6_MAGNETOSPHERE = "magnetosphere"
STAGE_7_CLIMATE = "climate"
STAGE_8_BIOSPHERE = "biosphere"
STAGE_9_TERRAFORMING = "terraforming"

# 지구 기준 상수 (SI; 스냅샷에 M, R 없을 때 사용)
G_SI = 6.67430e-11
M_EARTH_KG = 5.972e24
R_EARTH_M = 6.371e6


def stage_1_cosmic_field(snapshot: Dict[str, Any]) -> Dict[str, Any]:
    """Stage 1 — 우주 필드 탐사. F_star = L_star/(4πr²), Habitable Zone 여부.

    스냅샷에 L_star_watt, r_au 있으면 F_star, in_habitable_zone 추가.
    없으면 빈 dict (다음 단계에서 채움).
    """
    out: Dict[str, Any] = {}
    L = snapshot.get("L_star_watt")
    r_au = snapshot.get("r_au")
    if L is not None and r_au is not None and r_au > 0:
        r_m = r_au * 1.495978707e11
        F_star = L / (4 * math.pi * r_m * r_m)
        out["F_star_W_m2"] = F_star
        # 단순 HZ: 500~2500 W/m² (지구 ~1361)
        out["in_habitable_zone"] = 500 <= F_star <= 2500
    return out


def stage_2_mass_rotation(snapshot: Dict[str, Any]) -> Dict[str, Any]:
    """Stage 2 — 정지 질량·회전 안정성.

    g = GM/R², v_escape = √(2GM/R), centrifugal = ω²R.
    조건: ω²R < g 이면 회전 안정 (붕괴 안 함).
    """
    M = snapshot.get("M_kg")
    R = snapshot.get("R_m")
    omega = snapshot.get("omega_spin_rad_s")

    if M is None:
        M = M_EARTH_KG
    if R is None:
        R = R_EARTH_M
    if omega is None:
        omega = 7.2921159e-5  # 지구 자전 [rad/s]

    g = G_SI * M / (R * R) if R > 0 else 0.0
    v_escape = math.sqrt(2 * G_SI * M / R) if R > 0 else 0.0
    centrifugal = omega * omega * R

    rotation_stable = centrifugal < g if g > 0 else False

    return {
        "g_m_s2": g,
        "v_escape_m_s": v_escape,
        "centrifugal_m_s2": centrifugal,
        "rotation_stable": rotation_stable,
        "M_kg": M,
        "R_m": R,
        "omega_spin_rad_s": omega,
    }


def merge_stage_into_snapshot(base: Dict[str, Any], stage_out: Dict[str, Any]) -> None:
    """stage 출력을 base 스냅샷에 병합 (in-place)."""
    for k, v in stage_out.items():
        if k not in base or base[k] is None:
            base[k] = v


def build_extended_snapshot(
    snapshot: Dict[str, Any],
    run_stage_1: bool = True,
    run_stage_2: bool = True,
) -> Dict[str, Any]:
    """스냅샷에 Stage 1·2 결과를 병합해 반환. 조 observer에서 사용."""
    out = dict(snapshot)
    if run_stage_1:
        merge_stage_into_snapshot(out, stage_1_cosmic_field(out))
    if run_stage_2:
        merge_stage_into_snapshot(out, stage_2_mass_rotation(out))
    return out


__all__ = [
    "STAGE_1_COSMIC_FIELD",
    "STAGE_2_MASS_ROTATION",
    "STAGE_3_PLANET_FORMATION",
    "STAGE_4_ATMOSPHERE",
    "STAGE_5_HYDROLOGY",
    "STAGE_6_MAGNETOSPHERE",
    "STAGE_7_CLIMATE",
    "STAGE_8_BIOSPHERE",
    "STAGE_9_TERRAFORMING",
    "stage_1_cosmic_field",
    "stage_2_mass_rotation",
    "merge_stage_into_snapshot",
    "build_extended_snapshot",
]
