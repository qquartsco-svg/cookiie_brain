"""_07_polar_ice — 루시퍼 임팩트 후 극지방 결빙 시뮬레이션

L0_solar 서사 레이어 7번째 챕터:
  창공 붕괴(_04) → 노아 홍수(_05) → 루시퍼 충돌(_06)
  → 극지방 첫 결빙 · 빙하시대 개시  ← 여기

물리 레이어:
  climate.py        에어로졸 광학 깊이, 온도 강제, 수증기 캐노피
  energy_balance.py 극지방 복사 수지 (Budyko-Sellers + 자오선 열 수송)
  stefan_ice.py     Stefan 법칙 얼음 두께 성장
  simulation.py     통합 시간 적분 오케스트레이터 (암묵적 Euler)

빠른 시작:
  from L0_solar._07_polar_ice import run_polar_simulation
  result = run_polar_simulation(E_eff_MT=2.2e6, delta_T_pole_K=-7.0,
                                T_pole_preimpact_K=273.15)
  print(result.summary())

LuciferEngine 연결:
  from L0_solar._06_lucifer_impact import lucifer_strike
  ir, cr, ts = lucifer_strike(D_km=5.0, is_ocean=True)
  from L0_solar._07_polar_ice import run_polar_simulation
  result = run_polar_simulation(
      E_eff_MT           = ir.E_eff_MT,
      delta_H2O_kg       = ir.delta_H2O_canopy,
      delta_T_pole_K     = ir.delta_pole_eq_K,
      T_pole_preimpact_K = 273.15,
  )
"""

from .simulation   import run_polar_simulation, PolarSimResult, SimStep
from .climate      import (ImpactClimateForcingParams, ClimateState,
                            climate_state_at, climate_trajectory,
                            freeze_onset_time)
from .energy_balance import (PolarSurfaceState, polar_energy_balance,
                              equilibrium_temperature)
from .stefan_ice   import (IceState, stefan_thickness, ice_growth_rate,
                            snow_accumulation)

__all__ = [
    "run_polar_simulation", "PolarSimResult", "SimStep",
    "ImpactClimateForcingParams", "ClimateState",
    "climate_state_at", "climate_trajectory", "freeze_onset_time",
    "PolarSurfaceState", "polar_energy_balance", "equilibrium_temperature",
    "IceState", "stefan_thickness", "ice_growth_rate", "snow_accumulation",
]
