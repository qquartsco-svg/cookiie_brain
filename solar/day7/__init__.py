"""solar/day7 — 일곱째 날: 완성·안식 (Sabbath / Completion)

레이어 포지션:
    Day6: 진화 OS 수렴 (재생산 프로토콜 고정)
    Day7: 통합 러너 + 평형 판정 — "새 기어 없이 전체가 돌아간다"

개념:
    창세기 2:2-3 — 일곱째 날 안식.
    시스템 해석: 새 물리/생물 기어를 더하지 않고,
    Day1~6 전체가 결합된 상태로 안정적으로 작동하는 것을 관측·판정하는 계층.

핵심 구조:
    PlanetRunner  — Day1~6 통합 스텝 드라이버 (12개 위도 밴드 × 독립 엔진)
    SabbathJudge  — 평형/수렴 판정기 (안정성 관측)
    PlanetSnapshot — 한 스텝의 전 지구 상태 스냅샷

12의 의미 (시스템 관점):
    12개 위도 밴드 × 12개 독립 엔진의 만남 지점.
    "지파(tribe)" = 공간 단위 × 기능 단위가 교차하는 행렬.
"""

from __future__ import annotations

from .runner import PlanetRunner, PlanetSnapshot, make_planet_runner
from .sabbath import SabbathJudge, EquilibriumState, make_sabbath_judge

__version__ = "0.1.0"

__all__ = [
    "PlanetRunner",
    "PlanetSnapshot",
    "make_planet_runner",
    "SabbathJudge",
    "EquilibriumState",
    "make_sabbath_judge",
]
