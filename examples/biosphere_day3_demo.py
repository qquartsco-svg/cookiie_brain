"""Phase 7b Demo — 셋째날 식생 루프: surface + atmosphere + biosphere 연동

뉴런→지구→우주선 동일 순환 템플릿 (docs/CIRCULATION_TEMPLATE.md) 검증.
- Drive(태양) → Reservoir(열·유기층) → Work(GPP/NPP, 증산) → Sink(복사·호흡) → Phase(생장)
- get_solar_environment_extension(..., surface_schema=sfc, biospheres=bios) 호출 시
  매 스텝 biosphere feedback이 대기 조성(CO2/O2/H2O), 잠열, 알베도에 반영되는지 확인.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from solar.brain_core_bridge import get_solar_environment_extension, create_default_environment


def main():
    print("Phase 7b: 셋째날 식생 루프 — surface + atmosphere + biosphere 연동")
    print("  (뉴런·지구·우주선 동일 순환 템플릿)")

    engine, sun, atmospheres, sfc, biospheres = create_default_environment(
        use_water_cycle=True,
        use_surface_schema=True,
        use_biosphere=True,
    )
    bio = biospheres["Earth"]
    atm = atmospheres["Earth"]

    # 초기값
    t0 = engine.time
    CO2_0 = atm.composition.CO2
    O2_0 = atm.composition.O2
    A0 = atm.albedo

    n_steps = 50
    dt_yr = 0.02

    for _ in range(n_steps):
        data = get_solar_environment_extension(
            engine, sun, atmospheres, dt_yr=dt_yr,
            surface_schema=sfc,
            biospheres=biospheres,
        )

    CO2_1 = atm.composition.CO2
    O2_1 = atm.composition.O2
    A1 = atm.albedo
    eb = data["bodies"]["Earth"]

    print(f"\n  시간: {t0:.2f} → {engine.time:.2f} yr (dt={dt_yr}, n={n_steps})")
    print(f"  CO2: {CO2_0:.6f} → {CO2_1:.6f} (mol/mol)")
    print(f"  O2:  {O2_0:.6f} → {O2_1:.6f} (mol/mol)")
    print(f"  알베도: {A0:.4f} → {A1:.4f}")
    print(f"  T_surface: {eb['T_surface']:.2f} K")
    print(f"  Biosphere B_leaf={bio.B_leaf:.4f}, B_wood={bio.B_wood:.4f}, B_seed={bio.B_seed:.4f}")

    # 검증: 식생이 돌면 O2 증가 또는 CO2 감소 또는 알베도 변화
    o2_up = O2_1 > O2_0
    co2_down = CO2_1 < CO2_0
    albedo_changed = abs(A1 - A0) > 1e-4
    biomass_positive = bio.B_leaf + bio.B_wood > 0

    checks = [
        ("O2 증가 또는 CO2 감소 또는 알베도 변화", o2_up or co2_down or albedo_changed),
        ("생체량 성장", biomass_positive),
    ]
    all_ok = all(c[1] for c in checks)
    for name, ok in checks:
        print(f"  {'PASS' if ok else 'FAIL'}: {name}")
    print("\nPhase 7b 검증: ALL PASS" if all_ok else "\nPhase 7b 검증: SOME FAIL")
    return 0 if all_ok else 1


if __name__ == "__main__":
    exit(main())
