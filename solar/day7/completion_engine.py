"""completion_engine — Day7 완성·안식 레이어

역할:
  - Day1~6를 "읽기/쓰기 포트"로만 결선해 한 스텝 진행.
  - 새 물리/생물 기어를 추가하지 않음 (쉼 = 구조 고정).
  - 통합 상태 스냅샷(CompletionState) 반환 — 평형 판정·로깅용.

12와의 관계:
  - n_bands=12, n_wells=12 등은 호출자가 넘기는 설정으로만 사용.
  - 12의 시스템적 의미는 docs/WHY_12_SYSTEMIC.md 참고.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional


@dataclass
class CompletionState:
    """Day7 한 스텝 후 통합 스냅샷.

    각 필드는 Day1~6에서 올라온 요약값 또는 플래그.
    평형 판정·로깅·시각화용. 필드는 확장 가능.
    """
    step_count: int = 0
    t_yr: float = 0.0
    # 요약 (호출자가 채우거나, runner가 서브엔진 출력으로 채움)
    snapshot: Dict[str, Any] = field(default_factory=dict)
    # 평형/안정 플래그 (선택)
    equilibrium_detected: bool = False
    notes: List[str] = field(default_factory=list)


class CompletionEngine:
    """완성·안식 레이어: 서브엔진을 포트로만 결선해 한 스텝 실행.

    서브엔진 인스턴스는 외부에서 주입. Day1~6의 step(…) 호출 순서만 정의.
    n_bands, n_wells 등 12 관련 파라미터는 설정으로 받아 그대로 하위에 전달.

    Parameters
    ----------
    n_bands : int
        위도 밴드 수 (기본 12). 시스템적 의미는 WHY_12_SYSTEMIC.md 참고.
    n_wells : int
        해양 우물 수 (기본 12). 동일 문서 참고.
    """

    def __init__(
        self,
        n_bands: int = 12,
        n_wells: int = 12,
    ) -> None:
        self.n_bands = max(1, n_bands)
        self.n_wells = max(1, n_wells)
        self._step_count = 0
        self._t_yr = 0.0

    def step(
        self,
        dt_yr: float,
        ports: Dict[str, Any],
    ) -> CompletionState:
        """한 스텝 진행.

        ports: 서브엔진/상태를 담은 dict. 예:
          - evolution_engine, atmosphere_engine, biosphere_bands, ...
          - 또는 이미 계산된 snapshot만 넘겨서 "메타 관측"만 수행

        실제로 Day1~6를 호출하려면 호출자가 ports에 엔진을 넣어주고,
        여기서는 ports["runner"](dt_yr) 같은 단일 콜백을 호출하거나,
        혹은 step 내부에서 ports의 각 엔진을 순서대로 step 호출.

        현재는 "스텝 카운트와 스냅샷 전달"만 수행 (실제 결선은 호출자).
        """
        self._step_count += 1
        self._t_yr += dt_yr

        snapshot = dict(ports.get("snapshot", {}))
        snapshot["step_count"] = self._step_count
        snapshot["t_yr"] = self._t_yr
        snapshot["n_bands"] = self.n_bands
        snapshot["n_wells"] = self.n_wells

        return CompletionState(
            step_count=self._step_count,
            t_yr=self._t_yr,
            snapshot=snapshot,
            equilibrium_detected=ports.get("equilibrium_detected", False),
            notes=list(ports.get("notes", [])),
        )

    @property
    def step_count(self) -> int:
        return self._step_count

    @property
    def t_yr(self) -> float:
        return self._t_yr


def make_completion_engine(
    n_bands: int = 12,
    n_wells: int = 12,
) -> CompletionEngine:
    return CompletionEngine(n_bands=n_bands, n_wells=n_wells)


__all__ = ["CompletionEngine", "CompletionState", "make_completion_engine"]
