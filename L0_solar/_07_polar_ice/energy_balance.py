"""polar_ice.energy_balance — 극지방 복사 수지 모델

극지방 에너지 방정식:
  C · dT/dt = Q_sw_in - Q_lw_out + Q_ocean + Q_latent

  Q_sw_in  = S₀/4 · cos(θ_z) · (1 - α) · (1 - f_block)   [태양 단파 입사]
  Q_lw_out = ε · σ · T⁴                                    [Stefan-Boltzmann 복사]
  Q_ocean  = 극지방 해양 열 공급 (충돌 후 감소)
  Q_latent = 결빙/융해 잠열 (얼음 있을 때)

알베도 피드백:
  α_ocean = 0.06  (개방 해양)
  α_ice   = 0.70  (신설)  → 0.50 (노화 얼음)
  α_mixed = α_ocean · (1 - f_ice) + α_ice · f_ice

극지방 태양 입사 기하:
  북위 90° 기준: 연평균 일사량 Q_polar ≈ S₀/4 · (1 - α) · insolation_factor
  insolation_factor ≈ 0.20  (연평균 극지방 ~20% of S₀)
"""

from __future__ import annotations

import numpy as np
from dataclasses import dataclass
from math import pi, cos, sin, acos, sqrt, exp
from typing import Optional


# ── 물리 상수 ─────────────────────────────────────────────────────────────────
S0           = 1361.0     # W/m²  태양 상수
SIGMA        = 5.6704e-8  # W/(m²·K⁴)  Stefan-Boltzmann
EMISSIVITY   = 0.95       # 해양/얼음 복사율
HEAT_CAP_OCN = 4e8        # J/(m²·K)  혼합층 열용량 (100m, ρ=1025, c=4000)
HEAT_CAP_ICE = 5e6        # J/(m²·K)  얼음층 열용량 (얼음 있을 때)

# 알베도
ALBEDO_OCEAN     = 0.06
ALBEDO_ICE_FRESH = 0.75   # 신설 (fresh snow)
ALBEDO_ICE_OLD   = 0.50   # 노화 해빙

# 극지방 연평균 일사량 보정 계수 (위도 θ)
# Q_polar(θ) = S₀/4 · f_lat(θ)
# f_lat(90°) ≈ 0.17,  f_lat(75°) ≈ 0.30,  f_lat(60°) ≈ 0.46
def insolation_factor(lat_deg: float) -> float:
    """위도에 따른 연평균 일사량 계수 (0~1)."""
    lat = abs(lat_deg) * pi / 180.0
    # 단순 근사: Q ∝ cos(lat)^0.6 (실제보다 보수적)
    return max(0.0, cos(lat) ** 0.6)


# 자오선 대기 열 수송 계수 (Budyko-Sellers 기후 모델)
# Q_atm = λ · (T_global - T_pole)
# λ ≈ 3.3 W/(m²·K)  (관측 기반)
LAMBDA_TRANSPORT = 3.3   # W/(m²·K)


@dataclass
class PolarSurfaceState:
    """극지방 표면 상태."""
    T_K:           float   # 표면 온도 [K]
    albedo:        float   # 현재 알베도
    f_ice:         float   # 얼음 피복률 (0-1)
    Q_net:         float   # 순 에너지 플럭스 [W/m²]
    Q_sw_in:       float   # 단파 입사 [W/m²]
    Q_lw_out:      float   # 장파 방출 [W/m²]
    Q_ocean_in:    float   # 해양 열 공급 [W/m²]


