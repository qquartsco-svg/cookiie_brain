"""cycles/ — 장주기 순환 드라이버 (넷째날 순환 2)

Milankovitch 3주기 → 계절성 진폭 → 빙하기-간빙기 자연 창발

  이심률  eccentricity(t): T ~ 100kyr
  경사각  obliquity(t):    T ~ 41kyr   ← Loop C와 연결됨
  세차    precession(t):   T ~ 26kyr

설계 원칙:
  - GaiaLoopConnector.Loop C가 이미 obliquity_scale() 입력 포트 열어놓음
  - cycles/milankovitch.py → obliquity(t) 계산
  - → GaiaLoopConnector.make_fire_env(obliquity_deg=obliquity(t)) 에 주입

구현 예정:
  milankovitch.py   — 이심률/경사/세차 시계열 계산
  insolation.py     — 위도×시간 일사량 (Berger 1978 공식)
  ice_albedo.py     — 빙하 알베도 피드백 (얼음↑→A↑→T↓→얼음↑)

[PLACEHOLDER — 넷째날 구현 예정]
"""

__version__ = "0.0.0-placeholder"
__all__: list = []
