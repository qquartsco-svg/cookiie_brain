"""Layer 5 — 확률역학 (Stochastic Mechanics)

Layer 1–4의 궤적(trajectory) 관점을 확률 밀도 ρ(x,t) 진화 관점으로 전환한다.

┌──────────────────────────────────────────────────────┐
│  Layer 5: 확률역학                                     │
│  ─────────────                                        │
│                                                        │
│  관점 전환:                                             │
│    Langevin (궤적):  mẍ = −∇V − γv + σξ               │
│    Fokker-Planck (밀도): ∂ρ/∂t = ∇·(∇V·ρ/(mγ)) + D∇²ρ│
│                                                        │
│  범위: overdamped Langevin에 대응하는 FP만 구현.         │
│  underdamped Kramers FP:                                │
│    ∂ρ/∂t = −v∂ₓρ + ∂ᵥ(γvρ + V'ρ/m) + (γT/m)∂²ᵥρ     │
│  는 현재 범위 밖 (향후 확장).                             │
│                                                        │
│  핵심 구성:                                             │
│    FokkerPlanckSolver1D : 1D 격자 위 ρ(x,t) 시간 진화  │
│    NelsonDecomposition  : v = v_current + v_osmotic     │
│    ProbabilityCurrent   : J = bρ − D∇ρ 분석            │
│                                                        │
│  Nelson 확률역학:                                       │
│    v_+ = b + D∇ln ρ   (forward drift)                  │
│    v_- = b − D∇ln ρ   (backward drift)                 │
│    v_osmotic = D∇ln ρ  (삼투 속도)                      │
│    v_current = b        (표류 속도)                      │
│                                                        │
│  정상 상태:                                              │
│    ρ_eq ∝ exp(−V/T)    (볼츠만 분포)                     │
│    J_eq = 0             (detailed balance)              │
│                                                        │
│  Layer 1 의존성:                                        │
│    D = T/(mγ) — FDT로부터 유도                          │
│    σ² = 2γT/m ⟺ D = σ²/(2γ) = T/(mγ)                  │
│                                                        │
│  Parisi-Wu 확률적 양자화:                                │
│    허시간 τ의 Langevin이 τ→∞에서 양자 분배함수에 수렴.    │
│    현재 구현은 고전 Fokker-Planck에 한정.                 │
│    양자 확장은 향후 과제.                                 │
└──────────────────────────────────────────────────────┘
"""

from __future__ import annotations
import numpy as np
from typing import Callable, Optional, Tuple


# ================================================================== #
#  FokkerPlanckSolver1D — 1D Fokker-Planck 시간 진화
# ================================================================== #

