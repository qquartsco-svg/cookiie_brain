"""_04_firmament_era / stage.py — 궁창 환경시대 서사 스테이지

설계 원칙
─────────
* ENGINE_HUB 엔진 직접 import 없음 (레이어 분리 유지)
* snapshot dict 하나를 입력으로 받아 FirmamentStageResult 반환
* run() 는 항상 성공 — 복잡한 내부 모듈이 없어도 독립 실행 가능
* 결과 snapshot_updates 키를 통해 다음 스테이지로 상태 전달

물리 요약
─────────
  창세기 1장 기준 "궁창(firmament/raqia)" = 수증기 캐노피 + 자기권 차폐 복합체
  JOE instability 가 collapse_threshold(0.85) 를 넘으면 붕괴 트리거
  shield_strength = max(0, 1 − instability / threshold)
  env_load       = instability × env_scale

서사 흐름 → 다음 스테이지 전달 키
  firmament_shield     : 현재 캐노피 차폐 강도 [0, 1]
  firmament_phase      : "intact" | "weakening" | "collapsed"
  firmament_instability: 이 스테이지에서 계산된 불안정도
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

# ── 궁창 물리 상수 ────────────────────────────────────────────────────────────
COLLAPSE_THRESHOLD: float = 0.85   # 궁창 붕괴 임계 instability
WEAKENING_START:    float = 0.40   # 약화 시작 임계
ENV_SCALE:          float = 2.0    # env_load 스케일 계수


# ── 결과 ────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class FirmamentStageResult:
    """궁창 환경시대 스테이지 실행 결과 (불변)."""

    stage_id:   str   = "_04_firmament_era"
    name:       str   = "궁창 환경시대"

    # 물리 출력
    instability:       float = 0.0    # 이 스테이지 불안정도 [0, 1]
    shield_strength:   float = 1.0    # 궁창 차폐 강도 [0, 1]
    env_load:          float = 0.0    # 환경 부하 [0, 1]
    canopy_intact:     bool  = True   # 캐노피 유지 여부
    collapse_triggered:bool  = False  # 이 스테이지에서 붕괴 여부
    phase:             str   = "intact"  # intact | weakening | collapsed

    # 서사 메타
    summary:           str          = ""
    events:            List[str]    = field(default_factory=list)
    snapshot_updates:  Dict[str, Any] = field(default_factory=dict)


# ── 핵심 물리 함수 ────────────────────────────────────────────────────────────

def _compute_instability(snapshot: Dict[str, Any]) -> float:
    """스냅샷에서 궁창용 불안정도를 합성.

    설계:
      JOE instability 가 주 신호 (궁창 붕괴 직접 트리거).
      MOE 리스크는 ±0.05 범위 내 미세 보정만 한다.
      → 외부에서 joe_instability=0.92 를 전달하면 0.92 근방이 그대로 반영됨.
    """
    joe_inst = snapshot.get("joe_instability", None)
    if joe_inst is not None:
        base = float(joe_inst)
    else:
        base = float(snapshot.get("instability", 0.0))

    # MOE 보조 (미세 보정: ±0.05 이내)
    water_risk = float(snapshot.get("water_cycle_risk",   0.0))
    mag_risk   = float(snapshot.get("magnetosphere_risk", 0.0))
    gh_proxy   = float(snapshot.get("greenhouse_proxy",   0.0))

    correction = 0.03 * water_risk + 0.01 * mag_risk + 0.01 * gh_proxy
    effective  = base + correction
    return max(0.0, min(1.0, effective))


def _phase_from_instability(inst: float) -> str:
    if inst >= COLLAPSE_THRESHOLD:
        return "collapsed"
    if inst >= WEAKENING_START:
        return "weakening"
    return "intact"


# ── 공개 API ─────────────────────────────────────────────────────────────────

def run(world_state: Dict[str, Any]) -> FirmamentStageResult:
    """궁창 환경시대 스테이지를 실행하고 결과를 반환한다.

    Parameters
    ----------
    world_state : dict
        현재 세계 스냅샷. JOE/MOE 결과 키를 포함할 수 있음.

    Returns
    -------
    FirmamentStageResult
        snapshot_updates 에 다음 스테이지로 전달할 키가 담겨 있음.
    """
    inst   = _compute_instability(world_state)
    phase  = _phase_from_instability(inst)

    # 차폐 강도: threshold 에 근접할수록 선형 감소
    if inst >= COLLAPSE_THRESHOLD:
        shield = 0.0
    else:
        shield = max(0.0, 1.0 - inst / COLLAPSE_THRESHOLD)

    env_load = min(1.0, inst * ENV_SCALE)
    canopy_intact = (phase != "collapsed")
    collapse_triggered = (phase == "collapsed")

    # 서사 이벤트 목록
    events: List[str] = []
    if phase == "intact":
        events.append("궁창 안정 — 수증기 캐노피 정상 유지")
    elif phase == "weakening":
        events.append(f"궁창 약화 시작 (instability={inst:.3f} ≥ {WEAKENING_START})")
        events.append("UV 차단 능력 저하, 극지방 온도 상승 시작")
    else:
        events.append(f"궁창 붕괴 임계 도달 (instability={inst:.3f} ≥ {COLLAPSE_THRESHOLD})")
        events.append("수증기 캐노피 붕괴 → 강수 가속 → 홍수 트리거 조건 충족")
        events.append("자기권 차폐 약화 → 우주선 유입 증가 → 돌연변이율 상승")

    summary = (
        f"궁창={phase} | 차폐={shield:.3f} | 환경부하={env_load:.3f} | "
        f"instability={inst:.3f}"
    )

    # 다음 스테이지로 전달할 상태 업데이트
    updates: Dict[str, Any] = {
        "firmament_shield":          shield,
        "firmament_phase":           phase,
        "firmament_instability":     inst,
        "firmament_env_load":        env_load,
        "firmament_collapse":        collapse_triggered,
    }

    return FirmamentStageResult(
        instability=inst,
        shield_strength=shield,
        env_load=env_load,
        canopy_intact=canopy_intact,
        collapse_triggered=collapse_triggered,
        phase=phase,
        summary=summary,
        events=events,
        snapshot_updates=updates,
    )


__all__ = ["FirmamentStageResult", "run", "COLLAPSE_THRESHOLD"]
