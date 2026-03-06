"""simulation.py — 탈빙하기 통합 시뮬레이션

2024년 현재 상태에서 출발해 미래 빙하 소멸 과정을 추적한다.

물리 파이프라인:
  CO₂ 시나리오 → 복사 강제 → 전지구/극지 온도 변화
      → 그린란드/서남극/동남극 질량수지
      → 해수면 변화 → MISI 피드백 (서남극)
      → 북극 해빙 면적 변화
"""
from __future__ import annotations

from dataclasses import dataclass, field
from math import log
from typing import Optional

from .forcing import (
    co2_trajectory_ppm, co2_radiative_forcing, milankovitch_forcing,
    delta_T_global, delta_T_arctic, delta_T_antarctic,
    T_2024, T_ARCTIC_2024, T_ANT_2024,
)
from .ice_dynamics import (
    IceState,
    greenland_mass_balance, wais_mass_balance, eais_mass_balance,
    arctic_sea_ice_area, ice_to_sea_level,
    GT_TO_KM3,
    V_G_2024, V_WA_2024, V_EA_2024,
    A_ICE_SUMMER_2024,
)


# ── 이벤트 임계값 ────────────────────────────────────────────────────────
SLR_DANGEROUS    = 1.0    # m  — 저지대 침수 시작
SLR_CATASTROPHIC = 3.0    # m  — 연안 도시 위협
SLR_WAIS_TRIGGER = 1.5    # m  — 서남극 MISI 시작
A_ICE_FREE       = 1.0e6  # km² — 여름 빙하 소멸 기준 (실질적 빙하 소멸)


@dataclass
class DeglaciationStep:
    """시뮬레이션 1스텝 상태"""
    year:              float
    co2_ppm:           float
    forcing_W_m2:      float
    T_global_C:        float
    T_arctic_C:        float
    T_antarctic_C:     float
    V_G_km3:           float   # 그린란드
    V_WA_km3:          float   # 서남극
    V_EA_km3:          float   # 동남극
    A_ice_summer_km2:  float   # 북극 여름 해빙
    sea_level_m:       float
    melt_G_Gt_yr:      float
    melt_WA_Gt_yr:     float
    melt_EA_Gt_yr:     float


@dataclass
class DeglaciationResult:
    """시뮬레이션 전체 결과"""
    scenario:           str
    steps:              list[DeglaciationStep] = field(default_factory=list)

    # 이벤트 기록
    year_arctic_ice_free:    Optional[float] = None   # 북극 여름 빙하 소멸
    year_slr_1m:             Optional[float] = None   # 해수면 +1m
    year_slr_3m:             Optional[float] = None   # 해수면 +3m
    year_greenland_half:     Optional[float] = None   # 그린란드 절반 소멸
    year_greenland_gone:     Optional[float] = None   # 그린란드 완전 소멸
    year_wais_gone:          Optional[float] = None   # 서남극 소멸
    year_wais_misi:          Optional[float] = None   # MISI 시작

    def summary(self) -> str:
        lines = [
            "=" * 70,
            f"  탈빙하기 시뮬레이션 결과  [시나리오: {self.scenario}]",
            "=" * 70,
        ]

        # 이벤트 요약
        events = [
            ("북극 여름 빙하 소멸",   self.year_arctic_ice_free),
            ("서남극 MISI 시작",      self.year_wais_misi),
            ("해수면 +1m",            self.year_slr_1m),
            ("해수면 +3m",            self.year_slr_3m),
            ("그린란드 절반 소멸",    self.year_greenland_half),
            ("그린란드 완전 소멸",    self.year_greenland_gone),
            ("서남극 완전 소멸",      self.year_wais_gone),
        ]
        lines.append(f"  {'이벤트':<24}  {'발생 연도'}")
        lines.append("  " + "-" * 40)
        for label, yr in events:
            if yr is not None:
                lines.append(f"  {label:<24}  {yr:.0f}년")
            else:
                lines.append(f"  {label:<24}  시뮬레이션 기간 내 발생 안 함")

        # 타임라인
        lines.append("")
        lines.append(f"  {'연도':>8}  {'CO₂(ppm)':>9}  {'T_전지구':>9}  "
                     f"{'T_북극':>8}  {'해수면':>8}  {'그린란드%':>9}  {'북극해빙(km²)':>13}")
        lines.append("  " + "-" * 75)
        milestones = [0, 10, 25, 50, 76, 100, 200, 500, 1000, 2000, 5000]
        s0_year = self.steps[0].year
        for s in self.steps:
            yr_elapsed = s.year - s0_year
            if any(abs(yr_elapsed - m) < 1 for m in milestones):
                g_pct = 100 * s.V_G_km3 / V_G_2024
                lines.append(
                    f"  {s.year:>8.0f}  {s.co2_ppm:>9.0f}  "
                    f"{s.T_global_C:>+8.2f}°C  {s.T_arctic_C:>+7.1f}°C  "
                    f"{s.sea_level_m:>+7.2f}m  {g_pct:>8.1f}%  "
                    f"{s.A_ice_summer_km2/1e6:>10.2f}M km²"
                )
        lines.append("=" * 70)
        return "\n".join(lines)


