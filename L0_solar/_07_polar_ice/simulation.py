"""polar_ice.simulation — 루시퍼 임팩트 후 극지방 결빙 통합 시뮬레이션

전체 물리 연쇄:
  [LuciferEngine output]
      E_eff_MT, delta_H2O_kg, delta_T_pole_K
        ↓
  [climate.py]
      AOD(t), f_block(t), T_global(t), T_pole_forcing(t)
        ↓
  [energy_balance.py]
      복사 수지 → T_pole(t) 시간 적분 (Euler)
      알베도 피드백: 얼음 생기면 α 상승 → 추가 냉각
        ↓
  [stefan_ice.py]
      T_pole < T_freeze → 결빙 시작 타이밍 기록
      h_ice(t): Stefan 법칙으로 얼음 두께 성장
      h_snow(t): 수증기 캐노피 → 적설량
        ↓
  [PolarSimResult]
      시계열 전체 + 이벤트 기록

상태벡터 (매 스텝):
  [T_pole, h_ice, h_snow, f_ice, aod, H2O_canopy]
"""

from __future__ import annotations

import numpy as np
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

from .climate       import (ImpactClimateForcingParams, climate_state_at,
                             _SEAWATER_FREEZE_K, T_POLE_PREIMPACT)
from .energy_balance import (polar_energy_balance, temperature_tendency,
                              ocean_heat_flux_after_impact,
                              HEAT_CAP_OCN)
from .stefan_ice    import (stefan_thickness, ice_growth_rate,
                             snow_accumulation, IceState,
                             T_FREEZE_SW, H_MAX_MULTI_YEAR)


# ── 시뮬레이션 스텝 상태 ────────────────────────────────────────────────────

@dataclass
class SimStep:
    """단일 시간 스텝의 전체 상태."""
    t_yr:         float   # 충돌 후 경과 [년]
    t_days:       float   # [일]
    T_pole_K:     float   # 극지방 표면 온도 [K]
    T_pole_C:     float   # [°C]
    h_ice_m:      float   # 얼음 두께 [m]
    h_snow_m:     float   # 적설 두께 [m]
    f_ice:        float   # 얼음 피복률 (0-1)
    albedo:       float   # 표면 알베도
    aod:          float   # 에어로졸 광학 깊이
    f_solar_block: float  # 태양광 차단율
    Q_net:        float   # 순 에너지 플럭스 [W/m²]
    Q_ocean:      float   # 해양 열 공급 [W/m²]
    H2O_canopy_kg: float  # 잔여 수증기 [kg]
    is_frozen:    bool    # 결빙 상태
    growth_rate_m_yr: float  # 연간 얼음 성장률 [m/yr]


@dataclass
class PolarSimResult:
    """시뮬레이션 전체 결과."""
    steps:           List[SimStep]
    freeze_onset_yr: Optional[float]   # 첫 결빙 시각 [년]
    max_ice_m:       float             # 최대 얼음 두께 [m]
    max_ice_yr:      float             # 최대 두께 도달 시각 [년]
    ice_persists:    bool              # 시뮬레이션 종료 시 얼음 유지 여부
    t_max_yr:        float
    lat_deg:         float
    events:          List[Dict[str, Any]] = field(default_factory=list)

    def summary(self) -> str:
        lines = [
            "=" * 62,
            "  루시퍼 임팩트 → 극지방 결빙 시뮬레이션 결과",
            "=" * 62,
            f"  시뮬레이션 기간: {self.t_max_yr:.0f}년  |  위도: {self.lat_deg:.0f}°N",
            "",
        ]
        if self.freeze_onset_yr is not None:
            lines.append(f"  ✦ 첫 결빙 발생:  충돌 후 {self.freeze_onset_yr:.2f}년")
        else:
            lines.append("  ✦ 결빙 미발생 (시뮬레이션 기간 내)")

        lines += [
            f"  ✦ 최대 얼음 두께: {self.max_ice_m:.2f} m  ({self.max_ice_yr:.1f}년 차)",
            f"  ✦ 얼음 유지:      {'YES — 항구적 해빙 형성' if self.ice_persists else 'NO — 일시적 결빙'}",
            "",
            f"  {'시각(년)':>8} {'T_극(°C)':>10} {'얼음(m)':>8} {'적설(m)':>8} {'알베도':>7} {'AOD':>6} {'차단률':>7}",
            f"  {'-'*56}",
        ]
        # 5년 간격으로 출력
        shown = [s for s in self.steps
                 if abs(s.t_yr - round(s.t_yr)) < 0.11
                 and round(s.t_yr) % 1 == 0
                 and (round(s.t_yr) % 5 == 0 or s.t_yr < 1.0)]
        for s in shown[:25]:
            marker = " ❄" if s.is_frozen else "  "
            lines.append(
                f"  {s.t_yr:>8.1f} {s.T_pole_C:>10.2f} {s.h_ice_m:>8.3f} "
                f"{s.h_snow_m:>8.3f} {s.albedo:>7.3f} {s.aod:>6.3f} "
                f"{s.f_solar_block*100:>6.1f}%{marker}"
            )
        lines.append("=" * 62)
        return "\n".join(lines)

    @property
    def times(self) -> np.ndarray:
        return np.array([s.t_yr for s in self.steps])

    @property
    def T_pole_C_arr(self) -> np.ndarray:
        return np.array([s.T_pole_C for s in self.steps])

    @property
    def h_ice_arr(self) -> np.ndarray:
        return np.array([s.h_ice_m for s in self.steps])


