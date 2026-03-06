"""cycles/ — 장주기 순환 드라이버 (넷째날 순환 2)

Milankovitch 3주기 → 계절성 진폭 → 빙하기-간빙기 자연 창발

  이심률  eccentricity(t): T ~ 100kyr / 413kyr
  경사각  obliquity(t):    T ~ 41kyr   ← Loop C와 연결됨
  세차    precession(t):   T ~ 26kyr

의존 방향:
  cycles/ → (없음, 독립)
  GaiaLoopConnector ← cycles/ 출력 주입

구현 완료:
  milankovitch.py   — 이심률/경사/세차 해석적 시계열 (Berger 1978)
  insolation.py     — 위도×시간 일사량 + MilankovitchDriver

구현 예정 (넷째날):
  ice_albedo.py     — 빙하 알베도 피드백 (is_glacial → Loop B 강화)
"""

from .milankovitch import (
    MilankovitchCycle,
    MilankovitchState,
    make_earth_cycle,
    make_custom_cycle,
)

from .insolation import (
    insolation_at,
    insolation_grid,
    MilankovitchDriver,
    DriverOutput,
    make_earth_driver,
)

__all__ = [
    # milankovitch
    "MilankovitchCycle",
    "MilankovitchState",
    "make_earth_cycle",
    "make_custom_cycle",
    # insolation
    "insolation_at",
    "insolation_grid",
    "MilankovitchDriver",
    "DriverOutput",
    "make_earth_driver",
]

__version__ = "1.0.0"
