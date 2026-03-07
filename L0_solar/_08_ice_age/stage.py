"""_08_ice_age / stage.py — 빙하기 서사 스테이지 (100~100,000년)

설계 원칙
─────────
* ENGINE_HUB 엔진 직접 import 없음 (레이어 분리)
* snapshot dict → IceAgeStageResult 반환
* _07 극지방 결빙 결과를 snapshot 에서 읽음

물리 요약 (장기 기후 피드백)
──────────────────────────────
  빙상-알베도 피드백:
    α(V_ice) = α0 + Δα × (V_ice / V_ice_max)
    Q_net    = S0/4 × (1 − α) − OLR_coeff × T_global
    T_global += Q_net / C_atm × dt

  빙상 질량 수지 (단순):
    B_net   = acc_rate − melt_rate
    acc_rate = max(0, A_acc × (T_freeze − T_pole))
    melt_rate = max(0, A_melt × (T_global − T_melt_ref))
    dV/dt   = B_net × Area_polar

  해수면:
    Δsea = −V_ice × RHO_ICE / (RHO_WATER × A_ocean)

  AVCE 연결 포인트 ★
    LGM 도달 시 해수면 −125m, 빙상 두께 ~2000m
    극지방 빙하 해역 → AVCE ICEBREAKER/UNDER_ICE 모드 운용 환경 정의

서사 흐름 → 다음 스테이지 전달 키
  ice_age_T_global_K    : LGM 전지구 기온 [K]
  ice_age_sea_level_m   : 해수면 이상 [m] (음수)
  ice_age_V_ice_km3     : 대륙 빙상 부피 [km³]
  ice_age_h_ice_max_m   : 최대 빙상 두께 [m]
  ice_age_lgm_reached   : LGM 도달 여부
  ice_age_avce_env      : AVCE 운용 환경 설명 dict
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List

# ── 빙하기 물리 상수 ──────────────────────────────────────────────────────────
S0:           float = 1361.0     # 태양 상수 [W/m²]
# Budyko 선형화 OLR = A_OLR + B_OLR × T_global
# 현재 지구 균형: S0/4×(1−α)=238 W/m², T=288K → A=-338, B=2.0
A_OLR:        float = -338.0     # Budyko 상수 [W/m²]
B_OLR:        float = 2.0        # 기후 민감도 [W/(m²·K)]
C_ATM:        float = 5.0e8     # 대기+해양 열용량 [J/(m²·K)]
ALPHA_0:      float = 0.30       # 기준 알베도 (홍수 후)
DELTA_ALPHA:  float = 0.25       # 최대 알베도 증가 (완전 빙하기)
T_GLOBAL_REF: float = 288.0      # 기준 전지구 기온 [K]

# 빙상 파라미터
V_ICE_MAX_KM3: float = 5.0e7    # 최대 대륙 빙상 부피 [km³] (LGM + 극지 해빙 포함)
V_ICE_SEED_KM3: float = 1.0e5  # 핵생성 후 초기 대륙 빙상 시드 [km³]
AREA_POLAR:    float = 2.0e12   # 극지방 빙상 면적 [m²]
POLE_OFFSET_K: float = 30.0     # 전지구 평균 대비 극지방 냉각도 [K]
A_ACC:         float = 2.0e9    # 적설 계수 [m³/yr/K] (극지방 기준)
A_MELT:        float = 1.5e9    # 용융 계수 [m³/yr/K] (전지구 기준)
T_MELT_REF:    float = 283.0    # 용융 기준 온도 [K] (~10°C)
T_FREEZE_K:    float = 271.15   # 결빙 기준 [K]

# 해수면 계산
RHO_ICE:      float = 917.0
RHO_WATER:    float = 1025.0
A_OCEAN:      float = 3.61e14   # 해양 면적 [m²]
KM3_TO_M3:    float = 1.0e9

# 적분 파라미터
DT_YR:        float = 100.0     # 타임스텝 [yr] (장기)
T_MAX_YR:     float = 50_000.0  # 최대 기간 [yr]
SEC_PER_YR:   float = 3.1557e7

# LGM 판정 기준
LGM_SEA_LEVEL_M:  float = -80.0   # 해수면 이상 기준 [m]
LGM_T_GLOBAL_K:   float = 282.0   # 전지구 기온 기준 [K]


# ── 결과 ─────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class IceAgeStageResult:
    """빙하기 스테이지 실행 결과 (불변)."""

    stage_id: str = "_08_ice_age"
    name:     str = "빙하기 (100~50,000yr)"

    # 최종 상태
    T_global_K:      float = T_GLOBAL_REF
    T_global_C:      float = T_GLOBAL_REF - 273.15
    sea_level_m:     float = 0.0       # 해수면 이상 [m]
    V_ice_km3:       float = 0.0       # 빙상 부피 [km³]
    h_ice_max_m:     float = 0.0       # 최대 빙상 두께 [m]
    lgm_reached:     bool  = False     # LGM 도달 여부
    lgm_yr:          float = -1.0      # LGM 도달 연도 [-1=미도달]
    alpha_final:     float = ALPHA_0   # 최종 알베도

    # AVCE 연결 포인트
    avce_env:        Dict[str, Any] = field(default_factory=dict)

    # 서사 메타
    summary:          str           = ""
    events:           List[str]     = field(default_factory=list)
    snapshot_updates: Dict[str, Any] = field(default_factory=dict)


# ── 핵심 물리 함수 ────────────────────────────────────────────────────────────

def _alpha(V_ice_km3: float) -> float:
    """빙상 부피 → 알베도."""
    frac = min(1.0, V_ice_km3 / V_ICE_MAX_KM3)
    return ALPHA_0 + DELTA_ALPHA * frac


def _sea_level(V_ice_km3: float) -> float:
    """빙상 부피 → 해수면 이상 [m] (음수)."""
    V_m3 = V_ice_km3 * KM3_TO_M3
    return -(V_m3 * RHO_ICE) / (RHO_WATER * A_OCEAN)


def _h_ice_from_V(V_km3: float) -> float:
    """빙상 부피 → 평균 두께 [m] (단순 평판 가정)."""
    V_m3 = V_km3 * KM3_TO_M3
    return V_m3 / AREA_POLAR


# ── AVCE 환경 설명 생성 ───────────────────────────────────────────────────────

def _avce_environment(T_global_K: float, sea_level_m: float,
                       h_ice_m: float) -> Dict[str, Any]:
    """LGM 환경 → AVCE 운용 파라미터 매핑.

    이 dict 는 CookiieBrain 서사에서 AVCE(60_APPLIED) 가
    어떤 환경에서 운용되는지를 명세한다. AVCE 를 직접 import 하지 않고
    환경 파라미터만 전달한다 (레이어 분리).
    """
    # 빙하기 환경 판정
    if h_ice_m > 100:
        primary_mode   = "ICEBREAKER"        # 빙상 위 쇄빙
        secondary_mode = "UNDER_ICE"         # 빙하 저면 잠항
        ice_hardness   = min(1.0, h_ice_m / 2000.0)
        depth_m        = abs(sea_level_m)    # 수심 감소
    elif h_ice_m > 10:
        primary_mode   = "SURFACE"
        secondary_mode = "ICEBREAKER"
        ice_hardness   = 0.3
        depth_m        = abs(sea_level_m)
    else:
        primary_mode   = "SURFACE"
        secondary_mode = "DIVE"
        ice_hardness   = 0.0
        depth_m        = 0.0

    return {
        "avce_primary_mode":   primary_mode,
        "avce_secondary_mode": secondary_mode,
        "ice_hardness":        ice_hardness,
        "sea_level_drop_m":    abs(sea_level_m),
        "ocean_depth_m":       depth_m,
        "T_ocean_K":           max(271.15, T_global_K - 5.0),  # 수온 추정
        "narrative_context":   (
            f"빙하기 LGM 환경: 해수면 {sea_level_m:.0f}m, "
            f"빙상 두께 {h_ice_m:.0f}m — AVCE {primary_mode}/{secondary_mode} 운용"
        ),
    }


# ── 공개 API ──────────────────────────────────────────────────────────────────

def run(world_state: Dict[str, Any]) -> IceAgeStageResult:
    """빙하기 스테이지 (장기 기후 피드백)를 실행하고 결과를 반환한다.

    _07 결과 키 사용:
      polar_T_pole_K  : 초기 극지방 기온
      polar_h_ice_m   : 초기 얼음 두께 (핵생성 조건)
    """
    T_pole_init  = float(world_state.get("polar_T_pole_K",  T_FREEZE_K - 10))
    h_ice_init   = float(world_state.get("polar_h_ice_m",   0.0))
    post_albedo  = float(world_state.get("post_albedo",      ALPHA_0))

    # 초기 빙상: _07 h_ice > 5m → 핵생성 조건 충족 → 대륙 빙상 시드
    # (극지방 해빙 두께가 아니라 핵생성 여부만 판단)
    if h_ice_init >= 5.0:
        V0_km3 = V_ICE_SEED_KM3   # 핵생성 완료 → 초기 대륙 빙상 10만 km³
    else:
        V0_km3 = 0.0               # 핵생성 미충족 → 빙하기 없음

    # 전지구 기온: Lucifer ΔT 가 있으면 기준 기온에서 절반 차감
    # (전지구 평균은 극지방보다 충격이 절반)
    delta_T_impact = float(world_state.get("lucifer_delta_T_K", 0.0))
    T_global = max(255.0, T_GLOBAL_REF + delta_T_impact * 0.4)

    events: List[str] = [f"초기 빙상 부피: V₀={V0_km3:.1f} km³"]

    lgm_reached = False
    lgm_yr      = -1.0
    T_min_K     = T_global

    V_ice = V0_km3
    dt_sec = DT_YR * SEC_PER_YR
    n = int(T_MAX_YR / DT_YR)

    for i in range(n):
        t_yr = i * DT_YR

        alpha  = _alpha(V_ice)
        q_in   = S0 / 4.0 * (1.0 - alpha)
        # 음함수 Euler (안정): T_new = (T_old*C + (q_in − A_OLR)*dt) / (C + B_OLR*dt)
        # → 어떤 dt에서도 발산하지 않음
        T_global = (T_global * C_ATM + (q_in - A_OLR) * dt_sec) / (C_ATM + B_OLR * dt_sec)

        # 빙상 질량 수지 (극지방 기준 적설 / 전지구 기준 용융)
        T_pole_eff = T_global - POLE_OFFSET_K        # 극지방 추정 기온
        acc  = max(0.0, A_ACC  * (T_FREEZE_K - T_pole_eff)) * DT_YR
        melt = max(0.0, A_MELT * (T_global - T_MELT_REF))   * DT_YR
        V_ice = max(0.0, V_ice + (acc - melt) / KM3_TO_M3)
        V_ice = min(V_ICE_MAX_KM3, V_ice)

        if T_global < T_min_K:
            T_min_K = T_global

        sea_lvl = _sea_level(V_ice)

        # LGM 판정
        if not lgm_reached and sea_lvl <= LGM_SEA_LEVEL_M and T_global <= LGM_T_GLOBAL_K:
            lgm_reached = True
            lgm_yr      = t_yr
            events.append(
                f"LGM 도달: t={t_yr:.0f}yr | T_global={T_global-273.15:.1f}°C "
                f"| 해수면={sea_lvl:.0f}m | V_ice={V_ice:.1e}km³"
            )

    # 최종 상태
    alpha_f   = _alpha(V_ice)
    sea_f     = _sea_level(V_ice)
    h_ice_f   = _h_ice_from_V(V_ice)

    events += [
        f"최종 전지구 기온: {T_global-273.15:.1f}°C",
        f"최종 해수면: {sea_f:.0f} m",
        f"최종 빙상 두께(평균): {h_ice_f:.0f} m",
        f"최종 빙상 부피: {V_ice:.2e} km³",
    ]

    # AVCE 연결 포인트
    avce_env = _avce_environment(T_global, sea_f, h_ice_f)
    events.append(
        f"★ AVCE 연결: {avce_env['narrative_context']}"
    )

    summary = (
        f"빙하기 | T={T_global-273.15:.1f}°C | 해수면={sea_f:.0f}m "
        f"| V_ice={V_ice:.1e}km³ | LGM={'도달' if lgm_reached else '미도달'}"
    )

    updates: Dict[str, Any] = {
        "ice_age_T_global_K":    T_global,
        "ice_age_sea_level_m":   sea_f,
        "ice_age_V_ice_km3":     V_ice,
        "ice_age_h_ice_max_m":   h_ice_f,
        "ice_age_lgm_reached":   lgm_reached,
        "ice_age_lgm_yr":        lgm_yr,
        "ice_age_avce_env":      avce_env,
    }

    return IceAgeStageResult(
        T_global_K=T_global,
        T_global_C=T_global - 273.15,
        sea_level_m=sea_f,
        V_ice_km3=V_ice,
        h_ice_max_m=h_ice_f,
        lgm_reached=lgm_reached,
        lgm_yr=lgm_yr,
        alpha_final=alpha_f,
        avce_env=avce_env,
        summary=summary,
        events=events,
        snapshot_updates=updates,
    )


__all__ = ["IceAgeStageResult", "run", "LGM_SEA_LEVEL_M"]
