# 루시퍼 임팩트 레이어 — 공개 API
#
# 우선순위:
#   1. lucifer_engine 설치됨  →  full pipeline (orbit + detection + effects)
#   2. 미설치               →  run_effects() 단독 파이프라인 (effects-only)
#   3. 완전 폴백            →  impact_estimator (에너지만, 레거시)
#
# 역할 분리 계약:
#   full_pipeline  : 궤도 → MOID → 확률 → [에너지 + 크레이터 + 쓰나미]
#   effects_only   : [에너지 + 크레이터 + 쓰나미]  (충돌은 기정사실로 가정)
#   impact_only    : 에너지만 (레거시 폴백)

from __future__ import annotations

LUCIFER_MODE: str

try:
    # ── 1. full pipeline ──────────────────────────────────────────────────
    from lucifer_engine import (
        LuciferEngine,
        run_effects,
        ImpactParams, ImpactResult, estimate_impact,
        CraterParams, CraterResult, compute_crater,
        TsunamiParams, TsunamiResult, compute_tsunami,
    )
    LUCIFER_MODE = "full_pipeline"

except ImportError:
    # ── 2. effects-only (lucifer_engine 미설치) ───────────────────────────
    try:
        from lucifer_engine.effects import (  # type: ignore[no-redef]
            run_effects,
            ImpactParams, ImpactResult, estimate_impact,
            CraterParams, CraterResult, compute_crater,
            TsunamiParams, TsunamiResult, compute_tsunami,
        )
        LUCIFER_MODE = "effects_only"

    except ImportError:
        # ── 3. 완전 폴백 (레거시) ─────────────────────────────────────────
        from .impact_estimator import (  # type: ignore[no-redef]
            ImpactParams, ImpactResult, estimate_impact,
        )

        def run_effects(D_km, rho_gcm3=0.6, v_kms=20.0, theta_deg=45.0,  # type: ignore[misc]
                        composition="ice", is_ocean=False,
                        water_depth_km=4.0, coast_dist_km=1000.0, **_):
            """레거시 폴백: 에너지만 계산, 크레이터/쓰나미 None 반환."""
            ip = ImpactParams(D_km=D_km, rho_gcm3=rho_gcm3,
                              v_kms=v_kms, theta_deg=theta_deg)
            return estimate_impact(ip), None, None

        LUCIFER_MODE = "impact_only"


def lucifer_strike(
    D_km:           float,
    rho_gcm3:       float = 0.6,
    v_kms:          float = 20.0,
    theta_deg:      float = 45.0,
    is_ocean:       bool  = False,
    water_depth_km: float = 4.0,
    coast_dist_km:  float = 1000.0,
):
    """루시퍼 충돌 효과 계산 — 서사 레이어의 단일 진입점.

    Noah 레이어에서 impulse_shock 주입 시 사용:
        ir, cr, ts = lucifer_strike(D_km=5.0, is_ocean=True)
        impulse = ir.E_eff_MT  →  Noah.compute_effective_instability()

    Returns
    -------
    (ImpactResult, CraterResult | None, TsunamiResult | None)
    """
    return run_effects(
        D_km=D_km, rho_gcm3=rho_gcm3, v_kms=v_kms, theta_deg=theta_deg,
        is_ocean=is_ocean, water_depth_km=water_depth_km,
        coast_dist_km=coast_dist_km,
    )


__all__ = [
    "LUCIFER_MODE",
    "lucifer_strike",
    "run_effects",
    "ImpactParams", "ImpactResult", "estimate_impact",
]
