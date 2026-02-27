"""gravity_tides/ — 중력-조석 주기 (넷째날 순환 3)

조석력 → 해양 혼합 → 영양염 순환 → 탄소 격리 → 대기 CO₂↓

  F_tidal(t) = F_moon(t) + F_sun(t)
  → mixing_depth → nutrient_upwelling → 식물플랑크톤↑ → 탄소격리↑

설계 원칙:
  - core/tidal_field.py가 이미 조석 계산 완료
  - gravity_tides/는 tidal_field 출력을 받아 해양 영양염 계산
  - 결과를 biosphere/와 atmosphere/에 주입 (GaiaLoopConnector 경유)

구현 예정:
  tidal_mixing.py      — 조석 혼합 깊이 ODE
  ocean_nutrients.py   — 영양염 upwelling 모델
  carbon_pump.py       — 생물학적 탄소 펌프 (biological pump)

[PLACEHOLDER — 넷째날 구현 예정]
"""

__version__ = "0.0.0-placeholder"
__all__: list = []
