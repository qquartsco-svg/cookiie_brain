"""조석장 합성기 — 태양 + 달의 힘을 합산

TidalField는 CentralBody(태양)와 OrbitalMoon(달)의 중력을 합쳐서
하나의 힘 벡터로 내보낸다. PFE의 injection_func으로 사용.

GaussianWell(우물/Tier 2)은 PFE가 직접 처리하므로 여기에 없다.

Author: GNJz (Qquarts)
"""

from __future__ import annotations
import numpy as np
from typing import Callable, Dict, List, Optional

from .central_body import CentralBody
from .orbital_moon import OrbitalMoon


class TidalField:
    """3계층 중력 합성: 중심장(태양) + 조석장(달)."""

    def __init__(
        self,
        central: Optional[CentralBody] = None,
        moons: Optional[List[OrbitalMoon]] = None,
    ):
        self.central = central
        self.moons: List[OrbitalMoon] = moons or []
        self._time: float = 0.0

    @property
    def time(self) -> float:
        return self._time

    def add_moon(self, moon: OrbitalMoon) -> None:
        self.moons.append(moon)

    def force(self, x: np.ndarray, t: float) -> np.ndarray:
        x = np.asarray(x, dtype=float)
        f = np.zeros_like(x)
        if self.central is not None:
            f += self.central.field(x)
        for moon in self.moons:
            f += moon.gravity(x, t)
        self._time = t
        return f

    def potential(self, x: np.ndarray, t: float) -> float:
        x = np.asarray(x, dtype=float)
        V = 0.0
        if self.central is not None:
            V += self.central.potential(x)
        for moon in self.moons:
            V += moon.potential(x, t)
        return V

    def tidal_tensor(self, x: np.ndarray, t: float) -> np.ndarray:
        x = np.asarray(x, dtype=float)
        dim = len(x)
        T = np.zeros((dim, dim))
        for moon in self.moons:
            T += moon.tidal_tensor(x, t)
        return T

    def tidal_eigenvalues(self, x: np.ndarray, t: float) -> np.ndarray:
        T = self.tidal_tensor(x, t)
        return np.linalg.eigvalsh(T)

    def create_injection_func(self) -> Callable:
        """PFE injection_func 시그니처: f(x, v, t) -> np.ndarray"""
        def injection(x: np.ndarray, v: np.ndarray, t: float) -> np.ndarray:
            return self.force(x, t)
        return injection

    def info(self) -> dict:
        return {
            "has_central": self.central is not None,
            "central_mass": self.central.mass if self.central else 0.0,
            "n_moons": len(self.moons),
            "moons": [m.info(self._time) for m in self.moons],
            "time": self._time,
        }
