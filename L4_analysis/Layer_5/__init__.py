"""Layer 5: 확률역학 (Stochastic Mechanics)

Layer 1–4의 궤적 관점을 확률 밀도 ρ(x,t) 진화 관점으로 전환한다.
Nelson 확률역학의 forward/backward 속도 분해를 포함한다.

핵심:
  - Fokker-Planck: ∂ρ/∂t = ∇·(∇V·ρ/(mγ)) + D∇²ρ
  - Nelson: v = v_current + v_osmotic
  - 정상 분포: ρ_eq ∝ exp(−V/T)  (볼츠만)
  - 확률류: J = bρ − D∇ρ  (평형: J=0)
"""

from .stochastic_mechanics import (
    FokkerPlanckSolver1D,
    NelsonDecomposition,
    ProbabilityCurrent,
    double_well_potential,
    gaussian_initial,
    langevin_ensemble_histogram,
)

__all__ = [
    "FokkerPlanckSolver1D",
    "NelsonDecomposition",
    "ProbabilityCurrent",
    "double_well_potential",
    "gaussian_initial",
    "langevin_ensemble_histogram",
]
