"""노아 대홍수 이벤트 — 실행·오케스트레이션 레이어.

이 모듈은 이미 구현된 Eden 쪽 구성요소들을 "한 줄"로 엮어

    JOE(instability) → FirmamentLayer → FloodEngine → postdiluvian IC

타임라인을 따라가 볼 수 있는 헬퍼를 제공한다.

- JOE 쪽에서는 time t에서의 `instability`(0~1)를 공급한다고 가정한다.
- MOE/환경 쪽에서는 선택적으로 water_cycle, magnetosphere 등의 리스크를
  스칼라로 넘겨주면 된다.
- FirmamentLayer/FloodEngine/InitialConditions/EdenSearch/EdenOS는
  이미 solar 내 다른 모듈에서 구현되어 있으며, 여기서는 그 위를
  흐르는 "시뮬레이션 시나리오"만 담당한다.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional


def run_flood_step(
    flood_engine: Any = None,
    dt_yr: float = 1.0,
) -> Any:
    """대홍수 한 스텝. FloodSnapshot 반환.

    기존 코드와의 호환성을 위해 남겨 둔 얇은 래퍼.
    새 시나리오에서는 run_noah_cycle() 사용을 권장한다.
    """
    from L0_solar._03_eden_os_underworld.eden import flood as _flood

    if flood_engine is None:
        flood_engine = _flood.make_flood_engine()
    return flood_engine.step(dt_yr=dt_yr)


def run_trigger_flood(firmament: Any) -> None:
    """궁창 붕괴 트리거 (대홍수 시작).

    FirmamentLayer 인스턴스를 받아 trigger_flood() 를 호출한다.
    """
    if firmament is not None and hasattr(firmament, "trigger_flood"):
        firmament.trigger_flood()


# ── 효과적 불안정도(effective_instability) 계산 ──────────────────────────────


def compute_effective_instability(
    joe_instability: float,
    *,
    water_cycle_risk: float | None = None,
    magnetosphere_risk: float | None = None,
    greenhouse_proxy: float | None = None,
    mode: str = "macro",
) -> float:
    """JOE 불안정도 + (선택) MOE 리스크를 합성해 궁창 붕괴에 쓸 지표를 만든다.

    Parameters
    ----------
    joe_instability : float
        PANGEA §4 Aggregator에서 나온 JOE 불안정도 [0~1].
    water_cycle_risk : float, optional
        MOE 쪽 수순환/수권 리스크 [0~1].
    magnetosphere_risk : float, optional
        자기권 관련 리스크 [0~1].
    greenhouse_proxy : float, optional
        온실 폭주 정도를 나타내는 proxy [0~1].
    mode : {'macro', 'decay', 'combined'}
        - 'macro'    : JOE 불안정도만 사용 (기본).
        - 'decay'    : 시간 경과에 따른 자연 붕괴를 시뮬레이션할 때
                       JOE 신호를 약하게 올려 잡는 용도.
        - 'combined' : water_cycle, magnetosphere, greenhouse를 함께 고려.

    Returns
    -------
    float
        effective_instability in [0, 1].
    """

    # 기본은 JOE 신호만 그대로.
    base = max(0.0, min(1.0, joe_instability))

    if mode == "macro":
        return base

    if mode == "decay":
        # JOE가 낮더라도 아주 긴 시간 스케일에서 천천히 임계값에 근접하게 하는
        # 느슨한 상향 보정. (상세 시간 의존성은 run_noah_cycle 루프에서 결정.)
        eff = 0.5 * base + 0.25
        return max(0.0, min(1.0, eff))

    # 'combined' 모드: 수권/자기권/온실 리스크를 합성.
    wc = max(0.0, min(1.0, water_cycle_risk or 0.0))
    mag = max(0.0, min(1.0, magnetosphere_risk or 0.0))
    gh = max(0.0, min(1.0, greenhouse_proxy or 0.0))

    # 가중치: 매크로 60% + 수권 20% + 자기권 10% + 온실 10%.
    eff = 0.6 * base + 0.2 * wc + 0.1 * mag + 0.1 * gh
    return max(0.0, min(1.0, eff))


# ── Noah 시나리오 결과 스냅샷 ──────────────────────────────────────────────


@dataclass
class NoahStepSnapshot:
    """노아 시나리오 타임라인 중 한 시점의 상태."""

    t_yr: float
    joe_instability: float
    effective_instability: float
    firmament_phase: str
    firmament_active: bool
    flood_phase: str | None = None
    sea_level_anomaly_m: float | None = None


@dataclass
class NoahSimulationResult:
    """노아 대홍수 시뮬레이션 결과.

    - steps: 시간 순서대로 누적된 스냅샷 목록.
    - flood_event: FirmamentLayer 가 생성한 FloodEvent (있다면).
    - post_ic: 홍수 종결 후 InitialConditions (make_postdiluvian 기준) 또는 None.
    """

    steps: List[NoahStepSnapshot]
    flood_event: Any | None = None
    post_ic: Any | None = None


# ── Noah 시나리오 실행 루프 ────────────────────────────────────────────────


def run_noah_cycle(
    *,
    years: float = 20.0,
    dt_yr: float = 0.1,
    joe_instability_fn: Callable[[float], float],
    risk_fn: Callable[[float], Dict[str, float]] | None = None,
    mode: str = "macro",
    firmament: Any | None = None,
    flood_engine: Any | None = None,
) -> NoahSimulationResult:
    """JOE→Firmament→Flood→postdiluvian 흐름을 한 번 따라가는 시뮬레이션.

    이 함수는 "알고리즘 단계"를 확인하는 용도다. JOE 엔진·PlanetRunner·MOE·Eden은
    외부에서 제공(또는 간단한 프록시 함수)한다고 가정한다.

    Parameters
    ----------
    years : float, default 20.0
        시뮬레이션 총 기간 [yr]. 홍수 전이(<=10yr) 이후 완충 기간을 포함하도록
        10년 이상을 권장.
    dt_yr : float, default 0.1
        타임스텝 크기 [yr].
    joe_instability_fn : Callable[[float], float]
        시간 t_yr → JOE instability[0~1] 를 반환하는 함수.
        예: lambda t: min(1.0, 0.1 * t).
    risk_fn : Callable[[float], Dict[str, float]], optional
        시간 t_yr → {'water_cycle_risk':..., 'magnetosphere_risk':..., 'greenhouse_proxy':...}
        형태의 dict를 반환하는 함수. 제공되지 않으면 combined 모드에서도 0으로 간주.
    mode : {'macro', 'decay', 'combined'}
        compute_effective_instability 모드와 동일.
    firmament : FirmamentLayer, optional
        None이면 solar._03_eden_os_underworld.eden.firmament.make_firmament() 로 생성.
    flood_engine : FloodEngine, optional
        None이면 궁창 붕괴 이후 solar._03_eden_os_underworld.eden.flood.make_flood_engine()
        로 생성.

    Returns
    -------
    NoahSimulationResult
        스텝별 스냅샷과 flood_event, postdiluvian IC가 포함된 결과.
    """

    from L0_solar._03_eden_os_underworld.eden import flood as _flood
    from L0_solar._03_eden_os_underworld.eden import firmament as _firm
    from L0_solar._03_eden_os_underworld.eden import initial_conditions as _ic

    if firmament is None:
        firmament = _firm.make_firmament()

    steps: List[NoahStepSnapshot] = []
    flood_event: Any | None = None
    post_ic: Any | None = None

    t = 0.0
    n_steps = int(years / dt_yr)

    for _ in range(n_steps):
        joe_inst = joe_instability_fn(t)

        risks: Dict[str, float] = {}
        if risk_fn is not None:
            risks = risk_fn(t) or {}

        eff_inst = compute_effective_instability(
            joe_instability=joe_inst,
            water_cycle_risk=risks.get("water_cycle_risk"),
            magnetosphere_risk=risks.get("magnetosphere_risk"),
            greenhouse_proxy=risks.get("greenhouse_proxy"),
            mode=mode,
        )

        # 궁창 상태 업데이트 (instability가 높아지면 내부에서 붕괴 판단)
        state = firmament.step(dt_yr=dt_yr, instability=eff_inst)

        flood_phase: str | None = None
        sea_anom: float | None = None

        # 궁창이 막 붕괴된 직후 FloodEngine 생성
        if not state.active and flood_engine is None:
            flood_engine = _flood.make_flood_engine()
            # FirmamentLayer가 FloodEvent를 제공한다면 한 번만 캡처
            flood_event = getattr(firmament, "flood_event", None)

        # 홍수 진행 중이면 FloodEngine을 따라 한 스텝 진행
        if flood_engine is not None and not getattr(flood_engine, "is_complete", False):
            snap = flood_engine.step(dt_yr=dt_yr)
            flood_phase = getattr(snap, "flood_phase", None)
            sea_anom = getattr(snap, "sea_level_anomaly_m", None)

            # 홍수 완결 후에는 postdiluvian IC를 한 번 만들어 둔다.
            if getattr(flood_engine, "is_complete", False) and post_ic is None:
                # 현재 구현에서는 standard postdiluvian 프리셋을 사용.
                post_ic = _ic.make_postdiluvian()

        steps.append(
            NoahStepSnapshot(
                t_yr=t,
                joe_instability=joe_inst,
                effective_instability=eff_inst,
                firmament_phase=getattr(state, "phase", "unknown"),
                firmament_active=bool(getattr(state, "active", False)),
                flood_phase=flood_phase,
                sea_level_anomaly_m=sea_anom,
            )
        )

        t += dt_yr

    return NoahSimulationResult(
        steps=steps,
        flood_event=flood_event,
        post_ic=post_ic,
    )


# ── postdiluvian 상태 평가 헬퍼 ────────────────────────────────────────────


def evaluate_postdiluvian(
    result: NoahSimulationResult,
    *,
    f_land_target: float = 0.29,
    albedo_target: float = 0.306,
    pressure_target: float = 1.0,
    T_C_target: float = 13.3,
    pole_eq_delta_target: float = 48.0,
    tol_f_land: float = 0.02,
    tol_albedo: float = 0.02,
    tol_pressure: float = 0.05,
    tol_T_C: float = 5.0,
    tol_pole_eq_delta: float = 5.0,
) -> Dict[str, Any]:
    """NoahSimulationResult 가 "지구형(postdiluvian)" 상태에 얼마나 근접했는지 평가한다.

    Parameters
    ----------
    result : NoahSimulationResult
        run_noah_cycle() 반환값.
    f_land_target, albedo_target, pressure_target, T_C_target, pole_eq_delta_target :
        현재 지구를 대표하는 목표값들.
    tol_* :
        각 항목 허용 오차.

    Returns
    -------
    dict
        {
          'ok': bool,
          'checks': {항목별 bool},
          'values': {항목별 실제값},
        }
    """

    ic = result.post_ic
    if ic is None:
        return {
            "ok": False,
            "checks": {"has_post_ic": False},
            "values": {},
        }

    T_C = ic.T_surface_K - 273.15

    checks = {
        "has_post_ic": True,
        "f_land": abs(ic.f_land - f_land_target) <= tol_f_land,
        "albedo": abs(ic.albedo - albedo_target) <= tol_albedo,
        "pressure_atm": abs(ic.pressure_atm - pressure_target) <= tol_pressure,
        "H2O_canopy": abs(ic.H2O_canopy - 0.0) <= 1e-3,
        "UV_shield": abs(ic.UV_shield - 0.0) <= 1e-2,
        "mutation_factor": abs(ic.mutation_factor - 1.0) <= 0.1,
        "T_surface_C": abs(T_C - T_C_target) <= tol_T_C,
        "pole_eq_delta_K": abs(ic.pole_eq_delta_K - pole_eq_delta_target) <= tol_pole_eq_delta,
    }

    ok = all(checks.values())

    values = {
        "f_land": ic.f_land,
        "albedo": ic.albedo,
        "pressure_atm": ic.pressure_atm,
        "H2O_canopy": ic.H2O_canopy,
        "UV_shield": ic.UV_shield,
        "mutation_factor": ic.mutation_factor,
        "T_surface_C": T_C,
        "pole_eq_delta_K": ic.pole_eq_delta_K,
    }

    return {
        "ok": ok,
        "checks": checks,
        "values": values,
    }


__all__ = [
    "run_flood_step",
    "run_trigger_flood",
    "compute_effective_instability",
    "NoahStepSnapshot",
    "NoahSimulationResult",
    "run_noah_cycle",
    "evaluate_postdiluvian",
]

