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

## 5. 날짜별 요약

| 날 | 내용 | Phase | 상태 |
|----|------|-------|------|
| 첫째 | 빛 (태양 광도) | Phase 5 | ✅ |
| 둘째 | 궁창 (바다-하늘 분리) | Phase 6a, 6b | ✅ |
| 셋째 | 땅, 풀, 씨, 열매 | Phase 7 | ✅ 1단계 (땅-바다) |
| 넷째~ | 해·달·별, 생명… | Phase 8+ | 예정 |
