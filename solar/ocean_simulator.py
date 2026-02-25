"""바다 시뮬레이터 — 우물 안의 유속/대류/와도 패턴

우물(지구) 안에 여러 tracer 입자를 놓고,
태양+달+코리올리+감쇠+요동의 합력으로 움직여서
대류, 난류, 유속 패턴을 관찰한다.

Author: GNJz (Qquarts)
"""

from __future__ import annotations
import numpy as np
from typing import Dict, Optional

from .tidal_field import TidalField


class OceanSimulator:
    """우물 안 다중 tracer 시뮬레이션."""

    def __init__(
        self,
        well_center: np.ndarray,
        well_amplitude: float = 5.0,
        well_sigma: float = 2.0,
        tidal_field: Optional[TidalField] = None,
        gamma: float = 0.05,
        omega: float = 0.5,
        noise_sigma: float = 0.0,
        mass: float = 1.0,
        rng_seed: Optional[int] = None,
    ):
        self.well_center = np.asarray(well_center, dtype=float)
        self.well_amplitude = well_amplitude
        self.well_sigma = well_sigma
        self.tidal = tidal_field
        self.gamma = gamma
        self.omega = omega
        self.noise_sigma = noise_sigma
        self.mass = mass
        self._rng = np.random.default_rng(rng_seed)
        self._dim = len(self.well_center)
        self._J = np.zeros((self._dim, self._dim))
        if self._dim >= 2:
            self._J[0, 1] = -1.0
            self._J[1, 0] = 1.0

    def _well_force(self, x: np.ndarray) -> np.ndarray:
        dx = x - self.well_center
        r2 = np.dot(dx, dx)
        return -self.well_amplitude * dx / (self.well_sigma**2) * np.exp(
            -r2 / (2 * self.well_sigma**2)
        )

    def run(
        self,
        n_tracers: int = 20,
        n_steps: int = 10000,
        dt: float = 0.005,
        init_radius: float = 0.5,
    ) -> Dict:
        dim = self._dim
        positions = np.zeros((n_steps, n_tracers, dim))
        velocities = np.zeros((n_steps, n_tracers, dim))
        vorticity = np.zeros(n_steps)
        mean_speed = np.zeros(n_steps)
        tidal_strength = np.zeros(n_steps)

        angles = np.linspace(0, 2 * np.pi, n_tracers, endpoint=False)
        xs = np.zeros((n_tracers, dim))
        vs = np.zeros((n_tracers, dim))
        for k in range(n_tracers):
            xs[k] = self.well_center.copy()
            xs[k][0] += init_radius * np.cos(angles[k])
            if dim >= 2:
                xs[k][1] += init_radius * np.sin(angles[k])

        for i in range(n_steps):
            t = i * dt
            for k in range(n_tracers):
                f = self._well_force(xs[k])
                if self.tidal is not None:
                    f = f + self.tidal.force(xs[k], t)
                f = f + self.omega * (self._J @ vs[k])
                f = f - self.gamma * vs[k]
                if self.noise_sigma > 0:
                    f = f + self.noise_sigma * self._rng.standard_normal(dim)

                a = f / self.mass
                vs[k] = vs[k] + dt * a
                xs[k] = xs[k] + dt * vs[k]

            positions[i] = xs.copy()
            velocities[i] = vs.copy()
            mean_speed[i] = np.mean(np.linalg.norm(vs, axis=1))

            if dim >= 2:
                offsets = xs - self.well_center
                cross = offsets[:, 0] * vs[:, 1] - offsets[:, 1] * vs[:, 0]
                r2 = np.sum(offsets**2, axis=1) + 1e-15
                vorticity[i] = np.mean(cross / r2)

            if self.tidal is not None and len(self.tidal.moons) > 0:
                eigs = self.tidal.tidal_eigenvalues(self.well_center, t)
                tidal_strength[i] = np.max(np.abs(eigs))

        return {
            "positions": positions,
            "velocities": velocities,
            "mean_vorticity": vorticity,
            "mean_speed": mean_speed,
            "tidal_strength": tidal_strength,
            "n_tracers": n_tracers,
            "n_steps": n_steps,
            "dt": dt,
        }
