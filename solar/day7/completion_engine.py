"""completion_engine — Day7 완성·안식 레이어 (CompletionEngine)

역할:
  - PlanetRunner(통합 스텝) + SabbathJudge(안정 판정)를 한 엔진으로 감싼다.
  - 새 물리/생물 기어를 추가하지 않음 (쉼 = 구조 고정).
  - 한 스텝마다 (PlanetSnapshot, EquilibriumState) 를 모아 CompletionState로 반환.

12와의 관계:
  - n_bands=12, n_wells=12 등은 호출자가 넘기는 설정으로만 사용.
  - 12의 시스템적 의미는 docs/WHY_12_SYSTEMIC.md 참고.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .runner import PlanetRunner, PlanetSnapshot, make_planet_runner
from .sabbath import SabbathJudge, EquilibriumState, make_sabbath_judge


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
    planet_snapshot: Optional[PlanetSnapshot] = None
    equilibrium: Optional[EquilibriumState] = None


class CompletionEngine:
    """완성·안식 레이어: PlanetRunner + SabbathJudge 통합 엔진.

    Parameters
    ----------
    n_bands : int
        위도 밴드 수 (기본 12). 시스템적 의미는 WHY_12_SYSTEMIC.md 참고.
    n_wells : int
        해양 우물 수 (기본 12). 현재 Day7 runner에 직접 결선되진 않지만,
        전 지구 해상도/설정 값으로 snapshot에 기록한다.
    runner : PlanetRunner, optional
        외부에서 runner를 주입하면 그대로 사용.
    judge : SabbathJudge, optional
        외부에서 judge를 주입하면 그대로 사용.
    """

    def __init__(
        self,
        n_bands: int = 12,
        n_wells: int = 12,
        runner: Optional[PlanetRunner] = None,
        judge: Optional[SabbathJudge] = None,
    ) -> None:
        self.n_bands = max(1, n_bands)
        self.n_wells = max(1, n_wells)
        self._step_count = 0
        self._t_yr = 0.0
        self.runner = runner or make_planet_runner(n_bands=self.n_bands)
        self.judge = judge or make_sabbath_judge(window=12)

    def step(
        self,
        dt_yr: float,
        ports: Optional[Dict[str, Any]] = None,
    ) -> CompletionState:
        """한 스텝 진행: runner.step → judge.push/judge.judge → CompletionState."""
        ports = ports or {}
        self._step_count += 1
        self._t_yr += dt_yr

        snap = self.runner.step(dt_yr=dt_yr)
        self.judge.push(snap)
        eq = self.judge.judge()

        snapshot = dict(ports.get("snapshot", {}))
        snapshot.update(
            {
                "step_count": self._step_count,
                "t_yr": self._t_yr,
                "n_bands": self.n_bands,
                "n_wells": self.n_wells,
                # 전 지구 핵심 스칼라 (PlanetSnapshot 요약)
                "CO2_ppm": snap.CO2_ppm,
                "T_surface_K": snap.T_surface_K,
                "obliquity_deg": snap.obliquity_deg,
                "insolation_scale": snap.insolation_scale,
                "planet_stress": snap.planet_stress,
                "mutation_events": snap.mutation_events,
            }
        )

        return CompletionState(
            step_count=self._step_count,
            t_yr=self._t_yr,
            snapshot=snapshot,
            equilibrium_detected=bool(eq.is_stable) if eq is not None else False,
            notes=list(ports.get("notes", [])),
            planet_snapshot=snap,
            equilibrium=eq,
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
