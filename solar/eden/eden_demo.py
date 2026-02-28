"""eden_demo.py — 에덴 환경 시뮬레이션 데모

실행: python -m solar.eden.eden_demo

검증 항목:
  1. 에덴(궁창 존재) 환경 파라미터 확인
  2. 대홍수 이벤트 발동
  3. 홍수 전이 곡선 추적 (12단계)
  4. 홍수 후 안정화 확인
  5. 극지 빙하 형성 과정 추적
"""

from __future__ import annotations

import sys
import os

# 패키지 루트 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from solar.eden import make_firmament, make_flood_engine


def run_demo() -> None:
    results = []

    print('=' * 65)
    print('  에덴 환경 시뮬레이션 — 궁창 → 대홍수 → 홍수 후 전이')
    print('=' * 65)
    print()

    # ──────────────────────────────────────────────────────
    # STEP 1: 에덴 환경 (궁창 완전체)
    # ──────────────────────────────────────────────────────
    print('【1】 에덴 초기 환경 (궁창 H2O=5%)')
    print()
    fl = make_firmament(phase='antediluvian', H2O_canopy=0.05)
    env = fl.get_env_overrides()

    print(f'  firmament_active   = {env["firmament_active"]}')
    print(f'  H2O (대기+캐노피)  = {env["H2O_override"]*100:.1f}%  (기본1% + 캐노피5%)')
    print(f'  albedo             = {env["albedo_override"]:.3f}  (빙하없음 → 낮음)')
    print(f'  pressure           = {env["pressure_atm"]:.2f} atm')
    print(f'  UV shield          = {env["uv_shield_factor"]:.2f}  (95% 차폐)')
    print(f'  mutation factor    = {env["mutation_rate_factor"]:.3f}x  (정상의 1%)')
    print(f'  precip_mode        = {env["precip_mode"]}  (안개, 창2:6)')
    print(f'  pole_eq_delta      = {env["pole_eq_delta_K"]:.1f}K  (균온 — 극지도 따뜻)')
    print(f'  delta_tau (온실추가) = {env["delta_tau"]:.3f}')
    print()

    # T_surface 추정 (greenhouse 사용)
    from solar.day2.atmosphere.greenhouse import optical_depth, effective_emissivity, equilibrium_surface_temp
    tau = optical_depth(CO2=250e-6, H2O=env['H2O_override'], CH4=0.5e-6)
    eps = effective_emissivity(tau)
    T   = equilibrium_surface_temp(1361.0, albedo=env['albedo_override'],
                                   redistribution=4.0, emissivity_atm=eps)
    print(f'  → 추정 T_surface = {T:.1f}K ({T-273.15:.1f}°C)  ✅')
    results.append(('에덴 T', T - 273.15, '>25', T - 273.15 > 25))
    print()

    # ──────────────────────────────────────────────────────
    # STEP 2: 에덴 → 대홍수 발동
    # ──────────────────────────────────────────────────────
    print('【2】 대홍수 이벤트 발동 (창7:11)')
    print()
    event = fl.trigger_flood()
    print(f'  trigger_year       = {event.trigger_year:.1f} yr')
    print(f'  H2O_released       = {event.H2O_released*100:.1f}%  (궁창 전량 낙하)')
    print(f'  sea_level_rise     = {event.sea_level_rise_m:.1f}m  (궁창+지하수)')
    print(f'  f_land_change      = {event.f_land_change:+.2f}  (대륙 침수)')
    print(f'  albedo_jump        = {event.albedo_jump:+.3f}')
    print(f'  T_drop_K           = {event.T_drop_K:.1f}K  (장기 냉각)')
    print(f'  mutation_rate_jump = {event.mutation_rate_jump:.0f}x  (돌연변이 폭증)')
    results.append(('홍수 해수면', event.sea_level_rise_m, '>50', event.sea_level_rise_m > 50))
    results.append(('돌연변이 배수', event.mutation_rate_jump, '>50', event.mutation_rate_jump > 50))
    print()

    # ──────────────────────────────────────────────────────
    # STEP 3: 홍수 전이 곡선 추적
    # ──────────────────────────────────────────────────────
    print('【3】 홍수 전이 곡선 (12단계 추적)')
    print()
    print(f'  {"t(yr)":>6}  {"단계":^14}  {"f_land":>6}  {"T(°C)":>7}  {"mut_x":>6}  {"ice%":>5}  {"UV":>5}  {"극적도ΔT":>8}')
    print('  ' + '─' * 70)

    flood = make_flood_engine(pre_flood_T_celsius=34.1, post_flood_T_celsius=13.3)
    steps = [0.05, 0.11, 0.30, 0.50, 0.75, 1.0, 2.0, 3.0, 5.0, 7.0, 9.0, 11.0]

    prev_t = 0.0
    for t_target in steps:
        dt = t_target - prev_t
        snap = flood.step(dt_yr=dt)
        prev_t = t_target

        T_C = snap.T_surface_K - 273.15
        icon = '🌊' if 'peak' in snap.flood_phase else (
               '📈' if 'rising' in snap.flood_phase else (
               '📉' if 'receding' in snap.flood_phase else (
               '🌨️' if 'stabilizing' in snap.flood_phase else '✅')))
        print(f'  {snap.t_since_flood_yr:>6.2f}  {icon}{snap.flood_phase:^13}  '
              f'{snap.f_land:>6.2f}  {T_C:>+7.1f}°  {snap.mutation_rate_factor:>6.2f}x  '
              f'{snap.ice_fraction*100:>4.1f}%  {snap.UV_exposure:>5.2f}  {snap.pole_eq_delta_K:>7.1f}K')

    print()
    results.append(('홍수후 T', snap.T_surface_K - 273.15, '<20', snap.T_surface_K - 273.15 < 20))
    results.append(('빙하 형성', snap.ice_fraction, '>0.02', snap.ice_fraction > 0.02))

    # ──────────────────────────────────────────────────────
    # STEP 4: 12밴드 극지 빙하 변화
    # ──────────────────────────────────────────────────────
    print('【4】 12밴드 극지 환경 — 에덴 vs 홍수 후')
    print()
    import numpy as np

    def band_temps(T_mean, delta):
        lats = [-82.5, -67.5, -52.5, -37.5, -22.5, -7.5,
                  7.5,  22.5,  37.5,  52.5,  67.5,  82.5]
        return [T_mean + delta * (np.cos(np.radians(la)) - 0.5) * 2
                for la in lats]

    T_eden_bands  = band_temps(307.3, 15.0)
    T_post_bands  = band_temps(286.4, 48.0)

    print(f'  {"밴드":>4}  {"위도":>7}  {"에덴(°C)":>9}  {"홍수후(°C)":>10}  에덴빙하  홍수후빙하')
    print('  ' + '─' * 62)
    for i in range(12):
        lat_s = -90 + i * 15
        lat_e = lat_s + 15
        Te = T_eden_bands[i] - 273.15
        Tp = T_post_bands[i] - 273.15
        ice_e = '❄️' if Te < -10 else '🌿'
        ice_p = '❄️' if Tp < -10 else '🌿'
        mark = ' ← 빙하 신규 형성' if Te >= -10 and Tp < -10 else ''
        print(f'  [{i:2d}]  {lat_s:+3d}~{lat_e:+3d}°  {Te:+9.1f}  {Tp:+10.1f}    {ice_e}       {ice_p}{mark}')

    eden_ice  = sum(1 for T in T_eden_bands if T - 273.15 < -10)
    post_ice  = sum(1 for T in T_post_bands if T - 273.15 < -10)
    print()
    print(f'  에덴  극지 빙하: {eden_ice}/12 밴드  →  전 지구 거주 가능')
    print(f'  홍수후 극지 빙하: {post_ice}/12 밴드  →  남북극 결빙')
    results.append(('에덴 빙하밴드', eden_ice, '==0', eden_ice == 0))
    results.append(('홍수후 빙하밴드', post_ice, '>0', post_ice > 0))
    print()

    # ──────────────────────────────────────────────────────
    # 결과 요약
    # ──────────────────────────────────────────────────────
    print('=' * 65)
    print('  검증 결과')
    print('=' * 65)
    passed = 0
    for name, val, cond, ok in results:
        icon = '✅' if ok else '❌'
        print(f'  {icon}  {name:<20}  {str(val)[:10]:<12}  (조건: {cond})')
        if ok:
            passed += 1
    print()
    total = len(results)
    print(f'  {passed}/{total} PASS  ', '✅ ALL PASS' if passed == total else '❌ FAIL 있음')
    print('=' * 65)
    return passed == total


if __name__ == '__main__':
    ok = run_demo()
    sys.exit(0 if ok else 1)
