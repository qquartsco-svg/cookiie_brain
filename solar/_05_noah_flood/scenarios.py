from __future__ import annotations

"""Noah 시나리오 모음 — run_noah_cycle 데모 드라이버.

이 모듈은 `_05_noah_flood/engine.py` 에 구현된 `run_noah_cycle()` /
`evaluate_postdiluvian()` 을 여러 형태의 트리거로 실행해 보는 헬퍼를 제공한다.

핵심 아이디어:

- JOE instability / MOE-style risk / 외부 임팩트를 시간 함수로 두고
- 같은 FirmamentLayer / FloodEngine / InitialConditions 위에서
- 서로 다른 상전이(궁창 붕괴·대홍수·postdiluvian 안착) 시나리오를 비교한다.

여기서 정의하는 시나리오 (약칭):

- 시나리오 A: macro_only
    - 거시 물리(JOE instability)만 서서히 증가.
- 시나리오 B: macro_decay
    - JOE instability는 낮게 유지되지만, decay 모드로 아주 긴 시간 축에서
      자연 붕괴를 가정.
- 시나리오 C: combined_ramp  (기본 예시)
    - 조(JOE) + 수순환 + 온실 + 자기권 리스크를 함께 올리는 복합 트리거.
- 시나리오 D: impulse_shock
    - 평소에는 안정적이지만, 특정 시점에 짧은 임펄스(혜성/플레어 등)를 주입.
- 시나리오 E: combined_impulse (Fuse Model)
    - C 시나리오처럼 임계 근처까지 올린 뒤, D 시나리오처럼 짧은 임펄스를 겹쳐
      “복합 스트레스 + 외부 도화선” 구조를 본다.

각 함수는 (result, report) 튜플을 반환한다.
result  : NoahSimulationResult (steps, flood_event, post_ic)
report  : evaluate_postdiluvian(result) 반환 dict
"""

from typing import Callable, Dict, Tuple

from .engine import NoahSimulationResult, evaluate_postdiluvian, run_noah_cycle
from solar._06_lucifer_impact import ImpactParams, ImpactResult, estimate_impact


YearsFn = Callable[[float], float]
RiskFn = Callable[[float], Dict[str, float]]


def _print_brief(name: str, result: NoahSimulationResult, report: Dict) -> None:
    """시뮬레이션 한 번 돌린 뒤 간단 요약을 stdout 에 찍는 유틸."""

    steps = result.steps
    n = len(steps)
    first = steps[0] if n else None
    last = steps[-1] if n else None

    print(f"[{name}] steps={n}")
    if first is not None:
        print(
            f"  t_start={first.t_yr:.2f} yr, "
            f"instability={first.effective_instability:.3f}, "
            f"firmament_phase={first.firmament_phase}",
        )
    if last is not None:
        print(
            f"  t_end={last.t_yr:.2f} yr, "
            f"instability={last.effective_instability:.3f}, "
            f"firmament_phase={last.firmament_phase}, "
            f"flood_phase={last.flood_phase}, "
            f"sea_level_anom={last.sea_level_anomaly_m}",
        )

    print(f"  postdiluvian_ok={bool(report.get('ok'))}")
    checks = report.get("checks", {})
    if checks:
        ok_keys = [k for k, v in checks.items() if v]
        ng_keys = [k for k, v in checks.items() if not v]
        print(f"  checks_ok={ok_keys}")
        if ng_keys:
            print(f"  checks_ng={ng_keys}")


def run_scenario_macro_only(
    *,
    years: float = 25.0,
    dt_yr: float = 0.1,
) -> Tuple[NoahSimulationResult, Dict]:
    """시나리오 A — 거시 물리(JOE)만으로 붕괴하는 경우.

    JOE instability 를 t=0 에서 0.1, t=years 에서 1.0 근방까지 선형 증가로 가정한다.
    risk_fn 은 사용하지 않고 mode='macro' 로 실행한다.
    """

    def joe_instability_fn(t: float) -> float:
        frac = max(0.0, min(1.0, t / years))
        return 0.1 + 0.9 * frac

    result = run_noah_cycle(
        years=years,
        dt_yr=dt_yr,
        joe_instability_fn=joe_instability_fn,
        risk_fn=None,
        mode="macro",
    )
    report = evaluate_postdiluvian(result)
    _print_brief("macro_only", result, report)
    return result, report


