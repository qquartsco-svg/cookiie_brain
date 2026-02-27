"""토양 형성 시뮬레이션 — 세차운동과 같은 방식: 물리 수식 → 결과가 나온다

세차운동:  τ = (3GM/r³)(C−A)(ŝ·r̂)(r̂×ŝ)  → G, M 넣으면 25,000년이 나온다
토양형성:  로지스틱 성장 + 풍화 + Q10 분해  → 관측 파라미터 넣으면 수백~수천년이 나온다

ODE 3개:
  d(pioneer)/dt = R · P · (1 - P/K(S)) · fT · fW  -  M · P
                  [로지스틱 성장]                       [사망]
                  K(S) = K0 + K_soil · S  ← 토양 쌓일수록 수용력 증가 (양성 피드백)

  d(mineral)/dt = W_weathering · P · fT · fW
                  [pioneer가 암석을 깎아냄 — 풍화]

  d(organic)/dt = ETA · M · P                  (사체 → humus)
                + W_mineral_humus · mineral     (광물이 humus 안정화 기여)
                - λ(T) · organic                (분해, Q10 온도 의존)

임계점: organic >= ORGANIC_THRESHOLD → 식물 착근 가능한 원시 토양
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from solar.day3.biosphere.pioneer import (
    d_pioneer_dt, lambda_decay, carrying_capacity,
)
from solar.day3.biosphere._constants import (
    ORGANIC_THRESHOLD, R_PIONEER, M_PIONEER,
    K0_CARRYING, K_SOIL_FEEDBACK,
    W_WEATHERING, W_MINERAL_HUMUS,
    ETA_ORGANIC, LAMBDA_DECAY,
)

# ── 지구 환경 조건 ────────────────────────────────────────────────
T_SURFACE   = 288.0    # [K] 지구 평균 지표 온도
WATER_PHASE = "liquid" # 액체 물 존재
H2O         = 0.01     # 대기 수증기

# ── 시뮬레이션 설정 ───────────────────────────────────────────────
DT_YR   = 1.0
MAX_YR  = 5000.0

# ── 초기 상태: 완전히 척박한 돌땅 ────────────────────────────────
pioneer = 0.001  # [kg C/m²] 극소량 (바람에 날아온 포자)
mineral = 0.0    # [kg/m²]   풍화 광물 없음
organic = 0.0    # [kg C/m²] 유기층 없음


def fmt_bar(val, max_val, width=18):
    n = int(min(max(val, 0.0) / max(max_val, 1e-30), 1.0) * width)
    return "█" * n + "·" * (width - n)


def stage_name(p, m, s):
    if s >= ORGANIC_THRESHOLD:
        return "★ 원시토양 완성"
    if s > ORGANIC_THRESHOLD * 0.3:
        return "  humus 축적 중"
    if m > 0.01:
        return "  풍화 진행 중"
    if p > 0.005:
        return "  pioneer 착생"
    return "  돌땅"


def should_print(t):
    if t <= 100:   return int(t) % 10 == 0
    if t <= 500:   return int(t) % 25 == 0
    if t <= 2000:  return int(t) % 100 == 0
    return int(t) % 200 == 0


def main():
    global pioneer, mineral, organic

    print()
    print("=" * 78)
    print("  토양 형성 시뮬레이션 (물리 기반 ODE — 세차운동과 동일한 설계)")
    print(f"  임계값: organic >= {ORGANIC_THRESHOLD} kg C/m²  →  식물 착근 가능 원시 토양")
    print()
    print("  ODE:")
    print("   dP/dt = R·P·(1-P/K(S))·fT·fW - M·P      K(S)=K0+K_soil·S [양성피드백]")
    print("   dM/dt = W_w·P·fT·fW                       [풍화: pioneer→광물]")
    print("   dS/dt = ETA·M·P + W_mh·M_min - lambda(T)·S  [Q10 온도의존 분해]")
    print()
    print(f"  파라미터: R={R_PIONEER}/yr, M={M_PIONEER}/yr, K0={K0_CARRYING}, Ksoil={K_SOIL_FEEDBACK}")
    print(f"            W_w={W_WEATHERING}, W_mh={W_MINERAL_HUMUS}, ETA={ETA_ORGANIC}")
    print(f"            λ_base={LAMBDA_DECAY}/yr, T={T_SURFACE}K → λ(T)={lambda_decay(T_SURFACE):.5f}/yr")
    print("=" * 78)
    print()
    print(f"  {'년':>6}  {'pioneer':>9}  {'mineral':>9}  {'organic (humus)':>26}  {'K':>6}  단계")
    print("  " + "-" * 76)

    t = 0.0
    threshold_reached = False
    threshold_yr = None

    while t <= MAX_YR:
        K = carrying_capacity(organic)
        just_reached = (not threshold_reached) and (organic >= ORGANIC_THRESHOLD)

        if just_reached:
            threshold_reached = True
            threshold_yr = t
            print()
            print("  " + "★" * 39)
            print(f"  ★  토양 형성 임계점 도달:  {t:.0f} 년")
            print(f"  ★  pioneer  = {pioneer:.4f} kg C/m²")
            print(f"  ★  mineral  = {mineral:.3f}  kg/m²")
            print(f"  ★  organic  = {organic:.4f} kg C/m²  (임계 {ORGANIC_THRESHOLD})")
            print(f"  ★  K(토양)  = {K:.4f} kg C/m²")
            print("  ★  → 광합성 식물이 착근할 수 있는 원시 토양")
            print("  " + "★" * 39)
            print()

        if should_print(t) or just_reached:
            bar = fmt_bar(organic, ORGANIC_THRESHOLD)
            print(
                f"  {t:>6.0f}  "
                f"{pioneer:>9.5f}  "
                f"{mineral:>9.4f}  "
                f"{organic:>8.5f} [{bar}]  "
                f"{K:>6.4f}  "
                f"{stage_name(pioneer, mineral, organic)}"
            )

        if threshold_reached and t > threshold_yr + 100:
            break

        # ODE 진화 (Euler, dt=1yr)
        dp, ds, dm = d_pioneer_dt(pioneer, organic, mineral, T_SURFACE, WATER_PHASE, H2O)
        pioneer = max(0.0, pioneer + dp * DT_YR)
        mineral = max(0.0, mineral + dm * DT_YR)
        organic = max(0.0, organic + ds * DT_YR)
        t += DT_YR

    print()
    print("=" * 78)
    if threshold_reached:
        print(f"  토양 임계 도달: {threshold_yr:.0f} 년\n")
        print("  물리 흐름:")
        print("    [돌땅]  →  pioneer(지의류·균사·이끼) 포자 착생")
        print("    pioneer 로지스틱 성장  +  풍화(W_w) → mineral 축적")
        print("    사체(ETA) + mineral 안정화(W_mh) → organic(humus) 축적")
        print("    organic 쌓일수록 K(토양) 증가 → pioneer 더 많이 → 가속")
        print(f"    → organic >= {ORGANIC_THRESHOLD} 도달  ({threshold_yr:.0f}년)")
        print()
        print("  세차운동과 같은 방식:")
        print("    세차: G·M·r 넣음 → 25,000년 주기가 나온다")
        print(f"    토양: R·W·ETA·λ 넣음 → {threshold_yr:.0f}년이 나온다")
    else:
        print(f"  {MAX_YR:.0f}년 내 임계 미달. organic={organic:.5f}")
    print()


if __name__ == "__main__":
    main()
