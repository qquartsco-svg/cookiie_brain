"""_08_ice_age.scenarios — 시나리오 비교 시뮬레이션

에덴 → 루시퍼 충돌 → 빙하시대 → 현재 지구까지
4개 시나리오를 나란히 실행해 비교한다.

시나리오:
  S1. 기준선 — 루시퍼 충돌 후 빙하시대 진입 (창공 붕괴 포함)
  S2. 에덴 상태 — 충돌 없음, 창공 유지 (빙하시대가 오는가?)
  S3. 약한 충돌 — 소행성급 (E_eff 1/100 규모)
  S4. 탈빙하기 — LGM에서 현재 지구(14.2°C)로 복귀하려면?

실행:
  cd CookiieBrain
  python3 -m L0_solar._08_ice_age.scenarios
"""

from __future__ import annotations

from dataclasses import dataclass
from .simulation import run_ice_age_simulation, IceAgeResult


# ── 시나리오 정의 ──────────────────────────────────────────────────────────────

@dataclass
class Scenario:
    name:            str
    label:           str
    T_pole_init_K:   float
    T_global_init_K: float
    V_ice_init_km3:  float
    t_max_yr:        float
    dt_yr:           float
    co2_forcing:     float
    description:     str


SCENARIOS: list[Scenario] = [
    Scenario(
        name            = "S1_lucifer_lgm",
        label           = "S1 루시퍼 → 빙하시대 (기준선)",
        T_pole_init_K   = 243.15,   # −30°C  (_07 결빙 후)
        T_global_init_K = 285.0,    # +12°C  (에어로졸 소산 후)
        V_ice_init_km3  = 1e5,
        t_max_yr        = 100_000.0,
        dt_yr           = 100.0,
        co2_forcing     = 0.0,
        description     = (
            "루시퍼 충돌 + 창공 붕괴 이후 기준 시나리오.\n"
            "충돌 직후(T_pole=-30°C)부터 빙상 성장을 추적한다.\n"
            "→ 빙하시대 LGM 재현 목표"
        ),
    ),
    Scenario(
        name            = "S2_eden_no_impact",
        label           = "S2 에덴 상태 — 충돌 없음",
        T_pole_init_K   = 273.15,   # 0°C   (창공 온실, 극지도 온난)
        T_global_init_K = 297.0,    # +24°C (수증기 캐노피 온실 효과)
        V_ice_init_km3  = 1e5,      # 초기 소형 빙상 (안정성 테스트)
        t_max_yr        = 100_000.0,
        dt_yr           = 100.0,
        co2_forcing     = 0.0,
        description     = (
            "창공(Firmament) 유지, 충돌 없음.\n"
            "에덴 시대 기온 조건(전지구 24°C, 극지 0°C)에서\n"
            "빙하시대가 자연 발생하는지 검증한다.\n"
            "→ 창공 없이는 빙하시대가 불가능함을 보이는 대조군"
        ),
    ),
    Scenario(
        name            = "S3_weak_impact",
        label           = "S3 약한 충돌 — 소행성급 (Chicxulub 1/10)",
        T_pole_init_K   = 258.15,   # −15°C (중간 냉각)
        T_global_init_K = 287.0,    # +14°C (현재 지구 근접)
        V_ice_init_km3  = 1e5,
        t_max_yr        = 100_000.0,
        dt_yr           = 100.0,
        co2_forcing     = 0.0,
        description     = (
            "루시퍼보다 1/10 규모 충돌.\n"
            "창공 붕괴 없이 소행성 충돌만으로\n"
            "빙하시대가 유발되는지 확인한다.\n"
            "→ 창공 붕괴가 빙하시대의 핵심 조건임을 검증"
        ),
    ),
    Scenario(
        name            = "S4_deglaciation",
        label           = "S4 탈빙하기 — LGM → 현재 지구(+14.2°C)",
        T_pole_init_K   = 243.15,   # −30°C (LGM 극지 기온)
        T_global_init_K = 285.0,    # 기준 (에어로졸 소산 후)
        V_ice_init_km3  = 5.0e7,    # LGM 최대 빙상에서 시작
        t_max_yr        = 50_000.0,
        dt_yr           = 50.0,
        co2_forcing     = 19.0,     # W/m²  화산 CO₂ + 궤도 강제 복합
        description     = (
            "LGM 최대 빙상(V=5×10⁷ km³)에서 출발.\n"
            "화산 CO₂ + 궤도 강제 복합(+19 W/m²)을 가해\n"
            "현재 지구 상태(T=14.2°C, SL≈0m)로 복귀하는\n"
            "탈빙하기 경로를 추적한다."
        ),
    ),
]