def run_scenario_macro_decay(
    *,
    years: float = 80.0,
    dt_yr: float = 0.5,
) -> Tuple[NoahSimulationResult, Dict]:
    """시나리오 B — decay 모드 기반 장기 붕괴.

    JOE instability 는 전 구간에서 0.3 근방의 낮은 값으로 유지하되,
    mode='decay' 를 사용하여 아주 긴 시간 축에서 궁창이 피로 누적으로
    붕괴하는 경우를 본다.
    """

    def joe_instability_fn(t: float) -> float:
        return 0.3

    result = run_noah_cycle(
        years=years,
        dt_yr=dt_yr,
        joe_instability_fn=joe_instability_fn,
        risk_fn=None,
        mode="decay",
    )
    report = evaluate_postdiluvian(result)
    _print_brief("macro_decay", result, report)
    return result, report


def run_scenario_combined_ramp(
    *,
    years: float = 25.0,
    dt_yr: float = 0.1,
) -> Tuple[NoahSimulationResult, Dict]:
    """시나리오 C — 복합 램프(조 + 수순환 + 온실 + 자기권).

    - t < years*0.4     : 비교적 안정 (instability≈0.2, risk≈0.1).
    - years*0.4~0.7 구간: water_cycle / greenhouse 를 강하게 올려 감.
    - t > years*0.7     : high-risk 구간 유지.
    """

    def joe_instability_fn(t: float) -> float:
        frac = max(0.0, min(1.0, t / years))
        return 0.2 + 0.6 * frac

    def risk_fn(t: float) -> Dict[str, float]:
        frac = max(0.0, min(1.0, t / years))
        if frac < 0.4:
            w = 0.1
            g = 0.1
            m = 0.1
        elif frac < 0.7:
            ramp = (frac - 0.4) / 0.3
            w = 0.1 + 0.7 * ramp
            g = 0.1 + 0.7 * ramp
            m = 0.2 + 0.4 * ramp
        else:
            w = 0.8
            g = 0.8
            m = 0.6
        return {
            "water_cycle_risk": w,
            "greenhouse_proxy": g,
            "magnetosphere_risk": m,
        }

    result = run_noah_cycle(
        years=years,
        dt_yr=dt_yr,
        joe_instability_fn=joe_instability_fn,
        risk_fn=risk_fn,
        mode="combined",
    )
    report = evaluate_postdiluvian(result)
    _print_brief("combined_ramp", result, report)
    return result, report


def run_scenario_impulse_shock(
    *,
    years: float = 20.0,
    dt_yr: float = 0.1,
    shock_time: float = 10.0,
) -> Tuple[NoahSimulationResult, Dict]:
    """시나리오 D — 외부 임팩트(혜성/플레어 등) 임펄스.

    - 기본선: instability≈0.25, risk≈0.15 로 거의 안정 상태 유지.
    - shock_time 근처에서 짧은 시간 동안 instability / risk 를 강하게 스파이크.
    """

    def joe_instability_fn(t: float) -> float:
        base = 0.25
        if abs(t - shock_time) < 0.5:
            return 0.9
        if abs(t - shock_time) < 1.0:
            return 0.7
        return base

    def risk_fn(t: float) -> Dict[str, float]:
        base = 0.15
        if abs(t - shock_time) < 0.5:
            k = 0.9
        elif abs(t - shock_time) < 1.0:
            k = 0.6
        else:
            k = base
        return {
            "water_cycle_risk": k,
            "greenhouse_proxy": k,
            "magnetosphere_risk": k * 0.8,
        }

    result = run_noah_cycle(
        years=years,
        dt_yr=dt_yr,
        joe_instability_fn=joe_instability_fn,
        risk_fn=risk_fn,
        mode="combined",
    )
    report = evaluate_postdiluvian(result)
    _print_brief("impulse_shock", result, report)
    return result, report


