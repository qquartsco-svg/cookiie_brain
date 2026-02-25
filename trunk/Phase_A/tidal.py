"""3계층 중력 동역학 — 태양(CentralBody) · 달(OrbitalMoon) · 조석(TidalField)

Tier 1: CentralBody  — 1/r 중심 퍼텐셜 (장거리, 태양)
Tier 3: OrbitalMoon  — 공전하는 달 + 조석력
TidalField           — 여러 달의 조석력 합성

Tier 2(지구/바다)는 기존 GaussianWell (hippo/memory_store.py)이 담당.

수식:
  V_sun(r)  = -G·M / (r + ε)               장거리 중력
  x_moon(t) = c + R·[cos(Ωt), sin(Ωt)]     달 공전
  V_moon(x,t) = -G_m·M_m / (‖x-x_moon(t)‖ + ε)  달 중력
  F_tidal   = -∇V_moon                      조석력

안정 공전:
  v_circ = √(GM/r)
  γ < ω 일 때 준안정 궤도 가능

Author: GNJz (Qquarts)
Version: 0.7.0
"""

from __future__ import annotations
import numpy as np
from dataclasses import dataclass, field
from typing import Callable, List, Optional, Tuple


@dataclass
class CentralBody:
    """Tier 1: 중심 퍼텐셜 (태양)

    1/r 중력으로 전체 시스템을 묶는 장거리 힘.
    Gaussian 우물과 달리 멀어져도 끌림이 살아있다.

    안정 원궤도: v = √(GM/r)
    탈출 속도:   v = √(2GM/r)
    """
    position: np.ndarray
    mass: float = 10.0
    G: float = 1.0
    softening: float = 1e-4

    def __post_init__(self):
        self.position = np.asarray(self.position, dtype=float)

    def potential(self, x: np.ndarray) -> float:
        """V = -GM / (r + ε)"""
        r = np.linalg.norm(x - self.position) + self.softening
        return -self.G * self.mass / r

    def field(self, x: np.ndarray) -> np.ndarray:
        """-∇V = -GM·(x - x_sun) / (r + ε)³  (인력: 중심을 향함)"""
        dx = x - self.position
        r = np.linalg.norm(dx) + self.softening
        return -self.G * self.mass * dx / (r ** 3)

    def circular_speed(self, r: float) -> float:
        """반지름 r에서의 원궤도 속도"""
        return np.sqrt(self.G * self.mass / (r + self.softening))

    def escape_speed(self, r: float) -> float:
        """반지름 r에서의 탈출 속도"""
        return np.sqrt(2.0 * self.G * self.mass / (r + self.softening))


@dataclass
class OrbitalMoon:
    """Tier 3: 공전하는 달 (위성)

    host_center 주위를 원궤도로 공전하며 조석력을 생성한다.

    조석(tidal)의 물리:
      달 중력의 공간적 기울기 차이가 우물 안의 상태를
      타원형으로 순환시킨다.
    """
    host_center: np.ndarray
    orbit_radius: float = 1.5
    orbit_frequency: float = 2.0
    mass: float = 0.3
    G: float = 1.0
    softening: float = 1e-4
    initial_phase: float = 0.0

    def __post_init__(self):
        self.host_center = np.asarray(self.host_center, dtype=float)
        self._dim = len(self.host_center)

    def position(self, t: float) -> np.ndarray:
        """시각 t에서의 달 위치 (원궤도)"""
        phase = self.orbit_frequency * t + self.initial_phase
        pos = self.host_center.copy()
        pos[0] += self.orbit_radius * np.cos(phase)
        if self._dim >= 2:
            pos[1] += self.orbit_radius * np.sin(phase)
        return pos

    def potential(self, x: np.ndarray, t: float) -> float:
        """V_moon = -G_m · M_m / (‖x - x_moon(t)‖ + ε)"""
        dx = x - self.position(t)
        r = np.linalg.norm(dx) + self.softening
        return -self.G * self.mass / r

    def gravity(self, x: np.ndarray, t: float) -> np.ndarray:
        """-∇V_moon = -G_m · M_m · (x - x_moon) / (r + ε)³"""
        moon_pos = self.position(t)
        dx = x - moon_pos
        r = np.linalg.norm(dx) + self.softening
        return -self.G * self.mass * dx / (r ** 3)


class TidalField:
    """3계층 중력 합성: 중심장 + 조석장

    CentralBody(태양) + OrbitalMoon(달)의 힘을 합성.
    GaussianWell(지구/Tier 2)은 PFE/MemoryStore가 처리.
    """

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
        """전체 외부 힘: 중심장 + 모든 달의 조석력

        이 값이 PFE의 injection 또는 external_force에 합산된다.
        """
        x = np.asarray(x, dtype=float)
        f = np.zeros_like(x)

        if self.central is not None:
            f += self.central.field(x)

        for moon in self.moons:
            f += moon.gravity(x, t)

        self._time = t
        return f

    def potential(self, x: np.ndarray, t: float) -> float:
        """전체 외부 퍼텐셜: V_sun + Σ V_moon"""
        x = np.asarray(x, dtype=float)
        V = 0.0

        if self.central is not None:
            V += self.central.potential(x)

        for moon in self.moons:
            V += moon.potential(x, t)

        return V

    def create_injection_func(self) -> Callable:
        """PFE에 주입할 수 있는 injection_func 생성

        PFE의 injection_func 시그니처: f(x, v, t) -> np.ndarray
        """
        def injection(x: np.ndarray, v: np.ndarray, t: float) -> np.ndarray:
            return self.force(x, t)

        return injection

    def info(self) -> dict:
        return {
            "has_central": self.central is not None,
            "central_mass": self.central.mass if self.central else 0.0,
            "n_moons": len(self.moons),
            "moons": [
                {
                    "host_center": m.host_center.tolist(),
                    "orbit_radius": m.orbit_radius,
                    "orbit_frequency": m.orbit_frequency,
                    "mass": m.mass,
                }
                for m in self.moons
            ],
            "time": self._time,
        }
