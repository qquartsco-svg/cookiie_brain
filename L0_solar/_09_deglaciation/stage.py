"""_09_deglaciation / stage.py — 해빙(解氷) 서사 스테이지 (최후 빙하기 이후)

설계 원칙
─────────
* ENGINE_HUB 엔진 직접 import 없음 (레이어 분리)
* snapshot dict → DeglaciationStageResult 반환
* _08 빙하기 결과를 snapshot 에서 읽음

물리 요약 (밀란코비치 주기 + 알베도 피드백)
────────────────────────────────────────────
  밀란코비치 강제력 (단순화):
    F_orb(t) = F_amp × sin(2π × t / T_milankovitch)
    ΔQ_orb   = F_orb × S0 / 4   [W/m²]

  기온 응답:
    Q_net    = S0/4 × (1 − α) + ΔQ_orb − OLR_coeff × T_global
    T_global += Q_net / C_atm × dt

  빙상 질량 수지:
    melt_rate = A_melt × max(0, T_global − T_melt_ref)
    dV/dt     = −melt_rate

  해수면 회복:
    Δsea = −V_ice × ρ_ice / (ρ_water × A_ocean)

  완전 해빙 판정:
    V_ice < V_thresh → 해빙 완료

서사 흐름 → 최종 세계 상태
  deglac_T_global_K    : 해빙 후 전지구 기온 [K]
  deglac_sea_level_m   : 해빙 후 해수면 이상 [m]
  deglac_V_ice_km3     : 잔존 빙상 [km³]
  deglac_complete_yr   : 해빙 완료 연도 [yr]
  deglac_holocene      : 홀로세 진입 여부
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List

# ── 물리 상수 ─────────────────────────────────────────────────────────────────
S0:             float = 1361.0
A_OLR:          float = -338.0    # Budyko 상수 [W/m²]
B_OLR:          float = 2.0       # 기후 민감도 [W/(m²·K)]
C_ATM:          float = 5.0e8
ALPHA_0:        float = 0.30
DELTA_ALPHA:    float = 0.25

# 밀란코비치
T_MILANKOVITCH: float = 41_000.0   # 사교 주기 [yr]
F_AMP:          float = 0.012      # 강제력 진폭 (S0 대비)

# 빙상
V_ICE_MAX_KM3:  float = 3.0e7
A_MELT:         float = 5.0e9      # 용융 계수 [m³/yr/K]
T_MELT_REF:     float = 280.0      # 용융 기준 온도 [K]
V_THRESH_KM3:   float = 1.0e6      # 해빙 완료 기준 [km³]

# 해수면
RHO_ICE:        float = 917.0
RHO_WATER:      float = 1025.0
A_OCEAN:        float = 3.61e14
KM3_TO_M3:      float = 1.0e9

# 적분
DT_YR:          float = 200.0
T_MAX_YR:       float = 20_000.0
SEC_PER_YR:     float = 3.1557e7

# 홀로세 기준
HOLOCENE_T_K:   float = 287.0      # 현재 기온 근사 [K]
HOLOCENE_SEA_M: float = 0.0        # 현재 해수면 [m]


# ── 결과 ─────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class DeglaciationStageResult:
    """해빙 스테이지 실행 결과 (불변)."""

    stage_id: str = "_09_deglaciation"
    name:     str = "해빙 / 홀로세 진입"

    # 최종 상태
    T_global_K:        float = HOLOCENE_T_K
    T_global_C:        float = HOLOCENE_T_K - 273.15
    sea_level_m:       float = 0.0
    V_ice_km3:         float = 0.0
    deglac_complete_yr: float = -1.0   # 해빙 완료 연도 (-1=미완)
    holocene:          bool  = False   # 홀로세 진입 여부

    # 서사 메타
    summary:          str           = ""
    events:           List[str]     = field(default_factory=list)
    snapshot_updates: Dict[str, Any] = field(default_factory=dict)


# ── 핵심 물리 함수 ────────────────────────────────────────────────────────────

def _alpha(V_km3: float) -> float:
    frac = min(1.0, V_km3 / V_ICE_MAX_KM3)
    return ALPHA_0 + DELTA_ALPHA * frac


def _milankovitch(t_yr: float) -> float:
    """밀란코비치 궤도 강제력 [W/m²]."""
    return F_AMP * S0 / 4.0 * math.sin(2.0 * math.pi * t_yr / T_MILANKOVITCH)


def _sea_level(V_km3: float) -> float:
    V_m3 = V_km3 * KM3_TO_M3
    return -(V_m3 * RHO_ICE) / (RHO_WATER * A_OCEAN)


# ── 공개 API ──────────────────────────────────────────────────────────────────

def run(world_state: Dict[str, Any]) -> DeglaciationStageResult:
    """해빙 스테이지를 실행하고 결과를 반환한다.

    _08 결과 키 사용:
      ice_age_T_global_K  : 빙하기 후 전지구 기온
      ice_age_V_ice_km3   : 빙하기 빙상 부피
    """
    T_global_raw = world_state.get("ice_age_T_global_K", None)
    if T_global_raw is None or (isinstance(T_global_raw, float) and T_global_raw != T_global_raw):
        # NaN 방어: 빙하기 결과 없으면 LGM 기준값 사용
        T_global = HOLOCENE_T_K - 6.0   # ~281K
    else:
        T_global = max(240.0, float(T_global_raw))

    V_ice_raw = world_state.get("ice_age_V_ice_km3", None)
    if V_ice_raw is None or (isinstance(V_ice_raw, float) and V_ice_raw != V_ice_raw):
        V_ice = V_ICE_MAX_KM3 * 0.7
    else:
        V_ice = max(0.0, float(V_ice_raw))

    events: List[str] = [
        f"해빙 시작 조건: T={T_global-273.15:.1f}°C, V_ice={V_ice:.2e}km³"
    ]

    deglac_yr  = -1.0
    holocene   = False
    dt_sec     = DT_YR * SEC_PER_YR
    n          = int(T_MAX_YR / DT_YR)

    for i in range(n):
        t_yr = i * DT_YR

        alpha   = _alpha(V_ice)
        orb_f   = _milankovitch(t_yr)
        q_in    = S0 / 4.0 * (1.0 - alpha) + orb_f
        # 음함수 Euler (안정적 장기 적분)
        T_global = (T_global * C_ATM + (q_in - A_OLR) * dt_sec) / (C_ATM + B_OLR * dt_sec)

        melt    = max(0.0, A_MELT * (T_global - T_MELT_REF)) * DT_YR
        V_ice   = max(0.0, V_ice - melt / KM3_TO_M3)

        if deglac_yr < 0 and V_ice < V_THRESH_KM3:
            deglac_yr = t_yr
            holocene  = True
            events.append(
                f"해빙 완료: t={t_yr:.0f}yr | T={T_global-273.15:.1f}°C "
                f"| 잔존 빙상={V_ice:.2e}km³ → 홀로세 진입"
            )

    sea_f = _sea_level(V_ice)

    events += [
        f"최종 전지구 기온: {T_global-273.15:.1f}°C",
        f"최종 해수면: {sea_f:.0f} m",
        f"잔존 빙상: {V_ice:.2e} km³",
        "창세기 서사 완결 — 현재 지구 초기 조건 확립",
    ]

    summary = (
        f"해빙 | T={T_global-273.15:.1f}°C | 해수면={sea_f:.0f}m "
        f"| 홀로세={'진입' if holocene else '미진입'} ({deglac_yr:.0f}yr)"
    )

    updates: Dict[str, Any] = {
        "deglac_T_global_K":     T_global,
        "deglac_sea_level_m":    sea_f,
        "deglac_V_ice_km3":      V_ice,
        "deglac_complete_yr":    deglac_yr,
        "deglac_holocene":       holocene,
    }

    return DeglaciationStageResult(
        T_global_K=T_global,
        T_global_C=T_global - 273.15,
        sea_level_m=sea_f,
        V_ice_km3=V_ice,
        deglac_complete_yr=deglac_yr,
        holocene=holocene,
        summary=summary,
        events=events,
        snapshot_updates=updates,
    )


__all__ = ["DeglaciationStageResult", "run"]
