"""_05_noah_flood / stage.py — 노아 대홍수 서사 스테이지

설계 원칙
─────────
* ENGINE_HUB 엔진 직접 import 없음 (레이어 분리)
* snapshot dict → NoahFloodStageResult 반환
* 궁창 붕괴(_04) 결과를 snapshot 키로 수신

물리 요약
─────────
  궁창(H2O canopy) 붕괴 → 대기 중 수증기 전량 강수
  총 강수량 Q_precip ≈ H2O_canopy_frac × W_total
  해수면 상승 Δsea_level_m = Q_precip / (A_ocean × ρ_water)
  홍수 단계: rising(0~40yr) → peak(40~120yr) → receding(120~370yr) → stable

  홍수 후 초기조건 변화:
    f_land       ↓ (최고조 시 육지 비율 감소)
    H2O_canopy   → 0 (궁창 소멸)
    albedo       ↑ (해수면 확대)
    T_pole_delta ↑ (극-적도 온도차 증가)
    mutation_factor → 1.0 (UV 차단 상실)

서사 흐름 → 다음 스테이지 전달 키
  flood_occurred          : bool
  sea_level_anomaly_m     : 최고조 해수면 이상 [m]
  flood_peak_yr           : 홍수 최고조 연도 [yr]
  post_H2O_canopy         : 0.0 (홍수 후 캐노피 소멸)
  post_albedo             : 홍수 후 알베도
  post_mutation_factor    : 홍수 후 돌연변이율
  post_pole_eq_delta_K    : 홍수 후 극-적도 온도차 [K]
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List

# ── 홍수 물리 상수 ────────────────────────────────────────────────────────────
OCEAN_AREA_M2:        float = 3.61e14   # 현재 해양 면적 [m²]
WATER_DENSITY:        float = 1_025.0   # 해수 밀도 [kg/m³]
# 창세기 홍수 모델: 수증기 캐노피 붕괴 → 해수면 이상
# 지질 기록(LGM 대비 +125m) + Genesis 수문학 모델 기준
FLOOD_SEA_LEVEL_RISE_M: float = 125.0  # 홍수 최고조 해수면 상승 [m]
ALBEDO_OCEAN:         float = 0.06      # 해수면 알베도
ALBEDO_LAND:          float = 0.30      # 육지 알베도
F_LAND_BASE:          float = 0.29      # 홍수 후 육지 비율 (현재 지구)
MUTATION_POST:        float = 1.0       # 홍수 후 돌연변이율 (UV 차단 소멸)
POLE_EQ_DELTA_BASE_K: float = 13.3     # 홍수 후 극-적도 온도차 기준 [K]


# ── 결과 ─────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class NoahFloodStageResult:
    """노아 대홍수 스테이지 실행 결과 (불변)."""

    stage_id: str = "_05_noah_flood"
    name:     str = "노아 대홍수"

    # 홍수 물리 출력
    flood_triggered:       bool  = False
    sea_level_anomaly_m:   float = 0.0    # 최고조 해수면 이상 [m]
    flood_peak_yr:         float = 0.0    # 최고조 연도 (홍수 기준)
    total_precip_m3:       float = 0.0    # 총 강수 부피 [m³]
    flood_phase:           str   = "none" # none|rising|peak|receding|stable

    # 홍수 후 세계 상태
    post_f_land:            float = F_LAND_BASE
    post_H2O_canopy:        float = 0.0
    post_albedo:            float = 0.30
    post_mutation_factor:   float = MUTATION_POST
    post_pole_eq_delta_K:   float = POLE_EQ_DELTA_BASE_K

    # 서사 메타
    summary:          str           = ""
    events:           List[str]     = field(default_factory=list)
    snapshot_updates: Dict[str, Any] = field(default_factory=dict)


# ── 핵심 물리 함수 ────────────────────────────────────────────────────────────

def _sea_level_rise(world_state: Dict[str, Any]) -> float:
    """홍수 최고조 해수면 상승 [m].

    스냅샷에 flood_sea_level_rise_m 이 있으면 사용,
    없으면 Genesis 수문학 기본값(125m) 사용.
    """
    return float(world_state.get("flood_sea_level_rise_m", FLOOD_SEA_LEVEL_RISE_M))


def _post_albedo(f_land: float) -> float:
    """홍수 후 알베도 = 육지×0.30 + 해양×0.06."""
    return f_land * ALBEDO_LAND + (1.0 - f_land) * ALBEDO_OCEAN


# ── 공개 API ──────────────────────────────────────────────────────────────────

def run(world_state: Dict[str, Any]) -> NoahFloodStageResult:
    """노아 대홍수 스테이지를 실행하고 결과를 반환한다.

    _04 결과가 snapshot 에 반영되어 있어야 한다:
      firmament_collapse : True → 홍수 트리거
      firmament_shield   : 0.0 (붕괴 시)
    """
    collapse    = bool(world_state.get("firmament_collapse", False))
    w_total     = float(world_state.get("W_total", 1.4e9))
    w_surface   = float(world_state.get("W_surface", 1.0e9))

    events: List[str] = []

    if not collapse:
        # 궁창 유지 — 홍수 없음
        summary = "궁창 유지 — 대홍수 미발생"
        events.append("궁창 안정 → 홍수 트리거 조건 미충족")
        updates: Dict[str, Any] = {
            "flood_occurred":       False,
            "sea_level_anomaly_m":  0.0,
        }
        return NoahFloodStageResult(
            flood_triggered=False,
            flood_phase="none",
            summary=summary,
            events=events,
            snapshot_updates=updates,
        )

    # ── 홍수 발생 계산 ──────────────────────────────────────────────────────
    delta_h_m   = _sea_level_rise(world_state)
    peak_yr     = 40.0  # 홍수 최고조 표준 40년

    # 홍수 후 지형 변화: 침수로 인해 육지 일시 감소 (delta_h에 비례)
    # delta_f_land ≈ −delta_h / 200m (대략적 추정)
    f_land_flood = max(0.05, F_LAND_BASE - delta_h_m / 200.0)
    post_f_land  = F_LAND_BASE  # 물 빠진 후 복원 (현재 지구 기준)

    post_alb = _post_albedo(post_f_land)

    # 극-적도 온도차: 캐노피 소멸로 열 재분배 약화 → 증가
    # Δ ≈ 기준 + 고위도 수증기 냉각 보정
    pole_eq_delta = POLE_EQ_DELTA_BASE_K + max(0, delta_h_m * 0.5)

    events += [
        "궁창 붕괴 → 대기 수증기 전량 강수 시작",
        f"해수면 최고조 상승 ≈ {delta_h_m:.1f} m (홍수 {peak_yr:.0f}년 후)",
        "홍수 최고조: 육지 면적 일시 감소",
        "홍수 후: H2O 캐노피 소멸, UV 차단 상실 → mutation_factor=1.0",
        f"홍수 후 알베도 = {post_alb:.3f}, 극-적도 온도차 = {pole_eq_delta:.1f} K",
    ]

    summary = (
        f"대홍수 발생 | Δsea={delta_h_m:.1f}m | peak={peak_yr:.0f}yr "
        f"| post_albedo={post_alb:.3f}"
    )

    updates = {
        "flood_occurred":          True,
        "sea_level_anomaly_m":     delta_h_m,
        "flood_peak_yr":           peak_yr,
        "post_f_land":             post_f_land,
        "post_H2O_canopy":         0.0,
        "post_albedo":             post_alb,
        "post_mutation_factor":    MUTATION_POST,
        "post_pole_eq_delta_K":    pole_eq_delta,
    }

    return NoahFloodStageResult(
        flood_triggered=True,
        sea_level_anomaly_m=delta_h_m,
        flood_peak_yr=peak_yr,
        total_precip_m3=delta_h_m * OCEAN_AREA_M2,
        flood_phase="peak",
        post_f_land=post_f_land,
        post_H2O_canopy=0.0,
        post_albedo=post_alb,
        post_mutation_factor=MUTATION_POST,
        post_pole_eq_delta_K=pole_eq_delta,
        summary=summary,
        events=events,
        snapshot_updates=updates,
    )


__all__ = ["NoahFloodStageResult", "run"]
