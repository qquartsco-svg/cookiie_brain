"""Layer 1 — 통계역학 분석 모듈

trunk: m ẍ = −∇V(x) + ωJv − γv + I(x,v,t) + σξ(t),  σ² = 2γT/m

이 모듈은 trunk 위에 올라가는 첫 번째 층이다.
시뮬레이션이 만들어낸 궤적(trajectory)을 확률·열역학 언어로 번역한다.

┌────────────────────────────────────────────┐
│  Layer 1  통계역학 정식화                     │
│  ─────────────────────────                   │
│  ① Kramers 탈출률      k(i→j)              │
│  ② 전이 행렬            P[i,j]              │
│  ③ 엔트로피 생산률      dS/dt               │
│                                              │
│  → 이 위에 Layer 2(다체), Layer 3(게이지)    │
│     Layer 4(비평형), Layer 5(양자) 가 올라감  │
└────────────────────────────────────────────┘

수학적 배경:
  Kramers (1940) — ΔV, T, γ, 곡률 → 탈출률
  Große-Hynes    — 중간 감쇠 보정
  Lebowitz-Spohn — 비평형 엔트로피 생산
"""

from __future__ import annotations
import numpy as np
from typing import TYPE_CHECKING, List, Optional, Tuple
from dataclasses import dataclass, field

if TYPE_CHECKING:
    from Phase_B.multi_well_potential import MultiWellPotential


# ================================================================== #
#  ① Kramers 탈출률
# ================================================================== #

def well_frequency(
    mwp: "MultiWellPotential",
    well_idx: int,
    mass: float = 1.0,
    eps: float = 1e-5,
) -> float:
    """우물 바닥에서의 고유 진동수 ω_a

    합성 퍼텐셜 V(x)의 수치 Hessian으로부터 계산.
    ω_a = √(λ_max / m)  (λ_max = Hessian 최대 고유값, 양수)

    multi-well에서는 다른 우물들의 꼬리가 곡률에 기여하므로,
    단일 우물 해석해 A/σ² 대신 실제 합성 Hessian을 사용한다.
    """
    center = mwp.wells[well_idx].center
    dim = mwp.dim

    hessian = np.zeros((dim, dim))
    for a in range(dim):
        for b in range(dim):
            e_a = np.zeros(dim); e_a[a] = eps
            e_b = np.zeros(dim); e_b[b] = eps

            Vpp = mwp.potential(center + e_a + e_b)
            Vpm = mwp.potential(center + e_a - e_b)
            Vmp = mwp.potential(center - e_a + e_b)
            Vmm = mwp.potential(center - e_a - e_b)

            hessian[a, b] = (Vpp - Vpm - Vmp + Vmm) / (4.0 * eps * eps)

    eigenvalues = np.linalg.eigvalsh(hessian)
    lambda_max = eigenvalues[-1]

    if lambda_max <= 0:
        return 0.0

    return float(np.sqrt(lambda_max / mass))


def saddle_frequency(
    mwp: "MultiWellPotential",
    i: int,
    j: int,
    mass: float = 1.0,
    eps: float = 1e-5,
) -> float:
    """안장점에서의 불안정 진동수 ω_b

    V(x)의 Hessian 고유값 중 가장 음수인 것의 절댓값 → ω_b² = |λ_min|/m
    수치 Hessian (중심 차분)으로 계산한다.
    """
    saddle_pos, _ = mwp.find_saddle_between(i, j)
    dim = mwp.dim

    hessian = np.zeros((dim, dim))
    for a in range(dim):
        for b in range(dim):
            e_a = np.zeros(dim); e_a[a] = eps
            e_b = np.zeros(dim); e_b[b] = eps

            Vpp = mwp.potential(saddle_pos + e_a + e_b)
            Vpm = mwp.potential(saddle_pos + e_a - e_b)
            Vmp = mwp.potential(saddle_pos - e_a + e_b)
            Vmm = mwp.potential(saddle_pos - e_a - e_b)

            hessian[a, b] = (Vpp - Vpm - Vmp + Vmm) / (4.0 * eps * eps)

    eigenvalues = np.linalg.eigvalsh(hessian)
    lambda_min = eigenvalues[0]

    if lambda_min >= 0:
        return 0.0

    return float(np.sqrt(abs(lambda_min) / mass))


