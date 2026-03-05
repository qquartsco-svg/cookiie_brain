"""eden_search_demo.py — 에덴 탐색 엔진 데모

실행:
    python -m solar.eden.eden_search_demo
"""

from solar._03_eden_os_underworld.eden.search import (
    make_eden_search,
    make_antediluvian_space,
    make_postdiluvian_space,
    EdenCriteria,
)
from solar._03_eden_os_underworld.eden.initial_conditions import make_antediluvian, make_postdiluvian
from solar._03_eden_os_underworld.eden.biology import compute_biology, compare_biology

BANNER = """
╔══════════════════════════════════════════════════════════════╗
║          에덴 탐색 엔진 (Eden Search Engine) v1.0           ║
║  "에덴은 좌표가 아니라 파라미터 상태(state basin)이다"       ║
╚══════════════════════════════════════════════════════════════╝
"""

def main():
    print(BANNER)

    # ── 1. 에덴 vs 현재 빠른 비교 ────────────────────────────────────────────
    print("【1】 에덴 vs 현재 지구 — 에덴 점수 비교\n")
    engine = make_eden_search(phase='antediluvian', verbose=False)
    engine.compare_phases()

    # ── 2. 에덴 시대 탐색 ────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("【2】 에덴 시대 파라미터 공간 탐색 (antediluvian)\n")

    space = make_antediluvian_space()
    print(f"  탐색 공간: ~{space.total_combinations():,}개 조합")
    print("  조건: 전 지구 빙하=0, T=15~45°C, GPP≥3.0, mutation≤10%\n")

    engine_a = make_eden_search(phase='antediluvian', verbose=True)
    result_a = engine_a.search(space=space, max_candidates=20, min_score=0.55)

    if result_a.candidates:
        print("\n상위 5개 에덴 후보:")
        for c in result_a.top(5):
            print(c.summary())
            print()

        print(result_a.band_heatmap())

        # Grid Engine 연동 (있으면)
        try:
            from solar.bridge import grid_engine_bridge
            if result_a.grid_agent is not None:
                ag = result_a.grid_agent
                band_lats = [-82.5,-67.5,-52.5,-37.5,-22.5,-7.5, 7.5, 22.5, 37.5, 52.5, 67.5, 82.5]
                b = ag.get_band_index()
                print("\n  [Grid Engine 연동] 에덴 최적 밴드 → Grid 2D 위도축 에이전트")
                print(f"    포커스 밴드 = {b}  (위도 {band_lats[b]:+.1f}°)")
                b1 = ag.step(velocity_lat=0.3)
                print(f"    step(velocity_lat=0.3) 후 밴드 = {b1}  (위도 {band_lats[b1]:+.1f}°)")
        except Exception:
            pass

    # ── 3. 현재 지구 탐색 (비교용) ───────────────────────────────────────────
    print("\n" + "=" * 60)
    print("【3】 현재 지구 탐색 (postdiluvian) — 에덴 상태 가능한가?\n")

    space_p = make_postdiluvian_space()
    engine_p = make_eden_search(phase='postdiluvian', verbose=True)
    result_p = engine_p.search(space=space_p, max_candidates=10, min_score=0.30)

    if result_p.candidates:
        print("\n현재 지구 최우선 후보:")
        print(result_p.best.summary())
    else:
        print("  → 현재 지구 조건에서 에덴 기준 통과 없음 (예상된 결과)")

    # ── 4. 결론 ──────────────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("【4】 탐색 결론\n")

    eden_score = result_a.best.score if result_a.best else 0.0
    post_score = result_p.best.score if result_p.best else 0.0

    print(f"  에덴 시대 최고 점수: {eden_score:.3f}")
    print(f"  현재 지구 최고 점수: {post_score:.3f}")
    print(f"  에덴 우위: {eden_score - post_score:+.3f}")
    print()

    if result_a.best:
        b = result_a.best
        T_C = b.ic.T_surface_K - 273.15
        print("  최적 에덴 파라미터:")
        print(f"    CO2     = {b.ic.CO2_ppm:.0f} ppm")
        print(f"    H2O(대기)= {b.ic.H2O_atm_frac*100:.1f}%")
        print(f"    H2O(궁창)= {b.ic.H2O_canopy*100:.1f}%")
        print(f"    O2      = {b.ic.O2_frac*100:.1f}%")
        print(f"    albedo  = {b.ic.albedo:.3f}")
        print(f"    f_land  = {b.ic.f_land:.2f}")
        print(f"    UV차폐  = {b.ic.UV_shield:.2f}")
        print(f"    T_surface = {T_C:.1f}°C")
        print(f"    GPP     = {b.ic.band.GPP.sum():.2f} kg C/m²/yr")
        print(f"    빙하    = {b.ic.band.ice_mask.sum()}/12 밴드")
        print(f"    mutation= {b.ic.mutation_factor:.4f}x")
        print()

        # 최고 에덴 점수 밴드
        best_band_idx = b.band_eden_score.index(max(b.band_eden_score))
        band_lats = [-82.5,-67.5,-52.5,-37.5,-22.5,-7.5,
                       7.5, 22.5, 37.5, 52.5, 67.5, 82.5]
        print(f"  최적 에덴 위도 밴드: {band_lats[best_band_idx]:+.1f}°  "
              f"(score={max(b.band_eden_score):.3f})")

    # ── 5. 생물학 레이어 ──────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("【5】 에덴 생물학 레이어 — 물리 환경 → 생물 특성\n")

    ic_eden = make_antediluvian()
    ic_post = make_postdiluvian()

    print(compare_biology(ic_eden, ic_post))
    print()

    # 최적 에덴 후보 → 생물학 계산
    if result_a.best:
        print("  최적 에덴 후보 생물학 상세:")
        bio = compute_biology(result_a.best.ic)
        print(bio.summary())
        print()
        print("  위도밴드별 수명 분포:")
        band_lats = [-82.5, -67.5, -52.5, -37.5, -22.5, -7.5,
                       7.5,  22.5,  37.5,  52.5,  67.5,  82.5]
        for i, (lat, ls) in enumerate(zip(band_lats, bio.band_lifespan)):
            if ls > 0:
                bar = "█" * int(ls / 10)
                print(f"    {lat:+6.1f}°  {ls:5.0f}yr  {bar}")

    print()
    print("  에덴 탐색 완료.")
    print("  결과를 docs/EDEN_SEARCH_RESULT.md 에 저장하려면 result.save() 호출.")
    print("=" * 60)


if __name__ == '__main__':
    main()
