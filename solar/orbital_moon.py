"""Tier 3: 달 — 타원 공전 + 자전 + 조석력 생성

우물(지구) 주위를 공전하는 소질량 천체.
달의 중력이 우물 안에 조석(힘의 차이)을 만든다.

공전: r(θ) = a(1-e²) / (1 + e·cos(θ-ω_p))  (Kepler)
자전: θ_spin = ω_spin·t  (tidal_locking이면 spin=orbit)
조석 텐서: T_ij = -∂²V/∂x_i∂x_j

Author: GNJz (Qquarts)
"""

from __future__ import annotations
import numpy as np
from dataclasses import dataclass
from typing import Dict


@dataclass
class OrbitalMoon:
    """타원 궤도 공전 + 자전하는 달."""

    host_center: np.ndarray
    semi_major_axis: float = 1.5
    eccentricity: float = 0.0
    orbit_frequency: float = 2.0
    mass: float = 0.3
    G: float = 1.0
    softening: float = 1e-4
    initial_phase: float = 0.0
    periapsis_angle: float = 0.0

    spin_frequency: float = 0.0
    tidal_locking: bool = True
    quadrupole_moment: float = 0.0

    def __post_init__(self):
        self.host_center = np.asarray(self.host_center, dtype=float)
        self._dim = len(self.host_center)
        if self.tidal_locking:
            self.spin_frequency = self.orbit_frequency

    @property
    def orbit_radius(self) -> float:
        return self.semi_major_axis

    def _true_anomaly(self, t: float) -> float:
        M = self.orbit_frequency * t + self.initial_phase
        if self.eccentricity < 1e-8:
            return M
        e = self.eccentricity
        E = M
        for _ in range(8):
            E = M + e * np.sin(E)
        theta = 2.0 * np.arctan2(
            np.sqrt(1 + e) * np.sin(E / 2),
            np.sqrt(1 - e) * np.cos(E / 2),
        )
        return theta

    def orbital_radius(self, t: float) -> float:
        theta = self._true_anomaly(t)
        e = self.eccentricity
        a = self.semi_major_axis
        if e < 1e-8:
            return a
        return a * (1 - e**2) / (1 + e * np.cos(theta - self.periapsis_angle))

    def position(self, t: float) -> np.ndarray:
        theta = self._true_anomaly(t)
        r = self.orbital_radius(t)
        pos = self.host_center.copy()
        pos[0] += r * np.cos(theta)
        if self._dim >= 2:
            pos[1] += r * np.sin(theta)
        return pos

    def spin_angle(self, t: float) -> float:
        return self.spin_frequency * t

    def velocity(self, t: float, dt: float = 1e-5) -> np.ndarray:
        return (self.position(t + dt) - self.position(t - dt)) / (2.0 * dt)

    def potential(self, x: np.ndarray, t: float) -> float:
        dx = x - self.position(t)
        r = np.linalg.norm(dx) + self.softening
        V = -self.G * self.mass / r

        if abs(self.quadrupole_moment) > 1e-15 and self._dim >= 2:
            spin_ang = self.spin_angle(t)
            cos_a = np.cos(spin_ang)
            sin_a = np.sin(spin_ang)
            dx_rot = dx[0] * cos_a + dx[1] * sin_a if self._dim >= 2 else dx[0]
            P2 = (3.0 * (dx_rot / r) ** 2 - 1.0) / 2.0
            V += -self.G * self.mass * self.quadrupole_moment * P2 / (r ** 3)

        return V

    def gravity(self, x: np.ndarray, t: float) -> np.ndarray:
        x = np.asarray(x, dtype=float)
        eps = 1e-6
        dim = len(x)
        grad = np.zeros(dim)
        for i in range(dim):
            xp = x.copy(); xp[i] += eps
            xm = x.copy(); xm[i] -= eps
            grad[i] = (self.potential(xp, t) - self.potential(xm, t)) / (2.0 * eps)
        return -grad

    def tidal_tensor(self, x: np.ndarray, t: float) -> np.ndarray:
        """T_ij = -∂²V/∂x_i∂x_j. trace=0 (진공)."""
        x = np.asarray(x, dtype=float)
        dim = len(x)
        eps = 1e-5
        T = np.zeros((dim, dim))
        for i in range(dim):
            for j in range(dim):
                xpp = x.copy(); xpp[i] += eps; xpp[j] += eps
                xpm = x.copy(); xpm[i] += eps; xpm[j] -= eps
                xmp = x.copy(); xmp[i] -= eps; xmp[j] += eps
                xmm = x.copy(); xmm[i] -= eps; xmm[j] -= eps
                T[i, j] = -(
                    self.potential(xpp, t) - self.potential(xpm, t)
                    - self.potential(xmp, t) + self.potential(xmm, t)
                ) / (4.0 * eps**2)
        return T

    def info(self, t: float = 0.0) -> Dict:
        return {
            "position": self.position(t).tolist(),
            "orbital_radius": self.orbital_radius(t),
            "spin_angle": self.spin_angle(t),
            "velocity": self.velocity(t).tolist(),
            "eccentricity": self.eccentricity,
            "tidal_locking": self.tidal_locking,
        }
