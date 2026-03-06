"""eden_os_bridge — Cherubim/EdenSearch → EdenOSRunner 브리지.

테라포밍 파이프라인 서사 기준:

    조(JOE) → (_02_creation_days) → EdenSearchEngine → CherubimGuard → EdenOSRunner

여기서는 EdenSearchEngine/체루빔 단계에서 나온 결과를 받아
곧바로 `EdenOSRunner` 인스턴스로 올려 주는 helper를 제공한다.

설계 원칙:
- 이 모듈은 `_03_eden_os_underworld` 안에서만 사용되는 브리지다.
- `solar._03_eden_os_underworld.eden.search` 의 `EdenCandidate`, `SearchResult`
  와 `eden_os_runner.make_eden_os_runner` 를 연결한다.
- Day7 PlanetRunner, Joe 엔진 등 상위 레이어로 역의존하지 않는다.
"""

from __future__ import annotations

from typing import Optional

from ..search import EdenCandidate, SearchResult
from .eden_os_runner import EdenOSRunner, make_eden_os_runner


def make_eden_os_from_candidate(
    candidate: EdenCandidate,
    *,
    seed: Optional[int] = None,
) -> EdenOSRunner:
    """단일 `EdenCandidate` 에서 바로 `EdenOSRunner` 를 생성한다.

    Parameters
    ----------
    candidate : EdenCandidate
        `solar._03_eden_os_underworld.eden.search.EdenSearchEngine` 가 산출한 후보.
        내부에 `InitialConditions`(ic)가 포함되어 있으며, 이는 Day7 PlanetRunner와
        동일한 구조의 환경 스냅샷이다.
    seed : int, optional
        EdenOS 내부 난수 시드. None이면 기본값 사용.
    """

    ic = candidate.ic
    runner = make_eden_os_runner(world_ic=ic, seed=seed)
    return runner


def make_eden_os_from_search_result(
    result: SearchResult,
    *,
    rank: int = 1,
    seed: Optional[int] = None,
) -> EdenOSRunner:
    """`SearchResult` 에서 순위 기반으로 후보를 골라 EdenOSRunner 를 만든다.

    Parameters
    ----------
    result : SearchResult
        EdenSearchEngine.search() 의 반환값.
    rank : int, default 1
        사용할 후보 순위 (1 기반). 기본은 최상위 에덴 후보.
    seed : int, optional
        EdenOS 내부 난수 시드.
    """

    if not result.candidates:
        raise ValueError("SearchResult.candidates 가 비어 있습니다 (에덴 후보 없음).")

    if rank < 1 or rank > len(result.candidates):
        raise IndexError(
            f"rank={rank} 는 유효 범위를 벗어났습니다 (1..{len(result.candidates)}).",
        )

    candidate = result.candidates[rank - 1]
    return make_eden_os_from_candidate(candidate, seed=seed)


__all__ = [
    "make_eden_os_from_candidate",
    "make_eden_os_from_search_result",
]
