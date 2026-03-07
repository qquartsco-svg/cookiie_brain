"""L0_solar / narrative_runner.py — 창조 서사 전체 오케스트레이터

설계 원칙
─────────────────────────────────────────────────────────────────────────────
1. ENGINE_HUB 엔진 직접 import 없음 — 레이어 경계 유지
   CookiieBrain(서사) ↔ ENGINE_HUB(엔진) 은 snapshot dict 로만 통신

2. 스테이지는 독립 실행 가능 — run(world_state) → StageResult 단일 API
   각 stage.py 의 snapshot_updates 가 다음 스테이지 입력으로 흐름

3. 오케스트레이터는 순서 보장 + 중단 내성
   개별 스테이지가 실패해도 partial result 반환 (서사 중단 없음)

4. AVCE 연결은 _08_ice_age/stage.py 의 avce_env dict 를 통해 명세
   AVCE 를 직접 import 하지 않음 (60_APPLIED 레이어 분리)

서사 흐름
─────────────────────────────────────────────────────────────────────────────
  세계 초기 스냅샷 (Cherubim/JOE/MOE 결과 포함)
      │
      ▼ _04_firmament_era  : 궁창 안정성 평가 → 붕괴 여부
      │
      ▼ _05_noah_flood     : 궁창 붕괴 → 대홍수 → 홍수 후 초기 조건
      │
      ▼ _06_lucifer_impact : 루시퍼 혜성 충돌 → AOD / ΔT / 충격
      │
      ▼ _07_polar_ice      : 에어로졸 냉각 → 극지방 결빙 (0~50yr)
      │
      ▼ _08_ice_age        : 알베도 피드백 → 빙하기 / LGM / AVCE 환경 정의
      │
      ▼ _09_deglaciation   : 밀란코비치 → 해빙 → 홀로세 진입

사용 예시
─────────────────────────────────────────────────────────────────────────────
  from L0_solar.narrative_runner import run_narrative, make_world_snapshot

  snap = make_world_snapshot(
      joe_instability=0.90,     # 궁창 붕괴 수준
      lucifer_D_km=10.0,
  )
  result = run_narrative(snap)
  print(result.summary)

또는 스크립트에서:
  python narrative_runner.py
"""

from __future__ import annotations

import importlib.util
import sys
import traceback
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

# ── 경로 ──────────────────────────────────────────────────────────────────────
_L0_DIR = Path(__file__).resolve().parent


# ── 공통 결과 타입 ────────────────────────────────────────────────────────────

@dataclass
class StageOutcome:
    """단일 스테이지 실행 결과 (외부 보고용)."""
    stage_id:   str
    name:       str
    ok:         bool
    summary:    str
    events:     List[str]          = field(default_factory=list)
    error:      Optional[str]      = None


@dataclass
class NarrativeResult:
    """창조 서사 전체 실행 결과."""
    stages:          List[StageOutcome]
    final_snapshot:  Dict[str, Any]
    ok:              bool
    summary:         str
    timeline_events: List[str]     = field(default_factory=list)

    # 특이 이벤트 플래그
    firmament_collapsed: bool = False
    flood_occurred:      bool = False
    lgm_reached:         bool = False
    holocene_entered:    bool = False

    # AVCE 연결 포인트
    avce_env: Dict[str, Any] = field(default_factory=dict)


# ── 스테이지 로더 ─────────────────────────────────────────────────────────────

def _load_stage_module(stage_dir: str, module_name: str = "stage"):
    """stage.py 를 동적으로 로드하고 모듈 객체 반환. 없으면 None."""
    stage_file = _L0_DIR / stage_dir / f"{module_name}.py"
    if not stage_file.exists():
        return None
    mod_key = f"_l0_{stage_dir}_{module_name}"
    if mod_key in sys.modules:
        return sys.modules[mod_key]
    spec = importlib.util.spec_from_file_location(mod_key, stage_file)
    if spec is None:
        return None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[mod_key] = mod
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


