"""_08_ice_age.simulation — 빙하시대 장기 시뮬레이션 (수천~수만 년)

_07_polar_ice 출력을 초기 조건으로 받아, 대륙 빙상 성장 → 알베도 런어웨이 →
해수면 하강 → 빙하시대 도달까지의 전지구 기후 진화를 적분한다.

시간 단계:  dt = 50 yr  (단기 기후 변동 평균, 빙상 역학 분해 충분)
적분 기간:  10,000 ~ 100,000 yr
적분 방법:  explicit Euler  (빙상 질량 변화 스케일 >> 수치 오차, 안정)

피드백 루프:
  V_ice → φ_ice → α_global → ΔQ → T_global → T_pole
  T_pole → B_net → dV_ice/dt (루프 닫힘)

_07 연결:
  run_ice_age_simulation(
      T_pole_init_K  = polar_result.steps[-1].T_pole_K,
      T_global_init_K = 288.0,
      V_ice_init_km3  = 1e5,     # _07 결빙으로 핵생성된 초기 대륙 빙상
  )
"""

from __future__ import annotations

import numpy as np
from dataclasses import dataclass, field
from typing import Optional

from .ice_sheet import (IceSheetParams, mass_balance,
                        volume_to_geometry, sea_level_change)
from .feedback  import (global_albedo, radiative_forcing,
                        global_temperature, polar_temperature, is_snowball,
                        T_GLOBAL_0_K, ALPHA_GLOBAL_0, LAMBDA_CLIMATE)


# ── 스노우볼 평형 온도 (Budyko 1969 완전 빙하 평형) ─────────────────────────
T_SNOWBALL_K = 220.0   # K  전지구 결빙 평형 기온 추정


@dataclass
class IceAgeParams:
    """빙하시대 시뮬레이션 입력 파라미터."""
    # _07 연결 — 초기 조건
    T_pole_init_K:    float = 243.15   # K  _07 결빙 후 극지 기온
    T_global_init_K:  float = 285.0    # K  에어로졸 제거 후 전지구 기온
    V_ice_init_km3:   float = 1.0e5    # km³ 초기 대륙 빙상 부피

    # 시뮬레이션 제어
    t_max_yr:         float = 50_000.0
    dt_yr:            float = 50.0

    # 빙상 질량수지
    ice_sheet:        IceSheetParams = field(default_factory=IceSheetParams)

    # 기후 감도
    climate_sensitivity: float = LAMBDA_CLIMATE   # K/(W/m²)

    # 장기 안정화 강제 (화산 CO₂, 궤도 강제 등)
    # 양수 = 온난화 (탈빙하기 시뮬레이션)
    co2_forcing_W_m2: float = 0.0


@dataclass
class IceAgeStep:
    """시뮬레이션 한 스텝 출력."""
    t_yr:          float
    V_ice_km3:     float
    A_ice_km2:     float
    phi_ice_deg:   float   # 빙하선 위도 [°N]
    sea_level_m:   float   # 해수면 변화 [m]
    T_global_K:    float
    T_global_C:    float
    T_pole_K:      float
    T_pole_C:      float
    alpha_global:  float
    delta_Q:       float   # 알베도 복사 강제 [W/m²]
    B_acc:         float   # 강설 누적 [m/yr]
    B_abl:         float   # 융빙 제거 [m/yr]
    B_net:         float   # 순 질량수지 [m/yr]
    is_snowball:   bool


@dataclass
class IceAgeResult:
    """시뮬레이션 전체 결과."""
    steps:            list[IceAgeStep]
    snowball_yr:      Optional[float]   # 스노우볼 진입 시각
    max_extent_yr:    float             # 최대 빙하 확장 시각
    max_extent_lat:   float             # 최대 빙하선 위도 [°N]  (낮을수록 멀리)
    sea_level_min_m:  float             # 최저 해수면 [m]
    t_max_yr:         float
    events:           list[dict]

    def summary(self) -> str:
        sep = "=" * 65
        lines = [
            sep,
            "  빙하시대 시뮬레이션 결과  (_08_ice_age)",
            sep,
            f"  시뮬레이션 기간  : {self.t_max_yr:>10,.0f} yr",
            f"  최대 빙하 확장   : {self.max_extent_lat:>7.1f}°N"
            f"  ({self.max_extent_yr:>10,.0f} yr 차)",
            f"  최저 해수면      : {self.sea_level_min_m:>7.1f} m",
            f"  스노우볼 진입    : "
            + ("없음" if self.snowball_yr is None
               else f"{self.snowball_yr:,.0f} yr"),
            "",
            f"  {'시각(yr)':>10}  {'빙하선(°N)':>10}  {'해수면(m)':>9}"
            f"  {'T_전지구(°C)':>11}  {'빙상(km³)':>12}  {'상태':>4}",
            "  " + "-" * 63,
        ]
        # 로그 스케일로 표시 시각 선택
        display = set()
        for exp10 in range(2, 6):
            for m in [1, 2, 5]:
                v = m * 10**exp10
                if v <= self.t_max_yr:
                    display.add(float(v))
        display.add(0.0)
        display.add(float(self.t_max_yr))

        shown = 0
        for s in self.steps:
            if shown >= 20:
                break
            if not any(abs(s.t_yr - d) < 1.0 for d in display):
                continue
            tag = "❄❄" if s.is_snowball else ("❄ " if s.phi_ice_deg < 60 else "  ")
            lines.append(
                f"  {s.t_yr:>10,.0f}  {s.phi_ice_deg:>10.1f}  {s.sea_level_m:>9.1f}"
                f"  {s.T_global_C:>11.1f}  {s.V_ice_km3:>12,.0f}  {tag}"
            )
            shown += 1

        lines.append(sep)
        return "\n".join(lines)


