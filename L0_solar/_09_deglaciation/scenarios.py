"""scenarios.py — 탈빙하기 시나리오 비교

4개 CO₂ 경로 시나리오를 동시 실행해 비교한다.

시나리오:
  S1 RCP 8.5  : 현재 추세 지속 (2100년 ~1050ppm)
  S2 RCP 6.0  : 중간 경로     (2100년 ~670ppm)
  S3 RCP 4.5  : 파리협약 부분 이행 (2100년 ~550ppm)
  S4 RCP 2.6  : 넷제로 2050  (2050년 ~490ppm 정점 후 감소)
"""
from __future__ import annotations
from dataclasses import dataclass
from .simulation import run_deglaciation_simulation, DeglaciationResult


SCENARIO_LABELS = {
    "rcp85":   "S1 현재 추세 유지 (RCP 8.5)",
    "rcp60":   "S2 중간 경로     (RCP 6.0)",
    "rcp45":   "S3 파리협약 부분 (RCP 4.5)",
    "rcp26":   "S4 넷제로 2050  (RCP 2.6)",
    "current": "S0 현재 증가율  (선형 추정)",
}


def run_all(t_max_yr: float = 500.0, dt_yr: float = 1.0) -> dict[str, DeglaciationResult]:
    """모든 시나리오 실행 후 결과 딕셔너리 반환"""
    results = {}
    for sc in ["rcp85", "rcp60", "rcp45", "rcp26"]:
        results[sc] = run_deglaciation_simulation(
            scenario=sc, t_max_yr=t_max_yr, dt_yr=dt_yr
        )
    return results


def comparison_table(results: dict[str, DeglaciationResult]) -> str:
    """핵심 이벤트 발생 연도 비교 표"""
    sep = "-" * 90
    rows = [
        sep,
        "  탈빙하기 시나리오 비교 — 핵심 이벤트 발생 연도",
        sep,
        f"  {'시나리오':<36}  {'북극빙하소멸':>10}  {'MISI':>6}  {'SLR+1m':>7}"
        f"  {'SLR+3m':>7}  {'그린란드50%':>10}  {'그린란드소멸':>10}  {'서남극소멸':>8}",
        "  " + "-" * 86,
    ]

    def fmt(v):
        return f"{v:.0f}" if v is not None else "—"

    for sc, r in results.items():
        label = SCENARIO_LABELS.get(sc, sc)
        rows.append(
            f"  {label:<36}  {fmt(r.year_arctic_ice_free):>10}  {fmt(r.year_wais_misi):>6}"
            f"  {fmt(r.year_slr_1m):>7}  {fmt(r.year_slr_3m):>7}"
            f"  {fmt(r.year_greenland_half):>10}  {fmt(r.year_greenland_gone):>10}"
            f"  {fmt(r.year_wais_gone):>8}"
        )
    rows.append(sep)
    return "\n".join(rows)


if __name__ == "__main__":
    print("시나리오 실행 중...")
    results = run_all(t_max_yr=500.0, dt_yr=1.0)
    print(comparison_table(results))
    print()
    # 대표 시나리오 상세 출력
    print(results["rcp85"].summary())
