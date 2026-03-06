"""
천지창조 레이어 — World Generation Pipeline 순서로 실행.

흐름 (시간 = 폴더): precreation(조) → fields(궁창) → governance(하데스) → monitoring(사이렌).
행성 형성 → 환경 → 인지 → Edge AI 피드백.
"""
from __future__ import annotations

from typing import Any, List, Optional, Tuple

try:
    from L0_solar import PIPELINE_ORDER
except Exception:
    PIPELINE_ORDER = ()

# 지연 import: eden 로드 시 fields/governance 순환 참조 방지
joe_run = firmament_step = firmament_get_layer0 = hades_listen = None  # type: ignore
_L0 = _L2 = _L8 = False


def _ensure_layers():
    global joe_run, firmament_step, firmament_get_layer0, hades_listen, _L0, _L2, _L8
    if _L0:
        return
    try:
        from L0_solar._01_beginnings.joe import run as _joe_run
        from L0_solar._02_creation_days.fields.firmament import step as _firmament_step, get_layer0 as _firmament_get_layer0
        from L0_solar._03_eden_os_underworld.governance.hades import listen as _hades_listen
        joe_run = _joe_run
        firmament_step = _firmament_step
        firmament_get_layer0 = _firmament_get_layer0
        hades_listen = _hades_listen
        _L0 = _L2 = _L8 = True
    except Exception:
        pass


def run_creation_layers(
    tick: int,
    world: Any,
    firmament: Any,
    hades_observer: Any,
    deep_engine: Any = None,
    *,
    lineage: Any = None,
) -> Tuple[float, Any, Optional[List[Any]]]:
    """precreation(조) → fields(궁창) → governance(하데스) 순서. (instability, layer0_snapshot, hades_signal) 반환."""
    _ensure_layers()
    instability = 0.0
    layer0 = None
    hades_signal = None

    ic = getattr(world, "ic", None)
    if ic is None:
        return (0.0, None, hades_signal)

    # precreation: 조 탐색 (1일 이전)
    if _L0 and joe_run is not None:
        w_ref = getattr(ic, "W_canopy_ref_km3", None) or 1.0
        h2o_canopy = getattr(ic, "H2O_canopy", 0.0)
        h2o_atm = getattr(ic, "H2O_atm_frac", 0.01)
        water_snapshot = {
            "W_total": float(w_ref),
            "W_surface": float(w_ref * (1.0 - max(0.0, min(1.0, h2o_canopy + h2o_atm)))),
            "W_canopy": float(w_ref * max(0.0, min(1.0, h2o_canopy))),
            "dW_surface_dt_norm": 0.0,
        }
        _ps, instability = joe_run(ic, water_snapshot=water_snapshot)

    # fields: 2일 궁창(퍼머넌트)
    if _L2 and firmament is not None:
        if firmament_step is not None:
            firmament_step(firmament, dt_yr=1.0, instability=instability)
        if firmament_get_layer0 is not None:
            layer0 = firmament_get_layer0(firmament)

    # governance: 하데스 (physics/Lucifer는 listen 내부에서 deep_engine으로 사용)
    if _L8 and hades_listen is not None and hades_observer is not None:
        hades_signal = hades_listen(
            hades_observer, tick, world,
            deep_engine=deep_engine,
            layer0_snapshot=layer0,
        )

    return (instability, layer0, hades_signal)


def build_scenario_overlay(layer0: Any, lineage: Any) -> dict:
    """layer0 + lineage → make_eden_world(ic, scenario_overlay) 에 넣을 dict."""
    if layer0 is None:
        return {}
    group = "admin_line" if (lineage is not None and getattr(lineage, "is_immortal", False)) else "general"
    gen = max(0, getattr(lineage, "depth", lambda: 1)() - 1) if lineage is not None else 0
    return {
        "shield_strength": getattr(layer0, "shield_strength", 1.0),
        "env_load": getattr(layer0, "env_load", 0.0),
        "lifespan_group": group,
        "lifespan_generation": gen,
    }
