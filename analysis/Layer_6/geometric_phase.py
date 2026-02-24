"""Layer 6 — 기하학적 위상 + 정보 기하학 (Geometric Phase + Information Geometry)

매개변수 공간의 기하학적 구조를 분석한다.

┌──────────────────────────────────────────────────────┐
│  Layer 6: 기하학적 위상 + 정보 기하학                    │
│  ─────────────────────────────                        │
│                                                        │
│  Layer 3 (공간 내 게이지) vs Layer 6 (매개변수 공간 기하):│
│    Layer 3: Ω(x)v — 물리 공간의 자기장/게이지 구조      │
│    Layer 6: g_μν, K — 매개변수 공간의 기하학             │
│                                                        │
│  핵심 도구: Fisher 정보 기하학                           │
│    Fisher 계량: g_μν = (1/T²) Cov(∂_μV, ∂_νV)         │
│    가우스 곡률: K — 매개변수 공간의 내재적 곡률           │
│    측지선 거리: 매개변수 변화의 "통계적 구별 가능성"      │
│                                                        │
│  왜 naive Berry phase = 0인가 (1D 고전):               │
│    A_μ = ∂⟨x⟩/∂λ_μ = ∇_λ f  (gradient)               │
│    F = curl(∇f) = 0  (항상)                            │
│    → 1D overdamped 고전계에서 스칼라 기대값의            │
│      Berry connection은 trivial하다.                    │
│    → Fisher 계량의 곡률은 NON-trivial하다.              │
│                                                        │
│  Fisher 계량의 물리적 의미:                              │
│    g_μν = 매개변수 변화에 대한 분포의 민감도              │
│    K > 0: 매개변수 공간이 "구면 같음" (수렴)             │
│    K < 0: "쌍곡면 같음" (발산)                           │
│    K = 0: "평탄" (유클리드)                              │
│                                                        │
│  양자 Berry 위상과의 관계:                               │
│    양자: |ψ⟩의 복소 위상 → U(1) fiber bundle            │
│    고전: ρ(x;λ)는 실수 → trivial Berry phase            │
│    정보: Fisher metric → 진짜 Riemannian geometry       │
│    연결: Fisher 계량 = 양자 Fubini-Study 계량의 고전 극한│
└──────────────────────────────────────────────────────┘
"""

from __future__ import annotations
import numpy as np
from typing import Callable, Tuple


# ================================================================== #
#  ParameterSpace — 매개변수 공간 격자
# ================================================================== #

class ParameterSpace:
    """2D 매개변수 공간 (λ₁, λ₂) 격자."""

    def __init__(
        self,
        lam1_range: Tuple[float, float],
        lam2_range: Tuple[float, float],
        n1: int,
        n2: int,
    ):
        self.lam1 = np.linspace(*lam1_range, n1)
        self.lam2 = np.linspace(*lam2_range, n2)
        self.n1 = n1
        self.n2 = n2
        self.dlam1 = self.lam1[1] - self.lam1[0]
        self.dlam2 = self.lam2[1] - self.lam2[0]


# ================================================================== #
#  FisherMetricCalculator — Fisher 정보 기하학
# ================================================================== #

