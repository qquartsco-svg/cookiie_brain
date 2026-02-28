# 대홍수 전후 지구 환경 — 3단계 설정

**한 줄 결론**:
궁창(Raqia)의 존재와 붕괴는 지구 환경 파라미터의 대격변 이벤트다.
Day7 모델은 **대홍수 이후(postdiluvian)** 지구를 기준으로 한다.
에덴 시스템(solar/eden/)은 **대홍수 이전(antediluvian)** 파라미터를 구현한다.

---

## 1. 3단계 환경 타임라인

```
창세기 1장           창세기 2~6장           창세기 7장
Day1~7 완성          에덴 → 문명            대홍수 이벤트
    ↓                    ↓                      ↓
[Phase 1]           [Phase 2]              [Phase 3]
antediluvian        antediluvian           flood → postdiluvian
궁창 완전체          궁창 약화 중             궁창 붕괴
```

---

## 2. 단계별 물리 파라미터

| 파라미터 | 에덴 (창조 초기) | 홍수 직전 | 대홍수 절정 | 홍수 후 (현재) |
|---------|---------------|---------|-----------|-------------|
| **T_surface** | **35.1°C** | 28.1°C | ~39°C (일시) | **13.3°C** |
| **H2O_canopy** | **5%** | 2.5% | 붕괴 | **0%** |
| **albedo** | **0.20** | 0.22 | 0.10 | **0.306** |
| **CO2** | 250 ppm | 300 ppm | — | 280 ppm |
| **τ (광학깊이)** | **2.56** | 2.00 | — | **1.44** |
| **UV 차폐** | **95%** | 60% | 0% | **0%** |
| **돌연변이율** | **0.01×** | 0.3× | 1× | **1×** |
| **강수 방식** | **안개(mist)** | 이슬비 | 폭우 | **강우(rain)** |
| **f_land** | **0.40** | 0.38 | 0.10 | **0.29** |
| **극적도 ΔT** | **15K** | 20K | 35K | **48K** |
| **극지 빙하** | **없음 (0/12)** | 없음 | 없음 | **있음 (2/12)** |
| **대기압** | **1.25 atm** | 1.12 atm | 1.0 atm | **1.0 atm** |
| **평균 수명** | **수백 년** | 수십~수백 년 | — | **수십 년** |

---

## 3. 궁창(Raqia)의 물리 해석

### 창세기 1:6-7
> "하나님이 궁창을 만드사 궁창 위의 물과 궁창 아래의 물로 나뉘게 하시니라"

시스템 해석:
```
궁창 위의 물  →  상층 수증기 캐노피 (H2O_canopy ≈ 5%)
궁창          →  대류권과 성층권 경계 / 차폐막
궁창 아래의 물 →  강·바다·지하수 (지표 수계)
```

### 물리 효과 4가지

**① 추가 온실효과** (`delta_tau = 1.162`)
```
H2O_canopy 5% → 광학깊이 τ = 2.56
현재 H2O 1%  → 광학깊이 τ = 1.44
차이: +1.12 → T_surface +21K
```

**② UV 차폐** (`uv_shield_factor = 0.95`)
```
수증기층이 UV-B/C 흡수 → 지표 UV 95% 차단
→ DNA 손상 극소화
→ 돌연변이율 0.01× (정상의 1%)
→ 개체 수명 수백 년 가능 (아담 930세, 노아 950세)
```

**③ 강수 억제** (`precip_mode = 'mist'`)
```
창세기 2:5-6: "비가 없고 안개만 땅에서 올라와 온 지면을 적셨더라"
→ 상층 캐노피로 대기 수분 충분 → 강수 없이도 습도 유지
→ 이슬·안개로만 지표 공급
```

**④ 극지 균온화** (`pole_eq_delta_K = 15K vs 현재 48K`)
```
캐노피가 전 지구 IR 복사를 균등 포집
→ 극지-적도 온도차 15K로 억제
→ 12밴드 전체 거주 가능 (극지 포함)
→ 거대 파충류·식물 전 대륙 분포 가능
```

---

