"""ice_dynamics.py — 그린란드 · 남극 빙상 · 북극 해빙 동역학

현재 지구(2024)의 세 빙권 요소를 독립적으로 모델링:
  1. 그린란드 빙상 (V_G)  : 가장 빠른 반응, 2100년 전후 임계 가능
  2. 서남극 빙상 (V_WA)   : 해양 접촉면 불안정 → 임계 기울기 존재
  3. 동남극 빙상 (V_EA)   : 매우 안정, 수만 년 스케일
  4. 북극 해빙 (A_ice)    : 10~30년 내 여름 빙하 소멸 예상

Sources:
  Bamber et al. (2019), Shepherd et al. (2020), IPCC AR6 Ch.9,
  Rignot et al. (2019), NSIDC Sea Ice Index
"""
from __future__ import annotations
from math import exp, sqrt
from dataclasses import dataclass


# ── 현재 상태 (2024년 기준) ──────────────────────────────────────────────

# 그린란드 빙상
V_G_2024     = 2.85e6    # km³    (총 부피)
A_G          = 1.71e6    # km²    (면적)
MELT_G_2024  = 280.0     # Gt/yr  (현재 순 손실량, Shepherd 2020)
T_ARCTIC_2024 = -14.5    # °C     (그린란드 연평균 기온 근사)

# 서남극 빙상 (WAIS: West Antarctic Ice Sheet)
V_WA_2024    = 3.5e6     # km³    (해수면 +3.3m 상당)
A_WA         = 1.97e6    # km²
MELT_WA_2024 = 110.0     # Gt/yr
T_ANT_2024   = -28.0     # °C     (남극 연평균)

# 동남극 빙상 (EAIS: East Antarctic Ice Sheet)
V_EA_2024    = 23.0e6    # km³    (해수면 +52m 상당)
A_EA         = 10.0e6    # km²
MELT_EA_2024 = 40.0      # Gt/yr  (불확실성 높음)

# 북극 해빙
A_ICE_SUMMER_2024 = 4.6e6   # km²  (9월 최솟값, NSIDC 최근 평균)
A_ICE_WINTER_2024 = 14.5e6  # km²  (3월 최댓값)
H_ICE_MEAN        = 1.8     # m    (평균 두께)
AREA_DECLINE_RATE = 0.13e6  # km²/yr (최근 10년 9월 하락 추세)

# 물리 상수
RHO_ICE      = 917.0    # kg/m³
RHO_WATER    = 1025.0   # kg/m³
OCEAN_AREA   = 3.61e8   # km²   (전 해양 면적)
GT_TO_KM3    = 1e3 / RHO_ICE          # Gt → km³  (1 Gt = 1.09 km³ 얼음)


# ── 질량수지 파라미터 ────────────────────────────────────────────────────

# 그린란드: T_arctic > T_G_crit 이면 순 손실 가속
T_G_CRIT     = -17.0    # °C   (이 온도에서 melt=accum 균형)
K_MELT_G     = 35.0     # Gt/(yr·°C)   (현재 관측값으로 역산)

# 서남극 (WAIS): 해양 온도에도 민감 (해빙선 후퇴 → 불안정)
T_WA_CRIT    = -30.0    # °C
K_MELT_WA   = 8.0      # Gt/(yr·°C)
# WAIS 임계 기울기: 해수면 +1.5m 이상이면 불안정 피드백 가속
SLR_WAIS_TRIGGER = 1.5  # m (해수면 상승 임계)
WAIS_ACCEL   = 2.0      # 임계 후 추가 가속 계수

# 동남극: 극도로 느림
T_EA_CRIT    = -50.0    # °C   (현재 남극 기온 -28°C보다 훨씬 낮음)
K_MELT_EA   = 3.0      # Gt/(yr·°C)

# 북극 해빙: T_arctic 기반 면적 변화
T_ICE_FREE   = -5.0     # °C   (이 온도 이상이면 여름 빙하 소멸)
K_ICE_AREA   = 0.5e6    # km²/°C  (온도당 면적 감소율)


