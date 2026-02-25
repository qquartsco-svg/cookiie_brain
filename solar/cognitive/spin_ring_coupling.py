"""Spin-Ring Coupling — EvolutionEngine ↔ RingAttractor 필드 연결
================================================================

물리 엔진(EvolutionEngine)의 자전축 상태를
인지 기억 엔진(RingAttractor)에 투영하여 연결하는 커플링 레이어.

구조:
  EvolutionEngine (물리 계산)
       ↓  spin_axis → azimuth (S² → S¹ 투영)
  RingAttractorEngine (관성 기억)
       ↓  phase, stability, drift
  CouplingState (통합 관측)

원리:
  - 물리 엔진은 건드리지 않는다 (순수 물리 보존)
  - Ring Attractor는 물리 상태의 관측자로 작동한다
  - 둘은 필드를 통해 간접 결합된다 (직접 합치지 않음)
  - 기어가 맞물리듯, 중력장 안에서 위상이 동기화된다
"""

import numpy as np
from dataclasses import dataclass
from typing import Optional, List

from ..core.evolution_engine import EvolutionEngine, Body3D
from .ring_attractor import RingAttractorEngine, RingState


@dataclass
class CouplingState:
    """물리-인지 통합 상태."""

    # 물리 층 (EvolutionEngine)
    time: float                     # 시뮬레이션 시간 [yr]
    spin_axis: np.ndarray           # 자전축 벡터 (단위 벡터)
    obliquity_deg: float            # 경사각 [°]
    spin_azimuth: float             # 자전축 방위각 [rad] (S² → S¹ 투영)

    # 인지 층 (RingAttractor)
    ring_phase: float               # Ring이 기억하는 위상 [rad]
    ring_amplitude: float           # 범프 진폭
    ring_stability: float           # 안정성 점수
    ring_drift: float               # 위상 변화량

    # 커플링 층
    phase_error: float              # |물리 방위각 - Ring 위상| [rad]
    coupling_strength: float        # 현재 결합 강도
    synchronized: bool              # 동기화 여부