def kramers_rate(
    mwp: "MultiWellPotential",
    i: int,
    j: int,
    temperature: float,
    gamma: float,
    mass: float = 1.0,
) -> float:
    """Kramers-Grote-Hynes 탈출률 (중간 감쇠 보정)

    k(i→j) = (λ₊ / ω_b) · (ω_a / 2π) · exp(−ΔV / T)

    λ₊ = −γ/(2m) + √((γ/(2m))² + ω_b²)   (안장점의 불안정 고유값)

    물리:
      ω_a : 우물 바닥 곡률 → 진동주기 결정
      ω_b : 안장점 곡률 → 장벽 넘는 속도 결정
      λ₊  : 감쇠 보정 → γ 클수록 느려짐
      ΔV/T: Boltzmann 인자 → 장벽/온도 비율

    이 공식은 γ→0 (에너지 확산)과 γ→∞ (오버댐프) 양쪽의
    점근적 극한을 올바르게 내삽한다.
    """
    if temperature <= 0:
        return 0.0

    delta_V = mwp.barrier_height(i, j)
    if delta_V <= 0:
        return float("inf")

    omega_a = well_frequency(mwp, i, mass)
    omega_b = saddle_frequency(mwp, i, j, mass)

    if omega_b <= 0:
        return 0.0

    half_gamma_m = gamma / (2.0 * mass)
    lambda_plus = -half_gamma_m + np.sqrt(half_gamma_m ** 2 + omega_b ** 2)

    rate = (lambda_plus / omega_b) * (omega_a / (2.0 * np.pi)) * np.exp(-delta_V / temperature)
    return float(rate)


def kramers_rate_matrix(
    mwp: "MultiWellPotential",
    temperature: float,
    gamma: float,
    mass: float = 1.0,
) -> np.ndarray:
    """전체 우물 간 Kramers rate 행렬 K[i,j]

    K[i,j] = k(i→j),  K[i,i] = −Σ_{j≠i} K[i,j]

    이 행렬은 연속시간 Markov chain 의 생성 행렬(generator)이다.
    dp/dt = K^T p  →  정상 분포는 K^T p_ss = 0
    """
    n = len(mwp.wells)
    K = np.zeros((n, n))

    for i in range(n):
        for j in range(n):
            if i != j:
                K[i, j] = kramers_rate(mwp, i, j, temperature, gamma, mass)

    for i in range(n):
        K[i, i] = -np.sum(K[i, :])

    return K


# ================================================================== #
#  ② 전이 행렬 분석기
# ================================================================== #

@dataclass
class TransitionAnalyzer:
    """시뮬레이션 궤적에서 전이 통계를 추출한다.

    사용법:
        analyzer = TransitionAnalyzer(n_wells=3)
        for x in trajectory:
            analyzer.observe(x, mwp, dt)
        P = analyzer.transition_matrix()
        tau = analyzer.mean_residence_times()
    """
    n_wells: int
    _counts: np.ndarray = field(init=False)
    _current_well: int = field(init=False, default=-1)
    _total_time: float = field(init=False, default=0.0)
    _well_time: np.ndarray = field(init=False)

    def __post_init__(self):
        self._counts = np.zeros((self.n_wells, self.n_wells), dtype=int)
        self._well_time = np.zeros(self.n_wells)

    def observe(self, x: np.ndarray, mwp: "MultiWellPotential", dt: float) -> None:
        """한 타임스텝 관측. 우물 전이가 일어나면 카운트."""
        well = mwp.nearest_well(x)
        if self._current_well < 0:
            self._current_well = well

        if well != self._current_well:
            self._counts[self._current_well, well] += 1
            self._current_well = well

        self._well_time[well] += dt
        self._total_time += dt

    def transition_matrix(self) -> np.ndarray:
        """관측된 전이 확률 행렬 P[i,j] = N(i→j) / Σ_k N(i→k)

        행 합이 1 이 되는 stochastic matrix.
        전이가 없는 우물은 자기 자신으로 돌아가는 것으로 처리.
        """
        P = np.zeros((self.n_wells, self.n_wells))
        for i in range(self.n_wells):
            row_sum = self._counts[i].sum()
            if row_sum > 0:
                P[i] = self._counts[i] / row_sum
            else:
                P[i, i] = 1.0
        return P

    def transition_counts(self) -> np.ndarray:
        return self._counts.copy()

    def mean_residence_times(self) -> np.ndarray:
        """각 우물의 평균 체류 시간 τᵢ"""
        departures = self._counts.sum(axis=1)
        tau = np.zeros(self.n_wells)
        for i in range(self.n_wells):
            if departures[i] > 0:
                tau[i] = self._well_time[i] / departures[i]
            else:
                tau[i] = self._well_time[i] if self._well_time[i] > 0 else float("inf")
        return tau

    def occupation_fractions(self) -> np.ndarray:
        """각 우물의 점유 비율 (시간 기준)"""
        if self._total_time > 0:
            return self._well_time / self._total_time
        return np.zeros(self.n_wells)

    def net_circulation(self) -> np.ndarray:
        """J[i,j] = N(i→j) − N(j→i) : 순환 흐름

        양수면 i→j 가 우세, 음수면 j→i 가 우세.
        비평형일 때 이것이 0이 아니다 → 시간 역전 대칭 깨짐.
        """
        return self._counts - self._counts.T

    def detailed_balance_violation(self) -> float:
        """상세 균형 위반 지표: Σ|J[i,j]| / Σ|N[i,j]|

        0이면 평형 (detailed balance 성립)
        1에 가까울수록 비평형
        """
        J = self.net_circulation()
        total = self._counts.sum()
        if total == 0:
            return 0.0
        return float(np.abs(J).sum() / (2 * total))


