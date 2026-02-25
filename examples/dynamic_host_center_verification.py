#!/usr/bin/env python3
"""동적 host_center 검증 — 달 공전 중심이 지구 위치를 따라가는지

v0.7.2: OrbitalMoon.host_center가 Callable이면 매번 동적으로 위치를 가져온다.
        지구(상태점)가 이동하면 달의 공전 중심도 자동으로 따라간다.

검증 항목:
  1. 하위 호환: 고정 배열 host_center가 동일하게 동작
  2. 동적 콜백: Callable host_center가 매번 새 위치 반환
  3. 추적 정확성: 지구가 원운동 → 달이 지구를 따라 공전
  4. 조석 방향: 이동 중에도 조석 텐서가 올바르게 계산

Author: GNJz (Qquarts)
Version: 0.7.2
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
from solar import CentralBody, OrbitalMoon, TidalField

PASS = "\033[92mPASS\033[0m"
FAIL = "\033[91mFAIL\033[0m"
results = []


def check(name: str, condition: bool, detail: str = ""):
    tag = PASS if condition else FAIL
    results.append(condition)
    print(f"  [{tag}] {name}")
    if detail:
        print(f"         {detail}")


print("=" * 65)
print("동적 host_center 검증 (v0.7.2)")
print("=" * 65)
print()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# [1] 하위 호환: 고정 배열
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("[1] 하위 호환 — 고정 배열 host_center")

moon_fixed = OrbitalMoon(
    host_center=np.array([5.0, 0.0]),
    semi_major_axis=1.0,
    orbit_frequency=2.0,
    mass=0.3,
)

pos_0 = moon_fixed.position(0.0)
pos_1 = moon_fixed.position(1.0)
center = moon_fixed._get_host_center()

check("고정 host_center", np.allclose(center, [5.0, 0.0]),
      f"center = {center}")
check("position(0) 계산", np.linalg.norm(pos_0 - np.array([5.0, 0.0])) <= 1.0 + 0.01,
      f"pos(0) = [{pos_0[0]:.4f}, {pos_0[1]:.4f}]")
check("host_dynamic = False", not moon_fixed._host_func,
      "info: host_dynamic = False")
print()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# [2] 동적 콜백 기본
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("[2] 동적 콜백 — Callable host_center")

earth_pos = np.array([10.0, 0.0])


def get_earth_pos():
    return earth_pos.copy()


moon_dynamic = OrbitalMoon(
    host_center=get_earth_pos,
    semi_major_axis=1.0,
    orbit_frequency=2.0,
    mass=0.3,
)

pos_at_10 = moon_dynamic.position(0.0)
check("동적 center = [10, 0]", np.allclose(moon_dynamic._get_host_center(), [10.0, 0.0]),
      f"center = {moon_dynamic._get_host_center()}")
check("position이 [10, 0] 근처", abs(pos_at_10[0] - 10.0) <= 1.1,
      f"pos = [{pos_at_10[0]:.4f}, {pos_at_10[1]:.4f}]")

# 지구 이동
earth_pos[:] = [20.0, 5.0]
pos_at_20 = moon_dynamic.position(0.0)
check("지구 이동 후 center 추적", np.allclose(moon_dynamic._get_host_center(), [20.0, 5.0]),
      f"center = {moon_dynamic._get_host_center()}")
check("position이 [20, 5] 근처", abs(pos_at_20[0] - 20.0) <= 1.1,
      f"pos = [{pos_at_20[0]:.4f}, {pos_at_20[1]:.4f}]")
check("host_dynamic = True", moon_dynamic._host_func is not None,
      "info: host_dynamic = True")
print()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# [3] 추적 시뮬레이션: 지구 원운동 + 달 공전
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("[3] 추적 시뮬레이션 — 지구가 원운동, 달이 따라 공전")

R_earth_orbit = 50.0
omega_earth = 0.1
earth_sim = np.array([R_earth_orbit, 0.0])


def get_earth_sim():
    return earth_sim.copy()


moon_tracking = OrbitalMoon(
    host_center=get_earth_sim,
    semi_major_axis=2.0,
    eccentricity=0.0,
    orbit_frequency=1.0,
    mass=0.5,
)

tidal_tracking = TidalField(
    central=CentralBody(position=np.array([0.0, 0.0]), mass=100.0),
    moons=[moon_tracking],
)

dt = 0.1
n_steps = 200
moon_positions = []
earth_positions = []

for i in range(n_steps):
    t = i * dt
    earth_sim[0] = R_earth_orbit * np.cos(omega_earth * t)
    earth_sim[1] = R_earth_orbit * np.sin(omega_earth * t)

    moon_pos = moon_tracking.position(t)
    moon_positions.append(moon_pos.copy())
    earth_positions.append(earth_sim.copy())

moon_positions = np.array(moon_positions)
earth_positions = np.array(earth_positions)

# 달-지구 거리가 항상 semi_major_axis 근처인지 확인
distances = np.linalg.norm(moon_positions - earth_positions, axis=1)
mean_dist = np.mean(distances)
max_dev = np.max(np.abs(distances - 2.0))

print(f"  달-지구 평균 거리: {mean_dist:.4f} (이론: 2.0)")
print(f"  최대 편차: {max_dev:.6f}")

check("달-지구 거리 ≈ semi_major_axis", abs(mean_dist - 2.0) < 0.1,
      f"평균 = {mean_dist:.4f}")
check("거리 편차 작음", max_dev < 0.1,
      f"최대 편차 = {max_dev:.6f}")

# 달이 지구를 따라 이동하는지 (달 궤적의 중심이 지구 궤적과 일치)
moon_mean = np.mean(moon_positions, axis=0)
earth_mean = np.mean(earth_positions, axis=0)
center_diff = np.linalg.norm(moon_mean - earth_mean)
check("달 궤적 중심 ≈ 지구 궤적 중심", center_diff < 5.0,
      f"차이 = {center_diff:.4f}")
print()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# [4] 조석 방향 — 이동 중에도 정확한지
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("[4] 조석 텐서 — 이동 중 정확성")

# t=0: 지구=[50,0], 달=[52,0] (오른쪽)
earth_sim[:] = [R_earth_orbit, 0.0]
t_check = 0.0
moon_pos_now = moon_tracking.position(t_check)
print(f"  지구: {earth_sim}")
print(f"  달:   [{moon_pos_now[0]:.2f}, {moon_pos_now[1]:.2f}]")

T = moon_tracking.tidal_tensor(earth_sim, t_check)
eigs = np.linalg.eigvalsh(T)
trace = np.trace(T)

print(f"  조석 텐서 trace: {trace:.6e}")
print(f"  고유값: {eigs}")

check("trace ≈ 0 (라플라시안)", abs(trace) < 0.1,
      f"trace = {trace:.6e}")
check("고유값 부호 반대 (신장↔압축)",
      (eigs[0] < 0 and eigs[1] > 0) or (eigs[0] > 0 and eigs[1] < 0),
      f"고유값 = [{eigs[0]:.6f}, {eigs[1]:.6f}]")

# t=π: 지구가 반대편에 갔을 때도 조석이 작동
t_pi = np.pi / omega_earth
earth_sim[0] = R_earth_orbit * np.cos(omega_earth * t_pi)
earth_sim[1] = R_earth_orbit * np.sin(omega_earth * t_pi)
moon_pos_pi = moon_tracking.position(t_pi)
T_pi = moon_tracking.tidal_tensor(earth_sim, t_pi)
trace_pi = np.trace(T_pi)

print(f"  t=π 지구: [{earth_sim[0]:.2f}, {earth_sim[1]:.2f}]")
print(f"  t=π 달:   [{moon_pos_pi[0]:.2f}, {moon_pos_pi[1]:.2f}]")
print(f"  t=π trace: {trace_pi:.6e}")

check("t=π에서도 trace ≈ 0", abs(trace_pi) < 0.1,
      f"trace = {trace_pi:.6e}")
check("t=π에서 조석력 크기 유지",
      np.max(np.abs(np.linalg.eigvalsh(T_pi))) > 0.001,
      f"|T| = {np.max(np.abs(np.linalg.eigvalsh(T_pi))):.6f}")
print()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 최종
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
n_pass = sum(results)
n_total = len(results)
print("=" * 65)
print(f"결과: {n_pass}/{n_total} PASS")
if n_pass == n_total:
    print("전체 PASS — 동적 host_center 추적 확인")
else:
    print(f"FAIL 항목: {n_total - n_pass}개")
print("=" * 65)