def _run_stage(
    stage_dir: str,
    world_state: Dict[str, Any],
    *,
    stage_name: str = "",
) -> tuple[StageOutcome, Dict[str, Any]]:
    """단일 스테이지를 실행하고 (StageOutcome, 업데이트된 world_state) 를 반환."""
    mod = _load_stage_module(stage_dir)
    label = stage_name or stage_dir

    if mod is None or not hasattr(mod, "run"):
        outcome = StageOutcome(
            stage_id=stage_dir,
            name=label,
            ok=False,
            summary=f"[{stage_dir}] stage.py 없음 — 스킵",
            error="stage.py not found",
        )
        return outcome, world_state

    try:
        result = mod.run(world_state)

        # snapshot_updates 적용
        updates: Dict[str, Any] = getattr(result, "snapshot_updates", {}) or {}
        new_state = {**world_state, **updates}

        outcome = StageOutcome(
            stage_id=getattr(result, "stage_id", stage_dir),
            name=getattr(result, "name", label),
            ok=True,
            summary=getattr(result, "summary", ""),
            events=list(getattr(result, "events", []) or []),
        )
        return outcome, new_state

    except Exception as exc:  # noqa: BLE001
        tb = traceback.format_exc()
        outcome = StageOutcome(
            stage_id=stage_dir,
            name=label,
            ok=False,
            summary=f"[{stage_dir}] 실행 오류",
            error=f"{exc}\n{tb}",
        )
        return outcome, world_state


# ── 기본 세계 스냅샷 팩토리 ───────────────────────────────────────────────────

def make_world_snapshot(
    *,
    # JOE/MOE 기반 (에덴 초기 조건)
    joe_instability: float = 0.20,
    sigma_plate:     float = 0.10,
    P_w:             float = 0.50,
    S_rot:           float = 0.20,
    W_surface:       float = 1.00e9,
    W_total:         float = 1.40e9,
    greenhouse_proxy: float = 0.30,
    magnetosphere_risk: float = 0.20,
    water_cycle_risk: float = 0.15,
    biosphere_window_score: float = 0.85,
    post_albedo:     float = 0.30,

    # 루시퍼 충돌체 파라미터
    lucifer_D_km:      float = 10.0,
    lucifer_rho_gcm3:  float = 1.5,
    lucifer_v_kms:     float = 30.0,
    lucifer_theta_deg: float = 45.0,

    # 추가 오버라이드
    **kwargs: Any,
) -> Dict[str, Any]:
    """창조 서사 초기 세계 스냅샷 생성."""
    snap: Dict[str, Any] = {
        # JOE 물리
        "joe_instability":      joe_instability,
        "instability":          joe_instability,
        "sigma_plate":          sigma_plate,
        "P_w":                  P_w,
        "S_rot":                S_rot,
        "W_surface":            W_surface,
        "W_total":              W_total,
        "dW_surface_dt_norm":   0.0,

        # MOE proxy
        "greenhouse_proxy":     greenhouse_proxy,
        "magnetosphere_risk":   magnetosphere_risk,
        "water_cycle_risk":     water_cycle_risk,
        "biosphere_window_score": biosphere_window_score,

        # 홍수 후 초기 조건
        "post_albedo":          post_albedo,

        # 루시퍼 충돌체
        "lucifer_D_km":         lucifer_D_km,
        "lucifer_rho_gcm3":     lucifer_rho_gcm3,
        "lucifer_v_kms":        lucifer_v_kms,
        "lucifer_theta_deg":    lucifer_theta_deg,
    }
    snap.update(kwargs)
    return snap


# ── 공개 API ──────────────────────────────────────────────────────────────────

# 스테이지 실행 순서 (stage_dir, 표시 이름)
STAGE_SEQUENCE: List[tuple[str, str]] = [
    ("_04_firmament_era",  "궁창 환경시대"),
    ("_05_noah_flood",     "노아 대홍수"),
    ("_06_lucifer_impact", "루시퍼 충돌"),
    ("_07_polar_ice",      "극지방 결빙"),
    ("_08_ice_age",        "빙하기"),
    ("_09_deglaciation",   "해빙·홀로세"),
]