# ================================================================== #
#  ③ 엔트로피 생산률
# ================================================================== #

def entropy_production_rate(
    velocities: np.ndarray,
    gamma: float,
    temperature: float,
    mass: float = 1.0,
    injection_powers: Optional[np.ndarray] = None,
) -> float:
    """비평형 엔트로피 생산률 Ṡ (medium entropy production)

    Ṡ = (γ/T)(⟨|v|²⟩ − dT/m) − (1/T)⟨v·I⟩

    극한 일관성:
      평형 (I=0, FDT 성립, 등분배):
        ⟨|v|²⟩ = dT/m  →  Ṡ = 0  ✓

      비평형 (I≠0 또는 ⟨|v|²⟩ ≠ dT/m):
        Ṡ > 0  (제2법칙)

    각 항의 물리:
      (γ/T)⟨|v|²⟩      : 마찰에 의한 소산 파워 / T
      (γ/T)(dT/m)       : 열욕조(노이즈)가 되돌려주는 평형 유지 비용 (baseline)
      (1/T)⟨v·I⟩        : 외부 구동이 하는 일

    baseline을 빼는 이유:
      underdamped Langevin에서 마찰 소산 γ⟨|v|²⟩와 노이즈 주입은
      평형에서 정확히 상쇄된다. 이 상쇄를 명시적으로 반영하지 않으면
      평형에서도 Ṡ ≠ 0이 되어 열역학 제2법칙과 모순된다.
    """
    if temperature <= 0:
        return 0.0

    dim = velocities.shape[-1] if velocities.ndim > 1 else 1
    v2_mean = np.mean(np.sum(velocities ** 2, axis=-1))

    equilibrium_baseline = dim * temperature / mass
    excess = v2_mean - equilibrium_baseline
    ep = gamma * excess / temperature

    if injection_powers is not None:
        ep -= np.mean(injection_powers) / temperature

    return float(ep)


def entropy_production_trajectory(
    velocities: np.ndarray,
    gamma: float,
    temperature: float,
    mass: float = 1.0,
    injection_powers: Optional[np.ndarray] = None,
    window: int = 100,
) -> np.ndarray:
    """시간에 따른 엔트로피 생산률 (이동 평균)

    Ṡ(t) = (γ/T)(⟨|v|²⟩_window − dT/m) − (1/T)⟨v·I⟩_window

    velocities: shape (n_steps, dim)
    반환: shape (n_steps - window + 1,)
    """
    if temperature <= 0:
        return np.zeros(max(1, len(velocities) - window + 1))

    dim = velocities.shape[-1] if velocities.ndim > 1 else 1
    equilibrium_baseline = dim * temperature / mass

    v2 = np.sum(velocities ** 2, axis=-1)

    cumsum = np.cumsum(v2)
    cumsum = np.insert(cumsum, 0, 0)
    v2_avg = (cumsum[window:] - cumsum[:-window]) / window

    result = gamma * (v2_avg - equilibrium_baseline) / temperature

    if injection_powers is not None:
        ip_cumsum = np.cumsum(injection_powers)
        ip_cumsum = np.insert(ip_cumsum, 0, 0)
        ip_avg = (ip_cumsum[window:] - ip_cumsum[:-window]) / window
        result -= ip_avg / temperature

    return result