def run_all(verbose: bool = True) -> dict[str, IceAgeResult]:
    """4개 시나리오 전체 실행."""
    results: dict[str, IceAgeResult] = {}

    for sc in SCENARIOS:
        if verbose:
            print(f"\n{'─'*60}")
            print(f"  {sc.label}")
            print(f"{'─'*60}")
            print(f"  T_pole  = {sc.T_pole_init_K - 273.15:+.1f}°C"
                  f"  T_global = {sc.T_global_init_K - 273.15:+.1f}°C"
                  f"  V_init  = {sc.V_ice_init_km3:.0e} km³")
            print(f"  CO₂ 강제 = {sc.co2_forcing:+.1f} W/m²"
                  f"  기간 = {sc.t_max_yr:,.0f} yr\n")

        r = run_ice_age_simulation(
            T_pole_init_K       = sc.T_pole_init_K,
            T_global_init_K     = sc.T_global_init_K,
            V_ice_init_km3      = sc.V_ice_init_km3,
            t_max_yr            = sc.t_max_yr,
            dt_yr               = sc.dt_yr,
            co2_forcing_W_m2    = sc.co2_forcing,
        )
        results[sc.name] = r

        if verbose:
            print(r.summary())

    return results


def comparison_table(results: dict[str, IceAgeResult]) -> str:
    """4개 시나리오 최종 상태 비교 테이블."""
    sep  = "=" * 80
    sep2 = "-" * 80
    lines = [
        sep,
        "  시나리오 비교 — 최종 상태 (10만 년 기준 / S4는 5만 년)",
        sep,
        f"  {'시나리오':<30}  {'빙하선':>8}  {'해수면':>9}  {'T_전지구':>10}  {'스노우볼':>8}",
        "  " + sep2,
    ]

    # 현재 지구 기준선
    lines.append(
        f"  {'◎ 현재 지구 (2026년)':<30}  {'~85°N':>8}  {'+0.0 m':>9}"
        f"  {'+14.2°C':>10}  {'없음':>8}"
    )
    lines.append(
        f"  {'◎ 실제 LGM (~2만 년 전)':<30}  {'~55-65°N':>8}  {'-120 m':>9}"
        f"  {'~+8°C':>10}  {'없음':>8}"
    )
    lines.append("  " + sep2)

    sc_labels = {
        "S1_lucifer_lgm":    "S1 루시퍼→빙하시대 (기준선)",
        "S2_eden_no_impact": "S2 에덴 (충돌 없음)",
        "S3_weak_impact":    "S3 약한 충돌 (소행성급)",
        "S4_deglaciation":   "S4 탈빙하기 (CO₂+19 W/m²)",
    }

    for sc in SCENARIOS:
        r   = results[sc.name]
        s   = r.steps[-1]
        sb  = "진입" if r.snowball_yr is not None else "없음"
        lbl = sc_labels[sc.name]
        lines.append(
            f"  {lbl:<30}  {s.phi_ice_deg:>7.1f}°N  {s.sea_level_m:>8.1f}m"
            f"  {s.T_global_C:>+10.1f}°C  {sb:>8}"
        )

    lines.append(sep)
    return "\n".join(lines)


if __name__ == "__main__":
    results = run_all(verbose=True)
    print()
    print(comparison_table(results))