class FisherMetricCalculator:
    """Fisher 정보 계량 on 매개변수 공간.

    ρ(x; λ) ∝ exp(−V(x;λ)/T) 일 때:

      g_μν(λ) = ∫ ρ(x;λ) · ∂_μ ln ρ · ∂_ν ln ρ dx
              = (1/T²) · Cov_λ(∂_μ V, ∂_ν V)

    이것은 매개변수 공간 위의 Riemannian 계량이다.
    가우스 곡률 K는 일반적으로 0이 아니다.

    물리적 의미:
      ds² = g_μν dλ^μ dλ^ν  = 매개변수를 dλ만큼 바꿀 때
      분포가 "얼마나 다른지"의 제곱 (통계적 구별 가능성).

    Parameters
    ----------
    x_grid : ndarray
        물리 공간 격자
    V_func : (x, lam1, lam2) -> ndarray
        매개변수 의존 퍼텐셜
    T : float
        온도
    """

    def __init__(
        self,
        x_grid: np.ndarray,
        V_func: Callable,
        T: float,
    ):
        self.x = x_grid
        self.dx = x_grid[1] - x_grid[0]
        self._V = V_func
        self.T = T

    def _rho(self, lam1: float, lam2: float) -> np.ndarray:
        """ρ_eq(x; λ) ∝ exp(−V/T), 정규화."""
        V = self._V(self.x, lam1, lam2)
        log_rho = -V / self.T
        log_rho -= np.max(log_rho)
        rho = np.exp(log_rho)
        norm = np.trapezoid(rho, self.x)
        if norm > 0:
            rho /= norm
        return rho

    def _expect(self, f: np.ndarray, rho: np.ndarray) -> float:
        return float(np.trapezoid(f * rho, self.x))

    def _cov(self, f: np.ndarray, g: np.ndarray, rho: np.ndarray) -> float:
        ef = self._expect(f, rho)
        eg = self._expect(g, rho)
        return self._expect(f * g, rho) - ef * eg

    def _dV_dlam(self, lam1: float, lam2: float, eps: float = 1e-5) -> Tuple[np.ndarray, np.ndarray]:
        """∂V/∂λ₁ 과 ∂V/∂λ₂ 수치 계산."""
        dV1 = (self._V(self.x, lam1 + eps, lam2) -
               self._V(self.x, lam1 - eps, lam2)) / (2 * eps)
        dV2 = (self._V(self.x, lam1, lam2 + eps) -
               self._V(self.x, lam1, lam2 - eps)) / (2 * eps)
        return dV1, dV2

    def metric_tensor(self, lam1: float, lam2: float) -> np.ndarray:
        """Fisher 계량 텐서 g_μν = (1/T²) Cov(∂_μV, ∂_νV).

        Returns 2×2 symmetric positive semi-definite matrix.
        """
        rho = self._rho(lam1, lam2)
        dV1, dV2 = self._dV_dlam(lam1, lam2)

        g = np.zeros((2, 2))
        g[0, 0] = self._cov(dV1, dV1, rho) / self.T**2
        g[0, 1] = self._cov(dV1, dV2, rho) / self.T**2
        g[1, 0] = g[0, 1]
        g[1, 1] = self._cov(dV2, dV2, rho) / self.T**2
        return g

    def gaussian_curvature(self, lam1: float, lam2: float, eps: float = 0.02) -> float:
        """가우스 곡률 K — Brioschi 공식.

        K = [det(A) − det(B)] / det(g)²

        K > 0: 구면 유사, K < 0: 쌍곡면 유사, K = 0: 평탄.
        """
        g_c = self.metric_tensor(lam1, lam2)
        E, F, G = g_c[0, 0], g_c[0, 1], g_c[1, 1]
        det_g = E * G - F**2
        if abs(det_g) < 1e-20:
            return 0.0

        def _g(l1, l2):
            return self.metric_tensor(l1, l2)

        g1p = _g(lam1 + eps, lam2)
        g1m = _g(lam1 - eps, lam2)
        g2p = _g(lam1, lam2 + eps)
        g2m = _g(lam1, lam2 - eps)

        E_u = (g1p[0, 0] - g1m[0, 0]) / (2 * eps)
        E_v = (g2p[0, 0] - g2m[0, 0]) / (2 * eps)
        F_u = (g1p[0, 1] - g1m[0, 1]) / (2 * eps)
        F_v = (g2p[0, 1] - g2m[0, 1]) / (2 * eps)
        G_u = (g1p[1, 1] - g1m[1, 1]) / (2 * eps)
        G_v = (g2p[1, 1] - g2m[1, 1]) / (2 * eps)

        E_uu = (g1p[0, 0] - 2 * E + g1m[0, 0]) / eps**2
        G_vv = (g2p[1, 1] - 2 * G + g2m[1, 1]) / eps**2
        E_vv = (g2p[0, 0] - 2 * E + g2m[0, 0]) / eps**2
        G_uu = (g1p[1, 1] - 2 * G + g1m[1, 1]) / eps**2

        g_pp = _g(lam1 + eps, lam2 + eps)
        g_pm = _g(lam1 + eps, lam2 - eps)
        g_mp = _g(lam1 - eps, lam2 + eps)
        g_mm = _g(lam1 - eps, lam2 - eps)

        F_uv = (g_pp[0, 1] - g_pm[0, 1] - g_mp[0, 1] + g_mm[0, 1]) / (4 * eps**2)

        A = np.array([
            [-0.5 * (E_vv - 2 * F_uv + G_uu), 0.5 * E_u, F_u - 0.5 * E_v],
            [F_v - 0.5 * G_u,                  E,          F],
            [0.5 * G_v,                         F,          G],
        ])
        B = np.array([
            [0.0,        0.5 * E_v, 0.5 * G_u],
            [0.5 * E_v,  E,         F],
            [0.5 * G_u,  F,         G],
        ])

        K = (np.linalg.det(A) - np.linalg.det(B)) / det_g**2
        return float(K)

    def geodesic_distance(self, path: np.ndarray) -> float:
        """경로를 따른 Fisher 측지선 거리 (상한).

        ds² = g_μν dλ^μ dλ^ν
        L = ∫ √(ds²)
        """
        L = 0.0
        for k in range(len(path) - 1):
            dlam = path[k + 1] - path[k]
            mid = 0.5 * (path[k] + path[k + 1])
            g = self.metric_tensor(mid[0], mid[1])
            ds2 = dlam @ g @ dlam
            L += np.sqrt(max(ds2, 0.0))
        return L

    def expectation_x(self, lam1: float, lam2: float) -> float:
        """⟨x⟩_λ"""
        rho = self._rho(lam1, lam2)
        return self._expect(self.x, rho)

    def variance_x(self, lam1: float, lam2: float) -> float:
        """Var(x)_λ"""
        rho = self._rho(lam1, lam2)
        return self._cov(self.x, self.x, rho)


# ================================================================== #
#  편의 함수
# ================================================================== #

def tilted_double_well(x: np.ndarray, lam1: float, lam2: float) -> np.ndarray:
    """기울어진 이중 우물: V(x; λ₁, λ₂) = x⁴ − 4x² + λ₁·x + λ₂·x²."""
    return x**4 - 4.0 * x**2 + lam1 * x + lam2 * x**2


def circular_path(
    center: Tuple[float, float],
    radius: float,
    n_points: int = 100,
) -> np.ndarray:
    """매개변수 공간의 원형 경로."""
    theta = np.linspace(0, 2 * np.pi, n_points + 1)
    return np.column_stack([
        center[0] + radius * np.cos(theta),
        center[1] + radius * np.sin(theta),
    ])