def run_deglaciation_simulation(
    scenario:   str   = "rcp85",
    t_max_yr:   float = 500.0,
    dt_yr:      float = 1.0,
    start_year: float = 2024.0,
) -> DeglaciationResult:
    """
    탈빙하기 시뮬레이션 메인 함수.

    Parameters
    ----------
    scenario   : 'rcp26' | 'rcp45' | 'rcp60' | 'rcp85' | 'current'
    t_max_yr   : 시뮬레이션 기간 [yr]
    dt_yr      : 시간 스텝 [yr]  (단기 1yr, 장기 10yr 권장)
    start_year : 시작 연도 (기본 2024)
    """
    result = DeglaciationResult(scenario=scenario)

    # 초기 상태
    state = IceState(
        V_G_km3=V_G_2024,
        V_WA_km3=V_WA_2024,
        V_EA_km3=V_EA_2024,
        A_ice_summer_km2=A_ICE_SUMMER_2024,
        sea_level_m=0.0,
        year=start_year,
    )

    # 기준 복사 강제 (2024년)
    forcing_2024 = co2_radiative_forcing(co2_trajectory_ppm(0.0, scenario))

    n_steps = int(t_max_yr / dt_yr)
    for i in range(n_steps + 1):
        t = i * dt_yr
        year = start_year + t

        # ── 1. 복사 강제 계산 ──────────────────────────────────────────
        co2 = co2_trajectory_ppm(t, scenario)
        rf  = co2_radiative_forcing(co2) + milankovitch_forcing(t)
        # 2024년 기준 증분 강제
        delta_rf = rf - forcing_2024

        # ── 2. 온도 변화 ──────────────────────────────────────────────
        T_global  = T_2024    + delta_T_global(delta_rf)
        T_arctic  = T_ARCTIC_2024  + delta_T_arctic(delta_rf)
        T_ant     = T_ANT_2024     + delta_T_antarctic(delta_rf)

        # ── 3. 현재 상태 스냅샷 기록 ──────────────────────────────────
        A_ice = arctic_sea_ice_area(T_arctic)
        step  = DeglaciationStep(
            year=year,
            co2_ppm=co2,
            forcing_W_m2=rf,
            T_global_C=T_global,
            T_arctic_C=T_arctic,
            T_antarctic_C=T_ant,
            V_G_km3=state.V_G_km3,
            V_WA_km3=state.V_WA_km3,
            V_EA_km3=state.V_EA_km3,
            A_ice_summer_km2=A_ice,
            sea_level_m=state.sea_level_m,
            melt_G_Gt_yr=-greenland_mass_balance(T_arctic, state.V_G_km3),
            melt_WA_Gt_yr=-wais_mass_balance(T_ant, state.V_WA_km3, state.sea_level_m),
            melt_EA_Gt_yr=-eais_mass_balance(T_ant, state.V_EA_km3),
        )
        result.steps.append(step)

        # ── 4. 이벤트 감지 ────────────────────────────────────────────
        if result.year_arctic_ice_free is None and A_ice < A_ICE_FREE:
            result.year_arctic_ice_free = year

        if result.year_slr_1m is None and state.sea_level_m >= SLR_DANGEROUS:
            result.year_slr_1m = year

        if result.year_slr_3m is None and state.sea_level_m >= SLR_CATASTROPHIC:
            result.year_slr_3m = year

        if result.year_greenland_half is None and state.V_G_km3 <= V_G_2024 * 0.5:
            result.year_greenland_half = year

        if result.year_greenland_gone is None and state.V_G_km3 <= 0.01 * V_G_2024:
            result.year_greenland_gone = year

        if result.year_wais_gone is None and state.V_WA_km3 <= 0.01 * V_WA_2024:
            result.year_wais_gone = year

        if result.year_wais_misi is None and state.sea_level_m >= SLR_WAIS_TRIGGER:
            result.year_wais_misi = year

        # ── 5. 상태 갱신 (explicit Euler) ────────────────────────────
        dV_G  = greenland_mass_balance(T_arctic, state.V_G_km3) * GT_TO_KM3 * dt_yr
        dV_WA = wais_mass_balance(T_ant, state.V_WA_km3, state.sea_level_m) * GT_TO_KM3 * dt_yr
        dV_EA = eais_mass_balance(T_ant, state.V_EA_km3) * GT_TO_KM3 * dt_yr

        state.V_G_km3  = max(0.0, state.V_G_km3  + dV_G)
        state.V_WA_km3 = max(0.0, state.V_WA_km3 + dV_WA)
        state.V_EA_km3 = max(0.0, state.V_EA_km3 + dV_EA)

        # 해수면: 부피 손실 → SLR
        state.sea_level_m += ice_to_sea_level(dV_G, dV_WA, dV_EA)
        state.year = year

    return result
