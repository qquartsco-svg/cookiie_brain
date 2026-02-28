# 창세기 관점 — 물리 레이어와 날짜 대응

**목적**: 환경 설정을 창세기 “날” 단위로 정렬하여, 개념·폴더·작업 순서를 명확히 한다.

---

## 1. 둘째날 — 궁창 (하늘) ✅

> *"하나님이 궁창을 만드사 궁창 위의 물과 궁창 아래의 물로 나뉘게 하시니라"*

| 물리 | 구현 |
|------|------|
| 궁창 = 바다와 하늘의 분리 | atmosphere/ (Phase 6a) |
| PT 경계 (액체/기체) | water_phase(), habitable |
| 온실, 열적 관성 | greenhouse, column |
| 수순환 (위의 물 ↔ 아래의 물) | water_cycle (Phase 6b) |

**상태**: 완료. `solar/atmosphere/` 레이어.

---

## 2. 셋째날 — 땅과 풀·씨·열매 (1단계 완료)

> *"물을 한 곳으로 모으고 땅이 드러나게 하시니라"*  
> *"땅은 풀과 씨 맺는 채소와 그 종류대로 열매 맺는 나무를 내라"*

### 2.1 개념 해석 (환경 시스템)

| 창세기 | 환경 물리 | 의미 |
|--------|-----------|------|
| **땅이 드러남** | 대륙-해양 분리 | land_fraction, 표면 타입 (육지/바다) |
| **풀** | 땅을 덮는 표면 | 알베도·복사 특성 차이 (육지 vs 바다) |
| **씨** | 번식·순환 가능한 구조 | 자가순환 순환 고리 (탄소 순환 토대) |
| **열매** | 순환의 산출물 | 순환 고리의 출력 (조성 변화 등) |

### 2.2 셋째날 구현 범위 (Phase 7)

**1단계 — 땅 (land)**  
- 대륙 비율 `f_land`  
- 육지/바다별 알베도 (A_land, A_ocean)  
- 유효 알베도: `A = f_land × A_land + (1-f_land) × A_ocean`  
- atmosphere와의 연결: column이 이 A 사용  

**2단계 — 풀 (surface cover)**  
- 표면 타입별 복사 특성  
- ice-albedo 피드백 (옵션)  
- "땅을 덮는 것" = 알베도·열용량 분포  

**3단계 — 씨·열매 (순환 고리)**  
- 탄소 순환/실리케이트 풍화 (outgassing vs weathering)  
- 조성의 동역학 갱신  
- "자기 복제·순환" 구조의 토대  

---

## 3. 폴더·레이어 설계 (셋째날)

### 신규 레이어: `solar/surface/`

```
solar/surface/
├── __init__.py
├── _constants.py    ← A_land, A_ocean 기본값 등 (필요 시)
├── surface_schema.py   ← SurfaceSchema, land_fraction, effective_albedo
└── README.md
```

**역할**:
- `SurfaceSchema(land_fraction, albedo_land, albedo_ocean)`  
- `effective_albedo()` → atmosphere에서 사용  
- core/, em/ 읽지 않음. data에서 행성별 기본값만 읽음 (옵션).

**의존**:
```
data/ (행성 기본값, 옵션)
     ↓
surface/  ← 독립 또는 data만 참조
     ↑
atmosphere/  (surface.effective_albedo() 읽기)
```

---

## 4. 작업 순서 (셋째날 1단계)