def equilibrium_temperature(
    lat_deg:     float,
    f_block:     float = 0.0,
    f_ice:       float = 0.0,
    Q_ocean:     float = 15.0,
    T_global_K:  float = 288.0,
    albedo_ice:  float = ALBEDO_ICE_FRESH,
) -> float:
    """복사 평형 극지방 온도 계산 [K].

    Budyko-Sellers 에너지 수지:
      S₀/4·f_lat·(1-α)·(1-f_block) + Q_ocean + λ·(T_global - T_pole) = ε·σ·T⁴

    대기 자오선 열 수송(λ)이 포함되어 있어 실제 극지방 온도(-20~-30°C)를 재현.
    """
    from math import exp
    f_lat  = insolation_factor(lat_deg)
    alpha  = ALBEDO_OCEAN * (1 - f_ice) + albedo_ice * f_ice
    Q_sw   = S0 / 4.0 * f_lat * (1.0 - alpha) * (1.0 - f_block)

    # 비선형 풀이 (Newton iteration)
    T = T_global_K - 30.0   # 초기값
    for _ in range(50):
        Q_atm  = LAMBDA_TRANSPORT * (T_global_K - T)
        Q_lw   = EMISSIVITY * SIGMA * T ** 4
        F      = Q_sw + Q_ocean + Q_atm - Q_lw
        dF     = -LAMBDA_TRANSPORT - 4.0 * EMISSIVITY * SIGMA * T ** 3
        T     -= F / dF
    return float(T)


def polar_energy_balance(
    T_K:        float,
    lat_deg:    float,
    f_block:    float,
    f_ice:      float,
    Q_ocean:    float = 15.0,
    T_global_K: float = 288.0,
) -> PolarSurfaceState:
    """현재 온도에서 복사 수지 계산 → 순 에너지 플럭스.

    Budyko-Sellers:
      Q_net = Q_sw + Q_ocean + Q_atm(λ·ΔT) - Q_lw

    Q_net > 0 : 가열 (온도 상승)
    Q_net < 0 : 냉각 (온도 하강 / 결빙)
    """
    f_lat  = insolation_factor(lat_deg)
    alpha  = ALBEDO_OCEAN * (1 - f_ice) + ALBEDO_ICE_OLD * f_ice
    Q_sw   = S0 / 4.0 * f_lat * (1.0 - alpha) * (1.0 - f_block)
    Q_lw   = EMISSIVITY * SIGMA * T_K ** 4
    Q_atm  = LAMBDA_TRANSPORT * (T_global_K - T_K)   # 자오선 열 수송
    Q_net  = Q_sw + Q_ocean + Q_atm - Q_lw

    return PolarSurfaceState(
        T_K=T_K, albedo=alpha, f_ice=f_ice,
        Q_net=Q_net, Q_sw_in=Q_sw, Q_lw_out=Q_lw, Q_ocean_in=Q_ocean,
    )


def temperature_tendency(
    T_K:        float,
    lat_deg:    float,
    f_block:    float,
    f_ice:      float,
    Q_ocean:    float = 15.0,
    T_global_K: float = 288.0,
    dt_s:       float = 86400.0,
) -> float:
    """dT/dt 계산 [K/s].

    C · dT/dt = Q_net
    """
    state = polar_energy_balance(T_K, lat_deg, f_block, f_ice, Q_ocean, T_global_K)
    C     = HEAT_CAP_OCN * (1 - f_ice) + HEAT_CAP_ICE * f_ice
    return state.Q_net / C


def ocean_heat_flux_after_impact(
    t_yr:      float,
    Q0:        float = 15.0,
    f_reduce:  float = 0.5,
    tau_yr:    float = 5.0,
) -> float:
    """충돌 후 해양 열 공급 감소 모델.

    충돌 직후: 해양 혼합층 교란 + 극 순환 약화로 Q_ocean 감소.
    Q(t) = Q0 · [f_reduce + (1-f_reduce)·exp(-t/τ)]

    f_reduce = 최솟값 분율 (기본 50% 감소)
    tau_yr   = 회복 시상수 [년]
    """
    reduction = f_reduce + (1.0 - f_reduce) * exp(-t_yr / tau_yr)
    return Q0 * reduction


__all__ = [
    "PolarSurfaceState",
    "insolation_factor", "equilibrium_temperature",
    "polar_energy_balance", "temperature_tendency",
    "ocean_heat_flux_after_impact",
    "S0", "SIGMA", "EMISSIVITY",
    "ALBEDO_OCEAN", "ALBEDO_ICE_FRESH", "ALBEDO_ICE_OLD",
    "HEAT_CAP_OCN", "LAMBDA_TRANSPORT",
]