def run_ice_age_simulation(
    T_pole_init_K:       float = 243.15,
    T_global_init_K:     float = 285.0,
    V_ice_init_km3:      float = 1.0e5,
    t_max_yr:            float = 50_000.0,
    dt_yr:               float = 50.0,
    climate_sensitivity: float = LAMBDA_CLIMATE,
    co2_forcing_W_m2:    float = 0.0,
    ice_params:          Optional[IceSheetParams] = None,
) -> IceAgeResult:
    """빙하시대 시뮬레이션 실행.

    Parameters
    ----------
    T_pole_init_K       : _07 결빙 이후 극지 초기 기온 [K]
    T_global_init_K     : 에어로졸 제거 후 전지구 초기 기온 [K]
    V_ice_init_km3      : 초기 대륙 빙상 부피 [km³]
                          _07 결빙 → 핵생성 대륙 빙상: 권장 1e4 ~ 1e5
    t_max_yr            : 시뮬레이션 기간 [yr]
    dt_yr               : 시간 간격 [yr]  (권장: 10~100)
    climate_sensitivity : 기후 감도 [K/(W/m²)]
    co2_forcing_W_m2    : 장기 온난화 강제 [W/m²]  (탈빙하기 시뮬레이션)
    ice_params          : 빙상 질량수지 파라미터 (None → 기본값)

    Returns
    -------
    IceAgeResult
    """
    if ice_params is None:
        ice_params = IceSheetParams()

    t_arr = np.arange(0.0, t_max_yr + dt_yr * 0.5, dt_yr)

    steps:   list[IceAgeStep] = []
    events:  list[dict]       = []

    V_ice        = max(1.0, V_ice_init_km3)
    V_ref        = V_ice              # 해수면 기준 부피 (초기값)
    T_global     = T_global_init_K
    T_pole       = T_pole_init_K

    snowball_yr     = None
    max_extent_lat  = 90.0
    max_extent_yr   = 0.0
    sea_level_min   = 0.0
    was_snowball    = False

    for t_yr in t_arr:
        # 1. 빙상 기하
        A_km2, phi_ice = volume_to_geometry(V_ice, ice_params.h_mean_km)
        dSL            = sea_level_change(V_ice, V_ref)

        # 2. 알베도 피드백
        alpha    = global_albedo(phi_ice)
        dQ       = radiative_forcing(alpha, ALPHA_GLOBAL_0)

        # 3. 전지구 기온 (알베도 + CO₂ 장기 강제)
        T_global = global_temperature(
            T_global_init_K, dQ, co2_forcing_W_m2, climate_sensitivity)

        # 4. 극지 기온 (극 증폭 포함)
        T_pole = polar_temperature(
            T_global, T_global_init_K, T_pole_init_K)

        # 5. 빙상 질량수지
        T_pole_C  = T_pole   - 273.15
        B_acc, B_abl = mass_balance(T_pole_C, phi_ice, ice_params)
        B_net = B_acc - B_abl

        # 6. 빙상 부피 갱신 (explicit Euler)
        #    dV/dt = B_net [m/yr] × A [km²] × 1e-3 [km³/(m·km²)]
        dV    = B_net * A_km2 * 1.0e-3 * dt_yr   # km³
        V_ice = max(0.0, V_ice + dV)

        # 7. 이벤트 감지
        sb = is_snowball(phi_ice)
        if sb and not was_snowball:
            snowball_yr = t_yr
            events.append({"event": "snowball_onset", "t_yr": t_yr,
                           "phi_ice": phi_ice, "T_global_C": T_global - 273.15})
        if not sb and was_snowball:
            events.append({"event": "snowball_end", "t_yr": t_yr})
        was_snowball = sb

        if phi_ice < max_extent_lat:
            max_extent_lat = phi_ice
            max_extent_yr  = t_yr

        sea_level_min = min(sea_level_min, dSL)

        steps.append(IceAgeStep(
            t_yr=t_yr,
            V_ice_km3=V_ice,
            A_ice_km2=A_km2,
            phi_ice_deg=phi_ice,
            sea_level_m=dSL,
            T_global_K=T_global,
            T_global_C=T_global - 273.15,
            T_pole_K=T_pole,
            T_pole_C=T_pole_C,
            alpha_global=alpha,
            delta_Q=dQ,
            B_acc=B_acc,
            B_abl=B_abl,
            B_net=B_net,
            is_snowball=sb,
        ))

    return IceAgeResult(
        steps=steps,
        snowball_yr=snowball_yr,
        max_extent_yr=max_extent_yr,
        max_extent_lat=max_extent_lat,
        sea_level_min_m=sea_level_min,
        t_max_yr=t_max_yr,
        events=events,
    )


__all__ = [
    "IceAgeParams", "IceAgeStep", "IceAgeResult",
    "run_ice_age_simulation",
]
