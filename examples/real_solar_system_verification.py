#!/usr/bin/env python3
"""실제 태양-지구-달 비율 균형 검증

실제 천문학적 질량비와 거리비를 시스템에 대입하여
물리적 균형 상태가 유지되는지 점검한다.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
실제 데이터 (NASA):
  태양 질량:     M_sun   = 1.989 × 10³⁰ kg
  지구 질량:     M_earth = 5.972 × 10²⁴ kg
  달   질량:     M_moon  = 7.342 × 10²² kg
  태양-지구 거리: R_se    = 1.496 × 10¹¹ m  (1 AU)
  지구-달 거리:   R_em    = 3.844 × 10⁸  m

무차원화 (단위계):
  거리 단위 = 지구-달 거리  (R_em = 1)
  질량 단위 = 지구 질량     (M_earth = 1)
  G = 1  (시간 단위가 이에 맞게 결정됨)

변환 결과:
  M_sun   = 332,946
  M_earth = 1.0
  M_moon  = 0.0123
  R_se    = 389.17  (지구-달 거리 단위)
  R_em    = 1.0

검증 항목:
  1. 지구 원궤도: v_circ = √(GM_sun/R_se), 에너지 보존
  2. 달 원궤도:   v_circ = √(GM_earth/R_em), 주기 비율
  3. 조석력 크기: 달 vs 태양 조석 비율 ≈ 2.17:1
  4. 3체 안정성:  태양+지구+달 동시 시뮬레이션
  5. Hill 구:     달이 지구 Hill 구 안에 있는지
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

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


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 실제 천문 데이터 (무차원화)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
M_SUN = 332_946.0       # 태양 질량 (지구=1)
M_EARTH = 1.0           # 지구 질량
M_MOON = 0.0123         # 달 질량
R_SUN_EARTH = 389.17    # 태양-지구 거리 (지구-달=1)
R_EARTH_MOON = 1.0      # 지구-달 거리
G = 1.0


def leapfrog_step(x, v, force_func, dt):
    """Symplectic leapfrog — 에너지 보존 적분기"""
    a = force_func(x)
    v_half = v + 0.5 * dt * a
    x_new = x + dt * v_half
    a_new = force_func(x_new)
    v_new = v_half + 0.5 * dt * a_new
    return x_new, v_new


print("=" * 70)
print("실제 태양-지구-달 비율 균형 검증")
print("=" * 70)
print(f"  M_sun   = {M_SUN:,.0f} (지구질량 단위)")
print(f"  M_earth = {M_EARTH}")
print(f"  M_moon  = {M_MOON}")
print(f"  R_se    = {R_SUN_EARTH} (지구-달 거리 단위)")
print(f"  R_em    = {R_EARTH_MOON}")
print()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# [1] 지구 원궤도 검증
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("[1] 지구 원궤도 — 태양 주위 케플러 운동")

sun = CentralBody(
    position=np.array([0.0, 0.0]),
    mass=M_SUN,
    G=G,
    softening=1e-6,
)

v_circ_earth = sun.circular_speed(R_SUN_EARTH)
v_escape_earth = sun.escape_speed(R_SUN_EARTH)
T_orbit_earth = 2 * np.pi * R_SUN_EARTH / v_circ_earth

print(f"  원궤도 속도:   v_circ  = {v_circ_earth:.4f}")
print(f"  탈출 속도:     v_esc   = {v_escape_earth:.4f}")
print(f"  공전 주기:     T       = {T_orbit_earth:.2f}")

x_earth = np.array([R_SUN_EARTH, 0.0])
v_earth = np.array([0.0, v_circ_earth])

E0 = 0.5 * np.dot(v_earth, v_earth) + sun.potential(x_earth)
print(f"  초기 에너지:   E₀      = {E0:.4f}")

dt = T_orbit_earth / 5000
n_steps = 5000
x, v = x_earth.copy(), v_earth.copy()
r_min, r_max = R_SUN_EARTH, R_SUN_EARTH
E_values = [E0]

for _ in range(n_steps):
    x, v = leapfrog_step(x, v, sun.field, dt)
    r = np.linalg.norm(x)
    r_min = min(r_min, r)
    r_max = max(r_max, r)
    E_values.append(0.5 * np.dot(v, v) + sun.potential(x))

E_final = E_values[-1]
dE_rel = abs((E_final - E0) / abs(E0))
r_deviation = (r_max - r_min) / R_SUN_EARTH

check("에너지 보존", dE_rel < 1e-4,
      f"ΔE/E₀ = {dE_rel:.2e} (허용: < 1e-4)")
check("원궤도 유지", r_deviation < 0.01,
      f"Δr/R = {r_deviation:.6f} (허용: < 1%)")
check("1주기 후 복귀", np.linalg.norm(x - x_earth) / R_SUN_EARTH < 0.02,
      f"오차 = {np.linalg.norm(x - x_earth) / R_SUN_EARTH:.6f}")

print()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# [2] 달 원궤도 검증
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("[2] 달 원궤도 — 지구 주위 케플러 운동")

earth_as_center = CentralBody(
    position=np.array([0.0, 0.0]),
    mass=M_EARTH,
    G=G,
    softening=1e-8,
)

v_circ_moon = earth_as_center.circular_speed(R_EARTH_MOON)
T_orbit_moon = 2 * np.pi * R_EARTH_MOON / v_circ_moon
period_ratio = T_orbit_earth / T_orbit_moon

print(f"  달 원궤도 속도: v_circ = {v_circ_moon:.4f}")
print(f"  달 공전 주기:   T      = {T_orbit_moon:.4f}")
print(f"  주기 비율:      T_지구/T_달 = {period_ratio:.2f} (실제: ~13.37)")

x_moon = np.array([R_EARTH_MOON, 0.0])
v_moon = np.array([0.0, v_circ_moon])

E0_moon = 0.5 * np.dot(v_moon, v_moon) + earth_as_center.potential(x_moon)

dt_moon = T_orbit_moon / 2000
n_steps_moon = 2000
x_m, v_m = x_moon.copy(), v_moon.copy()
r_min_m, r_max_m = R_EARTH_MOON, R_EARTH_MOON

for _ in range(n_steps_moon):
    x_m, v_m = leapfrog_step(x_m, v_m, earth_as_center.field, dt_moon)
    r = np.linalg.norm(x_m)
    r_min_m = min(r_min_m, r)
    r_max_m = max(r_max_m, r)

E_final_moon = 0.5 * np.dot(v_m, v_m) + earth_as_center.potential(x_m)
dE_moon = abs((E_final_moon - E0_moon) / abs(E0_moon))
r_dev_moon = (r_max_m - r_min_m) / R_EARTH_MOON

check("달 에너지 보존", dE_moon < 1e-4,
      f"ΔE/E₀ = {dE_moon:.2e}")
check("달 원궤도 유지", r_dev_moon < 0.01,
      f"Δr/R = {r_dev_moon:.6f}")
check("주기 비율 근사", abs(period_ratio - 13.37) < 1.0,
      f"계산: {period_ratio:.2f}, 실제: ~13.37")

print()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# [3] 조석력 비교: 달 vs 태양
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("[3] 조석력 비교 — 달 vs 태양 (이론 비율 ≈ 2.17)")

earth_pos = np.array([R_SUN_EARTH, 0.0])

moon_for_tidal = OrbitalMoon(
    host_center=earth_pos,
    semi_major_axis=R_EARTH_MOON,
    eccentricity=0.0,
    orbit_frequency=2 * np.pi / T_orbit_moon,
    mass=M_MOON,
    G=G,
    softening=1e-8,
    tidal_locking=True,
    quadrupole_moment=0.0,
)

T_moon = moon_for_tidal.tidal_tensor(earth_pos, 0.0)
tidal_moon = np.max(np.abs(np.linalg.eigvalsh(T_moon)))

sun_as_moon = OrbitalMoon(
    host_center=np.array([0.0, 0.0]),
    semi_major_axis=R_SUN_EARTH,
    eccentricity=0.0,
    orbit_frequency=0.001,
    mass=M_SUN,
    G=G,
    softening=1e-6,
)
sun_pos_at_t0 = sun_as_moon.position(0.0)

# 태양의 조석 텐서: T_ij = GM/r³ (δ_ij - 3 r_i r_j / r²)
# |T_sun| ≈ 2·G·M_sun / R_se³
tidal_sun_analytic = 2 * G * M_SUN / (R_SUN_EARTH ** 3)
tidal_moon_analytic = 2 * G * M_MOON / (R_EARTH_MOON ** 3)
ratio_analytic = tidal_moon_analytic / tidal_sun_analytic

print(f"  달 조석:       |T_moon| = {tidal_moon_analytic:.6f}")
print(f"  태양 조석:     |T_sun|  = {tidal_sun_analytic:.6f}")
print(f"  비율:          moon/sun = {ratio_analytic:.4f} (이론: ~2.17)")

check("달 조석 > 태양 조석", ratio_analytic > 1.5,
      f"비율 = {ratio_analytic:.4f}")
check("이론값 근사", abs(ratio_analytic - 2.17) < 0.5,
      f"계산: {ratio_analytic:.4f}, 이론: 2.17")

# 수치 조석 텐서 검증
check("조석 텐서 trace ≈ 0 (라플라시안)", abs(np.trace(T_moon)) < 0.1,
      f"trace = {np.trace(T_moon):.6e}")

print()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# [4] Hill 구 검증
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("[4] Hill 구 — 달이 지구의 중력 영향권 안에 있는지")

r_hill = R_SUN_EARTH * (M_EARTH / (3 * M_SUN)) ** (1/3)
print(f"  Hill 구 반지름: r_H = {r_hill:.4f} (지구-달 단위)")
print(f"  달 궤도 반지름: R_em = {R_EARTH_MOON:.4f}")
print(f"  비율:           R_em/r_H = {R_EARTH_MOON / r_hill:.4f}")

check("달이 Hill 구 안에 있음", R_EARTH_MOON < r_hill,
      f"R_em = {R_EARTH_MOON:.4f} < r_H = {r_hill:.4f}")

# 실제: 달은 Hill 구의 약 26% 위치 (384,400km / 1,500,000km)
check("Hill 구 ~26% 위치", abs(R_EARTH_MOON / r_hill - 0.26) < 0.05,
      f"위치 = {R_EARTH_MOON / r_hill * 100:.1f}% (실제: ~26%)")

print()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# [5] 3체 통합 시뮬레이션 — 지구 위 바다(점) + 달 조석
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("[5] 3체 통합 — 지구 표면 점에 달+태양 조석 작용")

R_earth_surface = 0.01655  # 지구 반지름 / 지구-달 거리 ≈ 6371/384400

# 태양: 원점
sun_3body = CentralBody(
    position=np.array([0.0, 0.0]),
    mass=M_SUN, G=G, softening=1e-6,
)

# 달: 지구 주위 공전
moon_3body = OrbitalMoon(
    host_center=earth_pos,
    semi_major_axis=R_EARTH_MOON,
    eccentricity=0.0549,  # 달의 실제 이심률
    orbit_frequency=2 * np.pi / T_orbit_moon,
    mass=M_MOON, G=G, softening=1e-8,
    tidal_locking=True,
)

tidal_3body = TidalField(central=sun_3body, moons=[moon_3body])

# 지구 표면 위 두 점 (달 방향 vs 직교 방향) 에서 조석력 비교
point_toward_moon = earth_pos + np.array([R_earth_surface, 0.0])
point_perpendicular = earth_pos + np.array([0.0, R_earth_surface])

f_toward = tidal_3body.force(point_toward_moon, 0.0)
f_perp = tidal_3body.force(point_perpendicular, 0.0)

# 지구 중심에서의 힘 (기준)
f_center = tidal_3body.force(earth_pos, 0.0)

# 조석력 = 해당 점 힘 - 중심 힘 (차등 중력)
tidal_toward = f_toward - f_center
tidal_perp = f_perp - f_center

print(f"  지구 반지름 (무차원): {R_earth_surface:.5f}")
print(f"  달 방향 조석력:       [{tidal_toward[0]:.6e}, {tidal_toward[1]:.6e}]")
print(f"  직교 방향 조석력:     [{tidal_perp[0]:.6e}, {tidal_perp[1]:.6e}]")

# 달 방향으로 당기고, 직교 방향으로 압축하는지 확인
check("달 방향: 인력 (바깥으로 당김)", tidal_toward[0] > 0,
      f"f_x = {tidal_toward[0]:.6e} > 0")
check("직교 방향: 압축 (안쪽으로)", tidal_perp[1] < 0,
      f"f_y = {tidal_perp[1]:.6e} < 0")

# 조석력 비율: 달 방향 ≈ 2 × 직교 방향 (이론)
ratio_tidal_dir = abs(tidal_toward[0]) / (abs(tidal_perp[1]) + 1e-30)
check("조석 비대칭: 달방향/직교 ≈ 2", abs(ratio_tidal_dir - 2.0) < 1.0,
      f"비율 = {ratio_tidal_dir:.2f} (이론: ~2)")

print()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# [6] 지구 궤도 안정성 (달 섭동 포함, 30주기)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("[6] 장기 안정성 — 지구 궤도 (달 섭동 포함, 30주기)")

tidal_orbit = TidalField(central=sun, moons=[moon_3body])

x_e = np.array([R_SUN_EARTH, 0.0])
v_e = np.array([0.0, v_circ_earth])

E0_orbit = 0.5 * np.dot(v_e, v_e) + tidal_orbit.potential(x_e, 0.0)

n_orbits = 30
dt_long = T_orbit_earth / 3000
n_steps_long = int(n_orbits * T_orbit_earth / dt_long)

r_min_long, r_max_long = R_SUN_EARTH, R_SUN_EARTH
t = 0.0

for i in range(n_steps_long):
    f = tidal_orbit.force(x_e, t)
    v_e = v_e + 0.5 * dt_long * f
    x_e = x_e + dt_long * v_e
    f = tidal_orbit.force(x_e, t + dt_long)
    v_e = v_e + 0.5 * dt_long * f
    t += dt_long

    r = np.linalg.norm(x_e)
    r_min_long = min(r_min_long, r)
    r_max_long = max(r_max_long, r)

E_final_orbit = 0.5 * np.dot(v_e, v_e) + tidal_orbit.potential(x_e, t)
dE_orbit = abs((E_final_orbit - E0_orbit) / abs(E0_orbit))
orbit_deviation = (r_max_long - r_min_long) / R_SUN_EARTH

print(f"  시뮬레이션: {n_orbits}주기 ({n_steps_long} steps)")
print(f"  r_min = {r_min_long:.4f}, r_max = {r_max_long:.4f}")
print(f"  궤도 편차: {orbit_deviation * 100:.4f}%")
print(f"  에너지 드리프트: ΔE/E₀ = {dE_orbit:.2e}")

check("30주기 궤도 안정", orbit_deviation < 0.05,
      f"편차 = {orbit_deviation * 100:.4f}%")
check("에너지 드리프트 제한", dE_orbit < 0.01,
      f"ΔE/E₀ = {dE_orbit:.2e}")

print()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# [7] 물리 상수 자기일관성 검증
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("[7] 물리 상수 자기일관성")

# Kepler 3법칙: T² = 4π²a³ / (GM)
T2_kepler_earth = 4 * np.pi**2 * R_SUN_EARTH**3 / (G * M_SUN)
T_kepler_earth = np.sqrt(T2_kepler_earth)

T2_kepler_moon = 4 * np.pi**2 * R_EARTH_MOON**3 / (G * M_EARTH)
T_kepler_moon = np.sqrt(T2_kepler_moon)

kepler_ratio = T_kepler_earth / T_kepler_moon

print(f"  Kepler 지구 주기: {T_kepler_earth:.4f}")
print(f"  Kepler 달 주기:   {T_kepler_moon:.4f}")
print(f"  주기 비율:        {kepler_ratio:.2f}")
print(f"  실제 비율:        ~13.37")

check("Kepler 지구 주기 = 시뮬레이션 주기",
      abs(T_kepler_earth - T_orbit_earth) / T_orbit_earth < 0.01,
      f"Kepler={T_kepler_earth:.4f}, sim={T_orbit_earth:.4f}")
check("Kepler 달 주기 = 시뮬레이션 주기",
      abs(T_kepler_moon - T_orbit_moon) / T_orbit_moon < 0.01,
      f"Kepler={T_kepler_moon:.4f}, sim={T_orbit_moon:.4f}")

# 실제 비율과 비교
check("주기 비율 오차 < 5%", abs(kepler_ratio - 13.37) / 13.37 < 0.05,
      f"오차 = {abs(kepler_ratio - 13.37) / 13.37 * 100:.2f}%")

# Roche 한계: d = R_primary × (2·M_primary/M_satellite)^(1/3)
roche_limit = R_earth_surface * (2 * M_EARTH / M_MOON) ** (1/3)
print(f"  Roche 한계:       {roche_limit:.5f} (지구-달 단위)")
print(f"  지구-달 거리:     {R_EARTH_MOON:.4f}")
check("달이 Roche 한계 밖", R_EARTH_MOON > roche_limit,
      f"R_em = {R_EARTH_MOON:.4f} >> Roche = {roche_limit:.5f}")

print()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 최종 결과
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
n_pass = sum(results)
n_total = len(results)
print("=" * 70)
print(f"결과: {n_pass}/{n_total} PASS")
if n_pass == n_total:
    print("전체 PASS — 실제 태양계 비율에서 물리적 균형 확인")
else:
    print(f"FAIL 항목: {n_total - n_pass}개")
print("=" * 70)
