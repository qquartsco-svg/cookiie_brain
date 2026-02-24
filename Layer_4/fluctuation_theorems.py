"""Layer 4 — 비평형 일 정리 (Non-equilibrium Work Theorems)

Layer 1(통계역학)의 평형/근평형 열역학을 **임의의 비평형 과정**으로 확장한다.

┌──────────────────────────────────────────────────────┐
│  Layer 4: 비평형 일 정리                               │
│  ─────────────────                                    │
│                                                        │
│  핵심 정리:                                             │
│    Jarzynski:  ⟨e^{-W/T}⟩ = e^{-ΔF/T}  (정확한 등식)   │
│    제2법칙:    ⟨W⟩ ≥ ΔF               (Jensen 부등식)   │
│    Crooks:     P_F(W)/P_R(-W) = e^{(W-ΔF)/T}          │
│                                                        │
│  구성 요소:                                             │
│    Protocol        : 시간 의존 퍼텐셜 V(x, λ(t))        │
│    ProtocolForce   : ForceLayer 프로토콜 준수            │
│    WorkAccumulator : 궤적 따라 일 W 축적                 │
│    JarzynskiEstimator : ΔF 추정 + 제2법칙 검증          │
│    CrooksAnalyzer  : 정방향/역방향 대칭 분석             │
│                                                        │
│  물리적 위치:                                           │
│    mẍ = −∇_x V(x, λ(t)) + Ω(x)v − γv + σξ(t)         │
│    λ(t): 외부 프로토콜 (퍼텐셜 매개변수의 시간 변화)      │
│    W = Σ [V(x_n, λ_{n+1}) − V(x_n, λ_n)]: 프로토콜 일  │
│                                                        │
│  Layer 1과의 관계:                                      │
│    Layer 1: 평형 근처 → Kramers, 전이행렬, EP            │
│    Layer 4: 임의 비평형 → Jarzynski, Crooks, ΔF 추출    │
└──────────────────────────────────────────────────────┘
"""

from __future__ import annotations
import numpy as np
from typing import Callable, Optional, Tuple


# ================================================================== #
#  Protocol — 시간 의존 프로토콜 정의
# ================================================================== #

class Protocol:
    """시간 의존 퍼텐셜 프로토콜 V(x, λ(t)).

    λ(t)는 외부에서 제어하는 매개변수(트랩 위치, 강성 등).
    시스템은 λ(t)에 따라 비평형으로 구동된다.

    Parameters
    ----------
    V_func : (x, lam) -> float
        퍼텐셜 V(x, λ)
    g_func : (x, lam) -> ndarray
        힘 g(x, λ) = −∇_x V(x, λ)
    lambda_schedule : (t) -> float
        프로토콜 경로 λ(t)
    """

    def __init__(
        self,
        V_func: Callable,
        g_func: Callable,
        lambda_schedule: Callable[[float], float],
    ):
        self._V = V_func
        self._g = g_func
        self._schedule = lambda_schedule

    def V(self, x: np.ndarray, t: float) -> float:
        return self._V(x, self._schedule(t))

    def gradient(self, x: np.ndarray, t: float) -> np.ndarray:
        return self._g(x, self._schedule(t))

    def lambda_value(self, t: float) -> float:
        return self._schedule(t)


# ================================================================== #
#  ProtocolForce — ForceLayer 프로토콜 준수
# ================================================================== #

class ProtocolForce:
    """프로토콜에 의한 시간 의존 힘.

    trunk의 ForceLayer 프로토콜(force(x,v,t), potential(x))을 준수한다.
    potential()은 시간 정보가 없으므로 마지막 force() 호출 시점의 값을 사용한다.
    """

    def __init__(self, protocol: Protocol):
        self._protocol = protocol
        self._last_t = 0.0

    def force(self, x: np.ndarray, v: np.ndarray, t: float) -> np.ndarray:
        self._last_t = t
        return self._protocol.gradient(x, t)

    def potential(self, x: np.ndarray) -> float:
        return self._protocol.V(x, self._last_t)


# ================================================================== #
#  WorkAccumulator — 궤적 따라 일 W 축적
# ================================================================== #

class WorkAccumulator:
    """프로토콜이 시스템에 한 일을 축적.

    W = Σ_n [V(x_n, λ_{n+1}) − V(x_n, λ_n)]

    λ가 변할 때 고정된 배치(x_n)에서의 퍼텐셜 변화.
    이것이 열역학적 '일'의 정의이다.
    """

    def __init__(self, protocol: Protocol, dt: float):
        self._protocol = protocol
        self._dt = dt
        self.W = 0.0
        self._step = 0

    def step(self, x: np.ndarray):
        """한 스텝의 일을 축적. engine.update() 전에 호출."""
        t_n = self._step * self._dt
        t_next = t_n + self._dt
        self.W += self._protocol.V(x, t_next) - self._protocol.V(x, t_n)
        self._step += 1

    def reset(self):
        self.W = 0.0
        self._step = 0


