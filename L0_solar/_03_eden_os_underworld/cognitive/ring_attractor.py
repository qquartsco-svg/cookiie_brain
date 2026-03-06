"""Ring Attractor — 관성 기억 엔진 (Inertial Memory Engine)
===========================================================

입력이 사라진 이후에도 위상(phase)을 안정적으로 유지하는 상태 기억 엔진.
Mexican-hat 연결 위상(topology)으로 범프(bump) 상태를 보존한다.

이것은 Archive/Integrated/2.Ring_Attractor_Engine의 핵심 역학만
추출한 경량 버전이다. 외부 의존성 없이 NumPy만으로 작동한다.

핵심 물리:
  - 위상 공간: S¹ (φ ∈ [0, 2π))
  - 동역학: Mexican-hat 에너지 함수에 의한 bump attractor
  - 관성: 입력 제거 후에도 상태(위상) 보존
  - 외란 복원: 노이즈/섭동에 대해 원래 상태로 복귀

Units: radians, dimensionless
"""

import numpy as np
from dataclasses import dataclass
from typing import Optional


@dataclass
class RingState:
    """Ring Attractor 출력 상태."""
    phase: float            # 현재 위상 [rad], 0 ~ 2π
    amplitude: float        # 범프 진폭 (0 = 비활성, 1 = 최대)
    stability: float        # 안정성 점수 (0.0 ~ 1.0)
    drift: float            # 이전 스텝 대비 위상 변화 [rad]
    sustained: bool         # 상태 유지 여부


class RingAttractorEngine:
    """경량 Ring Attractor 엔진.

    Mexican-hat 연결로 bump 위치를 유지하는 연속 어트랙터.
    원본(Archive/2.Ring_Attractor_Engine)의 핵심 역학을
    연속 위상 공간에서 재구현한다.

    수학:
      활성화: a_i(t+dt) = a_i(t) + dt * [-a_i + Σ_j W_ij * f(a_j) + I_i]
      W_ij = w_exc * exp(-d²/2σ²) - w_inh   (Mexican-hat)
      f(x) = max(0, x)                        (ReLU 활성화)

    Parameters
    ----------
    n_neurons : int
        링 위의 뉴런 수 (해상도). 기본 32.
    tau : float
        시간 상수 (안정성 제어). 클수록 느리고 안정적.
    w_exc : float
        흥분 연결 강도 (가까운 이웃).
    w_inh : float
        억제 연결 강도 (전역).
    sigma : float
        흥분 범위 (가우시안 폭, 뉴런 인덱스 단위).
    """

    def __init__(
        self,
        n_neurons: int = 32,
        tau: float = 1.0,
        w_exc: float = 2.0,
        w_inh: float = 0.8,
        sigma: float = 2.0,
    ):
        self.n = n_neurons
        self.tau = tau
        self.w_exc = w_exc
        self.w_inh = w_inh
        self.sigma = sigma

        self.activations = np.zeros(n_neurons)
        self._prev_phase: Optional[float] = None
        self._time = 0.0

        self._build_weights()

    def _build_weights(self):
        """Mexican-hat 연결 행렬 구축."""
        idx = np.arange(self.n, dtype=np.float64)
        diff = idx[np.newaxis, :] - idx[:, np.newaxis]
        ring_dist = np.minimum(np.abs(diff), self.n - np.abs(diff))

        exc = self.w_exc * np.exp(-ring_dist**2 / (2 * self.sigma**2))
        np.fill_diagonal(exc, 0.0)
        self.W = np.asarray(exc - self.w_inh, dtype=np.float64)
        self.W = np.nan_to_num(self.W, nan=0.0, posinf=5.0, neginf=-5.0)

    def inject(self, phase: float, strength: float = 1.0):
        """특정 위상에 외부 자극 주입.

        Parameters
        ----------
        phase : float
            목표 위상 [rad], 0 ~ 2π
        strength : float
            입력 강도 (0.0 ~ 1.0)
        """
        idx = np.arange(self.n)
        center_idx = (phase / (2 * np.pi)) * self.n
        dist = np.minimum(
            np.abs(idx - center_idx),
            self.n - np.abs(idx - center_idx),
        )
        self.activations += strength * np.exp(-dist**2 / (2 * self.sigma**2))

    def step(self, dt: float = 0.01, external_input: Optional[np.ndarray] = None):
        """한 스텝 전진.

        Parameters
        ----------
        dt : float
            시간 스텝.
        external_input : ndarray, optional
            외부 입력 벡터 (n_neurons,). None이면 자유 진화.
        """
        f_a = np.maximum(0.0, self.activations)
        total_a = np.sum(f_a)
        if total_a > 1e-10:
            f_norm = f_a / total_a
            with np.errstate(all="ignore"):
                recurrent = self.W @ f_norm
            recurrent = np.nan_to_num(recurrent, nan=0.0, posinf=5.0, neginf=-5.0)
        else:
            recurrent = np.zeros(self.n)

        I_ext = external_input if external_input is not None else np.zeros(self.n)

        da = (-self.activations + recurrent + I_ext) / self.tau
        self.activations += da * dt

        self.activations = np.clip(self.activations, 0.0, 10.0)

        self._time += dt

    def run(self, duration: float, dt: float = 0.01):
        """지정 시간만큼 실행."""
        n_steps = max(1, int(duration / dt))
        for _ in range(n_steps):
            self.step(dt)

    def get_state(self) -> RingState:
        """현재 상태 반환."""
        total = np.sum(self.activations)

        if total < 1e-10:
            phase = 0.0
            amplitude = 0.0
            sustained = False
        else:
            angles = np.linspace(0, 2 * np.pi, self.n, endpoint=False)
            cx = np.sum(self.activations * np.cos(angles)) / total
            cy = np.sum(self.activations * np.sin(angles)) / total
            phase = np.arctan2(cy, cx) % (2 * np.pi)
            amplitude = np.sqrt(cx**2 + cy**2)
            sustained = True

        drift = 0.0
        if self._prev_phase is not None and sustained:
            raw = phase - self._prev_phase
            drift = (raw + np.pi) % (2 * np.pi) - np.pi

        stability = 0.0
        if sustained:
            peak = np.max(self.activations)
            mean = np.mean(self.activations)
            if peak > 1e-10:
                stability = min(1.0, (peak - mean) / peak)

        self._prev_phase = phase if sustained else self._prev_phase

        return RingState(
            phase=phase,
            amplitude=amplitude,
            stability=stability,
            drift=abs(drift),
            sustained=sustained,
        )

    def reset(self):
        """전체 상태 초기화."""
        self.activations[:] = 0.0
        self._prev_phase = None
        self._time = 0.0
