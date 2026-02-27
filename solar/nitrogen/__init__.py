"""nitrogen/ — 질소 순환 (넷째날 순환 1)

N₂ ↔ 고정질소(NH₃, NO₃) ↔ 단백질 ↔ 사체분해 ↔ N₂

설계 원칙:
  - biosphere/column.py의 GPP에 N_soil 게이트 추가
  - pioneer 단계부터 질소고정 시작
  - 기어 분리: nitrogen/는 biosphere/를 읽지만, biosphere/는 nitrogen/를 모름
               → GaiaLoopConnector가 두 모듈을 연결

구현 예정:
  fixation.py     — 질소고정 ODE (pioneer + 번개)
  cycle.py        — 질소순환 통합 (토양↔대기↔식물)
  column.py       — NitrogenColumn (상태 + step)

[PLACEHOLDER — 넷째날 구현 예정]
"""

__version__ = "0.0.0-placeholder"
__all__: list = []
