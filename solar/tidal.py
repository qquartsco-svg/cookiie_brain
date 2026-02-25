"""3계층 중력 동역학 — 태양 · 지구(바다) · 달(공전+자전+조석)

Tier 1: CentralBody      — 1/r 중심 퍼텐셜 (장거리, 태양)
Tier 2: GaussianWell      — 국소 우물 (지구/바다) [hippo/memory_store.py]
Tier 3: OrbitalMoon       — 타원 공전 + 자전 + 조석력
TidalField                — 중심장 + 조석장 합성 + 조석 텐서
OceanSimulator            — 바다 내 다중 tracer 입자 시뮬레이션 (대류/난류/유속)

수식:
  V_sun(r)     = -G·M / (r + ε)                        장거리 중력
  x_moon(t)    = c + r(θ)·[cos θ, sin θ]               타원 공전 (Kepler)
  r(θ)         = a(1-e²) / (1 + e·cos(θ-ω_p))          타원 반경
  V_moon(x,t)  = -G_m·M_m / (‖x-x_moon(t)‖ + ε)       달 중력
  T_ij         = ∂²V_moon / ∂x_i∂x_j                   조석 텐서
  F_tidal      = T · (x - x_host)                       조석력 (차등 중력)

Author: GNJz (Qquarts)
Version: 0.7.1
"""

from __future__ import annotations
import numpy as np
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Tuple


# =====================================================================
#  Tier 1: CentralBody (태양)
# =====================================================================

@dataclass
class CentralBody:
    """1/r 중심 퍼텐셜 — 전체 시스템을 묶는 장거리 힘.

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


# =====================================================================
#  Tier 3: OrbitalMoon (달 — 타원 공전 + 자전 + 조석)
# =====================================================================

@dataclass
class OrbitalMoon:
    """타원 궤도 공전 + 자전하는 달.

    공전 (orbit):
      타원 궤도 — Kepler의 면적속도 일정 법칙 적용.
      r(θ) = a(1-e²) / (1 + e·cos(θ - ω_peri))
      eccentricity=0 → 원궤도 (v0.7.0 호환)

    자전 (spin):
      spin_frequency: 달 자체의 회전 각속도
      tidal_locking=True 이면 spin = orbit (동기 자전)
      달의 비구형 질량 분포를 quadrupole_moment로 모델링

    조석 (tidal):
      gravity()가 반환하는 힘의 공간 기울기가 조석을 만듦.
      tidal_tensor()로 정량적 조석 텐서 계산.
    """
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
        """하위 호환: semi_major_axis를 orbit_radius로도 접근"""
        return self.semi_major_axis

    def _true_anomaly(self, t: float) -> float:
        """평균 이각 → 진근점 이각 (Kepler 방정식 근사)"""
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
        """시각 t에서의 궤도 반경 r(θ)"""
        theta = self._true_anomaly(t)
        e = self.eccentricity
        a = self.semi_major_axis
        if e < 1e-8:
            return a
        return a * (1 - e**2) / (1 + e * np.cos(theta - self.periapsis_angle))

    def position(self, t: float) -> np.ndarray:
        """시각 t에서의 달 위치 (타원 궤도)"""
        theta = self._true_anomaly(t)
        r = self.orbital_radius(t)
        pos = self.host_center.copy()
        pos[0] += r * np.cos(theta)
        if self._dim >= 2:
            pos[1] += r * np.sin(theta)
        return pos

    def spin_angle(self, t: float) -> float:
        """시각 t에서의 달 자전각"""
        return self.spin_frequency * t

    def velocity(self, t: float, dt: float = 1e-5) -> np.ndarray:
        """수치 미분으로 달의 궤도 속도"""
        return (self.position(t + dt) - self.position(t - dt)) / (2.0 * dt)

    def potential(self, x: np.ndarray, t: float) -> float:
        """점질량 + 사극자(quadrupole) 퍼텐셜"""
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
        """달 중력 (수치 기울기)"""
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
        """조석 텐서 T_ij = -∂²V/∂x_i∂x_j

        이 텐서의 고유값이 조석 신장/압축 방향을 결정한다.
        trace(T) = 0 (진공에서 라플라시안 = 0).
        """
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


# =====================================================================
#  TidalField (합성)
# =====================================================================

class TidalField:
    """3계층 중력 합성: 중심장 + 조석장 + 조석 텐서.

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
        """전체 조석 텐서 (모든 달의 합)"""
        x = np.asarray(x, dtype=float)
        dim = len(x)
        T = np.zeros((dim, dim))
        for moon in self.moons:
            T += moon.tidal_tensor(x, t)
        return T

    def tidal_eigenvalues(self, x: np.ndarray, t: float) -> np.ndarray:
        """조석 텐서의 고유값 — 신장/압축 세기"""
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


# =====================================================================
#  OceanSimulator — 바다(우물) 안의 대류/유속 시뮬레이션
# =====================================================================

class OceanSimulator:
    """우물(지구/바다) 안에 다중 tracer 입자를 놓고
    태양+달+코리올리+감쇠+요동의 합력으로 유속 패턴을 생성한다.

    결과:
      positions: (n_steps, n_tracers, dim) — 대류/유속 궤적
      velocities: (n_steps, n_tracers, dim)
      vorticity: 각 timestep의 평균 와도 (2D 회전 성분)
    """

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
        """바다 시뮬레이션 실행.

        Returns:
            positions: (n_steps, n_tracers, dim)
            velocities: (n_steps, n_tracers, dim)
            mean_vorticity: (n_steps,)
            mean_speed: (n_steps,)
            tidal_strength: (n_steps,) — 조석 텐서 최대 고유값
        """
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
