"""Layer 2 — N-body 다체 동역학

trunk의 state_vector = [x₁¹, x₁², ..., xₙᵈ, v₁¹, v₁², ..., vₙᵈ]
(N 입자, d 차원, 총 2Nd 성분)

trunk은 이것을 그냥 큰 벡터로 적분한다.
이 모듈은 N-body 전용 레이어를 제공한다:

┌──────────────────────────────────────────────┐
│  Layer 2: 다체 동역학                          │
│  ─────────────────                            │
│  NBodyState    : flat ↔ (N,d) reshape 유틸    │
│  InteractionForce : 쌍체 상호작용 F_ij         │
│  ExternalForce    : 입자별 외부 퍼텐셜          │
│  NBodyGauge       : 입자별 코리올리 회전        │
│                                                │
│  극한 일관성:                                   │
│    N=1 → 단일 입자 trunk과 동일                 │
│    F_ij = -F_ji → 운동량 보존                  │
│    γ=0, σ=0 → 에너지 보존                     │
└──────────────────────────────────────────────┘
"""

from __future__ import annotations
import numpy as np
from typing import Callable, Optional


# ================================================================== #
#  NBodyState — flat ↔ (N, d) reshape 유틸리티
# ================================================================== #

class NBodyState:
    """N-body state vector를 (N, d) 행렬로 보는 뷰.

    trunk의 flat state_vector를 N 입자 × d 차원으로 해석한다.
    복사 없이 reshape view를 제공한다.

    사용법:
        nbs = NBodyState(n_particles=3, dim=2)
        X = nbs.positions(state_vector)   # shape (3, 2)
        V = nbs.velocities(state_vector)  # shape (3, 2)
    """

    def __init__(self, n_particles: int, dim: int):
        self.n_particles = n_particles
        self.dim = dim
        self.n_dof = n_particles * dim

    def positions(self, state_vector: np.ndarray) -> np.ndarray:
        """flat state → (N, d) 위치 행렬 (view)"""
        return state_vector[:self.n_dof].reshape(self.n_particles, self.dim)

    def velocities(self, state_vector: np.ndarray) -> np.ndarray:
        """flat state → (N, d) 속도 행렬 (view)"""
        return state_vector[self.n_dof:].reshape(self.n_particles, self.dim)

    def make_state_vector(self, positions: np.ndarray, velocities: np.ndarray) -> np.ndarray:
        """(N, d) 위치 + 속도 → flat state_vector"""
        return np.concatenate([positions.ravel(), velocities.ravel()])

    def kinetic_energy(self, state_vector: np.ndarray, mass: float = 1.0) -> float:
        """총 운동에너지 Σᵢ ½m|vᵢ|²"""
        V = self.velocities(state_vector)
        return float(0.5 * mass * np.sum(V ** 2))

    def total_momentum(self, state_vector: np.ndarray, mass: float = 1.0) -> np.ndarray:
        """총 운동량 Σᵢ m·vᵢ"""
        V = self.velocities(state_vector)
        return mass * np.sum(V, axis=0)

    def center_of_mass(self, state_vector: np.ndarray) -> np.ndarray:
        """질량 중심 (등질량 가정)"""
        X = self.positions(state_vector)
        return np.mean(X, axis=0)


# ================================================================== #
#  InteractionForce — 쌍체 상호작용 ForceLayer
# ================================================================== #

class InteractionForce:
    """쌍체 상호작용: Σ_{i<j} φ(r_ij)

    φ(r) : 쌍체 퍼텐셜 함수 (스칼라 → 스칼라)
    φ'(r): 쌍체 힘의 크기 (양수 = 척력, 음수 = 인력)

    힘:
      F_i = -∇_i Σ_{j≠i} φ(|x_i - x_j|)
          = -Σ_{j≠i} φ'(r_ij) · (x_i - x_j) / r_ij

    Newton 제3법칙: F_ij = -F_ji (구조적 보장)
    → 총 운동량 보존

    사용법:
        # 중력형: φ(r) = -G/r, φ'(r) = G/r²
        def gravity_potential(r): return -1.0 / r
        def gravity_force(r): return 1.0 / r**2

        interaction = InteractionForce(
            n_particles=3, dim=2,
            pair_potential=gravity_potential,
            pair_force=gravity_force,
            softening=1e-3,
        )
    """

    def __init__(
        self,
        n_particles: int,
        dim: int,
        pair_potential: Callable[[float], float],
        pair_force: Optional[Callable[[float], float]] = None,
        softening: float = 1e-6,
    ):
        self.n_particles = n_particles
        self.dim = dim
        self.n_dof = n_particles * dim
        self._phi = pair_potential
        self._dphi = pair_force
        self._eps2 = softening ** 2

    def _pairwise_distances(self, X: np.ndarray):
        """(N, d) → distances (N, N), displacement vectors (N, N, d)"""
        diff = X[:, np.newaxis, :] - X[np.newaxis, :, :]
        r2 = np.sum(diff ** 2, axis=-1) + self._eps2
        r = np.sqrt(r2)
        return r, diff

    def force(self, x: np.ndarray, v: np.ndarray, t: float) -> np.ndarray:
        """쌍체 힘 합산 → flat force vector"""
        X = x.reshape(self.n_particles, self.dim)
        r, diff = self._pairwise_distances(X)

        F = np.zeros_like(X)
        N = self.n_particles

        for i in range(N):
            for j in range(i + 1, N):
                rij = r[i, j]
                dij = diff[i, j]
                unit = dij / rij

                if self._dphi is not None:
                    f_mag = self._dphi(rij)
                else:
                    dr = max(rij * 1e-6, 1e-10)
                    f_mag = (self._phi(rij + dr) - self._phi(rij - dr)) / (2 * dr)

                fij = -f_mag * unit
                F[i] += fij
                F[j] -= fij

        return F.ravel()

    def potential(self, x: np.ndarray) -> float:
        """총 상호작용 퍼텐셜 Σ_{i<j} φ(r_ij)"""
        X = x.reshape(self.n_particles, self.dim)
        r, _ = self._pairwise_distances(X)

        V = 0.0
        for i in range(self.n_particles):
            for j in range(i + 1, self.n_particles):
                V += self._phi(r[i, j])
        return V


