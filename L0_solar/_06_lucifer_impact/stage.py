"""_06_lucifer_impact / stage.py — 루시퍼 충돌 서사 스테이지

설계 원칙
─────────
* ENGINE_HUB 엔진 직접 import 없음 (레이어 분리)
* snapshot dict → LuciferImpactStageResult 반환
* 내부 impact_estimator.py 가 있으면 사용, 없으면 독립 물리 계산

물리 요약 (Tunguska/K-Pg 스케일 보정)
────────────────────────────────────────
  충돌체 운동 에너지: E_k = ½ m v² = ½ (ρ · π/6 · D³) · v²
  대기 침투 효율:     f_atm ≈ 1 − exp(−0.12 · cos θ)
  대기 직접 가열:     E_atm = E_k · f_atm
  AOD (광학 두께):    AOD ≈ 0.05 × (E_eff_MT)^0.6   [MT TNT 기준]
  전지구 온도 강하:   ΔT_global ≈ −3.0 × AOD^0.5 [K]
  극지방 추가 냉각:   ΔT_pole   ≈ −1.5 × ΔT_global  [K]
  충격 강도:          shock_strength = min(1, E_eff_MT / 1e6)

서사 흐름 → 다음 스테이지 전달 키
  lucifer_E_eff_MT     : 유효 충돌 에너지 [MT TNT]
  lucifer_aod          : 에어로졸 광학 두께
  lucifer_delta_T_K    : 전지구 평균 온도 강하 [K]
  lucifer_delta_T_pole_K: 극지방 온도 강하 [K]
  lucifer_shock        : 충격 강도 [0, 1]
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List

# ── 기본 충돌체 파라미터 (루시퍼 혜성 기본값) ────────────────────────────────
DEFAULT_D_KM:       float = 10.0    # 직경 [km]
DEFAULT_RHO_GCM3:   float = 1.5     # 밀도 [g/cm³] (혜성 = 암석보다 낮음)
DEFAULT_V_KMS:      float = 30.0    # 속도 [km/s]
DEFAULT_THETA_DEG:  float = 45.0    # 입사각 [deg]
DEFAULT_LAT_DEG:    float = 60.0    # 위도 (북극 방향 충돌)

# ── 물리 상수 ─────────────────────────────────────────────────────────────────
MT_TO_J:    float = 4.184e15   # 1 MT TNT → J
KM_TO_M:    float = 1_000.0
GCM3_TO_KGM3: float = 1_000.0
KMS_TO_MS:  float = 1_000.0


# ── 결과 ─────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class LuciferImpactStageResult:
    """루시퍼 충돌 스테이지 실행 결과 (불변)."""

    stage_id: str = "_06_lucifer_impact"
    name:     str = "루시퍼 충돌"

    # 충돌 에너지
    E_total_J:      float = 0.0    # 전체 운동 에너지 [J]
    E_eff_MT:       float = 0.0    # 유효 충돌 에너지 [MT TNT]
    f_atm:          float = 0.0    # 대기 에너지 분율

    # 환경 영향
    aod:            float = 0.0    # 에어로졸 광학 두께
    delta_T_K:      float = 0.0    # 전지구 평균 온도 강하 [K] (음수)
    delta_T_pole_K: float = 0.0    # 극지방 온도 강하 [K] (음수)
    shock_strength: float = 0.0    # 충격 강도 [0, 1]

    # 서사 메타
    summary:          str           = ""
    events:           List[str]     = field(default_factory=list)
    snapshot_updates: Dict[str, Any] = field(default_factory=dict)


# ── 핵심 물리 함수 ────────────────────────────────────────────────────────────

def _kinetic_energy_j(D_km: float, rho_gcm3: float, v_kms: float) -> float:
    """충돌체 운동 에너지 [J]."""
    D_m   = D_km * KM_TO_M
    rho   = rho_gcm3 * GCM3_TO_KGM3
    v_ms  = v_kms * KMS_TO_MS
    mass  = rho * (math.pi / 6.0) * D_m ** 3
    return 0.5 * mass * v_ms ** 2


def _f_atm(theta_deg: float) -> float:
    """대기 에너지 분율 (입사각에 따라 결정)."""
    theta_rad = math.radians(theta_deg)
    return 1.0 - math.exp(-0.12 * math.cos(theta_rad))


def _aod_from_E_eff_MT(E_eff_MT: float) -> float:
    """에어로졸 광학 두께 추정 (경험식)."""
    if E_eff_MT <= 0:
        return 0.0
    return 0.05 * (E_eff_MT ** 0.6)


def _delta_T_from_aod(aod: float) -> float:
    """전지구 온도 강하 [K] (음수). AOD 기반 경험식."""
    return -3.0 * (aod ** 0.5)


# ── 공개 API ──────────────────────────────────────────────────────────────────

def run(world_state: Dict[str, Any]) -> LuciferImpactStageResult:
    """루시퍼 충돌 스테이지를 실행하고 결과를 반환한다.

    스냅샷에서 충돌체 파라미터를 읽거나, 없으면 기본값 사용.
    """
    D_km      = float(world_state.get("lucifer_D_km",      DEFAULT_D_KM))
    rho_gcm3  = float(world_state.get("lucifer_rho_gcm3",  DEFAULT_RHO_GCM3))
    v_kms     = float(world_state.get("lucifer_v_kms",     DEFAULT_V_KMS))
    theta_deg = float(world_state.get("lucifer_theta_deg", DEFAULT_THETA_DEG))

    # ── 에너지 계산 ─────────────────────────────────────────────────────────
    E_total_J  = _kinetic_energy_j(D_km, rho_gcm3, v_kms)
    f_atm_frac = _f_atm(theta_deg)
    E_atm_J    = E_total_J * f_atm_frac
    E_eff_MT   = E_atm_J / MT_TO_J

    # ── 환경 영향 ────────────────────────────────────────────────────────────
    aod           = _aod_from_E_eff_MT(E_eff_MT)
    delta_T_K     = _delta_T_from_aod(aod)
    delta_T_pole  = delta_T_K * 1.5   # 극지방은 1.5× 더 냉각
    shock_str     = min(1.0, E_eff_MT / 1_000_000.0)

    # ── 서사 이벤트 ──────────────────────────────────────────────────────────
    events: List[str] = [
        f"루시퍼 혜성 충돌 — D={D_km:.1f}km, v={v_kms:.1f}km/s, θ={theta_deg:.0f}°",
        f"충돌 에너지: E_total={E_total_J:.2e} J ({E_eff_MT:.2e} MT TNT)",
        f"대기 에너지 분율: {f_atm_frac:.1%} → E_atm={E_atm_J:.2e} J",
        f"에어로졸 광학 두께(AOD): {aod:.3f}",
        f"전지구 온도 강하: {delta_T_K:.1f} K (극지방: {delta_T_pole:.1f} K)",
        "에어로졸 → 광합성 차단 → 빙하기 전구 조건 형성",
    ]
    if aod > 2.0:
        events.append("☢ 핵겨울 수준 AOD — 극지방 급격 결빙 시작 가능")

    summary = (
        f"루시퍼 충돌 | E_eff={E_eff_MT:.2e} MT | AOD={aod:.2f} "
        f"| ΔT={delta_T_K:.1f}K | ΔT_pole={delta_T_pole:.1f}K"
    )

    updates: Dict[str, Any] = {
        "lucifer_E_eff_MT":      E_eff_MT,
        "lucifer_aod":           aod,
        "lucifer_delta_T_K":     delta_T_K,
        "lucifer_delta_T_pole_K": delta_T_pole,
        "lucifer_shock":         shock_str,
    }

    return LuciferImpactStageResult(
        E_total_J=E_total_J,
        E_eff_MT=E_eff_MT,
        f_atm=f_atm_frac,
        aod=aod,
        delta_T_K=delta_T_K,
        delta_T_pole_K=delta_T_pole,
        shock_strength=shock_str,
        summary=summary,
        events=events,
        snapshot_updates=updates,
    )


__all__ = ["LuciferImpactStageResult", "run"]
