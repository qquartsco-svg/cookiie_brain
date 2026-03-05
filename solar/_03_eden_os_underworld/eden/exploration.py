"""exploration.py — 행성 탐사 확장: Grid Engine 연동으로 에덴 탐색 성능 향상

목적:
  - 행성(12 위도밴드)을 "탐사 그리드"로 다루고,
  - Grid Engine으로 "탐사 포커스(유망 밴드)"를 유지해
  - 후보 수가 제한될 때 포커스 밴드 점수 기준 우선 유지 → 탐사 효율·성능 향상.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from .search import EdenCandidate

BAND_COUNT = 12


@dataclass
class EdenExplorationGrid:
    """행성 탐사 그리드: 12밴드별 탐사 결과 + Grid Engine 탐사 포커스.

    - band_best_score[i]: 지금까지 후보들 중 i번 밴드에서 나온 최고 에덴 점수.
    - Grid Engine 있으면: focus_band = 탐사 포커스 밴드 (유망 영역). 후보 트림 시 이 밴드 점수 우선 반영.
    """

    band_best_score: List[float] = field(default_factory=lambda: [0.0] * BAND_COUNT)
    _grid_agent: Optional[object] = field(default=None, repr=False)

    def __post_init__(self) -> None:
        try:
            from solar.bridge import grid_engine_bridge
            if grid_engine_bridge.is_available():
                self._grid_agent = grid_engine_bridge.create_latitude_grid_agent(
                    initial_band=0, ring_size=15
                )
        except Exception:
            pass

    def focus_band(self) -> int:
        """현재 탐사 포커스 밴드 (Grid Engine이 가리키는 밴드). 없으면 최고점 밴드."""
        if self._grid_agent is not None:
            return self._grid_agent.get_band_index()
        # fallback: 가장 점수 높은 밴드
        best = 0
        for i in range(BAND_COUNT):
            if self.band_best_score[i] > self.band_best_score[best]:
                best = i
        return best

    def update_from_candidate(self, c: EdenCandidate) -> None:
        """후보 한 건 반영: 밴드별 최고점 갱신, Grid 포커스를 이 후보의 최적 밴드로 이동."""
        for i in range(min(BAND_COUNT, len(c.band_eden_score))):
            s = c.band_eden_score[i]
            if s > self.band_best_score[i]:
                self.band_best_score[i] = s
        best_band = 0
        for i in range(min(BAND_COUNT, len(c.band_eden_score))):
            if c.band_eden_score[i] > c.band_eden_score[best_band]:
                best_band = i
        if self._grid_agent is not None:
            self._grid_agent.reset(band=best_band)

    def step_explore(self, velocity_lat: float) -> int:
        """탐사 포커스를 위도 방향으로 한 스텝 이동. (Grid Engine 있을 때만 의미 있음)"""
        if self._grid_agent is not None:
            return self._grid_agent.step(velocity_lat)
        return self.focus_band()

    def use_grid(self) -> bool:
        """Grid Engine 연동 여부."""
        return self._grid_agent is not None


def trim_candidates_by_exploration(
    candidates: List[EdenCandidate],
    max_candidates: int,
    exploration: Optional[EdenExplorationGrid],
) -> List[EdenCandidate]:
    """후보 리스트를 max_candidates로 줄일 때, 탐사 포커스 밴드 점수 반영해 우선 유지."""
    if exploration is None or not exploration.use_grid():
        candidates.sort(key=lambda x: x.score, reverse=True)
        return candidates[:max_candidates]
    focus = exploration.focus_band()
    # 전역 score 우선, 동점이면 포커스 밴드 점수로 정렬 → 탐사 성능 향상
    def key(c: EdenCandidate) -> tuple:
        fb_score = c.band_eden_score[focus] if focus < len(c.band_eden_score) else 0.0
        return (c.score, fb_score)
    candidates.sort(key=key, reverse=True)
    return candidates[:max_candidates]