## 4. 대홍수 이벤트 (창세기 7:11)

> "큰 깊음의 샘들이 터지며 하늘의 창문들이 열려"

두 수원(水源)의 동시 분출:

| 원천 | 메커니즘 | 해수면 기여 |
|------|---------|-----------|
| 하늘의 창문 (궁창) | H2O_canopy 5% 전량 낙하 | ~0.7m |
| 깊음의 샘 (지하수) | 지각 균열 → 지하대수층 분출 | ~80m |
| **합계** | | **~80.7m** |

### 홍수 전이 곡선

```
t=0.00yr  → 궁창 붕괴 시작 (창7:11)
t=0.11yr  → 40일: 홍수 절정 (f_land=0.10, T=+39°C)
t=0.50yr  → 150일: 물 빠지기 시작 (창8:3)
t=1.00yr  → 물 완전 빠짐 (창8:14)
t=1~10yr  → 극지 냉각 + 빙하 형성
t=10yr+   → 안정화 완료 (현재 Day7 기준점)
```

### 홍수 후 3가지 새 현상

1. **극지 빙하 형성**: 균온 15K → 48K 확대 → 남북극 -22°C → 결빙
2. **강우 시작**: 안개(mist) → 강우(rain) — 구름-강수 사이클 시작
3. **무지개 등장**: 창9:13 "내가 내 무지개를 구름 속에 두었나니"
   → 최초의 강우 → 광산란 → 무지개 (물리적으로 정확)

---

## 5. 코드 구조

```
solar/eden/
├── firmament.py     ← 궁창 레이어 (FirmamentLayer)
│                       - H2O_canopy, UV_shield, mutation_factor
│                       - get_env_overrides() → PlanetRunner 주입
│                       - trigger_flood() → FloodEvent 반환
├── flood.py         ← 대홍수 전이 엔진 (FloodEngine)
│                       - 4단계 전이 곡선 (rising/peak/receding/stabilizing)
│                       - f_land, T_surface, ice_fraction 시간 함수
└── eden_demo.py     ← 7/7 ALL PASS 검증
```

### 사용법

```python
from solar.eden import make_firmament, make_flood_engine

# 에덴 환경 초기화
fl  = make_firmament(phase='antediluvian', H2O_canopy=0.05)
env = fl.get_env_overrides()
# env['mutation_rate_factor'] == 0.01
# env['precip_mode'] == 'mist'
# env['pole_eq_delta_K'] == 15.0

# 대홍수 발동
event = fl.trigger_flood()
# event.sea_level_rise_m == 80.7
# event.mutation_rate_jump == 100x

# 전이 추적
flood = make_flood_engine()
for yr in range(12):
    snap = flood.step(dt_yr=1.0)
    print(snap.flood_phase, snap.T_surface_K - 273.15)
```

---

## 6. Day7 모델과의 관계

```
Day7 PlanetRunner 기준점
  = postdiluvian (대홍수 이후)
  = H2O 1%, albedo 0.306, mutation 1.0×, 빙하 존재

에덴 시스템 (solar/eden/)
  = antediluvian (대홍수 이전)
  = FirmamentLayer → PlanetRunner 파라미터 오버라이드
  = H2O 6%, albedo 0.20, mutation 0.01×, 빙하 없음

대홍수 이벤트
  = firmament.trigger_flood() → FloodEngine
  = antediluvian → postdiluvian 전이
  = 환경 파라미터 대격변 (-21K, 빙하 형성, 돌연변이 100× 상승)
```

---

## 7. 관련 문서

- [`docs/WHY_12_SYSTEMIC.md`](WHY_12_SYSTEMIC.md) — 12 시스템 구조
- [`docs/EDEN_CONCEPT.md`](EDEN_CONCEPT.md) — 에덴 시스템 전체 설계
- [`solar/day7/README.md`](../solar/day7/README.md) — Day7 (홍수 후 기준점)
- [`solar/eden/firmament.py`](../solar/eden/firmament.py) — 궁창 구현
- [`solar/eden/flood.py`](../solar/eden/flood.py) — 대홍수 구현
