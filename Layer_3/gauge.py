"""Layer 3 — 게이지/기하학: 위치 의존 자기장형 힘

trunk의 CoriolisGauge는 전역 상수 ω로 회전한다.
Layer 3는 B(x) — 위치 의존 자기장을 도입한다.

┌────────────────────────────────────────────────┐
│  Layer 3: 게이지/기하학                          │
│  ─────────────────                              │
│  MagneticForce      : F = B(x)·J·v (단일 입자)  │
│  NBodyMagneticForce : N 입자 각각에 B(x) 적용    │
│  GeometryAnalyzer   : Berry 위상, 자기 선속 계산  │
│                                                  │
│  핵심 물리:                                       │
│    F·v = 0 (일을 안 함) → 에너지 보존             │
│    B(x) = const → CoriolisGauge와 동일           │
│    ∮ A·dl = ∫∫ B dA (Stokes 정리)               │
│                                                  │
│  trunk 수정 불필요:                               │
│    ForceLayer 프로토콜 준수 (duck-typing)         │
└────────────────────────────────────────────────┘

2D에서의 수식:
  B(x) : 스칼라 (z 방향 자기장의 크기)
  J = [[0, -1], [1, 0]]  (2D symplectic 행렬)
  F = B(x) · J · v = B(x) · (-v_y, v_x)

  F·v = B(x)·(-v_y·v_x + v_x·v_y) = 0  (구조적 보장)

3D에서의 수식:
  B(x) : 3-벡터 (자기장)
  F = v × B(x)  (로렌츠 힘)
  F·v = (v × B)·v = 0  (구조적 보장)
"""

from __future__ import annotations
import numpy as np
from typing import Callable, Optional


# ================================================================== #
#  MagneticForce — 위치 의존 자기장형 힘 (단일 입자)
# ================================================================== #

class MagneticForce:
    """F = B(x) · J · v  (2D) 또는  F = v × B(x)  (3D)

    위치 의존 자기장이 만드는 로렌츠형 힘.
    v에 수직이므로 에너지를 보존한다 (F·v = 0, 구조적).

    극한 일관성:
      B(x) = const = ω  →  trunk의 CoriolisGauge와 동일
      B(x) = 0          →  힘 없음 (자유 입자)

    사용법 (2D):
        def B_field(x):
            return 0.5 * np.exp(-np.dot(x, x) / 4.0)

        magnetic = MagneticForce(B_func=B_field, dim=2)
        engine = PotentialFieldEngine(force_layers=[gradient, magnetic], ...)
    """

    def __init__(self, B_func: Callable[[np.ndarray], float], dim: int = 2):
        self._B = B_func
        self.dim = dim

    def force(self, x: np.ndarray, v: np.ndarray, t: float) -> np.ndarray:
        """위치 의존 자기장형 힘"""
        if self.dim == 2:
            B = self._B(x)
            return np.array([-B * v[1], B * v[0]])
        elif self.dim == 3:
            B = self._B(x)
            if np.isscalar(B):
                B = np.array([0.0, 0.0, B])
            return np.cross(v, B)
        else:
            raise ValueError(f"MagneticForce: dim={self.dim} not supported (2 or 3)")

    def potential(self, x: np.ndarray) -> float:
        return 0.0


# ================================================================== #
#  NBodyMagneticForce — N 입자 각각에 B(x) 적용
# ================================================================== #

class NBodyMagneticForce:
    """N 입자 각각에 위치 의존 자기장 적용.

    각 입자의 위치에서 B(xᵢ)를 평가하고,
    해당 입자의 속도에 로렌츠형 힘을 가한다.

    N=1이면 MagneticForce와 동일.
    """

    def __init__(
        self,
        n_particles: int,
        dim: int,
        B_func: Callable[[np.ndarray], float],
    ):
        self.n_particles = n_particles
        self.dim = dim
        self.n_dof = n_particles * dim
        self._B = B_func

    def force(self, x: np.ndarray, v: np.ndarray, t: float) -> np.ndarray:
        X = x.reshape(self.n_particles, self.dim)
        V = v.reshape(self.n_particles, self.dim)
        F = np.zeros_like(X)

        for i in range(self.n_particles):
            B = self._B(X[i])
            if self.dim == 2:
                F[i, 0] = -B * V[i, 1]
                F[i, 1] = B * V[i, 0]
            elif self.dim == 3:
                if np.isscalar(B):
                    B = np.array([0.0, 0.0, B])
                F[i] = np.cross(V[i], B)

        return F.ravel()

    def potential(self, x: np.ndarray) -> float:
        return 0.0


# ================================================================== #
#  GeometryAnalyzer — 기하학적 양 계산
# ================================================================== #

