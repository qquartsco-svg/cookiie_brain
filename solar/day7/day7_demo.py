"""day7_demo.py — Day7 통합 러너 + 안식 판정 smoke test

V1~V7 ALL PASS 목표.

Day1~6 엔진 12개가 12개 위도 밴드 위에서 돌아가는 전 지구 시뮬레이션.
"""

from __future__ import annotations
import sys, os

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from solar.day7 import (
    make_planet_runner,
    make_sabbath_judge,
    PlanetSnapshot,
)

_passed = 0
_failed = 0

def ok(label: str, cond: bool, detail: str = "") -> None:
    global _passed, _failed
    if cond:
        _passed += 1
        print(f"  ✓ {label}")
    else:
        _failed += 1
        print(f"  ✗ {label}" + (f"  ({detail})" if detail else ""))


print("\n── Day7 통합 러너 ──────────────────────────────────────────────────────")

# V1  PlanetRunner 인스턴스화
runner = make_planet_runner(n_bands=12, n_species=4, seed=42)
ok("V1  PlanetRunner 인스턴스화", runner is not None)

# V2  step(1yr) → PlanetSnapshot 반환
snap1 = runner.step(dt_yr=1.0)
ok("V2  step(1yr) → PlanetSnapshot",
   isinstance(snap1, PlanetSnapshot),
   f"t={snap1.time_yr}")

# V3  스냅샷 필드 검증 (12개 밴드)
ok("V3  band_T 길이 = 12", len(snap1.band_T) == 12,
   f"got {len(snap1.band_T)}")
ok("V4  band_seed 길이 = 12", len(snap1.band_seed) == 12,
   f"got {len(snap1.band_seed)}")

# V5  5스텝 연속 적분 (CO2·T 값 유효 범위)
print("\n── 5 스텝 연속 적분 ────────────────────────────────────────────────────")
for _ in range(4):
    runner.step(dt_yr=1.0)
snap5 = runner.step(dt_yr=1.0)
print(f"  {snap5.summary()}")
ok("V5  CO2_ppm 유효 범위 [200, 2000]",
   200.0 <= snap5.CO2_ppm <= 2000.0,
   f"CO2={snap5.CO2_ppm:.1f}")
ok("V6  T_surface 유효 범위 [200, 380]",
   200.0 <= snap5.T_surface_K <= 380.0,
   f"T={snap5.T_surface_K:.1f}K")

# V7  SabbathJudge — 12스텝 후 판정
print("\n── SabbathJudge (12스텝 창) ────────────────────────────────────────────")
runner2 = make_planet_runner(seed=0)
judge   = make_sabbath_judge(window=12)
for i in range(12):
    s = runner2.step(dt_yr=1.0)
    judge.push(s)
eq = judge.judge()
ok("V7  SabbathJudge.judge() → EquilibriumState", eq is not None)
if eq:
    print(f"  {eq}")

print(f"\n{'='*60}")
print(f"  Day7 Demo: {_passed}/{_passed+_failed} PASS  |  {_failed} FAIL")
print(f"{'='*60}")
if _failed == 0:
    print("  ✅  ALL PASS — Day7 통합 러너 동작 확인")
    print("     12개 엔진 × 12개 위도 밴드 = 전 지구 한 스텝")
else:
    print("  ❌  SOME FAILED")
    sys.exit(1)