class FokkerPlanckSolver1D:
    """1D Fokker-Planck 방정식 수치 풀이.

    overdamped Langevin: γ dx = −∇V dt + σ dW
    대응 Fokker-Planck:

      ∂ρ/∂t = ∂/∂x [V'(x)·ρ/(mγ)] + D·∂²ρ/∂x²

    여기서 D = T/(mγ) = σ²/(2γ) (FDT).

    격자 기반 유한 차분법으로 풀이한다.
    경계 조건: 반사 (no-flux) — J = 0 at boundaries.

    Parameters
    ----------
    x_min, x_max : float
        공간 범위
    nx : int
        격자 점 수
    V_func : (x) -> float
        퍼텐셜 V(x)
    T : float
        온도 (k_B = 1)
    gamma : float
        감쇠 계수
    mass : float
        질량
    """

    def __init__(
        self,
        x_min: float,
        x_max: float,
        nx: int,
        V_func: Callable[[np.ndarray], np.ndarray],
        T: float,
        gamma: float,
        mass: float = 1.0,
    ):
        self.x = np.linspace(x_min, x_max, nx)
        self.dx = self.x[1] - self.x[0]
        self.nx = nx
        self._V_func = V_func
        self.T = T
        self.gamma = gamma
        self.mass = mass
        self.D = T / (mass * gamma)

        self._V = V_func(self.x)
        self._dVdx = np.gradient(self._V, self.dx)

    @property
    def drift(self) -> np.ndarray:
        """b(x) = −V'(x)/(mγ) — overdamped drift velocity."""
        return -self._dVdx / (self.mass * self.gamma)

    def boltzmann(self) -> np.ndarray:
        """해석적 정상 분포 ρ_eq ∝ exp(−V/T), 정규화."""
        log_rho = -self._V / self.T
        log_rho -= np.max(log_rho)
        rho = np.exp(log_rho)
        rho /= np.trapezoid(rho, self.x)
        return rho

    def step(self, rho: np.ndarray, dt: float) -> np.ndarray:
        """Fokker-Planck 한 스텝 (FTCS + flux limiter).

        ∂ρ/∂t = ∂/∂x [V'/(mγ) · ρ] + D ∂²ρ/∂x²
               = −∂J/∂x

        J = b·ρ − D·∂ρ/∂x  (확률류)

        No-flux 경계: J = 0 at edges.
        """
        b = self.drift
        D = self.D
        dx = self.dx

        J = np.zeros(self.nx + 1)
        for i in range(1, self.nx):
            rho_face = 0.5 * (rho[i - 1] + rho[i])
            drho = (rho[i] - rho[i - 1]) / dx
            J[i] = b[min(i, self.nx - 1)] * rho_face - D * drho

        rho_new = rho.copy()
        for i in range(self.nx):
            rho_new[i] -= dt / dx * (J[i + 1] - J[i])

        rho_new = np.maximum(rho_new, 0.0)
        norm = np.trapezoid(rho_new, self.x)
        if norm > 0:
            rho_new /= norm

        return rho_new

    def evolve(self, rho0: np.ndarray, dt: float, n_steps: int) -> np.ndarray:
        """ρ(x,0) = ρ₀에서 n_steps만큼 진화."""
        rho = rho0.copy()
        for _ in range(n_steps):
            rho = self.step(rho, dt)
        return rho

    def probability_current(self, rho: np.ndarray) -> np.ndarray:
        """확률류 J(x) = b(x)·ρ(x) − D·∂ρ/∂x.

        격자 중심에서 계산 (내부 점만).
        """
        b = self.drift
        D = self.D
        drdx = np.gradient(rho, self.dx)
        return b * rho - D * drdx


# ================================================================== #
#  NelsonDecomposition — Nelson 확률 속도 분해
# ================================================================== #

class NelsonDecomposition:
    """Nelson 확률역학 속도 분해.

    확산 과정의 drift를 두 성분으로 분해한다:
      v_current = b(x)           (표류 속도, 전류)
      v_osmotic = D · ∇ln ρ(x)   (삼투 속도, 확산 유도)

    물리적 의미:
      v_current: 외력에 의한 체계적 이동
      v_osmotic: 밀도 기울기에 의한 확산 효과
                 ρ가 낮은 곳에서 높은 곳으로 "밀어내는" 속도

    Nelson의 forward/backward drift:
      v_+ = v_current + v_osmotic   (forward)
      v_- = v_current − v_osmotic   (backward)

    양자역학과의 대응 (형식적):
      Schrödinger 방정식의 확산 해석에서 v_osmotic은
      파동함수의 진폭 기울기에 대응한다.
      현재 구현은 고전 확산에 한정.
    """

    @staticmethod
    def current_velocity(
        x: np.ndarray,
        dVdx: np.ndarray,
        mass: float,
        gamma: float,
    ) -> np.ndarray:
        """v_current = −V'(x)/(mγ) — 표류 속도."""
        return -dVdx / (mass * gamma)

    @staticmethod
    def osmotic_velocity(
        rho: np.ndarray,
        dx: float,
        D: float,
        eps: float = 1e-30,
    ) -> np.ndarray:
        """v_osmotic = D · ∇ln ρ — 삼투 속도.

        ∇(ln ρ)를 직접 계산한다 (∇ρ/ρ보다 수치적으로 안정).
        ln ρ가 다항식에 가까울 때 (가우시안 → 이차식) 오차가 작다.
        """
        log_rho = np.log(np.maximum(rho, eps))
        grad_log_rho = np.gradient(log_rho, dx)
        return D * grad_log_rho

    @staticmethod
    def forward_velocity(v_current: np.ndarray, v_osmotic: np.ndarray) -> np.ndarray:
        """v_+ = v_current + v_osmotic"""
        return v_current + v_osmotic

    @staticmethod
    def backward_velocity(v_current: np.ndarray, v_osmotic: np.ndarray) -> np.ndarray:
        """v_- = v_current − v_osmotic"""
        return v_current - v_osmotic