class GeometryAnalyzer:
    """게이지 기하학 분석 도구.

    자기장 B(x)로부터 기하학적 물리량을 계산한다:
    - 자기 선속 (magnetic flux)
    - Berry 위상 (holonomy)
    - 국소 곡률
    """

    @staticmethod
    def magnetic_flux(
        B_func: Callable[[np.ndarray], float],
        center: np.ndarray,
        radius: float,
        n_points: int = 200,
    ) -> float:
        """원형 영역의 자기 선속 Φ = ∫∫ B dA

        2D에서 B(x)는 스칼라. 원형 영역을 동심 고리로 적분한다.
        """
        total = 0.0
        n_rings = max(n_points // 4, 10)
        n_theta = max(n_points // n_rings, 8)

        for ir in range(n_rings):
            r = radius * (ir + 0.5) / n_rings
            dr = radius / n_rings
            for it in range(n_theta):
                theta = 2.0 * np.pi * it / n_theta
                x = center + r * np.array([np.cos(theta), np.sin(theta)])
                total += B_func(x) * r * dr * (2.0 * np.pi / n_theta)

        return total

    @staticmethod
    def berry_phase_loop(
        B_func: Callable[[np.ndarray], float],
        path: np.ndarray,
    ) -> float:
        """닫힌 경로의 Berry 위상 = ∫∫_S B dA (Stokes 정리)

        path: shape (M, 2) — 닫힌 경로의 꼭짓점들
        Green 정리로 면적분을 선적분으로 변환하여 계산:
          Φ = Σ_triangles B(centroid) · signed_area
        """
        M = len(path)
        if M < 3:
            return 0.0

        centroid = np.mean(path, axis=0)
        total = 0.0

        for k in range(M):
            p1 = path[k]
            p2 = path[(k + 1) % M]
            tri_center = (centroid + p1 + p2) / 3.0
            signed_area = 0.5 * ((p1[0] - centroid[0]) * (p2[1] - centroid[1])
                                 - (p2[0] - centroid[0]) * (p1[1] - centroid[1]))
            total += B_func(tri_center) * signed_area

        return total

    @staticmethod
    def local_curvature(
        B_func: Callable[[np.ndarray], float],
        x: np.ndarray,
    ) -> float:
        """국소 곡률 = B(x)

        2D 게이지 이론에서 곡률 2-form의 유일한 독립 성분은 B(x) 자체이다.
        F₁₂ = ∂₁A₂ − ∂₂A₁ = B(x)
        """
        return B_func(x)

    @staticmethod
    def cyclotron_frequency(B: float, mass: float = 1.0) -> float:
        """사이클로트론 진동수 ω_c = B/m"""
        return abs(B) / mass

    @staticmethod
    def cyclotron_radius(v_perp: float, B: float, mass: float = 1.0) -> float:
        """사이클로트론 반경 r_c = mv_⊥/|B|"""
        if abs(B) < 1e-15:
            return float("inf")
        return mass * abs(v_perp) / abs(B)

    @staticmethod
    def exb_drift(grad_V: np.ndarray, B: float) -> np.ndarray:
        """E×B drift 속도 (2D)

        MagneticForce의 부호 규약 (F = B·J·v) 에서
        정상 상태 drift는:
          0 = -∂V/∂x − B·v_y  →  v_y = −(∂V/∂x)/B
          0 = -∂V/∂y + B·v_x  →  v_x = +(∂V/∂y)/B

        즉 v_drift = (∂V/∂y, −∂V/∂x) / B
        """
        if abs(B) < 1e-15:
            return np.zeros(2)
        return np.array([grad_V[1], -grad_V[0]]) / B


# ================================================================== #
#  편의 함수: 기본 자기장 구성
# ================================================================== #

def uniform_field(B0: float) -> Callable[[np.ndarray], float]:
    """균일 자기장 B(x) = B₀"""
    return lambda x: B0


def gaussian_field(
    B0: float,
    center: np.ndarray,
    sigma: float,
) -> Callable[[np.ndarray], float]:
    """가우시안 자기장: B(x) = B₀ · exp(−|x−c|²/(2σ²))"""
    def B_func(x):
        r2 = np.sum((x - center) ** 2)
        return B0 * np.exp(-r2 / (2.0 * sigma ** 2))
    return B_func


def dipole_field(
    moment: float,
    center: np.ndarray,
    softening: float = 0.1,
) -> Callable[[np.ndarray], float]:
    """쌍극자형 자기장: B(x) = μ / (|x−c|² + ε²)"""
    def B_func(x):
        r2 = np.sum((x - center) ** 2) + softening ** 2
        return moment / r2
    return B_func


def multi_well_field(
    wells_B: list,
    centers: list,
    sigmas: list,
) -> Callable[[np.ndarray], float]:
    """다중 우물 자기장: 각 우물 근처에서 다른 B 강도

    인지 해석: 기억마다 다른 '회전 경향'을 가진다.
    """
    def B_func(x):
        total = 0.0
        for B0, c, s in zip(wells_B, centers, sigmas):
            r2 = np.sum((x - np.asarray(c)) ** 2)
            total += B0 * np.exp(-r2 / (2.0 * s ** 2))
        return total
    return B_func
