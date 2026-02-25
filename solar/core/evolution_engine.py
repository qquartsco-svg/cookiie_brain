"""Evolution Engine — 3D N-body + Spin Precession + Surface Ocean
=================================================================

점 객체가 우물에 떨어지는 순간부터 세차운동까지의 전체 진화를 시뮬레이션.

Physics:
  - Symplectic leapfrog (kick-drift-kick) for N-body gravity
  - Torque-driven spin axis precession (oblate body + perturbers)
  - Surface ocean: tidal deformation (P2 Legendre) + Coriolis currents

Units:  AU, year, M_sun  →  G = 4π²
"""

import numpy as np
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Tuple


@dataclass
class Body3D:
    """3D celestial body with orbital and spin state."""
    name: str
    mass: float
    pos: np.ndarray
    vel: np.ndarray
    spin_axis: np.ndarray = field(
        default_factory=lambda: np.array([0.0, 0.0, 1.0])
    )
    spin_rate: float = 0.0          # rad/yr
    obliquity: float = 0.0          # rad
    J2: float = 0.0                 # oblateness (dimensionless)
    radius: float = 0.0            # AU
    C_MR2: float = 0.4             # C/(MR²);  0.3307 for Earth


class SurfaceOcean:
    """Wells on a body's surface — tidal deformation + Coriolis currents.

    Wells are distributed on the equatorial ring (2D cross-section).
    Tidal stretching uses the P2 Legendre pattern cos²θ.
    """

    def __init__(self, n_wells: int = 12, body_radius: float = 1.0):
        self.n_wells = n_wells
        angles = np.linspace(0, 2 * np.pi, n_wells, endpoint=False)
        self.positions = np.column_stack([
            body_radius * np.cos(angles),
            body_radius * np.sin(angles),
            np.zeros(n_wells),
        ])
        self.depths = np.full(n_wells, 0.5)
        self.widths = np.full(n_wells, 0.3)
        self.tidal_stretch = np.zeros(n_wells)
        self.current_vel = np.zeros((n_wells, 3))
        self.vorticity = np.zeros(n_wells)

    def update(
        self,
        tidal_sources: List[Tuple[np.ndarray, float]],
        spin_axis: np.ndarray,
        spin_rate: float,
        dt: float,
    ):
        # --- tidal deformation (P2 Legendre pattern) ---
        self.tidal_stretch[:] = 0.0
        for t_dir, strength in tidal_sources:
            t_hat = t_dir / (np.linalg.norm(t_dir) + 1e-30)
            for i in range(self.n_wells):
                p_hat = self.positions[i] / (
                    np.linalg.norm(self.positions[i]) + 1e-30
                )
                cos_a = np.dot(p_hat, t_hat)
                self.tidal_stretch[i] += strength * (3 * cos_a**2 - 1) / 2

        # Normalize to [-1, 1] then scale to visible amplitude
        max_s = np.max(np.abs(self.tidal_stretch))
        if max_s > 1e-15:
            self.tidal_stretch /= max_s
        self.tidal_stretch *= 0.3

        self.depths = 0.5 * (1 + self.tidal_stretch)
        self.widths = 0.3 * (1 + 0.5 * np.abs(self.tidal_stretch))

        # --- pressure-gradient driven currents ---
        MAX_CURRENT = 0.01
        for i in range(self.n_wells):
            j = (i + 1) % self.n_wells
            grad = self.depths[j] - self.depths[i]
            d = self.positions[j] - self.positions[i]
            d_hat = d / (np.linalg.norm(d) + 1e-30)
            self.current_vel[i] += 0.05 * grad * d_hat * dt
            self.current_vel[i] *= 0.98
            speed = np.linalg.norm(self.current_vel[i])
            if speed > MAX_CURRENT:
                self.current_vel[i] *= MAX_CURRENT / speed

        # --- Coriolis deflection + planetary vorticity ---
        if spin_rate > 1e-10:
            omega_eff = min(spin_rate, 0.4 / max(dt, 1e-30))
            for i in range(self.n_wells):
                v = self.current_vel[i]
                if np.linalg.norm(v) > 1e-15:
                    self.current_vel[i] -= (
                        2 * omega_eff * np.cross(spin_axis, v) * dt
                    )
                    speed = np.linalg.norm(self.current_vel[i])
                    if speed > MAX_CURRENT:
                        self.current_vel[i] *= MAX_CURRENT / speed
                p_hat = self.positions[i] / (
                    np.linalg.norm(self.positions[i]) + 1e-30
                )
                lat = np.arcsin(np.clip(np.dot(p_hat, spin_axis), -1, 1))
                self.vorticity[i] = 2 * spin_rate * np.sin(lat)


