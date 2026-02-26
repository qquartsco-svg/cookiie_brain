# Phase 6a 수치 안정성 재검증

**날짜**: 2026-02-26

## 시나리오

| 시나리오 | dt [yr] | T_init [K] | CO₂ | 검증 |
|----------|---------|------------|-----|------|
| 극단적 dt (10 yr) | 10.0 | 250 | 400 ppm | 수렴 |
| 극단적 dt (0.001 yr) | 0.001 | 288 | 400 ppm | 수렴 |
| Cold start | 0.1 | 150 | 400 ppm | 288K 도달 |
| Hot start | 0.1 | 500 | 400 ppm | 288K 도달 |
| 조성 급변 | 0.1 | 288 | 4000 ppm | τ 증가, T 안정 |

## 결과

- linearized implicit: dt 크기에 무관 수렴
- Cold/Hot start: 300 step 내 288K ± 0.1K
- 조성 변화: τ 반영, T 연속 변화

## 수증기 피드백 (Clausius-Clapeyron)

- e_sat(T) = 611.2 × exp(17.67×T_c/(T_c+243.5))
- q_sat = 0.622 × e_sat / P
- H₂O 피드백: τ 증가 → ε_a 증가 → T 증가 → q_sat 증가 (비선형)
