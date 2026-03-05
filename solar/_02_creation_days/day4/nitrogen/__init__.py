"""nitrogen/ — 질소 순환 (넷째날 순환 1)

N₂ ↔ 고정질소(NH₃, NO₃) ↔ 단백질 ↔ 사체분해 ↔ N₂

설계 원칙:
  - biosphere/column.py의 GPP에 N_limitation 게이트 추가
  - pioneer 단계부터 질소고정 시작
  - 기어 분리: nitrogen/는 biosphere/를 읽지만, biosphere/는 nitrogen/를 모름
               → GaiaLoopConnector가 두 모듈을 연결

구현 완료:
  fixation.py   — 질소고정 ODE (생물고정 + 번개)
  cycle.py      — 질소순환 통합 (토양↔대기↔식물)

구현 예정 (넷째날 후기):
  column.py     — NitrogenColumn (상태 + step, biosphere 연결)
"""

from .fixation import (
    NitrogenFixation,
    FixationResult,
    make_fixation_engine,
    K_FIX_MAX,
    O2_HALF_N2FIX,
    T_OPT_N2FIX,
)

from .cycle import (
    NitrogenCycle,
    NitrogenState,
    make_nitrogen_cycle,
    K_UPTAKE,
    K_DENITRIFY,
    K_DECOMP,
    GPP_REF,
    Q10_DECOMP,
    T_REF_DECOMP,
)

__all__ = [
    # fixation
    "NitrogenFixation",
    "FixationResult",
    "make_fixation_engine",
    "K_FIX_MAX",
    "O2_HALF_N2FIX",
    "T_OPT_N2FIX",
    # cycle
    "NitrogenCycle",
    "NitrogenState",
    "make_nitrogen_cycle",
    "K_UPTAKE",
    "K_DENITRIFY",
    "K_DECOMP",
    "GPP_REF",
    "Q10_DECOMP",
    "T_REF_DECOMP",
]

__version__ = "1.1.0"
