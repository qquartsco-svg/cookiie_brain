"""JOE 표준 스냅샷 키 규약.

조(JOE)는 "물리 → 스냅샷" 변환 결과만 소비한다. Aggregator(_core)는 아래 키 중
필요한 것만 읽어 planet_stress, instability, habitability_label을 산출한다.

핵심 6키 (PANGEA §4):
  sigma_plate, P_w, S_rot, W_surface, W_total, dW_surface_dt_norm

확장 키 (Feature Layer가 채움):
  (1) Cosmic: F_star_norm, cosmic_ray_flux_norm, stellar_wind_pressure_norm, in_habitable_zone
  (2) Mass/Gravity: g_surface_norm, v_escape_norm, atm_retention_score
  (3) Rotation: omega_spin_rad_s, S_rot = clamp01(centrifugal_ratio), rotation_stable
  (4) Water: T_eq_norm, liquid_window_score, P_surface_proxy_norm
  (5) Plate: tectonics_score → sigma_plate, P_w (proxy)
"""
from __future__ import annotations

# PANGEA §4 Aggregator가 직접 사용하는 키
CORE_KEYS = (
    "sigma_plate",
    "P_w",
    "S_rot",
    "W_surface",
    "W_total",
    "dW_surface_dt_norm",
)

# S_rot 표준 정의: 무차원 centrifugal_ratio를 [0,1]로 클램프
# centrifugal_ratio = (ω² R) / g  → 0에 가까우면 안정, 1 근처면 위험
def S_rot_from_centrifugal_ratio(centrifugal_ratio: float) -> float:
    """centrifugal_ratio = (ω² R)/g → S_rot ∈ [0,1]. 행성 크기/질량 무관 비교."""
    return max(0.0, min(1.0, float(centrifugal_ratio)))


__all__ = ["CORE_KEYS", "S_rot_from_centrifugal_ratio"]
