#!/usr/bin/env python3
"""
plant_lifecycle_sim.py — 씨→싹→줄기→나무→열매 생애주기 시뮬레이션

설계 철학: 세차운동·토양 ODE와 동일
  입력: NPP 분배율, Phase Gate 파라미터 (K_germ, K_sprout_to_stem, ...)
  출력: 생애주기 전이가 자연스럽게 나온다

Phase Gate 흐름:
  B_seed → (발아 게이트) → B_sprout → (sigmoid) → B_stem
         → (sigmoid) → B_wood → (성숙+O₂) → B_fruit → B_seed (순환)

시뮬레이션 조건:
  - 토양 완성 후 상태에서 시작 (organic=0.5, 즉 2739년 이후)
  - T=288K, F=1361 W/m², CO2=400ppm, O2=0.21 (현재 대기)
  - dt=1yr, max=500yr
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from solar.biosphere.column import BiosphereColumn

# ── 시뮬레이션 설정 ──────────────────────────────────────────────────────────

DT   = 1.0     # [yr]
TMAX = 500     # [yr]

# 토양 완성 후 상태로 시작 (2739년 이후)
bio = BiosphereColumn(
    body_name="Earth",
    land_fraction=0.29,
    pioneer_biomass_init=3.7,   # 2739년 시점 pioneer
    organic_layer_init=0.52,    # 토양 임계 넘은 상태
    mineral_layer_init=4.7,
    B_seed_init=0.001,          # 씨앗 최소값으로 시작
)

# 환경 (현재 지구 기준)
ENV = {
    "F_solar_si":  1361.0,
    "T_surface":   288.0,
    "P_surface":   101325.0,
    "CO2":         400e-6,
    "H2O":         0.01,
    "O2":          0.21,
    "water_phase": "liquid",
    "soil_moisture": 0.8,
}

# ── 출력 헤더 ────────────────────────────────────────────────────────────────

print("=" * 80)
print("  식물 생애주기 시뮬레이션 — Phase Gate ODE")
print("  씨(B_seed) → 싹(B_sprout) → 줄기(B_stem) → 나무(B_wood) → 열매(B_fruit)")
print()
print("  시작 조건: 토양 완성 직후 (organic=0.52 kg C/m², 씨앗 0.001)")
print("=" * 80)
print()
print(f"{'년':>6}  {'B_seed':>8}  {'B_sprout':>9}  {'B_stem':>8}  {'B_wood':>8}  {'B_fruit':>8}  {'B_leaf':>8}  단계")
print("-" * 80)

# 단계 판정
def stage_label(b):
    if b.B_fruit > 0.01:
        return "★ 열매 맺힘"
    elif b.B_wood > 0.1:
        return "나무 성장 중"
    elif b.B_stem > 0.01:
        return "줄기 형성 중"
    elif b.B_sprout > 0.001:
        return "싹 발아 중"
    elif b.B_seed > 0.0001:
        return "씨 준비 중"
    else:
        return "토양 준비"

# 이정표 기록
milestones = {
    "sprout": None, "stem": None, "wood": None, "fruit": None
}

PRINT_YEARS = set(list(range(0, 51, 5)) + list(range(50, 201, 10)) + list(range(200, 501, 25)))

# ── 메인 루프 ────────────────────────────────────────────────────────────────
t = 0.0
for step in range(int(TMAX / DT) + 1):
    s = bio.state()
    yr = int(t)

    # 이정표 기록
    if milestones["sprout"] is None and s.B_sprout > 0.001:
        milestones["sprout"] = yr
    if milestones["stem"] is None and s.B_stem > 0.01:
        milestones["stem"] = yr
    if milestones["wood"] is None and s.B_wood > 0.1:
        milestones["wood"] = yr
    if milestones["fruit"] is None and s.B_fruit > 0.01:
        milestones["fruit"] = yr

    if yr in PRINT_YEARS:
        label = stage_label(s)
        print(f"{yr:>6}  {s.B_seed:>8.4f}  {s.B_sprout:>9.4f}  {s.B_stem:>8.4f}"
              f"  {s.B_wood:>8.4f}  {s.B_fruit:>8.4f}  {s.B_leaf:>8.4f}  {label}")

    if t >= TMAX:
        break
    bio.step(ENV, DT)
    t += DT

# ── 결과 요약 ────────────────────────────────────────────────────────────────
print()
print("=" * 80)
print("  생애주기 이정표")
print("-" * 80)
for key, yr in milestones.items():
    label = {"sprout":"싹 발아", "stem":"줄기 형성", "wood":"나무 성장", "fruit":"열매 맺힘"}[key]
    if yr is not None:
        print(f"  {label:12s}: {yr:4d} 년")
    else:
        print(f"  {label:12s}: (미달)")
print()
print("  Phase Gate 흐름:")
print("    B_seed → (K_germ × g_soil × g_T × f_W) → B_sprout")
print("    B_sprout → (K_sprout_to_stem × sigmoid(B_sprout/B_sprout_half)) → B_stem")
print("    B_stem   → (K_stem_to_wood   × sigmoid(B_stem/B_stem_half))   → B_wood")
print("    B_wood   → (K_fruit × wood_maturity × f_O2)                   → B_fruit")
print("    B_fruit  → (K_fruit_to_seed)                                  → B_seed ↺")
print()
print("  세차운동과 같은 방식:")
print("    세차: G·M·r    입력 → 25,000년 주기")
print("    토양: R·W·ETA·λ 입력 → 2739년 원시토양")
print("    생애주기: K_germ·K_gate·NPP 입력 → 씨→열매 전이가 자연스럽게")
print("=" * 80)