class ExternalForce:
    """입자별 외부 퍼텐셜: V_ext = Σᵢ V(xᵢ)

    단일 입자 퍼텐셜을 N 입자 각각에 독립 적용한다.
    N=1이면 GradientForce와 동일하게 동작한다.
    """

    def __init__(
        self,
        n_particles: int,
        dim: int,
        potential_func: Callable[[np.ndarray], float],
        field_func: Optional[Callable[[np.ndarray], np.ndarray]] = None,
        epsilon: float = 1e-6,
    ):
        self.n_particles = n_particles
        self.dim = dim
        self.n_dof = n_particles * dim
        self._V = potential_func
        self._g = field_func
        self._eps = epsilon

    def _gradient(self, xi: np.ndarray) -> np.ndarray:
        """단일 입자 gradient"""
        if self._g is not None:
            return self._g(xi)
        grad = np.zeros(self.dim)
        for a in range(self.dim):
            xp = xi.copy(); xp[a] += self._eps
            xm = xi.copy(); xm[a] -= self._eps
            grad[a] = (self._V(xp) - self._V(xm)) / (2.0 * self._eps)
        return -grad

    def force(self, x: np.ndarray, v: np.ndarray, t: float) -> np.ndarray:
        X = x.reshape(self.n_particles, self.dim)
        F = np.zeros_like(X)
        for i in range(self.n_particles):
            F[i] = self._gradient(X[i])
        return F.ravel()

    def potential(self, x: np.ndarray) -> float:
        X = x.reshape(self.n_particles, self.dim)
        return sum(self._V(X[i]) for i in range(self.n_particles))


# ================================================================== #
#  NBodyGauge — 입자별 코리올리 회전
# ================================================================== #

class NBodyGauge:
    """입자별 코리올리 회전: 각 입자의 속도를 독립적으로 회전.

    단일 입자 CoriolisGauge를 N 입자로 확장.
    N=1이면 CoriolisGauge와 동일.
    """

    def __init__(self, n_particles: int, dim: int, omega: float, axis: tuple = (0, 1)):
        self.n_particles = n_particles
        self.dim = dim
        self.omega = omega
        self.axis = axis

    def rotate(self, v: np.ndarray, dt: float) -> np.ndarray:
        theta = self.omega * dt
        c, s = np.cos(theta), np.sin(theta)
        ai, aj = self.axis

        V = v.reshape(self.n_particles, self.dim).copy()
        for k in range(self.n_particles):
            vi, vj = V[k, ai], V[k, aj]
            V[k, ai] = c * vi - s * vj
            V[k, aj] = s * vi + c * vj

        return V.ravel()

    def check_skew(self) -> bool:
        return True


# ================================================================== #
#  편의 함수: 기본 상호작용 퍼텐셜
# ================================================================== #

def gravitational_interaction(
    n_particles: int,
    dim: int,
    G: float = 1.0,
    softening: float = 0.01,
) -> InteractionForce:
    """뉴턴 중력: φ(r) = -Gm²/r, F = Gm²/r² (인력)"""
    return InteractionForce(
        n_particles=n_particles,
        dim=dim,
        pair_potential=lambda r: -G / r,
        pair_force=lambda r: G / r ** 2,
        softening=softening,
    )


def spring_interaction(
    n_particles: int,
    dim: int,
    k: float = 1.0,
    r0: float = 1.0,
) -> InteractionForce:
    """조화 스프링: φ(r) = ½k(r-r₀)², F = -k(r-r₀)/r (복원력)"""
    return InteractionForce(
        n_particles=n_particles,
        dim=dim,
        pair_potential=lambda r: 0.5 * k * (r - r0) ** 2,
        pair_force=lambda r: k * (r - r0),
        softening=0.0,
    )


def coulomb_interaction(
    n_particles: int,
    dim: int,
    q: float = 1.0,
    softening: float = 0.01,
) -> InteractionForce:
    """쿨롱: φ(r) = q²/r, F = -q²/r² (척력, 동종 전하)"""
    return InteractionForce(
        n_particles=n_particles,
        dim=dim,
        pair_potential=lambda r: q ** 2 / r,
        pair_force=lambda r: -q ** 2 / r ** 2,
        softening=softening,
    )
