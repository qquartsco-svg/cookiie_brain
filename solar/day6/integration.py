"""integration — Day6 한 세대 진화 스텝 (contact → mutation → selection → reproduction)

확장 유지: 각 엔진은 그대로 두고, 호출 순서만 한 곳에서 정의.
Optional 인자로 graph, k_encounter_by_band 등 Day5·Species 연동.
"""

from __future__ import annotations

from typing import List, Dict, Any, Optional
import random

from .contact_engine import ContactEngine
from .mutation_engine import MutationEngine
from .reproduction_engine import ReproductionEngine, ReproductionResult
from .selection_engine import SelectionEngine
from .genome_state import GenomeState


def evolution_step(
    population: List[GenomeState],
    env: Dict[str, Any],
    band_densities: List[List[float]],
    contact_engine: ContactEngine,
    mutation_engine: MutationEngine,
    reproduction_engine: ReproductionEngine,
    selection_engine: SelectionEngine,
    n_offspring: int,
    k_encounter_by_band: Optional[List[float]] = None,
    dt_yr: float = 1.0,
    rng: Optional[random.Random] = None,
) -> List[GenomeState]:
    """한 세대: 밴드별 조우 → p_contact → 변이 이벤트 → 선택 → 재조합 → 자손군 반환.

    band_densities[band][species] = ρ 로 ContactEngine 호출.
    k_encounter_by_band 가 있으면 밴드별 k_encounter 적용 (Day5Coupler 연동).

    반환: n_offspring 명의 자손 (GenomeState 리스트). 기존 population 은 변경하지 않음.
    """
    rng = rng or random.Random()
    n_bands = len(band_densities)
    if n_bands == 0:
        p_contact = 0.0
    else:
        p_sum = 0.0
        for b, rho in enumerate(band_densities):
            k = None
            if k_encounter_by_band and b < len(k_encounter_by_band):
                k = k_encounter_by_band[b]
            cr = contact_engine.compute(rho, k_encounter_override=k)
            p_sum += cr.p_contact_scalar
        p_contact = p_sum / n_bands

    n_traits = len(population[0].traits) if population else 4
    mutation_engine.step(
        p_contact=p_contact,
        env=env,
        dt_yr=dt_yr,
        band_idx=0,
        n_traits=n_traits,
        rng=rng,
    )

    def select_a(pop: List[GenomeState]) -> int:
        res = selection_engine.select(pop, env, n_select=1, rng=rng)
        return res.survivors[0]

    def select_b(pop: List[GenomeState]) -> int:
        return selection_engine.select_exploration(pop, n_select=1, rng=rng)[0]

    results: List[ReproductionResult] = reproduction_engine.step(
        population,
        select_parent_a=select_a,
        select_parent_b=select_b,
        n_offspring=n_offspring,
        rng=rng,
    )
    return [r.child for r in results]


__all__ = ["evolution_step"]
