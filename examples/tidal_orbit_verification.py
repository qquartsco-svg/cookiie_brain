#!/usr/bin/env python3
"""3계층 중력 동역학 검증 v0.7.1 — 태양 · 지구(바다) · 달(공전+자전+조석)

7개 실험:
  1. 순수 원궤도: 1/r 중심 퍼텐셜 (에너지 보존)
  2. 타원 궤도: 이심률 e=0.3 (Kepler 면적속도)
  3. 달 자전 + 사극자: quadrupole 효과 확인
  4. 조석 텐서: trace=0 (라플라시안), 신장/압축 직교
  5. 달 조석 → 우물 내 타원 유속 (바닥 고착 방지)
  6. 바다 시뮬레이션: 20 tracer 대류/유속 패턴
  7. 전체 합성: 태양 + 우물 + 달(타원+자전) + 코리올리

Author: GNJz (Qquarts)
Version: 0.7.1
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
from L0_solar import CentralBody, OrbitalMoon, TidalField
from L4_analysis.ocean_simulator import OceanSimulator
from L1_dynamics.Phase_A.rotational_field import create_skew_symmetric_matrix

PASS = "\033[92mPASS\033[0m"
FAIL = "\033[91mFAIL\033[0m"
results = []


def check(name: str, condition: bool, detail: str = ""):
    status = PASS if condition else FAIL
    results.append(condition)
    print(f"  [{status}] {name}" + (f"  ({detail})" if detail else ""))


def leapfrog(x, v, dt, force_func, mass=1.0):
    a = force_func(x) / mass
    v_half = v + 0.5 * dt * a
    x_new = x + dt * v_half
    a_new = force_func(x_new) / mass
    v_new = v_half + 0.5 * dt * a_new
    return x_new, v_new


def simulate(x0, v0, force_func, dt, n_steps, mass=1.0):
    dim = len(x0)
    xs = np.zeros((n_steps, dim))
    vs = np.zeros((n_steps, dim))
    x, v = x0.copy(), v0.copy()
    for i in range(n_steps):
        x, v = leapfrog(x, v, dt, force_func, mass)
        xs[i] = x
        vs[i] = v
    return xs, vs


def simulate_tidal(x0, v0, tidal, dt, n_steps, mass=1.0,
                   gamma=0.0, omega=0.0, well_field=None):
    dim = len(x0)
    xs = np.zeros((n_steps, dim))
    vs = np.zeros((n_steps, dim))
    x, v = x0.copy(), v0.copy()
    J = create_skew_symmetric_matrix(dim) if dim >= 2 else np.zeros((dim, dim))
    for i in range(n_steps):
        t = i * dt
        f = tidal.force(x, t)
        if well_field is not None:
            f = f + well_field(x)
        f = f + omega * (J @ v) - gamma * v
        v = v + dt * f / mass
        x = x + dt * v
        xs[i] = x
        vs[i] = v
    return xs, vs


# =====================================================================
print("=" * 65)
print("3계층 중력 동역학 검증 v0.7.1")
print("  태양(1/r) · 지구(우물/바다) · 달(타원공전+자전+조석)")
print("=" * 65)


# ----- 실험 1: 순수 원궤도 -----
print("\n[1] 순수 원궤도 — 1/r 중심 퍼텐셜, γ=0")
sun = CentralBody(position=np.array([0.0, 0.0]), mass=10.0)
r0 = 5.0
v_circ = sun.circular_speed(r0)
xs, vs = simulate(
    np.array([r0, 0.0]), np.array([0.0, v_circ]),
    sun.field, dt=0.001, n_steps=50000,
)
radii = np.sqrt(xs[:, 0]**2 + xs[:, 1]**2)
r_var = np.std(radii) / np.mean(radii)
E = 0.5 * np.sum(vs**2, axis=1) + np.array([sun.potential(x) for x in xs])
e_drift = abs(E[-1] - E[0]) / (abs(E[0]) + 1e-15)
check("원궤도 반경 안정", r_var < 0.01, f"변동={r_var:.6f}")
check("에너지 보존", e_drift < 0.001, f"drift={e_drift:.8f}")


# ----- 실험 2: 타원 궤도 (Kepler) -----
print("\n[2] 타원 궤도 — e=0.3, 면적속도 일정")
moon_ellip = OrbitalMoon(
    host_center=np.array([0.0, 0.0]),
    semi_major_axis=5.0,
    eccentricity=0.3,
    orbit_frequency=1.0,
)
positions_moon = []
for i in range(1000):
    t = i * 0.00628
    positions_moon.append(moon_ellip.position(t))
positions_moon = np.array(positions_moon)
r_moon = np.sqrt(positions_moon[:, 0]**2 + positions_moon[:, 1]**2)
r_min, r_max = np.min(r_moon), np.max(r_moon)
expected_rmin = 5.0 * (1 - 0.3)
expected_rmax = 5.0 * (1 + 0.3)
check("근일점 정확", abs(r_min - expected_rmin) / expected_rmin < 0.15,
      f"r_min={r_min:.2f}, 이론={expected_rmin:.2f}")
check("원일점 정확", abs(r_max - expected_rmax) / expected_rmax < 0.15,
      f"r_max={r_max:.2f}, 이론={expected_rmax:.2f}")


# ----- 실험 3: 달 자전 + 사극자 -----
print("\n[3] 달 자전 + 사극자 — 비구형 질량 효과")
moon_spin = OrbitalMoon(
    host_center=np.array([0.0, 0.0]),
    semi_major_axis=3.0,
    orbit_frequency=1.0,
    mass=1.0,
    tidal_locking=True,
    quadrupole_moment=0.1,
)
check("동기 자전", moon_spin.spin_frequency == moon_spin.orbit_frequency,
      f"spin={moon_spin.spin_frequency}, orbit={moon_spin.orbit_frequency}")

V_q0 = moon_spin.potential(np.array([5.0, 0.0]), t=0.0)
V_q1 = moon_spin.potential(np.array([5.0, 0.0]), t=np.pi / moon_spin.orbit_frequency)
check("사극자: 시간에 따른 퍼텐셜 변화", abs(V_q0 - V_q1) > 1e-6,
      f"ΔV={abs(V_q0 - V_q1):.6f}")


# ----- 실험 4: 조석 텐서 -----
print("\n[4] 조석 텐서 — trace=0, 신장/압축 직교")
moon_tid = OrbitalMoon(
    host_center=np.array([0.0, 0.0]),
    semi_major_axis=5.0,
    orbit_frequency=1.0,
    mass=1.0,
    quadrupole_moment=0.0,
)
T = moon_tid.tidal_tensor(np.array([2.0, 0.0]), t=0.0)
trace = np.trace(T)
check("trace(T) ≈ 0 (라플라시안)", abs(trace) < 0.1,
      f"trace={trace:.6f}")

eigs = np.linalg.eigvalsh(T)
check("고유값 부호 반대 (신장↔압축)", eigs[0] * eigs[-1] < 0,
      f"고유값={eigs}")


# ----- 실험 5: 달 조석 → 우물 내 타원 유속 -----
print("\n[5] 달 조석 → 우물 내 타원 유속 (바닥 고착 방지)")
well_center = np.array([5.0, 0.0])
A_well, sigma_well = 5.0, 2.0

def well_field(x):
    dx = x - well_center
    return -A_well * dx / sigma_well**2 * np.exp(-np.dot(dx, dx) / (2 * sigma_well**2))

moon5 = OrbitalMoon(
    host_center=well_center,
    semi_major_axis=1.5,
    eccentricity=0.1,
    orbit_frequency=3.0,
    mass=0.3,
    tidal_locking=True,
)
tidal5 = TidalField(moons=[moon5])

xs5, vs5 = simulate_tidal(
    well_center + np.array([0.3, 0.0]), np.array([0.0, 0.2]),
    tidal5, dt=0.001, n_steps=30000,
    gamma=0.05, omega=0.5, well_field=well_field,
)
offsets5 = xs5 - well_center
dist5 = np.sqrt(offsets5[:, 0]**2 + offsets5[:, 1]**2)
check("바닥 고착 방지", np.mean(dist5[-5000:]) > 0.03,
      f"offset={np.mean(dist5[-5000:]):.4f}")

angles5 = np.arctan2(offsets5[-10000:, 1], offsets5[-10000:, 0])
dang5 = np.diff(np.unwrap(angles5))
check("타원 유속 순환", np.abs(np.mean(dang5)) > 1e-5,
      f"각속도={np.mean(dang5)/0.001:.4f} rad/s")


# ----- 실험 6: 바다 시뮬레이션 (OceanSimulator) -----
print("\n[6] 바다 시뮬레이션 — 20 tracer 대류/유속 패턴")
moon6 = OrbitalMoon(
    host_center=well_center,
    semi_major_axis=1.5,
    eccentricity=0.1,
    orbit_frequency=3.0,
    mass=0.3,
    tidal_locking=True,
)
tidal6 = TidalField(moons=[moon6])

ocean = OceanSimulator(
    well_center=well_center,
    well_amplitude=5.0,
    well_sigma=2.0,
    tidal_field=tidal6,
    gamma=0.05,
    omega=0.5,
    noise_sigma=0.01,
    rng_seed=42,
)
result = ocean.run(n_tracers=20, n_steps=10000, dt=0.005, init_radius=0.5)

check("tracer 궤적 생성", result["positions"].shape == (10000, 20, 2))

avg_speed = np.mean(result["mean_speed"][-3000:])
check("평균 유속 > 0 (대류 존재)", avg_speed > 0.01,
      f"avg_speed={avg_speed:.4f}")

avg_vort = np.mean(np.abs(result["mean_vorticity"][-3000:]))
check("와도 > 0 (순환 흐름)", avg_vort > 1e-4,
      f"avg_vorticity={avg_vort:.6f}")

tidal_str = np.mean(result["tidal_strength"][-3000:])
check("조석 텐서 세기 > 0", tidal_str > 0,
      f"tidal_strength={tidal_str:.6f}")


# ----- 실험 7: 전체 합성 -----
print("\n[7] 전체 합성 — 태양 + 우물(지구) + 달(타원+자전) + 코리올리")
sun7 = CentralBody(position=np.array([0.0, 0.0]), mass=10.0)
moon7 = OrbitalMoon(
    host_center=well_center,
    semi_major_axis=1.0,
    eccentricity=0.15,
    orbit_frequency=3.0,
    mass=0.15,
    tidal_locking=True,
    quadrupole_moment=0.02,
)
tidal7 = TidalField(central=sun7, moons=[moon7])

A7, sig7 = 8.0, 2.5

def well7(x):
    dx = x - well_center
    return -A7 * dx / sig7**2 * np.exp(-np.dot(dx, dx) / (2 * sig7**2))

xs7, vs7 = simulate_tidal(
    well_center + np.array([0.2, 0.0]), np.array([0.0, 0.3]),
    tidal7, dt=0.001, n_steps=50000,
    gamma=0.05, omega=0.5, well_field=well7,
)
radii7 = np.sqrt(xs7[:, 0]**2 + xs7[:, 1]**2)
check("태양 붕괴 없음", np.mean(radii7[-5000:]) > 0.5,
      f"r_final={np.mean(radii7[-5000:]):.3f}")
check("탈출 없음", np.all(radii7 < 30.0),
      f"r_max={np.max(radii7):.3f}")

offsets7 = xs7 - well_center
dist7 = np.sqrt(offsets7[:, 0]**2 + offsets7[:, 1]**2)
check("우물 근처 유지", np.mean(dist7[-10000:]) < 5.0,
      f"avg_dist={np.mean(dist7[-10000:]):.3f}")


# =====================================================================
print("\n" + "=" * 65)
passed = sum(results)
total = len(results)
print(f"결과: {passed}/{total} PASS")
if passed == total:
    print("전체 PASS")
else:
    print(f"{total - passed}개 실패")
print("=" * 65)