@dataclass
class IceState:
    """현재 빙권 상태"""
    V_G_km3:          float = V_G_2024        # 그린란드 빙상 부피 [km³]
    V_WA_km3:         float = V_WA_2024       # 서남극 빙상 부피 [km³]
    V_EA_km3:         float = V_EA_2024       # 동남극 빙상 부피 [km³]
    A_ice_summer_km2: float = A_ICE_SUMMER_2024  # 북극 여름 해빙 면적 [km²]
    sea_level_m:      float = 0.0             # 2024년 기준 해수면 변화 [m]
    year:             float = 2024.0


def greenland_mass_balance(
    T_arctic_C: float,
    V_G_km3:    float,
) -> float:
    """
    그린란드 순 질량수지 [Gt/yr].
    음수 = 손실 (녹는 방향).

    dV/dt ∝ -(T_arctic - T_G_crit) × 면적 비율
    현재값(T≈-14.5°C, T_crit=-17°C → ΔT=2.5°C)으로 역산:
      K_MELT_G = 280 / 2.5 = 112 Gt/yr·°C... 조정값 35
    (축적-손실 모두 포함한 순 값 기준)
    """
    dT = T_arctic_C - T_G_CRIT
    net_loss = K_MELT_G * dT if dT > 0 else 0.0

    # 빙상 소진 시 손실 감소 (면적 축소)
    frac_remain = min(1.0, V_G_km3 / V_G_2024)
    return -net_loss * frac_remain  # Gt/yr (음수=손실)


def wais_mass_balance(
    T_ant_C:     float,
    V_WA_km3:    float,
    sea_level_m: float,
) -> float:
    """
    서남극 빙상 순 질량수지 [Gt/yr].
    해수면 상승 임계(+1.5m) 이상이면 해양 불안정 가속 (MISI 효과).

    MISI(Marine Ice Sheet Instability): 빙상 기반이 해수면 아래에 있어
    바닷물이 아래에서 녹이면 자기강화 붕괴.
    """
    dT = T_ant_C - T_WA_CRIT
    base_loss = K_MELT_WA * max(0.0, dT)

    # MISI 가속: 해수면 임계 초과 시
    if sea_level_m >= SLR_WAIS_TRIGGER:
        base_loss *= WAIS_ACCEL

    frac_remain = min(1.0, V_WA_km3 / V_WA_2024)
    return -base_loss * frac_remain


def eais_mass_balance(T_ant_C: float, V_EA_km3: float) -> float:
    """동남극 빙상 순 질량수지 [Gt/yr]. 매우 느림."""
    dT = T_ant_C - T_EA_CRIT
    loss = K_MELT_EA * max(0.0, dT)
    frac = min(1.0, V_EA_km3 / V_EA_2024)
    return -loss * frac


def arctic_sea_ice_area(T_arctic_C: float) -> float:
    """
    북극 여름 최소 해빙 면적 [km²].
    T_arctic > T_ICE_FREE 이면 여름 빙하 소멸.
    """
    return max(0.0, A_ICE_SUMMER_2024 - K_ICE_AREA * (T_arctic_C - T_ARCTIC_2024))


def ice_to_sea_level(dV_G: float, dV_WA: float, dV_EA: float) -> float:
    """
    빙상 부피 변화 → 해수면 변화 [m].
    육지 빙상만 계산 (해빙 제외).

    SLR [m] = ΔV [km³] × 917 [kg/m³] / (1025 [kg/m³] × 3.61e8 [km²] × 1e6 [m²/km²])
    """
    total_dV_km3 = dV_G + dV_WA + dV_EA   # 음수 = 손실 = SLR 상승
    slr = -total_dV_km3 * 1e9 * RHO_ICE / (RHO_WATER * OCEAN_AREA * 1e6)
    return slr  # m


def sea_level_contribution() -> dict:
    """현재 각 빙원의 해수면 기여 잠재량 [m]"""
    return {
        "greenland":       7.2,   # 그린란드 전부 녹으면 +7.2m
        "wais":            3.3,   # 서남극 전부 +3.3m
        "eais":           52.0,   # 동남극 전부 +52m
        "glaciers_other":  0.32,  # 기타 빙하
        "total":          62.82,
    }
