"""_07_polar_ice / stage.py — 극지방 결빙 서사 스테이지 (0~50년)

설계 원칙
─────────
* ENGINE_HUB 엔진 직접 import 없음 (레이어 분리)
* snapshot dict → PolarIceStageResult 반환
* _06 루시퍼 충돌 결과(aod, delta_T_pole_K)를 snapshot 에서 읽음

물리 요약
─────────
  에너지 수지 모델 (간소화 Budyko):
    Q_in(t)  = Q0 × (1 − albedo) × (1 − f_block(t))
    f_block  = AOD / (AOD + 1)   [에어로졸 차단 효율]
    Q_out    = σ × T_pole^4 × ε
    dT/dt    = (Q_in − Q_out) / C_ocean   [C_ocean ≈ 4e8 J/(m²·K)]

  Stefan 결빙 법칙:
    h_ice(t) = √(2 λ_ice × |ΔT_freeze| × t / L_fusion)   [m]
    여기서 ΔT_freeze = max(0, T_freeze − T_pole)

  시간 적분: Euler, dt = 1yr, T_max = 50yr

서사 흐름 → 다음 스테이지 전달 키
  polar_T_pole_K       : 50yr 후 극지방 온도 [K]
  polar_h_ice_m        : 50yr 후 얼음 두께 [m]
  polar_f_ice          : 얼음 면적 비율 [0, 1]
  polar_ice_onset_yr   : 결빙 시작 연도 [yr]
  polar_aod_50yr       : 50yr 후 잔존 AOD
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Tuple

# ── 물리 상수 ─────────────────────────────────────────────────────────────────
SIGMA:        float = 5.67e-8    # Stefan-Boltzmann [W/(m²·K⁴)]
EMISSIVITY:   float = 0.95       # 극지방 장파 방출률
C_OCEAN:      float = 4.0e8     # 해양 열용량 [J/(m²·K)]
Q0_POLE:      float = 160.0     # 극지방 입사 태양 복사 [W/m²]
T_PREIMPACT_K: float = 263.15   # 충돌 전 극지방 기온 [K] (빙점보다 낮음)
T_FREEZE_K:   float = 271.15    # 해수 빙점 [K] (~−2°C)
LAMBDA_ICE:   float = 2.1       # 얼음 열전도도 [W/(m·K)]
L_FUSION:     float = 3.35e5    # 융해 잠열 [J/kg]
RHO_ICE:      float = 917.0     # 얼음 밀도 [kg/m³]

# AOD 감쇠 시상수 (에어로졸 침강)
AOD_TAU_YR:   float = 3.0       # 에어로졸 e-폴딩 시간 [yr]
AOD_FLOOR:    float = 0.02      # 배경 AOD (잔존 먼지)

# 적분 파라미터
DT_YR:        float = 1.0       # 타임스텝 [yr]
T_MAX_YR:     float = 50.0      # 최대 시뮬레이션 기간 [yr]
SEC_PER_YR:   float = 3.1557e7  # 초/년


# ── 결과 ─────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class PolarIceStageResult:
    """극지방 결빙 스테이지 실행 결과 (불변)."""

    stage_id: str = "_07_polar_ice"
    name:     str = "극지방 결빙 (0~50yr)"

    # 최종 상태 (t=50yr)
    T_pole_K:         float = T_PREIMPACT_K
    T_pole_C:         float = T_PREIMPACT_K - 273.15
    h_ice_m:          float = 0.0     # 얼음 두께 [m]
    f_ice:            float = 0.0     # 얼음 면적 비율 [0, 1]
    ice_onset_yr:     float = -1.0    # 결빙 시작 연도 (−1=미결빙)
    aod_50yr:         float = 0.0     # 50yr 후 잔존 AOD

    # 시계열 요약
    T_pole_min_K:     float = T_PREIMPACT_K   # 가장 추웠던 온도
    T_pole_min_yr:    float = 0.0

    # 서사 메타
    summary:          str           = ""
    events:           List[str]     = field(default_factory=list)
    snapshot_updates: Dict[str, Any] = field(default_factory=dict)


# ── 핵심 물리 함수 ────────────────────────────────────────────────────────────

def _aod_at(aod0: float, t_yr: float) -> float:
    """t_yr 시점의 AOD (지수 감쇠 + 배경)."""
    return AOD_FLOOR + (aod0 - AOD_FLOOR) * math.exp(-t_yr / AOD_TAU_YR)


def _q_in(aod: float) -> float:
    """극지방 순입사 태양 복사 [W/m²]."""
    f_block = aod / (aod + 1.0)
    return Q0_POLE * (1.0 - f_block)


def _q_out(T_K: float) -> float:
    """극지방 장파 방출 [W/m²]."""
    return SIGMA * EMISSIVITY * T_K ** 4


def _stefan_thickness(delta_T_K: float, t_yr: float) -> float:
    """Stefan 결빙 법칙: 얼음 두께 [m]."""
    if delta_T_K <= 0 or t_yr <= 0:
        return 0.0
    t_sec = t_yr * SEC_PER_YR
    return math.sqrt(2.0 * LAMBDA_ICE * delta_T_K * t_sec / (L_FUSION * RHO_ICE))


def _f_ice_from_T_pole(T_pole_K: float, T_freeze_K: float = T_FREEZE_K) -> float:
    """극지방 온도 → 빙면적 비율 (간소 선형 파라미터화)."""
    if T_pole_K >= T_freeze_K:
        return 0.0
    # T_pole 이 −30°C(243K) 이면 f_ice ≈ 1
    cold_ref = T_freeze_K - 30.0
    return min(1.0, (T_freeze_K - T_pole_K) / (T_freeze_K - cold_ref))


# ── 공개 API ──────────────────────────────────────────────────────────────────

def run(world_state: Dict[str, Any]) -> PolarIceStageResult:
    """극지방 결빙 스테이지 (0~50yr) 를 실행하고 결과를 반환한다.

    _06 결과 키 사용:
      lucifer_aod           : 초기 AOD
      lucifer_delta_T_pole_K: 충돌에 의한 극지방 온도 강하
    """
    aod0       = float(world_state.get("lucifer_aod",            0.0))
    dT_impact  = float(world_state.get("lucifer_delta_T_pole_K", 0.0))

    # 초기 극지방 온도 = 충돌 전 기준 + 충돌 강하
    T0_K = T_PREIMPACT_K + dT_impact  # dT_impact 는 음수

    events: List[str] = []

    if aod0 <= 0.0 and dT_impact >= 0.0:
        # 충돌 없음 — 결빙 없음
        events.append("충돌 에너지 없음 → 극지방 결빙 미발생")
        summary = "극지방 결빙 없음 — 충돌 AOD=0"
        updates: Dict[str, Any] = {
            "polar_T_pole_K":     T0_K,
            "polar_h_ice_m":      0.0,
            "polar_f_ice":        0.0,
            "polar_ice_onset_yr": -1.0,
        }
        return PolarIceStageResult(
            T_pole_K=T0_K,
            T_pole_C=T0_K - 273.15,
            summary=summary,
            events=events,
            snapshot_updates=updates,
        )

    # ── Euler 적분 (t = 0 → T_MAX_YR) ─────────────────────────────────────
    T_K          = T0_K
    ice_onset_yr = -1.0
    T_min_K      = T0_K
    T_min_yr     = 0.0
    ice_frozen_since = 0.0  # 결빙 시작 후 경과 시간

    n = int(T_MAX_YR / DT_YR)
    dt_sec = DT_YR * SEC_PER_YR

    for i in range(n):
        t_yr = i * DT_YR
        aod  = _aod_at(aod0, t_yr)
        q_in  = _q_in(aod)
        q_out = _q_out(T_K)
        dT    = (q_in - q_out) / C_OCEAN * dt_sec
        T_K   = T_K + dT

        if T_K < T_min_K:
            T_min_K  = T_K
            T_min_yr = t_yr

        if T_K < T_FREEZE_K and ice_onset_yr < 0:
            ice_onset_yr = t_yr
            events.append(f"결빙 시작: t={t_yr:.1f}yr, T_pole={T_K-273.15:.1f}°C")

        if ice_onset_yr >= 0:
            ice_frozen_since += DT_YR

    aod_50 = _aod_at(aod0, T_MAX_YR)
    delta_T_freeze = max(0.0, T_FREEZE_K - T_K)
    h_ice = _stefan_thickness(delta_T_freeze, ice_frozen_since) if ice_frozen_since > 0 else 0.0
    f_ice = _f_ice_from_T_pole(T_K)

    events += [
        f"50yr 후 극지방 온도: {T_K-273.15:.1f}°C",
        f"50yr 후 얼음 두께(Stefan): {h_ice:.2f} m",
        f"50yr 후 빙면 비율: {f_ice:.1%}",
        f"잔존 AOD(50yr): {aod_50:.3f}",
    ]
    if h_ice > 0.5:
        events.append("다년생 해빙 형성 — 빙하기 핵생성 조건 충족")

    summary = (
        f"극지 결빙 | T_pole={T_K-273.15:.1f}°C | h_ice={h_ice:.1f}m "
        f"| f_ice={f_ice:.1%} | onset={ice_onset_yr:.0f}yr"
    )

    updates = {
        "polar_T_pole_K":      T_K,
        "polar_h_ice_m":       h_ice,
        "polar_f_ice":         f_ice,
        "polar_ice_onset_yr":  ice_onset_yr,
        "polar_aod_50yr":      aod_50,
    }

    return PolarIceStageResult(
        T_pole_K=T_K,
        T_pole_C=T_K - 273.15,
        h_ice_m=h_ice,
        f_ice=f_ice,
        ice_onset_yr=ice_onset_yr,
        aod_50yr=aod_50,
        T_pole_min_K=T_min_K,
        T_pole_min_yr=T_min_yr,
        summary=summary,
        events=events,
        snapshot_updates=updates,
    )


__all__ = ["PolarIceStageResult", "run"]