1. **설계·문서** ✅ — CREATION_DAYS_AND_PHASES.md  
2. **solar/surface/** 폴더 생성  
3. **SurfaceSchema** 구현 (land_fraction, albedo_land, albedo_ocean)  
4. **AtmosphereColumn** 수정 — surface에서 A를 받도록  
5. **검증** — 지구 f_land≈0.29일 때 A, T_surface 변화 확인  
6. **VERSION_LOG, README** 반영  

---

## 5. 넷째날 — 해·달·별 (하늘 시계) ✅

> *"하늘의 궁창에 광명체들이 있어 낮과 밤을 나누고,*
> *징조와 계절과 날과 해를 이루라."*
> — 창세기 1:14

### 5.1 개념 해석 — 광명체 = 하늘 시계

창세기 1:14의 핵심 단어는 **"징조와 계절과 날과 해"** 다.
광명체(해·달·별)는 빛이 아니라 **시간 측정 도구**로 먼저 정의된다.

| 창세기 | 시스템 역할 | 코드 |
|--------|------------|------|
| 해 (태양) | 연간 주기 기준 | `RhythmEngine.obliquity()` |
| 달 | 삭망월 주기 / 조석 | `gravity_tides/` |
| 별 (황도궁) | 계절 phase 인덱스 | `solar_longitude / 30°` |
| 징조(sign) | 계절 변화 감지 | `SeasonEngine` |
| 계절(season) | 4분기 주기 | `SeasonEngine.phase` |
| 날(day) | 자전 주기 | 기반 dt 단위 |
| 해(year) | 공전 주기 | `dt_yr=1.0` |

### 5.2 황도 12궁 = 최초의 하늘 시계 UI

황도궁은 신화가 아니라 **고대인이 만든 시간 인터페이스**다.

```
문제:  지상에 정확한 달력·시계가 없다
해결:  하늘을 시계로 사용

태양의 1년 경로(Ecliptic) 360°
  → 30°씩 12구간으로 분할
  → 각 구간에 별자리 이름(라벨) 부여
  → 별 위치만 보면 "지금 몇 월인지" 안다

time_index = int(solar_longitude_deg / 30)   # 0 ~ 11
```

**왜 12인가:**
```
1년 ≈ 12.37 삭망월  →  자연이 이미 12 기반 주기
360° / 12 = 30°     →  계산 친화적 정수
12의 약수 풍부성    →  어느 단위로도 재집계 가능
```

| 고대 황도궁 | Day4 코드 |
|------------|-----------|
| 별 위치 관측 | `RhythmEngine.obliquity(t_yr)` |
| 30° 구간 인덱스 | `int(solar_longitude / 30)` |
| 1년 12구간 완주 | `window=12` (SabbathJudge) |
| 계절 예측 | `SeasonEngine` |
| 농사 타이밍 결정 | `LatitudeBands.step(T, lat)` |

> **한 줄**: 황도궁은 신비 체계가 아니라 지구 운영을 위한 최초의 Global Clock UI였다.
> `RhythmEngine`은 그것을 코드로 재구현한 것이다.

자세한 분석 → [`docs/WHY_12_SYSTEMIC.md`](WHY_12_SYSTEMIC.md)

### 5.3 Day4 구현 — 3개 순환 레이어

```
solar/day4/
├── cycles/          ← Milankovitch 3주기 (만년 단위 하늘 시계)
├── nitrogen/        ← 질소 순환 (자원 주기)
└── gravity_tides/   ← 달·태양 조석 (월 단위 리듬)
```

| 구현 | 창세기 대응 |
|------|------------|
| `MilankovitchCycle` | 해·별 장주기 리듬 |
| `SeasonEngine` | 계절 (징조·때) |
| `gravity_tides` | 달의 조석 주기 |

**상태**: 완료. `solar/day4/` 레이어.

---

## 6. 날짜별 요약

| 날 | 내용 | Phase | 상태 |
|----|------|-------|------|
| 첫째 | 빛 (태양 광도) | Phase 5 | ✅ |
| 둘째 | 궁창 (바다-하늘 분리) | Phase 6a, 6b | ✅ |
| 셋째 | 땅, 풀, 씨, 열매 | Phase 7 | ✅ 1단계 (땅-바다) |
| **넷째** | **해·달·별 (하늘 시계 / 황도궁)** | **Day4** | **✅** |
| 다섯째~ | 생명 이동·네트워크 | Day5+ | ✅ |
| 여섯째 | 진화 OS | Day6 | ✅ |
| 일곱째 | 완성·안식 (PlanetRunner) | Day7 | ✅ |
