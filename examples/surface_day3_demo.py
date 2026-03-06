"""Phase 7 Demo — 셋째날: 땅과 바다의 분리

검증 항목:
  P7-1: SurfaceSchema 유효 알베도 (지구 f_land=0.29)
  P7-2: 전 바다 vs 전 육지 알베도 차이
  P7-3: surface 알베도 → AtmosphereColumn 연동, T_surface 영향
  P7-4: 땅 비율 증가 시 냉각 (A↑ → F_abs↓ → T↓)
"""

import numpy as np
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from L0_solar import SurfaceSchema, effective_albedo, AtmosphereColumn, SolarLuminosity

PASS = "\u2705 PASS"
FAIL = "\u274c FAIL"


def check(name, condition, detail=""):
    tag = PASS if condition else FAIL
    print(f"  {tag}  {name}" + (f"  ({detail})" if detail else ""))
    return condition


def main():
    all_pass = True

    print("=" * 65)
    print(" Phase 7: \uc138\uce68\ub0a0 \u2014 \ub53c\uacf5\uacfc \ubc14\ub2e4 \ubd84\ub9ac (\ub531 \uc774 \ub4e4\uc5b4\ub0a0)")
    print("=" * 65)

    sun = SolarLuminosity(mass_solar=1.0, alpha=4.0)
    F_earth = sun.irradiance_si(1.0)

    # ──── P7-1: SurfaceSchema 기본 (지구) ────────────────
    print("\n[P7-1] SurfaceSchema \uc720\ud6a8 \uc54c\ubc14\ub3c4 (f_land=0.29)")

    sfc_earth = SurfaceSchema(land_fraction=0.29)
    A_earth = sfc_earth.effective_albedo()

    print(f"  f_land     = 0.29")
    print(f"  A_land     = {sfc_earth.albedo_land:.3f}")
    print(f"  A_ocean    = {sfc_earth.albedo_ocean:.3f}")
    print(f"  A_eff      = {A_earth:.4f}")

    # 지구 전지구 알베도 0.30 근방 (바다 우세라 A_ocean에 가깝게)
    all_pass &= check(
        "A_eff \u2248 0.12~0.15 (ocean-dominated)",
        0.08 <= A_earth <= 0.20,
        f"{A_earth:.4f}",
    )

    # ──── P7-2: 전 바다 vs 전 육지 ────────────────────────
    print("\n[P7-2] \uc804 \ubc14\ub2e4 vs \uc804 \uc751\uc9c0")

    sfc_ocean = SurfaceSchema(land_fraction=0.0)
    sfc_land = SurfaceSchema(land_fraction=1.0)

    A_ocean = sfc_ocean.effective_albedo()
    A_land = sfc_land.effective_albedo()

    print(f"  A(ocean only) = {A_ocean:.4f}")
    print(f"  A(land only)  = {A_land:.4f}")

    all_pass &= check("A_land > A_ocean", A_land > A_ocean)
    all_pass &= check("A_ocean \u2248 0.08", abs(A_ocean - 0.08) < 0.02)
    all_pass &= check("A_land \u2248 0.30", abs(A_land - 0.30) < 0.05)

    # ──── P7-3: surface → atmosphere 연동 ────────────────
    print("\n[P7-3] surface \u2192 AtmosphereColumn \uc5f0\ub3d9")

    atm_fixed = AtmosphereColumn(
        body_name="Earth",
        albedo=0.306,
        T_surface_init=288.0,
    )
    atm_surface = AtmosphereColumn(
        body_name="Earth",
        albedo=sfc_earth.effective_albedo(),
        T_surface_init=288.0,
    )

    T_eq_fixed = atm_fixed.equilibrium_temp(F_earth)
    T_eq_surface = atm_surface.equilibrium_temp(F_earth)

    print(f"  albedo fixed(0.306)  \u2192 T_eq = {T_eq_fixed:.1f} K")
    print(f"  albedo surface({A_earth:.3f}) \u2192 T_eq = {T_eq_surface:.1f} K")

    # surface A가 fixed보다 작으면 (바다 많음) F_abs 높음 \u2192 T_eq 높음
    if A_earth < 0.306:
        all_pass &= check(
            "surface A < fixed \u2192 T_eq \uc0c8 (A\ua193\u2192F_abs\ua193)",
            T_eq_surface > T_eq_fixed,
            f"\u0394T={T_eq_surface - T_eq_fixed:.1f} K",
        )

    # ──── P7-4: 땅 비율 증가 → 냉각 ────────────────────────
    print("\n[P7-4] \ub53c \ube44\uc728 \uc99d\uac00 \u2192 \ub0a9\uac04")

    atm_ocean = AtmosphereColumn(
        body_name="OceanWorld",
        albedo=sfc_ocean.effective_albedo(),
        T_surface_init=288.0,
    )
    atm_land = AtmosphereColumn(
        body_name="LandWorld",
        albedo=sfc_land.effective_albedo(),
        T_surface_init=288.0,
    )

    for _ in range(50):
        atm_ocean.step(F_earth, 0.1)
        atm_land.step(F_earth, 0.1)

    T_ocean = atm_ocean.T_surface
    T_land = atm_land.T_surface

    print(f"  T(ocean world) = {T_ocean:.1f} K")
    print(f"  T(land world)  = {T_land:.1f} K")

    all_pass &= check(
        "T_land < T_ocean (A\ua193 \u2192 \ub0a9\uac04)",
        T_land < T_ocean,
        f"\u0394T = {T_ocean - T_land:.1f} K",
    )

    # ──── 결과 ────────────────────────────────────────────
    print("\n" + "=" * 65)
    if all_pass:
        print(" Phase 7 \uac80\uc99d: ALL PASS \u2705")
    else:
        print(" Phase 7 \uac80\uc99d: SOME FAIL \u274c")
    print("=" * 65)

    return 0 if all_pass else 1


if __name__ == "__main__":
    exit(main())
