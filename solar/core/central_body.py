"""Tier 1: 태양 — 1/r 중심 퍼텐셜

전체 시스템을 묶는 장거리 중력.
Gaussian 우물은 멀어지면 힘이 0이 되지만, 1/r은 멀어져도 끌림이 남는다.

V_sun(r) = -G·M / (r + ε)

안정 원궤도: v = √(GM/r)
탈출 속도:   v = √(2GM/r)

Author: GNJz (Qquarts)
"""

from __future__ import annotations
import numpy as np
from dataclasses import dataclass


@dataclass
class CentralBody:
    """거대질량 중심체. 상태공간의 코어."""

    position: np.ndarray
    mass: float = 10.0
    G: float = 1.0
    softening: float = 1e-4

    def __post_init__(self):
        self.position = np.asarray(self.position, dtype=float)

    def potential(self, x: np.ndarray) -> float:
        r = np.linalg.norm(x - self.position) + self.softening
        return -self.G * self.mass / r

    def field(self, x: np.ndarray) -> np.ndarray:
        dx = x - self.position
        r = np.linalg.norm(dx) + self.softening
        return -self.G * self.mass * dx / (r ** 3)

    def circular_speed(self, r: float) -> float:
        return np.sqrt(self.G * self.mass / (r + self.softening))

    def escape_speed(self, r: float) -> float:
        return np.sqrt(2.0 * self.G * self.mass / (r + self.softening))
