"""Layer 3 — 게이지/기하학: 위치 의존 반대칭 연산자

┌──────────────────────────────────────────────────────┐
│  Layer 3: 게이지/기하학                                │
│  ─────────────────                                    │
│                                                        │
│  수학적 본질:                                           │
│    G(x, v) = Ω(x) · v    (반대칭 선형 연산)             │
│    Ω(x)ᵀ = −Ω(x)         (skew-symmetric)             │
│    v · Ω(x)v = 0          → 에너지 보존 (구조적)        │
│                                                        │
│  게이지 ≠ 보존력:                                       │
│    ✗ 퍼텐셜에서 유도되지 않는다 (G ≠ −∇V)               │
│    ✔ Hamiltonian의 symplectic 구조 내 회전 항           │
│    ✔ geometric phase term / connection 연산자          │
│                                                        │
│  구성 요소:                                             │
│    GaugeForce         : Ω(x)v (단일 입자, 2D/3D)       │
│    NBodyGaugeForce    : N 입자 각각에 Ω(xᵢ)vᵢ 적용     │
│    GeometryAnalyzer   : Berry 위상, 선속, 곡률 계산      │
│                                                        │
│  극한 일관성:                                           │
│    Ω = const → trunk의 CoriolisGauge와 동일             │
│    B(x) = 0  → Ω = 0, 자유 입자                        │
│    ∮ A·dl = ∫∫ B dA (Stokes 정리)                      │
│                                                        │
│  구현 참고:                                             │
│    trunk의 GaugeLayer는 rotate(v, dt)만 받으므로         │
│    위치 의존 Ω(x)는 ForceLayer 프로토콜로 전달한다.       │
│    이것은 구현 편의이며, 물리적 본질은 gauge 연산이다.     │
└──────────────────────────────────────────────────────┘

연산자 분해 구조:

  mẍ = −∇V(x)  +  Ω(x)v   −  γv  +  σξ(t)
        ─────     ──────      ────    ─────
        Force     Gauge       Thermo  Fluctuation
        (보존력)  (반대칭)    (비가역)  (확률)

  Layer:  1,2       3          trunk    trunk

  Force:  퍼텐셜 기울기. 위치 의존. 에너지 교환 가능.
  Gauge:  반대칭 연산자. 속도에 작용. 에너지 보존 (구조적).
  Thermo: 감쇠 + 노이즈. 비가역.

2D 표현:
  Ω(x) = B(x) · J = B(x) · [[0, -1], [1, 0]]
  J는 반대칭 (Jᵀ = −J) → B(x)·J도 반대칭 (스칼라 × 반대칭 = 반대칭)
  v · Ω(x)v = B(x) · v·Jv = B(x) · (−v_y·v_x + v_x·v_y) = 0

3D 표현:
  G(v) = v × B(x)  (로렌츠 항)
  v · (v × B) = 0  (벡터 삼중곱 성질)
"""

from __future__ import annotations
import numpy as np
from typing import Callable, Optional


# ================================================================== #
#  GaugeForce — 위치 의존 반대칭 게이지 연산자 (단일 입자)
# ================================================================== #

class GaugeForce:
    """G(x, v) = Ω(x) · v  — 위치 의존 반대칭 게이지 연산자.

    이것은 보존력(−∇V)이 아니다.
    Hamiltonian의 symplectic 구조 내 회전 항(geometric phase term)이며,
    반대칭성 Ωᵀ = −Ω에 의해 v·Ωv = 0이 구조적으로 보장된다.

    2D: Ω(x) = B(x)·J,  J = [[0,-1],[1,0]]  (Jᵀ = −J)
    3D: G(v) = v × B(x)

    trunk의 ForceLayer 프로토콜로 전달하되(구현 편의),
    물리적 본질은 gauge 연산이다.

    극한 일관성:
      Ω(x) = ω·J (const)  →  trunk의 CoriolisGauge와 동일
      Ω(x) = 0            →  자유 입자

    사용법 (2D):
        def B_field(x):
            return 0.5 * np.exp(-np.dot(x, x) / 4.0)

        gauge = GaugeForce(B_func=B_field, dim=2)
        engine = PotentialFieldEngine(force_layers=[gradient, gauge], ...)
    """

    def __init__(self, B_func: Callable[[np.ndarray], float], dim: int = 2):
        self._B = B_func
        self.dim = dim

    def force(self, x: np.ndarray, v: np.ndarray, t: float) -> np.ndarray:
        """Ω(x)·v — 반대칭 게이지 연산자 적용"""
        if self.dim == 2:
            B = self._B(x)
            return np.array([-B * v[1], B * v[0]])
        elif self.dim == 3:
            B = self._B(x)
            if np.isscalar(B):
                B = np.array([0.0, 0.0, B])
            return np.cross(v, B)
        else:
            raise ValueError(f"GaugeForce: dim={self.dim} not supported (2 or 3)")

    def potential(self, x: np.ndarray) -> float:
        return 0.0

    def omega_matrix(self, x: np.ndarray) -> np.ndarray:
        """위치 x에서 반대칭 행렬 Ω(x) 반환 (2D 전용)."""
        B = self._B(x)
        if self.dim == 2:
            return np.array([[0.0, -B], [B, 0.0]])
        raise NotImplementedError("omega_matrix: 3D는 Levi-Civita 텐서 사용")

    def check_skew(self, x: np.ndarray) -> bool:
        """Ω(x) + Ω(x)ᵀ = 0 검증 (반대칭성)."""
        O = self.omega_matrix(x)
        return bool(np.allclose(O + O.T, 0.0))


MagneticForce = GaugeForce


# ================================================================== #
#  NBodyGaugeForce — N 입자 각각에 Ω(xᵢ)vᵢ 적용
# ================================================================== #

class NBodyGaugeForce:
    """N 입자 각각에 위치 의존 반대칭 게이지 연산자 적용.

    각 입자의 위치에서 Ω(xᵢ)를 평가하고,
    해당 입자의 속도에 반대칭 회전을 가한다.
    보존력이 아니라 geometric phase term이다.

    N=1이면 GaugeForce와 동일.
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

    def check_skew(self, x: np.ndarray, particle_idx: int = 0) -> bool:
        """입자 particle_idx 위치에서 Ω + Ωᵀ = 0 검증."""
        xi = x.reshape(self.n_particles, self.dim)[particle_idx]
        B = self._B(xi)
        if self.dim == 2:
            O = np.array([[0.0, -B], [B, 0.0]])
            return bool(np.allclose(O + O.T, 0.0))
        return True


NBodyMagneticForce = NBodyGaugeForce


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