# ================================================================== #
#  JarzynskiEstimator — Jarzynski 등식 분석
# ================================================================== #

class JarzynskiEstimator:
    """Jarzynski 등식: ⟨e^{-W/T}⟩ = e^{-ΔF/T}

    정확한 등식이다 (근사가 아님).
    임의의 비평형 과정에서 성립한다.
    """

    @staticmethod
    def free_energy(works: np.ndarray, T: float) -> float:
        """ΔF = −T · ln⟨e^{-W/T}⟩  (log-sum-exp for numerical stability)"""
        bW = np.asarray(works) / T
        c = np.max(-bW)
        log_avg = c + np.log(np.mean(np.exp(-bW - c)))
        return -T * log_avg

    @staticmethod
    def jarzynski_average(works: np.ndarray, T: float) -> float:
        """⟨e^{-W/T}⟩ — Jarzynski 평균. ΔF=0이면 1이어야 한다."""
        bW = np.asarray(works) / T
        c = np.max(-bW)
        return np.exp(c) * np.mean(np.exp(-bW - c))

    @staticmethod
    def dissipated_work(works: np.ndarray, delta_F: float) -> float:
        """⟨W_diss⟩ = ⟨W⟩ − ΔF  (항상 ≥ 0, 제2법칙)"""
        return float(np.mean(works) - delta_F)

    @staticmethod
    def second_law_satisfied(works: np.ndarray, delta_F: float) -> bool:
        """⟨W⟩ ≥ ΔF ?"""
        return float(np.mean(works)) >= delta_F - 1e-10


# ================================================================== #
#  CrooksAnalyzer — Crooks 요동 정리 분석
# ================================================================== #

class CrooksAnalyzer:
    """Crooks 요동 정리: P_F(W) / P_R(−W) = e^{(W−ΔF)/T}

    정방향 프로토콜(λ: a→b)의 일 분포 P_F(W)와
    역방향 프로토콜(λ: b→a)의 일 분포 P_R(W)가
    위 관계를 만족한다.

    따름정리: Jarzynski 등식은 Crooks로부터 유도된다.
    """

    @staticmethod
    def verify_symmetry(
        works_forward: np.ndarray,
        works_reverse: np.ndarray,
        T: float,
    ) -> Tuple[float, float]:
        """정방향/역방향 Jarzynski에서 추출한 ΔF가 일치하는지 검증.

        Returns (ΔF_forward, ΔF_reverse).
        Crooks 대칭이면 ΔF_forward ≈ −ΔF_reverse.
        """
        dF_f = JarzynskiEstimator.free_energy(works_forward, T)
        dF_r = JarzynskiEstimator.free_energy(works_reverse, T)
        return dF_f, dF_r


# ================================================================== #
#  편의 함수: 기본 프로토콜 구성
# ================================================================== #

def moving_trap(
    k: float,
    L: float,
    tau: float,
    dim: int = 2,
) -> Protocol:
    """이동 조화 트랩 프로토콜.

    V(x, λ) = ½k·|x − λê₁|²
    λ: 0 → L over time τ
    ΔF = 0 (트랩 이동은 자유 에너지를 바꾸지 않는다)
    """
    def V(x, lam):
        dx = x.copy()
        dx[0] -= lam
        return 0.5 * k * np.dot(dx, dx)

    def g(x, lam):
        dx = x.copy()
        dx[0] -= lam
        return -k * dx

    def lam(t):
        return L * np.clip(t / tau, 0.0, 1.0)

    return Protocol(V, g, lam)


def stiffness_change(
    k1: float,
    k2: float,
    tau: float,
    dim: int = 2,
) -> Tuple[Protocol, Callable[[float], float]]:
    """강성 변화 프로토콜.

    V(x, λ) = ½λ·|x|²
    λ: k₁ → k₂ over time τ
    ΔF(T) = (d/2)·T·ln(k₂/k₁)

    Returns (Protocol, analytical_dF(T)).
    """
    def V(x, lam):
        return 0.5 * lam * np.dot(x, x)

    def g(x, lam):
        return -lam * x

    def lam(t):
        s = np.clip(t / tau, 0.0, 1.0)
        return k1 + (k2 - k1) * s

    def analytical_dF(T):
        return (dim / 2.0) * T * np.log(k2 / k1)

    return Protocol(V, g, lam), analytical_dF


def equilibrium_sample(
    k: float,
    T: float,
    mass: float,
    dim: int,
    rng: np.random.Generator,
    center: Optional[np.ndarray] = None,
) -> np.ndarray:
    """평형 볼츠만 분포에서 초기 상태 샘플.

    x ~ N(center, T/k · I)
    v ~ N(0, T/m · I)

    Returns state_vector [x, v].
    """
    sigma_x = np.sqrt(T / k)
    sigma_v = np.sqrt(T / mass)
    x = rng.normal(0.0, sigma_x, dim)
    if center is not None:
        x += center
    v = rng.normal(0.0, sigma_v, dim)
    return np.concatenate([x, v])