# ================================================================== #
#  ProbabilityCurrent — 확률류 분석
# ================================================================== #

class ProbabilityCurrent:
    """확률류 J(x) = b(x)ρ(x) − D∇ρ(x) 분석.

    평형: J_eq = 0 everywhere (detailed balance)
    비평형: J ≠ 0 → 확률류 순환 (probability flux loops)

    Layer 1의 detailed_balance_violation()과의 관계:
      Layer 1: 전이행렬의 비가역성 (이산)
      Layer 5: 확률류의 비가역성 (연속)
    """

    @staticmethod
    def compute(
        rho: np.ndarray,
        drift: np.ndarray,
        D: float,
        dx: float,
    ) -> np.ndarray:
        """J = b·ρ − D·∇ρ"""
        grad_rho = np.gradient(rho, dx)
        return drift * rho - D * grad_rho

    @staticmethod
    def max_current(J: np.ndarray) -> float:
        """최대 확률류 크기 — 평형이면 0에 가까워야."""
        return float(np.max(np.abs(J)))

    @staticmethod
    def net_flux(J: np.ndarray) -> float:
        """순 플럭스 — 정상 상태에서 0."""
        return float(J[-1] - J[0])


# ================================================================== #
#  편의 함수
# ================================================================== #

def double_well_potential(a: float = 1.0, b: float = 4.0):
    """이중 우물 퍼텐셜: V(x) = a·x⁴ − b·x²

    극소: x = ±√(b/(2a))
    장벽: V(0) = 0, V(±√(b/2a)) = −b²/(4a)
    """
    def V(x):
        return a * x**4 - b * x**2

    return V


def gaussian_initial(x: np.ndarray, center: float, sigma: float) -> np.ndarray:
    """가우시안 초기 분포."""
    rho = np.exp(-0.5 * ((x - center) / sigma) ** 2)
    rho /= np.trapezoid(rho, x)
    return rho


def langevin_ensemble_histogram(
    V_func: Callable,
    T: float,
    gamma: float,
    mass: float,
    dt: float,
    n_steps: int,
    n_particles: int,
    x_grid: np.ndarray,
    seed: int = 0,
) -> np.ndarray:
    """Overdamped Langevin 앙상블로 히스토그램 생성.

    dx = −V'(x)/(mγ) dt + √(2D) dW

    FP 풀이와 비교하기 위한 참조 분포.
    """
    rng = np.random.default_rng(seed)
    D = T / (mass * gamma)
    noise_amp = np.sqrt(2.0 * D * dt)

    x0 = rng.normal(0.0, np.sqrt(T), n_particles)
    x_arr = x0.copy()

    eps = 1e-6
    for _ in range(n_steps):
        Vp = V_func(x_arr + eps)
        Vm = V_func(x_arr - eps)
        dVdx = (Vp - Vm) / (2.0 * eps)

        drift = -dVdx / (mass * gamma)
        x_arr += drift * dt + noise_amp * rng.standard_normal(n_particles)

    hist, edges = np.histogram(x_arr, bins=len(x_grid) - 1,
                               range=(x_grid[0], x_grid[-1]), density=True)
    centers = 0.5 * (edges[:-1] + edges[1:])
    rho_hist = np.interp(x_grid, centers, hist, left=0, right=0)
    norm = np.trapezoid(rho_hist, x_grid)
    if norm > 0:
        rho_hist /= norm
    return rho_hist
