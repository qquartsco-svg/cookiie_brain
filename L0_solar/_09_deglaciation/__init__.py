"""_09_deglaciation — 탈빙하기 동역학 시뮬레이션

2024년 현재 상태에서 출발해 CO₂ 시나리오별 빙하 소멸 과정을 추적.

공개 API
--------
run_deglaciation_simulation(scenario, t_max_yr, dt_yr) -> DeglaciationResult
run_all(t_max_yr, dt_yr) -> dict[scenario, DeglaciationResult]
comparison_table(results) -> str
"""
from .simulation import run_deglaciation_simulation, DeglaciationResult, DeglaciationStep
from .scenarios  import run_all, comparison_table
from .forcing    import co2_trajectory_ppm, total_forcing
from .ice_dynamics import IceState, sea_level_contribution

__all__ = [
    "run_deglaciation_simulation",
    "DeglaciationResult",
    "DeglaciationStep",
    "run_all",
    "comparison_table",
    "co2_trajectory_ppm",
    "total_forcing",
    "IceState",
    "sea_level_contribution",
]
