#!/usr/bin/env python3
"""3계층 중력 동역학 검증 — 태양 · 지구(우물) · 달(조석)

4단계 실험:
  1. 순수 공전: 중심 1/r 퍼텐셜에서 원궤도 (γ=0, σ=0)
  2. 감쇠 + 코리올리: γ>0 일 때 ωJv가 궤도를 유지하는가
  3. 달 조석: 우물 안에서 타원 유속 흐름이 나오는가
  4. 전체 합성: 태양 + 우물 + 달 + 코리올리

Author: GNJz (Qquarts)
Version: 0.7.0
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
from trunk.Phase_A.tidal import CentralBody, OrbitalMoon, TidalField
from trunk.Phase_A.rotational_field import create_skew_symmetric_matrix

PASS = "\033[92mPASS\033[0m"
FAIL = "\033[91mFAIL\033[0m"
results = []


def check(name: str, condition: bool, detail: str = ""):
    status = PASS if condition else FAIL
    results.append(condition)
    print(f"  [{status}] {name}" + (f"  ({detail})" if detail else ""))


def leapfrog_step(x, v, dt, force_func, mass=1.0):
    """Symplectic leapfrog (Verlet) integrator"""
    a = force_func(x) / mass
    v_half = v + 0.5 * dt * a
    x_new = x + dt * v_half
    a_new = force_func(x_new) / mass
    v_new = v_half + 0.5 * dt * a_new
    return x_new, v_new


def simulate(x0, v0, force_func, dt, n_steps, mass=1.0):
    """궤적 시뮬레이션 (leapfrog)"""
    dim = len(x0)
    xs = np.zeros((n_steps, dim))
    vs = np.zeros((n_steps, dim))
    x, v = x0.copy(), v0.copy()
    for i in range(n_steps):
        x, v = leapfrog_step(x, v, dt, force_func, mass)
        xs[i] = x
        vs[i] = v
    return xs, vs


def simulate_tidal(x0, v0, tidal: TidalField, dt, n_steps, mass=1.0,
                   gamma=0.0, omega=0.0, well_field=None):
    """시간 의존 힘 포함 시뮬레이션 (Euler-Maruyama)"""
    dim = len(x0)
    xs = np.zeros((n_steps, dim))
    vs = np.zeros((n_steps, dim))
    x, v = x0.copy(), v0.copy()

    J = create_skew_symmetric_matrix(dim, axis=[0, 1]) if dim >= 2 else np.zeros((dim, dim))

    for i in range(n_steps):
        t = i * dt
        f = tidal.force(x, t)
        if well_field is not None:
            f = f + well_field(x)
        f = f + omega * (J @ v)
        f = f - gamma * v

        a = f / mass
        v = v + dt * a
        x = x + dt * v
        xs[i] = x
        vs[i] = v
    return xs, vs


# =====================================================================
print("=" * 60)
print("3계층 중력 동역학 검증")
print("=" * 60)


# ----- 실험 1: 순수 공전 (2D, 감쇠 없음) -----
print("\n[실험 1] 순수 공전 — 중심 1/r 퍼텐셜, γ=0")

sun = CentralBody(position=np.array([0.0, 0.0]), mass=10.0, G=1.0)
r0 = 5.0
v_circ = sun.circular_speed(r0)

x0 = np.array([r0, 0.0])
v0 = np.array([0.0, v_circ])

xs, vs = simulate(
    x0, v0,
    force_func=sun.field,
    dt=0.001, n_steps=50000, mass=1.0,
)

radii = np.sqrt(xs[:, 0]**2 + xs[:, 1]**2)
r_mean = np.mean(radii)
r_std = np.std(radii)
r_variation = r_std / r_mean

energies = 0.5 * np.sum(vs**2, axis=1) + np.array([sun.potential(x) for x in xs])
e_drift = abs(energies[-1] - energies[0]) / (abs(energies[0]) + 1e-15)

check("원궤도 반경 안정", r_variation < 0.02,
      f"r={r_mean:.3f}±{r_std:.4f}, 변동={r_variation:.4f}")
check("에너지 보존", e_drift < 0.01,
      f"drift={e_drift:.6f}")


# ----- 실험 2: 감쇠 + 코리올리 -----
print("\n[실험 2] 감쇠 + 코리올리 — γ=0.01, ω=1.0")

tidal_sun = TidalField(central=sun)

xs2, vs2 = simulate_tidal(
    x0, v0, tidal_sun,
    dt=0.001, n_steps=50000, mass=1.0,
    gamma=0.01, omega=1.0,
)

radii2 = np.sqrt(xs2[:, 0]**2 + xs2[:, 1]**2)
r_final = np.mean(radii2[-5000:])
r_init = np.mean(radii2[:5000])
decay_ratio = r_final / r_init

still_orbiting = r_final > 1.0
check("궤도 유지 (완전 붕괴 아님)", still_orbiting,
      f"r_init={r_init:.2f} → r_final={r_final:.2f}, ratio={decay_ratio:.3f}")

is_spiraling = decay_ratio < 1.0
check("나선 낙하 (감쇠 효과 확인)", is_spiraling,
      f"decay_ratio={decay_ratio:.3f}")


# ----- 실험 3: 달 조석 — 우물 안 타원 유속 -----
print("\n[실험 3] 달 조석 — 우물 안에서 타원 유속 흐름")

well_center = np.array([5.0, 0.0])
moon = OrbitalMoon(
    host_center=well_center,
    orbit_radius=1.5,
    orbit_frequency=3.0,
    mass=0.3,
)

sigma_well = 2.0
A_well = 3.0

def well_field_func(x):
    dx = x - well_center
    r2 = np.dot(dx, dx)
    return -A_well * dx / (sigma_well**2) * np.exp(-r2 / (2 * sigma_well**2))

tidal_moon = TidalField(moons=[moon])

x0_well = well_center + np.array([0.3, 0.0])
v0_well = np.array([0.0, 0.2])

xs3, vs3 = simulate_tidal(
    x0_well, v0_well, tidal_moon,
    dt=0.001, n_steps=30000, mass=1.0,
    gamma=0.05, omega=0.5, well_field=well_field_func,
)

offsets = xs3 - well_center
dist_from_center = np.sqrt(offsets[:, 0]**2 + offsets[:, 1]**2)
not_collapsed = np.mean(dist_from_center[-5000:]) > 0.05
check("바닥 고착 방지 (달 조석 효과)", not_collapsed,
      f"평균 offset={np.mean(dist_from_center[-5000:]):.4f}")

angles = np.arctan2(offsets[-10000:, 1], offsets[-10000:, 0])
angle_diffs = np.diff(np.unwrap(angles))
has_circulation = np.abs(np.mean(angle_diffs)) > 1e-5
check("타원 유속 순환 존재", has_circulation,
      f"평균 각속도={np.mean(angle_diffs)/0.001:.4f} rad/s")


# ----- 실험 4: 전체 합성 — 태양 + 우물 + 달 + 코리올리 -----
print("\n[실험 4] 전체 합성 — 태양 + 우물(지구) + 달 + 코리올리")

sun4 = CentralBody(position=np.array([0.0, 0.0]), mass=10.0)
moon4 = OrbitalMoon(
    host_center=np.array([5.0, 0.0]),
    orbit_radius=1.0,
    orbit_frequency=3.0,
    mass=0.15,
)

tidal_full = TidalField(central=sun4, moons=[moon4])

A_well4 = 8.0
sigma_well4 = 2.5
well_center4 = np.array([5.0, 0.0])

def well_field_func4(x):
    dx = x - well_center4
    r2 = np.dot(dx, dx)
    return -A_well4 * dx / (sigma_well4**2) * np.exp(-r2 / (2 * sigma_well4**2))

x0_4 = np.array([5.2, 0.0])
v0_4 = np.array([0.0, 0.3])

xs4, vs4 = simulate_tidal(
    x0_4, v0_4, tidal_full,
    dt=0.001, n_steps=50000, mass=1.0,
    gamma=0.05, omega=0.5, well_field=well_field_func4,
)

radii4 = np.sqrt(xs4[:, 0]**2 + xs4[:, 1]**2)
not_escaped = np.all(radii4 < 30.0)
not_collapsed_to_sun = np.mean(radii4[-5000:]) > 0.5
check("태양에 붕괴하지 않음", not_collapsed_to_sun,
      f"최종 평균 r={np.mean(radii4[-5000:]):.3f}")
check("시스템에서 탈출하지 않음", not_escaped,
      f"최대 r={np.max(radii4):.3f}")

offsets4 = xs4 - well_center4
dist4 = np.sqrt(offsets4[:, 0]**2 + offsets4[:, 1]**2)
stays_near_well = np.mean(dist4[-10000:]) < 8.0
check("우물(지구) 근처에 머무름", stays_near_well,
      f"최종 평균 우물 거리={np.mean(dist4[-10000:]):.3f}")

# ----- TidalField API 검증 -----
print("\n[API 검증]")

info = tidal_full.info()
check("info() 정상", info["has_central"] and info["n_moons"] == 1)

inj_func = tidal_full.create_injection_func()
test_force = inj_func(np.array([5.0, 0.0]), np.array([0.0, 1.0]), 0.0)
check("create_injection_func() 정상", len(test_force) == 2)

v_esc = sun4.escape_speed(5.0)
check("circular < escape", sun4.circular_speed(5.0) < v_esc,
      f"v_circ={sun4.circular_speed(5.0):.3f}, v_esc={v_esc:.3f}")


# =====================================================================
print("\n" + "=" * 60)
passed = sum(results)
total = len(results)
print(f"결과: {passed}/{total} PASS")
if passed == total:
    print("전체 PASS")
else:
    print(f"{total - passed}개 실패")
print("=" * 60)