# ── 메인 시뮬레이션 ─────────────────────────────────────────────────────────

def run_polar_simulation(
    # 충돌 파라미터 (LuciferEngine 출력)
    E_eff_MT:        float,
    delta_H2O_kg:    float  = 0.0,
    delta_T_pole_K:  float  = 0.0,   # 음수 = 냉각 (LuciferEngine delta_pole_eq_K)

    # 시뮬레이션 설정
    lat_deg:             float  = 85.0,   # 북위 85° (북극해)
    t_max_yr:            float  = 50.0,
    dt_yr:               float  = 0.1,
    T_pole_preimpact_K:  float  = None,   # None → T_POLE_PREIMPACT 사용

    # 기후 파라미터
    tau_aerosol_yr:  float  = 2.0,
    tau_climate_yr:  float  = 10.0,
    tau_h2o_yr:      float  = 1.5,
    Q_ocean_base:    float  = 15.0,   # W/m²  충돌 전 해양 열 공급
    ocean_reduce:    float  = 0.5,    # 충돌 후 최솟값 분율
) -> PolarSimResult:
    """루시퍼 임팩트 후 극지방 결빙 시뮬레이션.

    Parameters
    ----------
    E_eff_MT       : LuciferEngine.E_eff_MT
    delta_H2O_kg   : LuciferEngine.delta_H2O_canopy
    delta_T_pole_K : LuciferEngine.delta_pole_eq_K (음수 → 냉각)
    lat_deg        : 시뮬레이션 위도 (85=북극해, 75=북극권)
    """
    cp = ImpactClimateForcingParams(
        E_eff_MT=E_eff_MT,
        delta_H2O_kg=delta_H2O_kg,
        delta_T_pole_K=delta_T_pole_K,
        tau_aerosol_yr=tau_aerosol_yr,
        tau_climate_yr=tau_climate_yr,
        tau_h2o_yr=tau_h2o_yr,
    )

    t_arr = np.arange(0.0, t_max_yr + dt_yr * 0.5, dt_yr)
    dt_s  = dt_yr * 365.25 * 86400.0   # [s]

    steps:  List[SimStep] = []
    events: List[Dict]   = []

    # 초기 상태
    # T_pole_preimpact_K: 충돌 전 극지방 기온
    #   기본값 = T_POLE_PREIMPACT (250K, 현재 기후 기준)
    #   서사 모드: 270K (수증기 캐노피 / 창공 온실 효과로 극지방도 온난)
    T_pole    = (T_pole_preimpact_K if T_pole_preimpact_K is not None
                 else T_POLE_PREIMPACT)
    h_ice     = 0.0
    h_snow    = 0.0
    f_ice     = 0.0
    t_freeze_start = None   # 결빙 시작 시각

    freeze_onset_yr = None
    max_ice_m       = 0.0
    max_ice_yr      = 0.0

    from .energy_balance import SIGMA, EMISSIVITY, LAMBDA_TRANSPORT, insolation_factor, ALBEDO_ICE_OLD

    # 선형화 암묵적 Euler 계수
    # Q_lw ≈ Q_lw0 + 4·ε·σ·T₀³·(T-T₀)
    # T_new = (C·T + dt·[Q_sw + Q_ocean + λ·T_global + 4·ε·σ·T₀³·T₀ - Q_lw0])
    #        / (C + dt·[4·ε·σ·T₀³ + λ])
    # → 무조건 안정 (수렴 보장)

    SIGMA_     = SIGMA
    EMISS_     = EMISSIVITY
    LAMBDA_    = LAMBDA_TRANSPORT
    f_lat_     = insolation_factor(lat_deg)

    was_frozen = False   # 직전 스텝 결빙 여부 (이벤트 중복 방지)

    for t_yr in t_arr:
        t_days = t_yr * 365.25

        # 1. 기후 강제
        clim = climate_state_at(t_yr, cp)

        # 2. 해양 열 공급
        Q_ocean = ocean_heat_flux_after_impact(t_yr, Q_ocean_base,
                                               ocean_reduce, tau_climate_yr)

        # 3. 알베도 (이전 스텝 f_ice 사용)
        albedo = 0.06 * (1 - f_ice) + ALBEDO_ICE_OLD * f_ice

        # 4. 단파 입사
        Q_sw = (1361.0 / 4.0) * f_lat_ * (1.0 - albedo) * (1.0 - clim.f_solar_block)

        # 5. 암묵적 Euler 온도 갱신 (선형화 Stefan-Boltzmann)
        #    T_new = (C·T_old + dt·[Q_sw + Q_ocean + λ·T_global + 4εσT_old³·T_old - εσT_old⁴])
        #           / (C + dt·[4εσT_old³ + λ])
        T0      = T_pole
        lw0     = EMISS_ * SIGMA_ * T0 ** 4              # Q_lw(T0)
        dlw_dT  = 4.0 * EMISS_ * SIGMA_ * T0 ** 3       # dQ_lw/dT
        Q_src   = Q_sw + Q_ocean + LAMBDA_ * clim.T_global_K
        numer   = HEAT_CAP_OCN * T0 + dt_s * (Q_src + dlw_dT * T0 - lw0)
        denom   = HEAT_CAP_OCN + dt_s * (dlw_dT + LAMBDA_)
        T_pole  = numer / denom

        # 6. 결빙 판정
        is_frozen = T_pole < T_FREEZE_SW

        # 결빙 이벤트 (상태 변화 시만 기록)
        if is_frozen and not was_frozen:
            if freeze_onset_yr is None:
                freeze_onset_yr = t_yr
            t_freeze_start = t_yr
            events.append({"event": "freeze_onset", "t_yr": t_yr,
                            "T_pole_K": T_pole})

        if not is_frozen and was_frozen:
            h_ice = 0.0
            h_snow = 0.0
            t_freeze_start = None
            events.append({"event": "melt", "t_yr": t_yr,
                            "T_pole_K": T_pole})

        was_frozen = is_frozen

        # 7. 얼음 두께 (Stefan — 진단적 계산)
        if is_frozen and t_freeze_start is not None:
            t_frozen_days = max(0.0, (t_yr - t_freeze_start) * 365.25)
            h_snow = snow_accumulation(t_frozen_days, clim.H2O_canopy_kg,
                                        lat_deg, tau_h2o_yr * 365.25)
            delta_T_ice = T_FREEZE_SW - T_pole
            h_ice = stefan_thickness(delta_T_ice, t_frozen_days, h_snow)
        elif not is_frozen:
            h_ice  = 0.0
            h_snow = 0.0

        # 8. 얼음 피복률 (얼음 두께 기준 점진적)
        f_ice  = min(1.0, h_ice / 2.0) if h_ice > 0.01 else 0.0

        # 9. 성장률
        if is_frozen and h_ice > 0:
            growth_yr = ice_growth_rate(h_ice, T_FREEZE_SW - T_pole, h_snow) * 365.25
        else:
            growth_yr = 0.0

        # 최대값 추적
        if h_ice > max_ice_m:
            max_ice_m  = h_ice
            max_ice_yr = t_yr

        albedo = 0.06 * (1 - f_ice) + ALBEDO_ICE_OLD * f_ice   # 출력용 갱신

        Q_net_out = Q_sw + Q_ocean + LAMBDA_ * (clim.T_global_K - T_pole) - EMISS_ * SIGMA_ * T_pole ** 4
        step = SimStep(
            t_yr=t_yr, t_days=t_days,
            T_pole_K=T_pole, T_pole_C=T_pole - 273.15,
            h_ice_m=h_ice, h_snow_m=h_snow,
            f_ice=f_ice, albedo=albedo,
            aod=clim.aod, f_solar_block=clim.f_solar_block,
            Q_net=Q_net_out, Q_ocean=Q_ocean,
            H2O_canopy_kg=clim.H2O_canopy_kg,
            is_frozen=is_frozen,
            growth_rate_m_yr=growth_yr,
        )
        steps.append(step)

    ice_persists = steps[-1].is_frozen if steps else False

    return PolarSimResult(
        steps=steps,
        freeze_onset_yr=freeze_onset_yr,
        max_ice_m=max_ice_m,
        max_ice_yr=max_ice_yr,
        ice_persists=ice_persists,
        t_max_yr=t_max_yr,
        lat_deg=lat_deg,
        events=events,
    )


__all__ = [
    "SimStep", "PolarSimResult", "run_polar_simulation",
]
