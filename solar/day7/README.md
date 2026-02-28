# Day 7 — 일곱째 날: 완성·안식 (Sabbath / Completion)

> *"하나님이 그가 하시던 일을 일곱째 날에 마치시니 그가 하시던 모든 일을 그치고 일곱째 날에 안식하시니라"*
> — 창세기 2:2

---

## 1. 포지션

```
Day1 → Day2 → Day3 → Day4 → Day5 → Day6 → Day7
빛    대기    땅/불  리듬   이동   진화   완성

Day7 = 새 기어 추가 없음
       Day1~6 전체가 하나로 돌아가는 것을 관측·판정
```

Day6까지 "창조"가 완성됐다. Day7은 그것이 **안정적으로 작동하는지 확인하는 메타 레이어**다.

---

## 2. 핵심 구조

### PlanetRunner — 통합 스텝 드라이버

```python
runner = make_planet_runner(n_bands=12, n_species=4, seed=42)
snap   = runner.step(dt_yr=1.0)   # ← 이게 "하루"
```

한 번의 `step(dt_yr)` 안에서 12개 엔진이 순서대로 실행된다:

| 순서 | 엔진 | 역할 | Day 원본 |
|------|------|------|---------|
| 1 | RhythmEngine | 장주기 리듬 (Milankovitch) | Day4 |
| 2 | AtmosphereEngine | 대기 온도·CO₂ | Day2 |
| 3 | LatitudeBands | 12개 밴드 생물권 | Day3 |
| 4 | SeasonEngine | 계절 위상·온도 편차 | Day4 |
| 5 | NitrogenEngine × 12 | 밴드별 질소 순환 | Day4 |
| 6 | OceanEngine | 조석·탄소 펌프 | Day4 |
| 7 | FoodWebEngine × 12 | 밴드별 트로픽 ODE | Day5 |
| 8 | TransportEngine | 씨드 밴드 간 확산 | Day5 |
| 9 | MutationEngine | 변이 이벤트 | Day6 |
| 10 | FeedbackEngine | Genome → 환경 피드백 | Day6 |
| 11 | NicheEngine | 자원 경쟁·점유 | Day6 |
| 12 | StressEngine | 스트레스 누적·요약 | Day3 |

**12번째 엔진(StressEngine)의 출력이 SabbathJudge로 연결된다.**

---

### SabbathJudge — 안식 판정기

```python
judge = make_sabbath_judge(window=12)
judge.push(snap)
eq = judge.judge()
# eq.is_stable → True  = 🌿 안식 (시스템 안정)
# eq.is_stable → False = ⚡ 불안정 (아직 진행 중)
```

판정 기준 3가지:

| 기준 | 임계값 | 의미 |
|------|--------|------|
| CO₂ drift | < 2.0 ppm/step | 탄소 순환 안정 |
| T drift | < 0.5 K/step | 온도 안정 |
| Stress | < 0.3 | 행성 스트레스 해소 |

`window=12` — 12개 스텝(= 12개 밴드 1 사이클)을 보고 판정.
**12지파가 모두 안정되어야 안식이 인정된다.**

---

### PlanetSnapshot — 전 지구 상태 스냅샷

```python
snap.CO2_ppm          # 전 지구 CO₂
snap.T_surface_K      # 전 지구 온도
snap.planet_stress    # 행성 스트레스 [0~1]
snap.band_T           # 12개 밴드 온도 리스트
snap.band_N_soil      # 12개 밴드 질소 리스트
snap.band_trophic     # 12개 밴드 먹이사슬 상태
snap.mutation_events  # 이 스텝 변이 이벤트 수
```

`snap.band_*` 길이는 항상 12. 각 인덱스 = 한 "지파(tribe)"의 환경 상태.

---

## 3. 12의 의미 — 이 레이어에서

```
12개 위도 밴드 (공간 분할)   ← Day3 LatitudeBands
     ×
12개 독립 엔진 (기능 분할)   ← solar/engines/
     ×
window=12 (시간 분할)        ← SabbathJudge
     ↓
PlanetRunner = 세 개의 12가 만나는 지점
```

자세한 분석 → [`docs/WHY_12_SYSTEMIC.md`](../../docs/WHY_12_SYSTEMIC.md)

---

## 4. 다음 단계 — 창세기 2장 이후

Day7이 완성됐다. 그 다음은 **에덴의 이야기**다.

```
천지창조 (Day1~7) → 에덴 시스템 (아담·이브)
                          ↓
                  12 시스템의 관리자/운영자 계승
```

→ [`docs/ADAM_EVE_SYSTEM.md`](../../docs/ADAM_EVE_SYSTEM.md) 참고

---

## 5. 파일 구조

```
solar/day7/
├── __init__.py          ← 공개 API (PlanetRunner, SabbathJudge)
├── runner.py            ← PlanetRunner — 12엔진 × 12밴드 통합 드라이버
├── sabbath.py           ← SabbathJudge — 평형·안정성 판정
├── day7_demo.py         ← V1~V7 smoke test (ALL PASS)
└── README.md            ← 이 파일
```

---

## 6. 빠른 시작

```python
from solar.day7 import make_planet_runner, make_sabbath_judge

runner = make_planet_runner()
judge  = make_sabbath_judge(window=12)

for i in range(24):          # 24스텝 = 12밴드 × 2사이클
    snap = runner.step(dt_yr=1.0)
    judge.push(snap)
    eq = judge.judge()
    if eq and eq.is_stable:
        print(f"🌿 안식 확인 — t={snap.time_yr:.0f}yr")
        break
    print(snap.summary())
```