# ──────────────────────────────────────────────────────────
#  EvolutionEngine
# ──────────────────────────────────────────────────────────

class EvolutionEngine:
    """3D N-body + spin precession + surface ocean dynamics.

    Phases modelled:
      0) Birth   — point mass in central potential
      1) Ocean   — surface wells accumulate
      2) Impact  — spin + obliquity + Moon creation
      3) Tidal   — well deformation, elliptical stretching
      4) Precess — spin axis wobble from Sun+Moon torque
      5) Currents— Coriolis + tidal → ocean flow patterns
    """

    G = 4 * np.pi**2  # AU³ / (M_sun · yr²)

    def __init__(self, softening: float = 1e-8):
        self.bodies: List[Body3D] = []
        self.oceans: Dict[str, SurfaceOcean] = {}
        self.time = 0.0
        self.softening = softening

        self._pos: Optional[np.ndarray] = None
        self._vel: Optional[np.ndarray] = None
        self._masses: Optional[np.ndarray] = None
        self._N = 0
        self._dirty = True

    # ── body management ──────────────────────────────────

    def add_body(self, body: Body3D):
        self.bodies.append(body)
        self._dirty = True

    def find(self, name: str) -> Optional[Body3D]:
        for b in self.bodies:
            if b.name == name:
                return b
        return None

    def form_ocean(self, body_name: str, n_wells: int = 12):
        body = self.find(body_name)
        if body:
            self.oceans[body_name] = SurfaceOcean(n_wells, body.radius)

    def giant_impact(
        self,
        target_name: str,
        obliquity_deg: float = 23.44,
        spin_period_days: float = 1.0,
        moon_mass_frac: float = 0.0123,
        moon_distance_au: float = 0.00257,
        J2: float = 0.00108263,
        C_MR2: float = 0.3307,
    ) -> Body3D:
        """Set post-impact state: spin, obliquity, and create Moon in orbit."""
        target = self.find(target_name)
        if target is None:
            raise ValueError(f"Body '{target_name}' not found")

        obl = np.radians(obliquity_deg)
        target.spin_axis = np.array([np.sin(obl), 0.0, np.cos(obl)])
        target.spin_rate = 2 * np.pi * 365.25 / spin_period_days
        target.obliquity = obl
        target.J2 = J2
        target.C_MR2 = C_MR2

        moon_mass = moon_mass_frac * target.mass
        v_orb = np.sqrt(self.G * target.mass / moon_distance_au)

        moon = Body3D(
            name="Moon",
            mass=moon_mass,
            pos=target.pos.copy() + np.array([moon_distance_au, 0.0, 0.0]),
            vel=target.vel.copy() + np.array([0.0, v_orb, 0.0]),
            radius=target.radius * 0.2724,
        )
        self.bodies.append(moon)
        self._dirty = True
        return moon

    # ── internal array management ────────────────────────

    def _ensure_arrays(self):
        if not self._dirty and self._N == len(self.bodies):
            return
        self._N = len(self.bodies)
        self._pos = np.zeros((self._N, 3))
        self._vel = np.zeros((self._N, 3))
        self._masses = np.zeros(self._N)
        for i, b in enumerate(self.bodies):
            self._pos[i] = b.pos
            self._vel[i] = b.vel
            self._masses[i] = b.mass
        for i, b in enumerate(self.bodies):
            b.pos = self._pos[i]
            b.vel = self._vel[i]
        self._dirty = False

    def _acc(self) -> np.ndarray:
        """Vectorised gravitational acceleration for all bodies."""
        p = self._pos
        m = self._masses
        diff = p[np.newaxis, :, :] - p[:, np.newaxis, :]  # diff[i,j] = r_j - r_i
        d2 = np.sum(diff**2, axis=-1) + self.softening**2
        d = np.sqrt(d2)
        id3 = 1.0 / (d2 * d)
        np.fill_diagonal(id3, 0.0)
        return self.G * np.einsum("j,ij,ijk->ik", m, id3, diff)

    # ── integration ──────────────────────────────────────

    def step(self, dt: float, ocean: bool = True):
        """One symplectic leapfrog step + precession + ocean."""
        self._ensure_arrays()
        if self._N < 2:
            self.time += dt
            return

        # Kick-Drift-Kick leapfrog
        a1 = self._acc()
        self._vel += 0.5 * a1 * dt
        self._pos += self._vel * dt
        a2 = self._acc()
        self._vel += 0.5 * a2 * dt

        self._precess(dt)

        if ocean and self.oceans:
            self._ocean(dt)

        self.time += dt

    def _precess(self, dt: float):
        """Torque from all perturbers on oblate spinning bodies.

        τ = (3GM_j/r³)(C−A)(ŝ·r̂)(r̂×ŝ)   →   dŝ/dt = τ/(Cω)
        Sign convention: r̂×ŝ gives retrograde precession (correct for Earth).
        """
        for i, body in enumerate(self.bodies):
            if body.spin_rate < 1e-10 or body.J2 < 1e-10 or body.radius < 1e-20:
                continue

            C_minus_A = body.J2 * body.mass * body.radius**2
            L_spin = body.C_MR2 * body.mass * body.radius**2 * body.spin_rate
            if L_spin < 1e-30:
                continue

            torque = np.zeros(3)
            for j, other in enumerate(self.bodies):
                if i == j:
                    continue
                r_vec = other.pos - body.pos
                r = np.linalg.norm(r_vec)
                if r < 1e-20:
                    continue
                r_hat = r_vec / r
                dot_sr = np.dot(body.spin_axis, r_hat)
                cross_rs = np.cross(r_hat, body.spin_axis)
                torque += (
                    (3 * self.G * other.mass / r**3)
                    * C_minus_A
                    * dot_sr
                    * cross_rs
                )

            dsdt = torque / L_spin
            body.spin_axis = body.spin_axis + dsdt * dt
            n = np.linalg.norm(body.spin_axis)
            if n > 1e-30:
                body.spin_axis /= n
            body.obliquity = np.arccos(np.clip(body.spin_axis[2], -1, 1))

    def _ocean(self, dt: float):
        """Tidal deformation + Coriolis on surface wells."""
        for name, ocean in self.oceans.items():
            body = self.find(name)
            if body is None:
                continue
            sources: List[Tuple[np.ndarray, float]] = []
            for other in self.bodies:
                if other.name == name:
                    continue
                r_vec = other.pos - body.pos
                r = np.linalg.norm(r_vec)
                if r < 1e-20:
                    continue
                sources.append((r_vec / r, self.G * other.mass / r**3))
            ocean.update(sources, body.spin_axis, body.spin_rate, dt)

    # ── diagnostics ──────────────────────────────────────

    def total_energy(self) -> float:
        self._ensure_arrays()
        ke = 0.5 * np.sum(self._masses[:, None] * self._vel**2)
        pe = 0.0
        for i in range(self._N):
            for j in range(i + 1, self._N):
                r = np.linalg.norm(self._pos[j] - self._pos[i])
                pe -= (
                    self.G
                    * self._masses[i]
                    * self._masses[j]
                    / (r + self.softening)
                )
        return float(ke + pe)

    def total_angular_momentum(self) -> np.ndarray:
        self._ensure_arrays()
        L = np.zeros(3)
        for i in range(self._N):
            L += self._masses[i] * np.cross(self._pos[i], self._vel[i])
        return L

    def snapshot(self) -> dict:
        earth = self.find("Earth")
        moon = self.find("Moon")
        snap = {
            "time": self.time,
            "energy": self.total_energy(),
            "L_total": self.total_angular_momentum().copy(),
        }
        if earth:
            snap["earth_pos"] = earth.pos.copy()
            snap["earth_obliquity_deg"] = np.degrees(earth.obliquity)
            snap["earth_spin_axis"] = earth.spin_axis.copy()
        if moon and earth:
            snap["moon_distance_au"] = float(
                np.linalg.norm(moon.pos - earth.pos)
            )
        if "Earth" in self.oceans:
            oc = self.oceans["Earth"]
            snap["ocean_depths"] = oc.depths.copy()
            snap["ocean_stretch"] = oc.tidal_stretch.copy()
            snap["ocean_max_current"] = float(
                np.max(np.linalg.norm(oc.current_vel, axis=1))
            )
            snap["ocean_max_vorticity"] = float(
                np.max(np.abs(oc.vorticity))
            )
        return snap
