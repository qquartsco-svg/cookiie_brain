#!/usr/bin/env python3
"""
gaia_attractor_sim.py — 행성 항상성 (Gaia Attractor) 검증 시뮬레이션

설계 철학: 세차운동·토양·생애주기와 동일
  입력: 물리 법칙/관측값 (GPP, 분해율, 대기 피드백)
  출력: 생태계 탄소 플럭스 균형·O₂ 생성·토양 갱신이 자연스럽게 나온다

Gaia Attractor 루프 3개 (Phase 7d):
  [루프 A] 사체 분해 → CO₂ 대기 방출
    biomass 사망률 × (1-ETA) → delta_CO2 > 0 (방출)

  [루프 B] 사체 일부 → organic_layer 환류
    biomass 사망률 × ETA → organic_layer 갱신

  [루프 C] 대기 CO₂/O₂ → 생물권 env 실시간 반영 (양방향 루프)
    CO₂↑ → GPP↑ → O₂ 방출↑ → CO₂↓ (음성 피드백 attractor)

시나리오:
  [S1] 현재 지구: 빈 생태계에서 시작 → 생태계 탄소 수지 균형 확인
  [S2] 대기 CO₂ 동적 갱신: CO2·O2 실시간 피드백 작동 확인
  [S3] 저O₂ 섭동: 목본 억제 → O₂ 회복 방향 확인
  [S4] 태초 지구: CO₂ 높음·O₂=0 → 생명이 O₂를 만드는 과정

부호 규약:
  delta_CO2 > 0 : 대기 CO₂ 증가 (생물권이 방출)
  delta_CO2 < 0 : 대기 CO₂ 감소 (생물권이 흡수)
  delta_O2  > 0 : 대기 O₂ 증가 (광합성)

대기 환산:
  1 ppm CO₂ ≈ 2.13 GtC = 2.13e12 kg C (전 지구 대기)
  전 지구 육지 면적 = 1.48e14 m²
  delta_CO2 [kg C/m²_land/yr] × 1.48e14 [m²] / 2.13e12 [kg/ppm] = Δ ppm/yr

  1 ppm O₂ ≈ 3.34e12 kg O₂ (대기 O₂ 총 1.2e18 kg × 0.21 / 21ppm 환산)
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from solar.biosphere.column import BiosphereColumn

# ── 지구 대기 물리 상수 ───────────────────────────────────────────────────────
LAND_AREA_M2   = 1.48e14     # [m²] 전 지구 육지 면적 (5.1e14 × 0.29)
KG_C_PER_PPM   = 2.13e12     # [kg C] 대기 CO₂ 1ppm에 해당하는 탄소 질량
KG_O2_PER_FRAC = 1.2e18      # [kg O₂] 대기 O₂ 1 mol/mol(=100%) 해당 질량


def flux_to_co2_ppm_yr(delta_co2_kg_m2_land, land_fraction=0.29):
    """
    column.step() delta_CO2 [kg C/m²_land/yr] → 대기 CO₂ 변화율 [ppm/yr].

    주의: column에서 delta_CO2는 land_fraction으로 이미 나눠진 값.
    전 지구 플럭스 = delta_CO2 × LAND_AREA_M2  [kg C/yr]
    Δ(CO₂) [ppm/yr] = 전 지구 플럭스 / KG_C_PER_PPM
    """
    flux_global = delta_co2_kg_m2_land * LAND_AREA_M2  # [kg C/yr]
    return flux_global / KG_C_PER_PPM                  # [ppm/yr]


def flux_to_o2_frac_yr(delta_o2_kg_m2_land):
    """
    delta_O2 [kg O₂/m²_land/yr] → 대기 O₂ mixing ratio 변화율 [1/yr].
    """
    flux_global = delta_o2_kg_m2_land * LAND_AREA_M2   # [kg O₂/yr]
    return flux_global / KG_O2_PER_FRAC                 # [mol/mol /yr]


# ── 시나리오 실행 함수 ────────────────────────────────────────────────────────

def run_scenario(label, CO2_ppm_init, O2_frac_init, T=288.0, F=1361.0,
                 dt=5.0, tmax=500, print_every=50,
                 pioneer_init=3.7, organic_init=0.52, mineral_init=4.7,
                 B_seed_init=0.001, B_wood_init=0.0, B_leaf_init=0.0):
    """
    단일 시나리오 실행.
    CO2_ppm_init: 초기 CO₂ [ppm]
    O2_frac_init: 초기 O₂ [mol/mol, 0~1]
    대기 CO₂·O₂ 동적 갱신 — 루프 C.
    """
    bio = BiosphereColumn(
        body_name="Earth",
        land_fraction=0.29,
        pioneer_biomass_init=pioneer_init,
        organic_layer_init=organic_init,
        mineral_layer_init=mineral_init,
        B_seed_init=B_seed_init,
        B_wood_init=B_wood_init,
        B_leaf_init=B_leaf_init,
    )

    CO2_ppm = float(CO2_ppm_init)
    O2_frac = float(O2_frac_init)

    history = []
    t = 0.0
    steps = int(tmax / dt) + 1

    for step in range(steps):
        env = {
            "F_solar_si":    F,
            "T_surface":     T,
            "P_surface":     101325.0,
            "CO2":           max(1e-6, CO2_ppm * 1e-6),  # [루프 C] 실시간
            "H2O":           0.01,
            "O2":            max(0.0, O2_frac),           # [루프 C] 실시간
            "water_phase":   "liquid",
            "soil_moisture": 0.8,
        }

        fb = bio.step(env, dt)
        s  = bio.state()

        # ── 루프 C: 대기 CO₂·O₂ 동적 갱신 ────────────────────────────────────
        dCO2_ppm_yr = flux_to_co2_ppm_yr(fb["delta_CO2"])   # [ppm/yr]
        dO2_frac_yr = flux_to_o2_frac_yr(fb["delta_O2"])    # [1/yr]

        CO2_ppm = max(1e-6, CO2_ppm + dCO2_ppm_yr * dt)    # ppm
        O2_frac = max(0.0,  O2_frac + dO2_frac_yr * dt)
        O2_frac = min(O2_frac, 0.35)                        # 물리 상한 35%

        if int(t) % print_every == 0 or step == 0:
            history.append({
                "yr":          int(t),
                "CO2_ppm":     CO2_ppm,
                "O2_pct":      O2_frac * 100.0,
                "GPP":         fb["GPP"],
                "NPP":         fb["NPP"],
                "dCO2_ppm_yr": dCO2_ppm_yr,
                "decomp":      fb["co2_from_decomp"],
                "organic_env": fb["organic_to_soil"],
                "B_wood":      s.B_wood,
                "B_fruit":     s.B_fruit,
                "organic":     s.organic_layer,
                "net_C_sign":  "흡수" if fb["delta_CO2"] < 0 else "방출",
            })

        if t >= tmax:
            break
        t += dt

    return history


# ── 출력 헬퍼 ─────────────────────────────────────────────────────────────────

def print_scenario_header(label, CO2_ppm_init, O2_frac_init, T=288.0, F=1361.0):
    print()
    print("=" * 85)
    print(f"  시나리오: {label}")
    print(f"  초기 조건: CO₂={CO2_ppm_init:.0f} ppm, O₂={O2_frac_init*100:.1f}%, "
          f"T={T-273:.0f}°C, F={F:.0f} W/m²")
    print("=" * 85)
    print(f"  {'년':>5}  {'CO₂(ppm)':>10}  {'O₂(%)':>7}  {'GPP':>5}  {'NPP':>5}"
          f"  {'dCO₂/yr':>9}  {'분해CO₂':>8}  {'B_wood':>7}  C수지")
    print("  " + "-" * 79)


def print_scenario_row(h):
    print(f"  {h['yr']:>5}  {h['CO2_ppm']:>10.1f}  {h['O2_pct']:>7.3f}"
          f"  {h['GPP']:>5.3f}  {h['NPP']:>5.3f}"
          f"  {h['dCO2_ppm_yr']:>9.2f}  {h['decomp']:>8.4f}"
          f"  {h['B_wood']:>7.3f}  {h['net_C_sign']}")


def print_summary(first, last):
    print()
    print(f"  ★ 수렴 결과 ({last['yr']}년):")
    print(f"    CO₂: {first['CO2_ppm']:.1f} → {last['CO2_ppm']:.1f} ppm  "
          f"(Δ={last['CO2_ppm']-first['CO2_ppm']:+.1f})")
    print(f"    O₂:  {first['O2_pct']:.3f} → {last['O2_pct']:.3f} %  "
          f"(Δ={last['O2_pct']-first['O2_pct']:+.3f})")
    print(f"    분해 CO₂: {last['decomp']:.4f} kg C/m²/yr  ← 루프 A 작동 ✓")
    print(f"    토양 환류: {last['organic_env']:.4f} kg C/m²/yr  ← 루프 B 작동 ✓")
    print(f"    B_wood: {last['B_wood']:.3f} kg C/m²  |  organic: {last['organic']:.2f} kg C/m²")


# ── 시나리오 1: 빈 생태계 → 탄소 수지 추적 ──────────────────────────────────

print("=" * 85)
print("  행성 항상성 (Gaia Attractor) 시뮬레이션 — Phase 7d")
print("  이끼·나무가 태어나고 죽고 썩고 다시 자라면서 CO₂·O₂를 스스로 조절")
print()
print("  루프 A: 사체 분해 → CO₂ 대기 방출  (탄소 순환 닫힘)")
print("  루프 B: 사체 일부 → organic_layer  (토양 갱신 유지)")
print("  루프 C: 대기 CO₂/O₂ → GPP·f_O2 실시간 반영  (음성 피드백)")
print("=" * 85)

results = {}

# ── S1: 현재 지구 — 빈 생태계에서 출발 ──────────────────────────────────────
label1 = "S1: 현재 지구 — 빈 생태계 → 균형 탄소 수지"
print_scenario_header(label1, 400.0, 0.21)
h1 = run_scenario(label1, CO2_ppm_init=400.0, O2_frac_init=0.21,
                  B_wood_init=0.0, B_leaf_init=0.0, dt=5, tmax=500)
for h in h1:
    print_scenario_row(h)
print_summary(h1[0], h1[-1])
results["S1"] = h1

# ── S2: 성숙 생태계 — 분해 vs 흡수 균형 확인 ────────────────────────────────
label2 = "S2: 성숙 생태계 (나무 3.5kg/m²) — 분해 CO₂ vs 광합성 흡수"
print_scenario_header(label2, 400.0, 0.21)
h2 = run_scenario(label2, CO2_ppm_init=400.0, O2_frac_init=0.21,
                  B_wood_init=3.5, B_leaf_init=1.0, dt=5, tmax=500)
for h in h2:
    print_scenario_row(h)
print_summary(h2[0], h2[-1])
results["S2"] = h2

# ── S3: 저O₂ 섭동 (O₂=5%) ─────────────────────────────────────────────────
label3 = "S3: 저O₂ 섭동 (O₂=5%) → 목본 성장 억제 → O₂ 점진 회복"
print_scenario_header(label3, 400.0, 0.05)
h3 = run_scenario(label3, CO2_ppm_init=400.0, O2_frac_init=0.05,
                  B_wood_init=0.0, B_leaf_init=0.0, dt=5, tmax=500)
for h in h3:
    print_scenario_row(h)
print_summary(h3[0], h3[-1])
results["S3"] = h3

# ── S4: 태초 지구 — CO₂=1%, O₂=0 → 생명이 O₂를 만드는 과정 ────────────────
label4 = "S4: 태초 지구 (CO₂=1%, O₂=0) → 생명이 대기를 만든다"
print_scenario_header(label4, 10000.0, 0.0)
h4 = run_scenario(label4, CO2_ppm_init=10000.0, O2_frac_init=0.0,
                  B_wood_init=0.0, B_leaf_init=0.0, dt=5, tmax=500)
for h in h4:
    print_scenario_row(h)
print_summary(h4[0], h4[-1])
results["S4"] = h4

# ── 항상성 검증 ───────────────────────────────────────────────────────────────

print()
print("=" * 85)
print("  Gaia Attractor 항상성 검증")
print("-" * 85)

checks = []

# 검증 1: 루프 A — 분해 CO₂ > 0 (탄소 순환 닫힘)
ok1 = results["S2"][-1]["decomp"] > 0.0
checks.append(("루프 A: 사체 분해 CO₂ > 0 (탄소 순환 닫힘)", ok1,
               f"{results['S2'][-1]['decomp']:.4f} kg C/m²/yr"))

# 검증 2: 루프 B — organic_layer 유지/증가 (토양 환류)
ok2 = results["S2"][-1]["organic"] >= results["S2"][0]["organic"]
checks.append(("루프 B: organic_layer 유지 (토양 환류)", ok2,
               f"{results['S2'][0]['organic']:.3f} → {results['S2'][-1]['organic']:.3f} kg C/m²"))

# 검증 3: 루프 C — O₂ 생성 (광합성 → O₂ 방출)
ok3 = results["S1"][-1]["O2_pct"] > results["S1"][0]["O2_pct"]
checks.append(("루프 C: O₂ 생성 (광합성 → 대기 O₂ 증가)", ok3,
               f"{results['S1'][0]['O2_pct']:.3f} → {results['S1'][-1]['O2_pct']:.3f} %"))

# 검증 4: 고CO₂ → GPP 증가 (루프 C 음성 피드백 방향)
ok4 = results["S4"][0]["GPP"] >= results["S1"][0]["GPP"] * 0.9  # S4가 고CO₂라 GPP 높거나 비슷
checks.append(("루프 C: 고CO₂(S4) → GPP ≥ 현재지구(S1) × 0.9", ok4,
               f"S4 GPP={results['S4'][0]['GPP']:.4f}, S1 GPP={results['S1'][0]['GPP']:.4f}"))

# 검증 5: S4 O₂ 생성 (태초 지구 → O₂ 방출 시작)
ok5 = results["S4"][-1]["O2_pct"] > results["S4"][0]["O2_pct"]
checks.append(("S4 태초 지구 → O₂ 생성 시작 (생명이 대기를 만든다)", ok5,
               f"{results['S4'][0]['O2_pct']:.4f} → {results['S4'][-1]['O2_pct']:.4f} %"))

# 검증 6: S3 저O₂에서 성장 차이 — f_O2 억제 작동
ok6 = results["S3"][-1]["B_wood"] <= results["S1"][-1]["B_wood"]  # 저O₂=목본 억제
checks.append(("S3 저O₂ → 목본 성장 억제 (f_O2 게이트)", ok6,
               f"S3 B_wood={results['S3'][-1]['B_wood']:.3f}, "
               f"S1 B_wood={results['S1'][-1]['B_wood']:.3f}"))

print()
all_pass = True
for desc, ok, detail in checks:
    status = "PASS ✓" if ok else "FAIL ✗"
    if not ok:
        all_pass = False
    print(f"  [{status}] {desc}")
    print(f"           → {detail}")

print()
if all_pass:
    print("  ★★★ ALL PASS — Gaia Attractor 항상성 3루프 모두 확인!")
    print()
    print("  세차운동과 동일한 방식:")
    print("    세차:   G·M·r  입력 → 25,000년 주기")
    print("    토양:   R·W·ETA·λ 입력 → 2739년 원시토양")
    print("    생애주기: K_germ·K_gate 입력 → 씨→열매 전이")
    print("    항상성: 루프A(분해)·루프B(토양)·루프C(대기↔생물) → 항상성")
    print()
    print("  씨앗들이 뿌려지고 — 자연스레 씨앗이 자라나는 환경 상태가 유지된다.")
else:
    print("  일부 FAIL — 파라미터 조정 필요")
print("=" * 85)
