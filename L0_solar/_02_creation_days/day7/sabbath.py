"""sabbath.py — Day7 평형·안정성 판정기 (SabbathJudge)

"일곱째 날 안식" — 시스템이 안정적으로 돌아가는지를 관측·판정하는 메타 레이어.

새 구조를 추가하지 않는다. PlanetSnapshot 시계열을 보고
"이 행성이 쉬고 있는지(안정)/혼돈인지"를 판정한다.

판정 기준:
    CO2 drift  : |ΔCO2_ppm / step| < threshold_co2
    T drift    : |ΔT_K / step|     < threshold_T
    stress     : planet_stress     < threshold_stress
    → 세 조건 모두 충족하면 EquilibriumState.is_stable = True

12라는 숫자와의 연결:
    window=12 기본값 — 12개 스텝(= 12개 밴드의 1 cycle) 을 보고 판정.
    "12지파가 모두 안정되어야 안식이 인정된다"는 개념과 동형.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Deque, List, Optional

from .runner import PlanetSnapshot


# ── 상태 ──────────────────────────────────────────────────────────────────────

@dataclass
class EquilibriumState:
    """안정성 판정 결과."""
    is_stable: bool          # True = 안식 (안정)
    co2_drift: float         # |ΔCO2| / step (window 평균)
    T_drift: float           # |ΔT| / step   (window 평균)
    stress_level: float      # 최근 스트레스 EMA
    window: int              # 판정에 사용한 스텝 수
    reason: str              # 판정 이유 한 줄

    def __str__(self) -> str:
        icon = "🌿 안식" if self.is_stable else "⚡ 불안정"
        return (
            f"{icon} | CO2_drift={self.co2_drift:.4f} | "
            f"T_drift={self.T_drift:.4f} | stress={self.stress_level:.3f} "
            f"[w={self.window}] {self.reason}"
        )


# ── SabbathJudge ─────────────────────────────────────────────────────────────

class SabbathJudge:
    """PlanetSnapshot 시계열을 보고 평형 여부를 판정.

    Parameters
    ----------
    window : int
        판정에 사용할 최근 스텝 수. 기본 12 (= 12 밴드 cycle).
    threshold_co2 : float
        안정 판정용 CO2 드리프트 상한 [ppm/step].
    threshold_T : float
        안정 판정용 온도 드리프트 상한 [K/step].
    threshold_stress : float
        안정 판정용 스트레스 상한 [0~1].
    """

    def __init__(
        self,
        window: int = 12,
        threshold_co2: float = 2.0,
        threshold_T: float = 0.5,
        threshold_stress: float = 0.3,
    ) -> None:
        self.window = window
        self.thr_co2 = threshold_co2
        self.thr_T = threshold_T
        self.thr_stress = threshold_stress

        self._history: Deque[PlanetSnapshot] = deque(maxlen=window + 1)

    def push(self, snapshot: PlanetSnapshot) -> None:
        """스냅샷 추가."""
        self._history.append(snapshot)

    def judge(self) -> Optional[EquilibriumState]:
        """현재 히스토리로 안정성 판정.

        window 개 스텝이 쌓이기 전에는 None 반환.
        """
        if len(self._history) < 2:
            return None

        snaps = list(self._history)

        # CO2, T 드리프트: 최근 window 구간의 |Δ| / step 평균
        co2_deltas, T_deltas = [], []
        for i in range(1, len(snaps)):
            co2_deltas.append(abs(snaps[i].CO2_ppm - snaps[i - 1].CO2_ppm))
            T_deltas.append(abs(snaps[i].T_surface_K - snaps[i - 1].T_surface_K))

        co2_drift  = sum(co2_deltas) / len(co2_deltas)
        T_drift    = sum(T_deltas) / len(T_deltas)
        stress_avg = sum(s.planet_stress for s in snaps) / len(snaps)

        # 안정 조건
        ok_co2    = co2_drift    < self.thr_co2
        ok_T      = T_drift      < self.thr_T
        ok_stress = stress_avg   < self.thr_stress
        is_stable = ok_co2 and ok_T and ok_stress

        if is_stable:
            reason = "CO2·T·stress 모두 임계 이하"
        else:
            parts = []
            if not ok_co2:
                parts.append(f"CO2_drift={co2_drift:.2f}>{self.thr_co2}")
            if not ok_T:
                parts.append(f"T_drift={T_drift:.2f}>{self.thr_T}")
            if not ok_stress:
                parts.append(f"stress={stress_avg:.2f}>{self.thr_stress}")
            reason = " | ".join(parts)

        return EquilibriumState(
            is_stable=is_stable,
            co2_drift=co2_drift,
            T_drift=T_drift,
            stress_level=stress_avg,
            window=len(snaps) - 1,
            reason=reason,
        )

    def is_stable(self) -> bool:
        """현재 안정 여부 (빠른 조회). 히스토리 부족 시 False."""
        eq = self.judge()
        return eq.is_stable if eq else False

    @property
    def last_snapshot(self) -> Optional[PlanetSnapshot]:
        """가장 최근 스냅샷."""
        return self._history[-1] if self._history else None


# ── 팩토리 ────────────────────────────────────────────────────────────────────

def make_sabbath_judge(
    window: int = 12,
    threshold_co2: float = 2.0,
    threshold_T: float = 0.5,
    threshold_stress: float = 0.3,
) -> SabbathJudge:
    """기본 SabbathJudge 생성 helper."""
    return SabbathJudge(
        window=window,
        threshold_co2=threshold_co2,
        threshold_T=threshold_T,
        threshold_stress=threshold_stress,
    )


__all__ = ["SabbathJudge", "EquilibriumState", "make_sabbath_judge"]
