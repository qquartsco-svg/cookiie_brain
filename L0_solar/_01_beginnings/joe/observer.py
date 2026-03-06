"""Joe Observer — 행성 동역학 관찰·분석 (1일 이전 거시 탐색).

JOE = Joe Observer Engine. 파인만 1권의 조(Joe) = 정지 관측자.
observe(rotation, water_budget, …) → analyze(planet_stress, instability) → detect(collapse).

테라포밍 탐색기 흐름: 조(JOE) → 모(MOE) → 체루빔.
- 조: 행성·우주 물리 탐사 (필드장, 중력, 회전, 대칭 등). 현재는 PANGEA §4 기반.
- 물리 확장 방향: Cosmic Field → Mass/Rotation → Formation → Atmosphere → Hydrology
  → Magnetosphere → Climate → Biosphere → Terraforming (단계별 확장 예정).
  상세: _meta/20_CONCEPT/maps/JOE_PHYSICS_EXPANSION.md, TERRAFORMING_EXPLORER_FLOW.md.
"""
from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

# InitialConditions는 eden에 있음. 순환 방지용 타입 힌트.
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from L0_solar._03_eden_os_underworld.eden.initial_conditions import InitialConditions

from .aggregator import JoeAssessmentResult, assess
from .feature_layers import build_joe_snapshot

JOE_ENGINE_FULL_NAME = "Joe Observer Engine"


def _compute_from_snapshot_local(
    snapshot: Dict[str, Any],
    config: None | Dict[str, Any] = None,
) -> Tuple[float, float]:
    """Feature Layer로 스냅샷 보강 후 PANGEA §4 Aggregator. (planet_stress, instability) 반환."""
    snapshot = build_joe_snapshot(snapshot)
    result = assess(snapshot, config=config)
    return (result.planet_stress, result.instability)


def compute_planet_stress_and_instability_from_snapshot(
    snapshot: Dict[str, Any],
    config: None | Dict[str, Any] = None,
) -> Tuple[float, float]:
    """스냅샷만 받아 (planet_stress, instability) 반환. config로 계수 오버라이드 가능."""
    return _compute_from_snapshot_local(snapshot, config=config)


def compute_planet_stress_and_instability(
    ic: "InitialConditions",
    water_snapshot: Optional[Any] = None,
    config: None | Dict[str, Any] = None,
) -> Tuple[float, float]:
    """InitialConditions + 물 예산 스냅샷 → (planet_stress, instability). FirmamentLayer.step(instability=...) 에 넣을 값."""
    snapshot: Dict[str, Any] = {}
    snapshot["omega_spin_rad_s"] = getattr(ic, "omega_spin_rad_s", None)
    snapshot["obliquity_deg"] = getattr(ic, "obliquity_deg", None)
    snapshot["GEL_surface_eden_m"] = getattr(ic, "GEL_surface_eden_m", None)
    snapshot["W_canopy_ref_km3"] = getattr(ic, "W_canopy_ref_km3", None)
    if water_snapshot and isinstance(water_snapshot, dict):
        snapshot.setdefault("W_surface", water_snapshot.get("W_surface"))
        snapshot.setdefault("W_canopy", water_snapshot.get("W_canopy"))
        snapshot.setdefault("W_total", water_snapshot.get("W_total"))
        snapshot.setdefault("dW_surface_dt_norm", water_snapshot.get("dW_surface_dt_norm"))
    for k in ("sigma_plate", "P_w", "S_rot"):
        if hasattr(ic, k):
            snapshot.setdefault(k, getattr(ic, k))
    return compute_planet_stress_and_instability_from_snapshot(snapshot, config=config)


def assess_planet(
    snapshot: Dict[str, Any],
    config: None | Dict[str, Any] = None,
) -> JoeAssessmentResult:
    """스냅샷 → 전체 평가(planet_stress, instability, habitability_label, config_used). API/리포트용."""
    snapshot = build_joe_snapshot(snapshot)
    return assess(snapshot, config=config)


__all__ = [
    "JOE_ENGINE_FULL_NAME",
    "compute_planet_stress_and_instability",
    "compute_planet_stress_and_instability_from_snapshot",
    "assess_planet",
    "JoeAssessmentResult",
]