def run_scenario_combined_impulse(
    *,
    years: float = 30.0,
    dt_yr: float = 0.1,
    shock_time: float = 20.0,
) -> Tuple[NoahSimulationResult, Dict]:
    """시나리오 E — 복합 램프 + 임펄스(퓨즈 모델).

    - t < years*0.4     : combined_ramp 와 유사한 완만한 상승 (instability≈0.2→0.6).
    - years*0.4~0.7 구간: 수순환/온실/자기권 리스크를 0.8 근방까지 올린다.
    - shock_time 근처   : impulse_shock 처럼 instability / risk 에 짧은 스파이크.

    목적:
      - “거시·환경·생물권 스트레스가 이미 임계 근처까지 쌓인 상태에서,
         혜성 같은 외부 임펄스가 마지막 도화선 역할을 하는” Fuse 모델을 본다.
    """

    def joe_instability_fn(t: float) -> float:
        frac = max(0.0, min(1.0, t / years))
        base = 0.2 + 0.6 * frac  # combined_ramp 와 동일 베이스
        # shock 구간에서는 추가로 상향
        if abs(t - shock_time) < 0.5:
            return min(1.0, base + 0.25)
        if abs(t - shock_time) < 1.0:
            return min(1.0, base + 0.10)
        return base

    def risk_fn(t: float) -> Dict[str, float]:
        frac = max(0.0, min(1.0, t / years))
        # 기본 램프 (combined_ramp 와 유사)
        if frac < 0.4:
            w = 0.2
            g = 0.2
            m = 0.15
        elif frac < 0.7:
            ramp = (frac - 0.4) / 0.3
            w = 0.2 + 0.6 * ramp
            g = 0.2 + 0.6 * ramp
            m = 0.2 + 0.4 * ramp
        else:
            w = 0.8
            g = 0.8
            m = 0.6

        # shock 구간에서는 impulse_shock 처럼 임펄스 추가
        if abs(t - shock_time) < 0.5:
            k = 0.9
        elif abs(t - shock_time) < 1.0:
            k = 0.7
        else:
            k = None

        if k is not None:
            w = max(w, k)
            g = max(g, k)
            m = max(m, k * 0.8)

        return {
            "water_cycle_risk": w,
            "greenhouse_proxy": g,
            "magnetosphere_risk": m,
        }

    result = run_noah_cycle(
        years=years,
        dt_yr=dt_yr,
        joe_instability_fn=joe_instability_fn,
        risk_fn=risk_fn,
        mode="combined",
    )
    report = evaluate_postdiluvian(result)
    _print_brief("combined_impulse", result, report)
    return result, report


def run_scenario_lucifer_impact_mid_ocean(
    *,
    years: float = 30.0,
    dt_yr: float = 0.1,
    shock_time: float = 20.0,
) -> Tuple[NoahSimulationResult, Dict]:
    """루시퍼 임팩트 시나리오 — 중간 크기 암석체, 심해 충돌.

    대략 "중간 규모(수 km) 충돌이 깊은 바다(h≈4km)에 떨어지는" 케이스를 가정한다.
    - D≈10km, rho≈3 g/cm³, v≈20 km/s, theta≈45°
    - 태평양/인도양과 유사한 심해를 대표하는 h_km=4.0 사용.

    결과로 나온 ImpactResult 의 shock_strength 를 combined_impulse 패턴에 얹어서
    Fuse 모델과의 결합 효과를 본다.
    """

    params = ImpactParams(
        D_km=10.0,
        rho_gcm3=3.0,
        v_kms=20.0,
        theta_deg=45.0,
        h_km=4.0,
        lat_deg=-30.0,
        lon_deg=120.0,
    )
    impact: ImpactResult = estimate_impact(params)

    def joe_instability_fn(t: float) -> float:
        frac = max(0.0, min(1.0, t / years))
        base = 0.2 + 0.6 * frac
        if abs(t - shock_time) < 0.5:
            return min(1.0, base + 0.25 * impact.shock_strength)
        if abs(t - shock_time) < 1.0:
            return min(1.0, base + 0.10 * impact.shock_strength)
        return base

    def risk_fn(t: float) -> Dict[str, float]:
        frac = max(0.0, min(1.0, t / years))
        if frac < 0.4:
            w = 0.2
            g = 0.2
            m = 0.15
        elif frac < 0.7:
            ramp = (frac - 0.4) / 0.3
            w = 0.2 + 0.6 * ramp
            g = 0.2 + 0.6 * ramp
            m = 0.2 + 0.4 * ramp
        else:
            w = 0.8
            g = 0.8
            m = 0.6

        if abs(t - shock_time) < 0.5:
            k = 0.9 * impact.shock_strength
        elif abs(t - shock_time) < 1.0:
            k = 0.7 * impact.shock_strength
        else:
            k = None

        if k is not None:
            w = max(w, k)
            g = max(g, k)
            m = max(m, k * 0.8)

        return {
            "water_cycle_risk": w,
            "greenhouse_proxy": g,
            "magnetosphere_risk": m,
        }

    result = run_noah_cycle(
        years=years,
        dt_yr=dt_yr,
        joe_instability_fn=joe_instability_fn,
        risk_fn=risk_fn,
        mode="combined",
    )
    report = evaluate_postdiluvian(result)
    _print_brief("lucifer_impact_mid_ocean", result, report)
    return result, report


if __name__ == "__main__":
    # 간단 CLI: python -m solar._05_noah_flood.scenarios
    print("Running Noah flood scenarios...")
    run_scenario_macro_only()
    print()
    run_scenario_macro_decay()
    print()
    run_scenario_combined_ramp()
    print()
    run_scenario_impulse_shock()
    print()
    run_scenario_combined_impulse()
    print()
    run_scenario_lucifer_impact_mid_ocean()