def run_narrative(
    initial_snapshot: Dict[str, Any],
    *,
    stages: Optional[List[str]] = None,
    verbose: bool = False,
) -> NarrativeResult:
    """창조 서사 전 단계를 순서대로 실행한다.

    Parameters
    ----------
    initial_snapshot : dict
        make_world_snapshot() 으로 생성한 세계 초기 스냅샷.
    stages : list[str] | None
        실행할 stage_dir 목록. None 이면 전체 STAGE_SEQUENCE 실행.
    verbose : bool
        True 이면 각 스테이지 이벤트를 stdout 에 출력.

    Returns
    -------
    NarrativeResult
        전체 서사 실행 결과 + 최종 세계 상태.
    """
    target = set(stages) if stages else None

    world_state: Dict[str, Any] = dict(initial_snapshot)
    stage_outcomes: List[StageOutcome] = []
    timeline: List[str] = []

    for stage_dir, stage_name in STAGE_SEQUENCE:
        if target is not None and stage_dir not in target:
            continue

        outcome, world_state = _run_stage(stage_dir, world_state, stage_name=stage_name)
        stage_outcomes.append(outcome)

        # 타임라인 이벤트 누적
        for ev in outcome.events:
            timeline.append(f"[{stage_name}] {ev}")

        if verbose:
            status = "✓" if outcome.ok else "✗"
            print(f"  {status} {stage_name}: {outcome.summary}")
            if outcome.error:
                print(f"      오류: {outcome.error[:120]}")

    # ── 특이 이벤트 플래그 ─────────────────────────────────────────────────
    firmament_collapsed = bool(world_state.get("firmament_collapse", False))
    flood_occurred      = bool(world_state.get("flood_occurred", False))
    lgm_reached         = bool(world_state.get("ice_age_lgm_reached", False))
    holocene            = bool(world_state.get("deglac_holocene", False))
    avce_env            = world_state.get("ice_age_avce_env", {})

    # ── 전체 요약 ───────────────────────────────────────────────────────────
    n_ok = sum(1 for s in stage_outcomes if s.ok)
    flags: List[str] = []
    if firmament_collapsed: flags.append("궁창붕괴")
    if flood_occurred:      flags.append("대홍수")
    if lgm_reached:         flags.append("LGM도달")
    if holocene:            flags.append("홀로세진입")

    summary = (
        f"창조 서사 완료 [{n_ok}/{len(stage_outcomes)} 성공] "
        + (" | ".join(flags) if flags else "| 특이 이벤트 없음")
    )
    if avce_env:
        summary += f" | AVCE={avce_env.get('avce_primary_mode', '?')}"

    return NarrativeResult(
        stages=stage_outcomes,
        final_snapshot=world_state,
        ok=(n_ok == len(stage_outcomes)),
        summary=summary,
        timeline_events=timeline,
        firmament_collapsed=firmament_collapsed,
        flood_occurred=flood_occurred,
        lgm_reached=lgm_reached,
        holocene_entered=holocene,
        avce_env=avce_env,
    )


# ── CLI 엔트리포인트 ──────────────────────────────────────────────────────────

def _print_result(result: NarrativeResult) -> None:
    """결과를 포맷해 stdout 에 출력."""
    print()
    print("=" * 64)
    print("  창조 서사 결과 (L0_solar narrative_runner)")
    print("=" * 64)

    for outcome in result.stages:
        status = "✓" if outcome.ok else "✗"
        print(f"\n[{status}] {outcome.name}")
        print(f"    {outcome.summary}")
        for ev in outcome.events:
            print(f"    · {ev}")
        if outcome.error:
            print(f"    ⚠ 오류: {outcome.error[:200]}")

    print()
    print("─" * 64)
    print("  타임라인 핵심 이벤트:")
    key_events = [e for e in result.timeline_events
                  if any(k in e for k in ["붕괴", "홍수", "충돌", "결빙", "LGM", "홀로세", "AVCE"])]
    for ev in key_events:
        print(f"  ▸ {ev}")

    print()
    print("─" * 64)
    if result.avce_env:
        print("  ★ AVCE 연결 포인트 (60_APPLIED_LAYER 인터페이스):")
        print(f"    primary_mode   : {result.avce_env.get('avce_primary_mode', '?')}")
        print(f"    secondary_mode : {result.avce_env.get('avce_secondary_mode', '?')}")
        print(f"    ice_hardness   : {result.avce_env.get('ice_hardness', 0):.2f}")
        print(f"    sea_level_drop : {result.avce_env.get('sea_level_drop_m', 0):.0f} m")
        print(f"    context        : {result.avce_env.get('narrative_context', '')}")
        print()

    print("=" * 64)
    print(f"  종합: {result.summary}")
    print("=" * 64)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="CookiieBrain L0_solar 창조 서사 실행")
    parser.add_argument("--instability", type=float, default=0.92,
                        help="JOE 불안정도 (0~1). 0.85 이상이면 궁창 붕괴")
    parser.add_argument("--lucifer-D",   type=float, default=10.0,
                        help="루시퍼 혜성 직경 [km]")
    parser.add_argument("--lucifer-v",   type=float, default=30.0,
                        help="루시퍼 혜성 속도 [km/s]")
    parser.add_argument("--no-flood",    action="store_true",
                        help="홍수 없음 시나리오 (instability=0.3 강제)")
    args = parser.parse_args()

    if args.no_flood:
        inst = 0.30
    else:
        inst = args.instability

    snap = make_world_snapshot(
        joe_instability=inst,
        lucifer_D_km=args.lucifer_D,
        lucifer_v_kms=args.lucifer_v,
    )

    print(f"\n초기 조건: instability={inst}, D={args.lucifer_D}km, v={args.lucifer_v}km/s")
    result = run_narrative(snap, verbose=True)
    _print_result(result)
