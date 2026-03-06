"""polar_ice.climate — 충돌 후 대기·기후 강제(forcing) 다이나믹스

루시퍼 임팩트 이후 대기 상태 변화를 시간 함수로 모델링.

물리 연쇄:
  충돌 에너지 → 분출물/에어로졸 주입 → 태양광 차단
             → 전지구 냉각 → 극지방 증폭 냉각
             → 수증기 캐노피 붕괴 → 강수/적설 급증

핵심 방정식:
  AOD(t)   = τ₀ · exp(-t / τ_aer)          [에어로졸 광학 깊이]
  f_block  = 1 - exp(-AOD(t))               [태양광 차단율]
  ΔT_g(t)  = ΔT₀ · exp(-t / τ_clim)        [전지구 평균 냉각]
  ΔT_p(t)  = A_polar · ΔT_g(t)             [극지방 증폭 냉각]
  C_H2O(t) = C₀ · exp(-t / τ_h2o)          [수증기 캐노피 감소]
"""

from __future__ import annotations

import numpy as np
from dataclasses import dataclass
from math import exp, log, sqrt
from typing import Optional


# ── 물리 상수 ────────────────────────────────────────────────────────────────
SOLAR_CONSTANT    = 1361.0      # W/m²  (태양 상수 S₀)
STEFAN_BOLTZMANN  = 5.6704e-8   # W/(m²·K⁴)
T_PREINDUSTRIAL   = 288.0       # K  충돌 전 전지구 평균 기온
T_POLE_PREIMPACT  = 250.0       # K  충돌 전 극지방 평균 기온 (북극권)
POLAR_AMPLIFY     = 2.5         # 극지방 냉각 증폭 계수 (전지구 평균 대비)


@dataclass
class ImpactClimateForcingParams:
    """충돌 기후 강제 파라미터.

    Parameters
    ----------
    E_eff_MT       : 유효 충돌 에너지 [메가톤 TNT]
    delta_H2O_kg   : 대기 주입 수증기 질량 [kg]  (LuciferEngine 출력)
    delta_T_pole_K : 충돌 직후 극지방 온도 강하 [K]  (LuciferEngine 출력)
    tau_aerosol_yr : 성층권 에어로졸 수명 [년]  (기본 2년)
    tau_climate_yr : 전지구 기온 회복 시상수 [년]  (기본 10년)
    tau_h2o_yr     : 수증기 캐노피 소진 시상수 [년]  (기본 1.5년)
    """
    E_eff_MT:        float
    delta_H2O_kg:    float = 0.0
    delta_T_pole_K:  float = 0.0    # 음수 = 냉각
    tau_aerosol_yr:  float = 2.0
    tau_climate_yr:  float = 10.0
    tau_h2o_yr:      float = 1.5


@dataclass
class ClimateState:
    """시각 t에서의 기후 상태."""
    t_yr:            float   # 충돌 후 경과 시간 [년]
    aod:             float   # 에어로졸 광학 깊이
    f_solar_block:   float   # 태양광 차단율  (0=완전 투과, 1=완전 차단)
    T_global_K:      float   # 전지구 평균 기온 [K]
    T_pole_K:        float   # 극지방 기온 [K]
    dT_pole_K:       float   # 충돌 전 대비 극지방 온도 변화 [K]
    H2O_canopy_kg:   float   # 잔여 수증기 캐노피 [kg]
    is_below_freeze: bool    # 극지방 빙점(-1.8°C = 271.35K) 이하 여부


_SEAWATER_FREEZE_K = 271.35   # 해수 결빙 온도 [K]  (-1.8°C)


def aod_from_energy(E_eff_MT: float) -> float:
    """충돌 에너지 → 초기 에어로졸 광학 깊이(AOD) 추정.

    경험식: τ₀ ≈ 0.5 · (E_MT / 1e5)^0.3
    기준: Chicxulub급(~1e8 MT) → τ₀ ≈ 5~10 (완전 핵겨울)
          Lucifer급 (5km, ~1e6 MT) → τ₀ ≈ 1~3
    """
    if E_eff_MT <= 0:
        return 0.0
    return 0.5 * (E_eff_MT / 1e5) ** 0.3


def climate_state_at(t_yr: float, p: ImpactClimateForcingParams) -> ClimateState:
    """시각 t_yr에서의 기후 상태 계산.

    Parameters
    ----------
    t_yr : 충돌 후 경과 시간 [년]  (t=0 = 충돌 직후)
    p    : ImpactClimateForcingParams

    Returns
    -------
    ClimateState
    """
    t = max(t_yr, 0.0)

    # 에어로졸 감쇠
    tau0  = aod_from_energy(p.E_eff_MT)
    aod   = tau0 * exp(-t / p.tau_aerosol_yr)
    f_blk = 1.0 - exp(-aod)   # 차단율

    # 전지구 기온 강하 (t=0 피크)
    # ΔT₀_global = -3 · log10(1 + E_MT/1e4) [K]  (경험 스케일링)
    dT0_global = -3.0 * log(1.0 + p.E_eff_MT / 1e4) / log(10.0)
    dT_global  = dT0_global * exp(-t / p.tau_climate_yr)
    T_global   = T_PREINDUSTRIAL + dT_global

    # 극지방 증폭 냉각
    # 충돌 직후 추가 강하 + 장기 회복
    dT0_pole  = p.delta_T_pole_K if p.delta_T_pole_K != 0.0 else dT0_global * POLAR_AMPLIFY
    dT_pole   = dT0_pole * exp(-t / p.tau_climate_yr)
    T_pole    = T_POLE_PREIMPACT + dT_pole

    # 수증기 캐노피 감소
    h2o = p.delta_H2O_kg * exp(-t / p.tau_h2o_yr) if p.delta_H2O_kg > 0 else 0.0

    return ClimateState(
        t_yr=t,
        aod=aod,
        f_solar_block=f_blk,
        T_global_K=T_global,
        T_pole_K=T_pole,
        dT_pole_K=dT_pole,
        H2O_canopy_kg=h2o,
        is_below_freeze=T_pole < _SEAWATER_FREEZE_K,
    )


def climate_trajectory(p: ImpactClimateForcingParams,
                        t_max_yr: float = 30.0,
                        dt_yr: float = 0.1):
    """충돌 후 기후 궤적 계산.

    Returns
    -------
    list[ClimateState]  시계열
    """
    t_arr = np.arange(0.0, t_max_yr + dt_yr * 0.5, dt_yr)
    return [climate_state_at(float(t), p) for t in t_arr]


def freeze_onset_time(p: ImpactClimateForcingParams,
                      t_max_yr: float = 50.0,
                      dt_yr: float = 0.01) -> Optional[float]:
    """극지방 빙점 이하로 처음 내려가는 시각 [년].

    Returns None if never freezes in t_max_yr.
    """
    t_arr = np.arange(0.0, t_max_yr, dt_yr)
    for t in t_arr:
        s = climate_state_at(float(t), p)
        if s.is_below_freeze:
            return float(t)
    return None


__all__ = [
    "ImpactClimateForcingParams", "ClimateState",
    "aod_from_energy", "climate_state_at",
    "climate_trajectory", "freeze_onset_time",
    "SOLAR_CONSTANT", "STEFAN_BOLTZMANN",
    "T_PREINDUSTRIAL", "T_POLE_PREIMPACT",
    "_SEAWATER_FREEZE_K",
]