class SpinRingCoupling:
    """EvolutionEngine과 RingAttractor를 필드로 연결하는 커플링 레이어.

    동작 방식:
      1. EvolutionEngine.step()이 물리를 계산한다
      2. 자전축의 방위각(azimuth)을 S² → S¹로 투영한다
      3. 그 방위각을 RingAttractor에 필드 입력으로 전달한다
      4. Ring이 그 위상을 기억하고 안정화한다
      5. 물리와 인지의 위상차(phase_error)를 관측한다

    Parameters
    ----------
    engine : EvolutionEngine
        물리 엔진 (수정하지 않음).
    target_body : str
        추적할 천체 이름 (기본 "Earth").
    n_neurons : int
        Ring Attractor 해상도.
    coupling_strength : float
        필드 결합 강도 (0 = 분리, 1 = 완전 동기).
        물리 → Ring 방향의 영향력. Ring → 물리는 없음 (관측자 모드).
    """

    def __init__(
        self,
        engine: EvolutionEngine,
        target_body: str = "Earth",
        n_neurons: int = 64,
        coupling_strength: float = 0.5,
    ):
        self.engine = engine
        self.target_name = target_body
        self.coupling_strength = coupling_strength

        self.ring = RingAttractorEngine(
            n_neurons=n_neurons,
            tau=1.0,
            w_exc=2.0,
            w_inh=0.8,
            sigma=3.0,
        )

        self._initialized = False
        self._history: List[CouplingState] = []

    def _get_azimuth(self) -> float:
        """자전축의 방위각 추출 (S² → S¹ 투영).

        spin_axis = (sx, sy, sz) 에서
        방위각 φ = atan2(sy, sx) ∈ [0, 2π)
        """
        body = self.engine.find(self.target_name)
        if body is None:
            return 0.0
        s = body.spin_axis
        return np.arctan2(s[1], s[0]) % (2 * np.pi)

    def _init_ring(self):
        """Ring Attractor를 현재 물리 상태로 초기화."""
        azimuth = self._get_azimuth()
        self.ring.inject(azimuth, strength=2.0)
        self.ring.run(duration=5.0, dt=0.01)
        self._initialized = True

    def step(self, dt: float, ocean: bool = True) -> CouplingState:
        """물리 + 인지 통합 스텝.

        1. 물리 엔진 전진 (EvolutionEngine.step)
        2. 자전축 방위각 추출
        3. Ring Attractor에 필드 입력
        4. Ring 전진
        5. 통합 상태 반환
        """
        if not self._initialized:
            self._init_ring()

        self.engine.step(dt, ocean=ocean)

        azimuth = self._get_azimuth()

        field_input = np.zeros(self.ring.n)
        center_idx = (azimuth / (2 * np.pi)) * self.ring.n
        idx = np.arange(self.ring.n)
        dist = np.minimum(
            np.abs(idx - center_idx),
            self.ring.n - np.abs(idx - center_idx),
        )
        field_input = self.coupling_strength * np.exp(
            -dist**2 / (2 * self.ring.sigma**2)
        )

        ring_dt = min(0.05, dt * 10)
        self.ring.step(dt=ring_dt, external_input=field_input)

        ring_state = self.ring.get_state()

        body = self.engine.find(self.target_name)
        obliquity_deg = np.degrees(body.obliquity) if body else 0.0
        spin_axis = body.spin_axis.copy() if body else np.zeros(3)

        raw_error = azimuth - ring_state.phase
        phase_error = abs((raw_error + np.pi) % (2 * np.pi) - np.pi)

        state = CouplingState(
            time=self.engine.time,
            spin_axis=spin_axis,
            obliquity_deg=obliquity_deg,
            spin_azimuth=azimuth,
            ring_phase=ring_state.phase,
            ring_amplitude=ring_state.amplitude,
            ring_stability=ring_state.stability,
            ring_drift=ring_state.drift,
            phase_error=phase_error,
            coupling_strength=self.coupling_strength,
            synchronized=(phase_error < 0.1),
        )

        self._history.append(state)
        return state

    def run(
        self, n_steps: int, dt: float, ocean: bool = True, log_interval: int = 0,
    ) -> List[CouplingState]:
        """다수 스텝 실행.

        Parameters
        ----------
        n_steps : int
            총 스텝 수.
        dt : float
            물리 시간 스텝 [yr].
        ocean : bool
            해양 업데이트 포함 여부.
        log_interval : int
            콘솔 출력 간격 (0 = 출력 없음).

        Returns
        -------
        list of CouplingState
        """
        states = []
        for i in range(n_steps):
            s = self.step(dt, ocean=ocean)
            states.append(s)

            if log_interval > 0 and (i + 1) % log_interval == 0:
                yr = s.time
                az_deg = np.degrees(s.spin_azimuth)
                rp_deg = np.degrees(s.ring_phase)
                err_deg = np.degrees(s.phase_error)
                print(
                    f"  t={yr:8.1f} yr | "
                    f"axis_az={az_deg:7.2f}° | "
                    f"ring_φ={rp_deg:7.2f}° | "
                    f"error={err_deg:5.2f}° | "
                    f"stab={s.ring_stability:.3f} | "
                    f"sync={'YES' if s.synchronized else 'no '}"
                )
        return states

    def summary(self) -> dict:
        """실행 결과 요약."""
        if not self._history:
            return {}

        errors = [s.phase_error for s in self._history]
        stabs = [s.ring_stability for s in self._history]
        synced = [s.synchronized for s in self._history]

        first = self._history[0]
        last = self._history[-1]

        total_precession = last.spin_azimuth - first.spin_azimuth
        total_ring_drift = sum(s.ring_drift for s in self._history)

        return {
            "total_time_yr": last.time - first.time,
            "total_steps": len(self._history),
            "mean_phase_error_deg": np.degrees(np.mean(errors)),
            "max_phase_error_deg": np.degrees(np.max(errors)),
            "mean_stability": np.mean(stabs),
            "sync_ratio": sum(synced) / len(synced),
            "total_precession_deg": np.degrees(total_precession),
            "ring_tracked_drift_deg": np.degrees(total_ring_drift),
            "final_obliquity_deg": last.obliquity_deg,
        }
