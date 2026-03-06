"""_08_ice_age.ice_sheet — 빙상 질량수지 & 기하학

Continental ice sheet growth following polar sea ice (_07).

물리 모델:
  질량수지:  dV/dt = B_net · A  [km³/yr]
  평균 두께:  h_mean = 1.5 km  (LGM calibrated)
  면적:       A = V / h_mean    [km²]
  적도측 위도: A_cap(φ) = 2π R² (1 − sin φ)  → φ = arcsin(1 − A/2πR²)
  해수면:     ΔSL = −(V − V₀) · ρ_ice/ρ_water / A_ocean  [m]

  강설 누적:  B_acc(T_pole) = B_max · exp(−½((T_pole−T_opt)/σ)²)
             극점의 온도 ~ −15°C에서 최대 강설 (수분 수송 최적)
  융빙 제거:  B_abl(T_margin) = k_abl · max(0, T_margin)
             T_margin = 빙하선(φ_ice) 위도 온도 (적도~극 선형 보간)

LGM 보정:
  V_LGM ≈ 5e7 km³  →  ΔSL ≈ −120 m        ✓
  A_LGM ≈ 3.3e7 km²  →  φ_ice ≈ 60°N       ✓
  성장 시간: V×2 ≈ 3500 yr  →  LGM 도달 ≈ 20,000 yr ✓

참조:
  Bahr et al. 1997, J. Geophys. Res.
  Oerlemans 1981, Nature
  CLIMAP 1981 (LGM extent)
"""

from __future__ import annotations

from dataclasses import dataclass
from math import sqrt, sin, cos, asin, exp, pi


# ── 지구 기하 ──────────────────────────────────────────────────────────────────
R_EARTH_KM   = 6371.0
A_OCEAN_M2   = 3.61e14       # m²  (전지구 해양 면적)
A_2PI_R2_KM2 = 2.0 * pi * R_EARTH_KM**2   # ≈ 2.55e8 km²

# ── 얼음 물리 상수 ─────────────────────────────────────────────────────────────
RHO_ICE      = 917.0         # kg/m³
RHO_WATER    = 1025.0        # kg/m³
H_MEAN_KM    = 1.5           # km   LGM 기준 대륙 빙상 평균 두께

# ── 질량수지 기본값 ────────────────────────────────────────────────────────────
B_ACC_MAX    = 0.50          # m/yr   최대 강설 누적률
T_OPT_ACC    = -15.0         # °C    최적 강설 기온
SIGMA_ACC    = 15.0          # K     강설 가우시안 폭
K_ABL        = 1.5           # m/yr/°C  빙하선 융빙 계수

# ── 온도 구조 ──────────────────────────────────────────────────────────────────
T_EQUATOR_C  = 30.0          # °C   적도 평균 기온 (근사 고정)
T_LAT_EXP    = 0.8           # 위도 온도 분포 지수


@dataclass
class IceSheetParams:
    """빙상 모델 파라미터."""
    b_acc_max:    float = B_ACC_MAX
    t_opt_acc_C:  float = T_OPT_ACC
    sigma_acc:    float = SIGMA_ACC
    k_abl:        float = K_ABL
    h_mean_km:    float = H_MEAN_KM


@dataclass
class IceSheetState:
    """빙상 현재 상태."""
    V_km3:       float   # 총 부피 [km³]
    A_km2:       float   # 면적 [km²]
    phi_ice_deg: float   # 적도측 한계 위도 [°N]
    sea_level_m: float   # 해수면 변화 [m]  (음수 = 하강)
    B_acc:       float   # 강설 누적률 [m/yr]
    B_abl:       float   # 융빙 제거률 [m/yr]
    B_net:       float   # 순 질량수지 [m/yr]


def temp_at_latitude(phi_deg: float, T_pole_C: float) -> float:
    """위도 φ에서의 기온 추정 [°C].

    극-적도 온도 기울기 경험 보간:
      T(φ) = T_pole + (T_equator − T_pole) × (1 − (φ/90)^α)
    """
    f = max(0.0, min(1.0, phi_deg / 90.0))
    return T_pole_C + (T_EQUATOR_C - T_pole_C) * (1.0 - f ** T_LAT_EXP)


def mass_balance(
    T_pole_C:    float,
    phi_ice_deg: float,
    params:      IceSheetParams,
) -> tuple[float, float]:
    """빙상 순 질량수지 계산.

    Returns
    -------
    (B_acc, B_abl) [m/yr water equivalent]
    """
    # 강설 누적 (가우시안, 극지 기온 기반)
    dT    = T_pole_C - params.t_opt_acc_C
    B_acc = params.b_acc_max * exp(-0.5 * (dT / params.sigma_acc) ** 2)

    # 융빙 제거 (빙하선 위도 기온 기반)
    T_margin = temp_at_latitude(phi_ice_deg, T_pole_C)
    B_abl    = max(0.0, params.k_abl * T_margin)

    return B_acc, B_abl


def volume_to_geometry(
    V_km3:    float,
    h_mean_km: float = H_MEAN_KM,
) -> tuple[float, float]:
    """빙상 부피 → (면적 [km²], 적도측 한계 위도 [°N]).

    A = V / h_mean
    φ_ice : sin φ = 1 − A / (2π R²)
    """
    V_km3  = max(0.0, V_km3)
    A_km2  = V_km3 / h_mean_km

    sin_phi  = 1.0 - min(1.0, A_km2 / A_2PI_R2_KM2)
    phi_deg  = max(0.0, asin(max(-1.0, sin_phi)) * 180.0 / pi)

    return A_km2, phi_deg


def sea_level_change(V_km3: float, V_ref_km3: float) -> float:
    """빙상 부피 변화 → 해수면 변화 [m].

    ΔSL = −(V − V₀) · ρ_ice/ρ_water / A_ocean
    V [km³] → V × 1e9 [m³]
    """
    dV_m3  = (V_km3 - V_ref_km3) * 1.0e9
    return -(dV_m3 * RHO_ICE / RHO_WATER) / A_OCEAN_M2


__all__ = [
    "IceSheetParams", "IceSheetState",
    "mass_balance", "volume_to_geometry", "sea_level_change",
    "temp_at_latitude",
    "H_MEAN_KM", "R_EARTH_KM", "RHO_ICE", "RHO_WATER",
]
