#!/usr/bin/env python3
"""3체 균형점(라그랑주 포인트) 존재 검증

3체 문제에서 5개의 균형점(L1~L5)이 우리 엔진의 상태공간에
실제로 존재하는지 수치적으로 확인한다.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
라그랑주 포인트란?
  태양-지구가 공전하는 회전 좌표계에서,
  중력 + 원심력 + 코리올리력이 균형을 이루는 5개 점.

  L1: 태양-지구 사이 (지구에서 태양 방향 ~150만km)
  L2: 지구 뒤쪽 (태양 반대편 ~150만km, JWST 위치)
  L3: 태양 반대편 (지구 궤도 건너편)
  L4: 지구 궤도 60° 앞 (트로이 소행성대)
  L5: 지구 궤도 60° 뒤 (트로이 소행성대)

검증 방법:
  1. 유효 퍼텐셜 V_eff = V_grav - ½Ω²r² 계산
  2. ∇V_eff = 0 인 점을 수치적으로 탐색
  3. 각 L점에서 실제 힘 균형 확인
  4. Jacobi 상수(보존량) 검증
  5. L4/L5 안정성 확인 (질량비 조건)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Author: GNJz (Qquarts)
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
from scipy.optimize import brentq, minimize
from solar import CentralBody

PASS = "\033[92mPASS\033[0m"
FAIL = "\033[91mFAIL\033[0m"
results = []


def check(name: str, condition: bool, detail: str = ""):
    tag = PASS if condition else FAIL
    results.append(condition)
    print(f"  [{tag}] {name}")
    if detail:
        print(f"         {detail}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 실제 태양계 파라미터 (무차원화)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
M_SUN = 332_946.0
M_EARTH = 1.0
R = 389.17  # 태양-지구 거리
G = 1.0

# 질량비
mu = M_EARTH / (M_SUN + M_EARTH)  # ≈ 3.003e-6
print("=" * 70)
print("3체 균형점 (라그랑주 포인트) 검증")
print("=" * 70)
print(f"  M_sun = {M_SUN:,.0f}, M_earth = {M_EARTH}")
print(f"  거리 R = {R}")
print(f"  질량비 μ = M_earth/(M_sun+M_earth) = {mu:.6e}")
print()

# 공전 각속도 Ω
Omega = np.sqrt(G * (M_SUN + M_EARTH) / R**3)
T_orbit = 2 * np.pi / Omega
print(f"  공전 각속도 Ω = {Omega:.6f}")
print(f"  공전 주기 T = {T_orbit:.4f}")
print()

# 중심: 질량 중심(barycenter) 기준
# 태양 위치: -mu * R, 지구 위치: (1-mu) * R
x_sun = -mu * R
x_earth = (1 - mu) * R

print(f"  태양 위치 (barycenter 기준): x = {x_sun:.6f}")
print(f"  지구 위치 (barycenter 기준): x = {x_earth:.4f}")
print()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 유효 퍼텐셜 (회전 좌표계)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def V_eff(x, y):
    """회전 좌표계 유효 퍼텐셜"""
    r_sun = np.sqrt((x - x_sun)**2 + y**2)
    r_earth = np.sqrt((x - x_earth)**2 + y**2)
    V_grav = -G * M_SUN / (r_sun + 1e-10) - G * M_EARTH / (r_earth + 1e-10)
    V_cent = -0.5 * Omega**2 * (x**2 + y**2)
    return V_grav + V_cent


def grad_V_eff(x, y, eps=1e-4):
    """∇V_eff 수치 미분"""
    dVdx = (V_eff(x + eps, y) - V_eff(x - eps, y)) / (2 * eps)
    dVdy = (V_eff(x, y + eps) - V_eff(x, y - eps)) / (2 * eps)
    return np.array([dVdx, dVdy])


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# [1] L1 탐색: 태양-지구 사이
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("[1] L1 — 태양과 지구 사이 (SOHO 위성 위치)")

def collinear_balance(x):
    """x축 위 y=0에서 유효 힘의 x성분"""
    return grad_V_eff(x, 0.0)[0]

# L1: 지구에서 태양 방향으로 약간 안쪽
# 이론: r_L1 ≈ R * (mu/3)^(1/3)
r_L1_theory = R * (mu / 3) ** (1/3)
L1_x = brentq(collinear_balance, x_earth - 2 * r_L1_theory, x_earth - 0.1 * r_L1_theory)
L1_grad = np.linalg.norm(grad_V_eff(L1_x, 0.0))
L1_dist_from_earth = abs(x_earth - L1_x)

print(f"  이론 L1 거리 (지구에서): {r_L1_theory:.4f}")
print(f"  수치 L1 위치: x = {L1_x:.4f}")
print(f"  수치 L1 거리 (지구에서): {L1_dist_from_earth:.4f}")
print(f"  |∇V_eff| at L1 = {L1_grad:.2e}")

check("L1 존재 (∇V_eff ≈ 0)", L1_grad < 1e-3,
      f"|∇V_eff| = {L1_grad:.2e}")
check("L1 거리 이론값 근사", abs(L1_dist_from_earth - r_L1_theory) / r_L1_theory < 0.05,
      f"오차 = {abs(L1_dist_from_earth - r_L1_theory) / r_L1_theory * 100:.2f}%")

# 실제 L1 거리 (km 환산): 1 unit = 384,400 km
L1_km = L1_dist_from_earth * 384400
print(f"  L1 거리 (km 환산): {L1_km:,.0f} km (실제: ~1,500,000 km)")
check("L1 거리 실측 근사", abs(L1_km - 1_500_000) / 1_500_000 < 0.15,
      f"계산: {L1_km:,.0f} km")
print()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# [2] L2 탐색: 지구 뒤쪽 (태양 반대편)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("[2] L2 — 지구 뒤쪽 (JWST 위치)")

L2_x = brentq(collinear_balance, x_earth + 0.1 * r_L1_theory, x_earth + 2 * r_L1_theory)
L2_grad = np.linalg.norm(grad_V_eff(L2_x, 0.0))
L2_dist_from_earth = abs(L2_x - x_earth)
L2_km = L2_dist_from_earth * 384400

print(f"  수치 L2 위치: x = {L2_x:.4f}")
print(f"  L2 거리 (지구에서): {L2_dist_from_earth:.4f}")
print(f"  |∇V_eff| at L2 = {L2_grad:.2e}")
print(f"  L2 거리 (km 환산): {L2_km:,.0f} km (실제: ~1,500,000 km)")

check("L2 존재 (∇V_eff ≈ 0)", L2_grad < 1e-3,
      f"|∇V_eff| = {L2_grad:.2e}")
check("L1 ≈ L2 (대칭)", abs(L1_dist_from_earth - L2_dist_from_earth) / L1_dist_from_earth < 0.05,
      f"L1={L1_dist_from_earth:.4f}, L2={L2_dist_from_earth:.4f}")
print()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# [3] L3 탐색: 태양 반대편
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("[3] L3 — 태양 반대편 (지구 궤도 건너편)")

L3_x = brentq(collinear_balance, x_sun - 1.5 * R, x_sun - 0.8 * R)
L3_grad = np.linalg.norm(grad_V_eff(L3_x, 0.0))
L3_dist_from_sun = abs(L3_x - x_sun)

print(f"  수치 L3 위치: x = {L3_x:.4f}")
print(f"  L3 거리 (태양에서): {L3_dist_from_sun:.4f}")
print(f"  |∇V_eff| at L3 = {L3_grad:.2e}")

check("L3 존재 (∇V_eff ≈ 0)", L3_grad < 1e-3,
      f"|∇V_eff| = {L3_grad:.2e}")
check("L3 ≈ 태양 반대편 (r ≈ R)", abs(L3_dist_from_sun - R) / R < 0.01,
      f"r/R = {L3_dist_from_sun / R:.6f}")
print()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# [4] L4, L5 탐색: 정삼각형 점 (60° 위치)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("[4] L4/L5 — 정삼각형 점 (트로이 소행성대)")

# 이론: L4 = barycenter에서 60° 위치, 태양과 지구 모두로부터 거리 R
# L4: (R/2 - mu*R, R*√3/2)
# L5: (R/2 - mu*R, -R*√3/2)
L4_theory_x = 0.5 * R - mu * R
L4_theory_y = R * np.sqrt(3) / 2

# 수치 최적화로 L4 정밀 위치 찾기
res4 = minimize(lambda p: np.linalg.norm(grad_V_eff(p[0], p[1]))**2,
                [L4_theory_x, L4_theory_y], method='Nelder-Mead',
                options={'xatol': 1e-8, 'fatol': 1e-16})
L4_x, L4_y = res4.x
L4_grad = np.linalg.norm(grad_V_eff(L4_x, L4_y))

# L5는 y 반전
res5 = minimize(lambda p: np.linalg.norm(grad_V_eff(p[0], p[1]))**2,
                [L4_theory_x, -L4_theory_y], method='Nelder-Mead',
                options={'xatol': 1e-8, 'fatol': 1e-16})
L5_x, L5_y = res5.x
L5_grad = np.linalg.norm(grad_V_eff(L5_x, L5_y))

# L4에서 태양/지구까지 거리
r_L4_sun = np.sqrt((L4_x - x_sun)**2 + L4_y**2)
r_L4_earth = np.sqrt((L4_x - x_earth)**2 + L4_y**2)

# L4의 각도 (barycenter 기준)
angle_L4 = np.degrees(np.arctan2(L4_y, L4_x))

print(f"  L4 위치: ({L4_x:.4f}, {L4_y:.4f})")
print(f"  L5 위치: ({L5_x:.4f}, {L5_y:.4f})")
print(f"  L4 각도: {angle_L4:.2f}° (이론: 60°)")
print(f"  L4→태양: {r_L4_sun:.4f}, L4→지구: {r_L4_earth:.4f} (이론: 둘 다 ≈ R={R})")
print(f"  |∇V_eff| at L4 = {L4_grad:.2e}")
print(f"  |∇V_eff| at L5 = {L5_grad:.2e}")

check("L4 존재 (∇V_eff ≈ 0)", L4_grad < 1e-2,
      f"|∇V_eff| = {L4_grad:.2e}")
check("L5 존재 (∇V_eff ≈ 0)", L5_grad < 1e-2,
      f"|∇V_eff| = {L5_grad:.2e}")
check("L4 정삼각형 (r_sun ≈ r_earth ≈ R)",
      abs(r_L4_sun - R) / R < 0.01 and abs(r_L4_earth - R) / R < 0.01,
      f"r_sun/R={r_L4_sun/R:.6f}, r_earth/R={r_L4_earth/R:.6f}")
check("L4 각도 ≈ 60°", abs(angle_L4 - 60) < 1.0,
      f"{angle_L4:.2f}°")
print()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# [5] Jacobi 상수 보존 (운동 적분)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("[5] Jacobi 상수 보존 — 3체 문제의 운동 적분")

sun_body = CentralBody(position=np.array([x_sun, 0.0]), mass=M_SUN, G=G, softening=1e-8)
earth_body = CentralBody(position=np.array([x_earth, 0.0]), mass=M_EARTH, G=G, softening=1e-10)


def jacobi_constant(x, y, vx, vy):
    """C_J = -2V_eff - (vx² + vy²)  (회전 좌표계)"""
    return -2 * V_eff(x, y) - (vx**2 + vy**2)


def total_force_rotating(x, y, vx, vy):
    """회전 좌표계에서의 총 힘 (중력 + 원심력 + 코리올리)"""
    pos = np.array([x, y])
    f_sun = sun_body.field(pos)
    f_earth = earth_body.field(pos)
    f_centrifugal = Omega**2 * pos
    f_coriolis = 2 * Omega * np.array([vy, -vx])
    return f_sun + f_earth + f_centrifugal + f_coriolis


# L4 근처에서 작은 속도로 시뮬레이션
x0, y0 = L4_x, L4_y
vx0, vy0 = 0.01, -0.01

CJ_0 = jacobi_constant(x0, y0, vx0, vy0)
print(f"  초기 Jacobi 상수: C_J = {CJ_0:.6f}")

dt = 0.01
n_steps = 50000
x_j, y_j, vx_j, vy_j = x0, y0, vx0, vy0
CJ_values = [CJ_0]

for _ in range(n_steps):
    fx, fy = total_force_rotating(x_j, y_j, vx_j, vy_j)
    vx_j += dt * fx
    vy_j += dt * fy
    x_j += dt * vx_j
    y_j += dt * vy_j
    CJ_values.append(jacobi_constant(x_j, y_j, vx_j, vy_j))

CJ_arr = np.array(CJ_values)
CJ_drift = abs(CJ_arr[-1] - CJ_0) / abs(CJ_0)
CJ_std = np.std(CJ_arr) / abs(CJ_0)

print(f"  최종 Jacobi 상수: C_J = {CJ_arr[-1]:.6f}")
print(f"  드리프트: ΔC_J/C_J = {CJ_drift:.2e}")
print(f"  변동폭: σ(C_J)/C_J = {CJ_std:.2e}")

check("Jacobi 상수 보존", CJ_std < 0.01,
      f"σ/C_J = {CJ_std:.2e}")
print()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# [6] L4/L5 안정성 조건 (Gascheau 정리)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("[6] L4/L5 안정성 — Gascheau 정리")

# L4/L5가 안정하려면: μ < μ_crit = (1 - √(23/27))/2 ≈ 0.03852
mu_crit = (1 - np.sqrt(23/27)) / 2
print(f"  질량비 μ = {mu:.6e}")
print(f"  임계값 μ_crit = {mu_crit:.6f}")
print(f"  μ/μ_crit = {mu/mu_crit:.6e}")

check("μ < μ_crit (L4/L5 안정 조건)",
      mu < mu_crit,
      f"μ = {mu:.2e} << μ_crit = {mu_crit:.4f}")

# L4 근처 궤적이 탈출하지 않는지 확인
dist_from_L4 = np.sqrt((x_j - L4_x)**2 + (y_j - L4_y)**2)
print(f"  시뮬레이션 후 L4로부터 거리: {dist_from_L4:.4f}")
print(f"  R 대비 비율: {dist_from_L4 / R * 100:.2f}%")

check("L4 근처 체류 (탈출 안 함)", dist_from_L4 < R * 0.5,
      f"L4로부터 {dist_from_L4:.4f} (R의 {dist_from_L4/R*100:.1f}%)")
print()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# [7] CentralBody.field()로 직접 확인
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("[7] 엔진 CentralBody.field()로 L1 힘 균형 직접 확인")

L1_pos = np.array([L1_x, 0.0])
f_sun_L1 = sun_body.field(L1_pos)
f_earth_L1 = earth_body.field(L1_pos)
f_cent_L1 = Omega**2 * L1_pos

f_total = f_sun_L1 + f_earth_L1 + f_cent_L1

print(f"  태양 힘 at L1: [{f_sun_L1[0]:.6f}, {f_sun_L1[1]:.6f}]")
print(f"  지구 힘 at L1: [{f_earth_L1[0]:.6f}, {f_earth_L1[1]:.6f}]")
print(f"  원심력 at L1:  [{f_cent_L1[0]:.6f}, {f_cent_L1[1]:.6f}]")
print(f"  합력 at L1:    [{f_total[0]:.6e}, {f_total[1]:.6e}]")

check("L1 합력 ≈ 0 (CentralBody 검증)",
      np.linalg.norm(f_total) < 1e-3,
      f"|F_total| = {np.linalg.norm(f_total):.2e}")

# L4도 확인
L4_pos = np.array([L4_x, L4_y])
f_sun_L4 = sun_body.field(L4_pos)
f_earth_L4 = earth_body.field(L4_pos)
f_cent_L4 = Omega**2 * L4_pos
f_total_L4 = f_sun_L4 + f_earth_L4 + f_cent_L4

print(f"  합력 at L4:    [{f_total_L4[0]:.6e}, {f_total_L4[1]:.6e}]")
check("L4 합력 ≈ 0 (CentralBody 검증)",
      np.linalg.norm(f_total_L4) < 1e-2,
      f"|F_total| = {np.linalg.norm(f_total_L4):.2e}")
print()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# [8] 유효 퍼텐셜 지형 요약
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("[8] 유효 퍼텐셜 지형 — 라그랑주 포인트 에너지 순서")

V_L1 = V_eff(L1_x, 0.0)
V_L2 = V_eff(L2_x, 0.0)
V_L3 = V_eff(L3_x, 0.0)
V_L4 = V_eff(L4_x, L4_y)
V_L5 = V_eff(L5_x, L5_y)

print(f"  V_eff(L1) = {V_L1:.4f}")
print(f"  V_eff(L2) = {V_L2:.4f}")
print(f"  V_eff(L3) = {V_L3:.4f}")
print(f"  V_eff(L4) = {V_L4:.4f}")
print(f"  V_eff(L5) = {V_L5:.4f}")

# 이론: V(L1) < V(L2) < V(L3) < V(L4) = V(L5)  (안장점 순서)
check("V(L1) < V(L2)", V_L1 < V_L2,
      f"{V_L1:.4f} < {V_L2:.4f}")
check("V(L2) < V(L3)", V_L2 < V_L3,
      f"{V_L2:.4f} < {V_L3:.4f}")
check("V(L3) < V(L4)", V_L3 < V_L4,
      f"{V_L3:.4f} < {V_L4:.4f}")
check("V(L4) ≈ V(L5) (대칭)", abs(V_L4 - V_L5) / abs(V_L4) < 1e-4,
      f"차이 = {abs(V_L4 - V_L5):.2e}")
print()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 최종 결과
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
n_pass = sum(results)
n_total = len(results)
print("=" * 70)
print(f"결과: {n_pass}/{n_total} PASS")
if n_pass == n_total:
    print("전체 PASS — 5개 라그랑주 포인트가 상태공간에 존재 확인")
else:
    print(f"FAIL 항목: {n_total - n_pass}개")
print()
print("라그랑주 포인트 요약:")
print(f"  L1: ({L1_x:.2f}, 0)     — 지구에서 {L1_km:,.0f} km (SOHO)")
print(f"  L2: ({L2_x:.2f}, 0)     — 지구에서 {L2_km:,.0f} km (JWST)")
print(f"  L3: ({L3_x:.2f}, 0)     — 태양 반대편")
print(f"  L4: ({L4_x:.2f}, {L4_y:.2f})  — 궤도 60° 앞 (트로이)")
print(f"  L5: ({L5_x:.2f}, {L5_y:.2f}) — 궤도 60° 뒤 (트로이)")
print("=" * 70)
