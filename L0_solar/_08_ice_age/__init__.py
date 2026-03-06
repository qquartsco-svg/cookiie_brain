"""_08_ice_age — 루시퍼 임팩트 후 빙하시대 진입 시뮬레이션

L0_solar 서사 레이어 8번째 챕터:
  창공 붕괴(_04) → 노아 홍수(_05) → 루시퍼 충돌(_06)
  → 극지방 첫 결빙(_07) → 대륙 빙상 성장 · 빙하시대 진입  ← 여기

물리 레이어:
  ice_sheet.py   질량수지, 부피-면적 관계, 해수면 변화
  feedback.py    빙상-알베도 피드백, 전지구/극지 온도 결합
  simulation.py  장기 시간 적분 오케스트레이터 (explicit Euler, dt=50 yr)

빠른 시작:
  from L0_solar._08_ice_age import run_ice_age_simulation
  r = run_ice_age_simulation(
      T_pole_init_K   = 243.15,   # _07 결빙 이후 극지 기온
      T_global_init_K = 285.0,
      V_ice_init_km3  = 1e5,
      t_max_yr        = 50_000.0,
  )
  print(r.summary())

_07 → _08 연결:
  from L0_solar._07_polar_ice import run_polar_simulation
  from L0_solar._08_ice_age   import run_ice_age_simulation

  p07 = run_polar_simulation(E_eff_MT=2.2e6, delta_T_pole_K=-7.03,
                              T_pole_preimpact_K=273.15)
  p08 = run_ice_age_simulation(
      T_pole_init_K   = p07.steps[-1].T_pole_K,
      T_global_init_K = 285.0,
      V_ice_init_km3  = 1e5,
  )
  print(p08.summary())
"""

from .simulation import run_ice_age_simulation, IceAgeParams, IceAgeStep, IceAgeResult
from .ice_sheet  import (IceSheetParams, IceSheetState,
                          mass_balance, volume_to_geometry, sea_level_change)
from .feedback   import (global_albedo, radiative_forcing,
                          global_temperature, polar_temperature, is_snowball)

__all__ = [
    "run_ice_age_simulation", "IceAgeParams", "IceAgeStep", "IceAgeResult",
    "IceSheetParams", "IceSheetState",
    "mass_balance", "volume_to_geometry", "sea_level_change",
    "global_albedo", "radiative_forcing",
    "global_temperature", "polar_temperature", "is_snowball",
]
