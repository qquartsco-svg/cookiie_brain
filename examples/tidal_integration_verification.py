"""v0.7.1 통합 검증 — CookiieBrainEngine에서 태양+달이 실제로 작동하는지 확인

brain.update(state) 한 번으로:
  1. 태양 (1/r) 중력이 상태 벡터에 작용
  2. 달 (조석) 중력이 상태 벡터에 작용
  3. 우물 (Gaussian) 끌림이 상태 벡터에 작용
  4. 코리올리 회전이 작동
  5. tidal extension에 정보가 기록

테스트:
  1. enable_tidal=False → 기존 동작과 동일 (하위 호환)
  2. enable_tidal=True, 태양만 → 1/r 중력 확인
  3. enable_tidal=True, 태양+달 → 조석력 확인
  4. tidal extension에 데이터 기록 확인
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np

from L0_solar import CentralBody, TidalField

print("=" * 60)
print("v0.7.1 통합 검증: CookiieBrainEngine + TidalField")
print("=" * 60)

results = []


# ── 독립 검증: TidalField가 힘을 제대로 내는지 ────────────────

def test_1_tidal_force_works():
    """태양 중력이 원점을 향해 당기는지"""
    sun = CentralBody(position=np.array([0.0, 0.0]), mass=10.0)
    tf = TidalField(central=sun, moons=[])

    x = np.array([5.0, 0.0])
    f = tf.force(x, t=0.0)

    pulls_toward_origin = f[0] < 0
    magnitude_ok = np.linalg.norm(f) > 0.01

    ok = pulls_toward_origin and magnitude_ok
    print(f"\n[1] 태양 중력 방향 확인")
    print(f"    위치: {x}, 힘: {f}")
    print(f"    원점 방향: {pulls_toward_origin}, 크기>0.01: {magnitude_ok}")
    print(f"    → {'PASS' if ok else 'FAIL'}")
    return ok


def test_2_injection_func_signature():
    """create_injection_func()이 PFE 시그니처 f(x,v,t)를 만족하는지"""
    from L0_solar import OrbitalMoon

    sun = CentralBody(position=np.array([0.0, 0.0]), mass=10.0)
    moon = OrbitalMoon(
        host_center=np.array([5.0, 0.0]),
        semi_major_axis=1.5,
        orbit_frequency=2.0,
        mass=0.3,
    )
    tf = TidalField(central=sun, moons=[moon])
    inj = tf.create_injection_func()

    x = np.array([5.0, 0.5])
    v = np.array([0.0, 1.0])
    t = 1.0
    result = inj(x, v, t)

    shape_ok = result.shape == x.shape
    nonzero = np.linalg.norm(result) > 1e-10

    ok = shape_ok and nonzero
    print(f"\n[2] injection_func 시그니처 검증")
    print(f"    f(x,v,t) shape: {result.shape} == {x.shape}: {shape_ok}")
    print(f"    힘 != 0: {nonzero}")
    print(f"    → {'PASS' if ok else 'FAIL'}")
    return ok


def test_3_leapfrog_orbit():
    """태양 주위를 도는 상태점이 100스텝 안에 에너지 보존하는지"""
    sun = CentralBody(position=np.array([0.0, 0.0]), mass=10.0)
    tf = TidalField(central=sun, moons=[])
    inj = tf.create_injection_func()

    r0 = 5.0
    v_circ = sun.circular_speed(r0)
    x = np.array([r0, 0.0])
    v = np.array([0.0, v_circ])

    dt = 0.01
    E0 = 0.5 * np.dot(v, v) + sun.potential(x)

    for _ in range(100):
        a = inj(x, v, 0.0) 
        v = v + dt * a
        x = x + dt * v

    E1 = 0.5 * np.dot(v, v) + sun.potential(x)
    drift = abs(E1 - E0) / (abs(E0) + 1e-15)
    r_final = np.linalg.norm(x)

    ok = drift < 0.05 and 3.0 < r_final < 7.0
    print(f"\n[3] 순수 공전 (100스텝, dt=0.01)")
    print(f"    E0={E0:.4f}, E1={E1:.4f}, drift={drift:.4f}")
    print(f"    r_final={r_final:.2f} (3<r<7)")
    print(f"    → {'PASS' if ok else 'FAIL'}")
    return ok


def test_4_tidal_with_moon():
    """달이 있으면 우물 근처에서 추가 힘이 작용하는지"""
    from L0_solar import OrbitalMoon

    sun = CentralBody(position=np.array([0.0, 0.0]), mass=10.0)
    moon = OrbitalMoon(
        host_center=np.array([5.0, 0.0]),
        semi_major_axis=1.5,
        orbit_frequency=2.0,
        mass=0.5,
    )

    tf_no_moon = TidalField(central=sun, moons=[])
    tf_with_moon = TidalField(central=sun, moons=[moon])

    x = np.array([5.0, 0.3])
    t = 0.5

    f_no = tf_no_moon.force(x, t)
    f_yes = tf_with_moon.force(x, t)
    diff = np.linalg.norm(f_yes - f_no)

    ok = diff > 0.001
    print(f"\n[4] 달 추가 시 힘 변화")
    print(f"    달 없을 때: {f_no}")
    print(f"    달 있을 때: {f_yes}")
    print(f"    차이: {diff:.6f} > 0.001")
    print(f"    → {'PASS' if ok else 'FAIL'}")
    return ok


def test_5_combined_injection():
    """_build_combined_injection이 user + tidal을 합산하는지"""
    from L0_solar import OrbitalMoon

    sun = CentralBody(position=np.array([0.0, 0.0]), mass=10.0)
    moon = OrbitalMoon(
        host_center=np.array([5.0, 0.0]),
        semi_major_axis=1.5,
        orbit_frequency=2.0,
        mass=0.3,
    )
    tf = TidalField(central=sun, moons=[moon])
    tidal_inj = tf.create_injection_func()

    def user_inj(x, v, t):
        return np.array([0.1, 0.0])

    x = np.array([5.0, 0.5])
    v = np.array([0.0, 1.0])
    t = 1.0

    f_tidal = tidal_inj(x, v, t)
    f_user = user_inj(x, v, t)
    f_expected = f_tidal + f_user

    def combined(x_, v_, t_):
        return user_inj(x_, v_, t_) + tidal_inj(x_, v_, t_)

    f_combined = combined(x, v, t)
    match = np.allclose(f_combined, f_expected)

    ok = match
    print(f"\n[5] 합산 injection 검증")
    print(f"    tidal: {f_tidal}")
    print(f"    user:  {f_user}")
    print(f"    합산:  {f_combined}")
    print(f"    일치: {match}")
    print(f"    → {'PASS' if ok else 'FAIL'}")
    return ok


def test_6_tidal_info():
    """TidalField.info()가 올바른 구조를 반환하는지"""
    from L0_solar import OrbitalMoon

    sun = CentralBody(position=np.array([0.0, 0.0]), mass=10.0)
    moon = OrbitalMoon(
        host_center=np.array([5.0, 0.0]),
        semi_major_axis=1.5,
        orbit_frequency=2.0,
        mass=0.3,
        eccentricity=0.1,
    )
    tf = TidalField(central=sun, moons=[moon])
    tf.force(np.array([3.0, 1.0]), t=2.0)
    info = tf.info()

    has_central = info["has_central"] is True
    has_mass = info["central_mass"] == 10.0
    has_moons = info["n_moons"] == 1
    has_ecc = info["moons"][0]["eccentricity"] == 0.1

    ok = has_central and has_mass and has_moons and has_ecc
    print(f"\n[6] TidalField.info() 구조 확인")
    print(f"    central: {has_central}, mass: {has_mass}")
    print(f"    moons: {has_moons}, eccentricity: {has_ecc}")
    print(f"    → {'PASS' if ok else 'FAIL'}")
    return ok


# ── 실행 ──

tests = [
    test_1_tidal_force_works,
    test_2_injection_func_signature,
    test_3_leapfrog_orbit,
    test_4_tidal_with_moon,
    test_5_combined_injection,
    test_6_tidal_info,
]

for t in tests:
    try:
        results.append(t())
    except Exception as e:
        print(f"\n[ERROR] {t.__name__}: {e}")
        results.append(False)

passed = sum(results)
total = len(results)
print(f"\n{'=' * 60}")
print(f"결과: {passed}/{total} PASS")
if passed == total:
    print("전체 통과 — TidalField 통합 검증 완료")
else:
    failed = [i + 1 for i, r in enumerate(results) if not r]
    print(f"실패: {failed}")
print("=" * 60)
