# 셋째날 환경 구성 — 어디서 어떻게 되어 있는지

**목적**: 셋째날(Phase 7) 환경 설정·구성 **파일**과 **연결 관계**를 한곳에서 확인.

---

## 1. 셋째날이 뭔지 (한 줄)

> *"물을 한 곳으로 모으고 땅이 드러나게 하시니라"* → **땅-바다 분리** + **유효 알베도**  
> (풀·씨·열매는 Phase 7의 2·3단계로, 아직 미구현)

---

## 2. 구성이 정의되는 곳 (파일 목록)

### 2.1 코드 — 실제 “환경 설정”이 살아 있는 곳

| 경로 (CookiieBrain 기준) | 역할 | 셋째날 관련 내용 |
|--------------------------|------|------------------|
| **solar/surface/surface_schema.py** | 땅-바다 스키마 + 유효 알베도 | `SurfaceSchema`, `effective_albedo()`, 상수 `A_LAND_DEFAULT`, `A_OCEAN_DEFAULT`, `F_LAND_EARTH` |
| **solar/surface/__init__.py** | surface 패키지 API | `SurfaceSchema`, `effective_albedo` export |
| **solar/atmosphere/column.py** | 대기 열평형 | `albedo` 인자로 **surface에서 준 A** 받아서 T_surface 계산 |
| **solar/brain_core_bridge.py** | BrainCore 연동 | `use_surface_schema=True`일 때 `SurfaceSchema(land_fraction=0.29)`로 `albedo` 계산 후 column에 전달 |

**환경 “설정값”이 정해지는 곳**  
- **기본값**: `solar/surface/surface_schema.py`  
  - `F_LAND_EARTH = 0.29`, `A_LAND_DEFAULT = 0.30`, `A_OCEAN_DEFAULT = 0.08`  
- **연동 시**: `solar/brain_core_bridge.py`  
  - 지구만 `SurfaceSchema(land_fraction=0.29)` 사용, 그 외 행성은 `albedo=0.306` 등 고정

별도 **설정 파일(JSON/YAML)** 은 없음. 코드 기본값 + 호출 시 인자로만 구성됨.

---

### 2.2 문서 — 셋째날 “개념·설계·범위”를 설명하는 것

| 경로 | 내용 |
|------|------|
| **docs/CREATION_DAYS_AND_PHASES.md** | 창세기 날짜 ↔ Phase 매핑, **셋째날 구현 범위**(1단계 땅 / 2단계 풀 / 3단계 씨·열매), 폴더 설계, 작업 순서 |
| **solar/surface/README.md** | surface 레이어 개념, 땅-바다, 유효 알베도 식, 사용 예시, atmosphere와 연동 방법 |
| **solar/surface/__init__.py** (docstring) | 셋째날 구절 인용, surface 역할 한 줄 |
| **solar/README.md** | solar 전체 구조 안에서 surface(Phase 7 / 셋째날) 위치 |
| **docs/EMERGENCE_TRAJECTORY.md** | Phase 7 = 셋째날 땅과 바다 완료 표시 |
| **docs/VERSION_LOG.md** | v1.6.0 셋째날 항목 |
| **README.md** (루트) | v1.6.0 셋째날 완료 표 |

---

### 2.3 검증(데모) — 셋째날이 제대로 동작하는지 보는 것

| 경로 | 내용 |
|------|------|
| **examples/surface_day3_demo.py** | Phase 7 전용 데모. P7-1~P7-4 (SurfaceSchema 알베도, 전 바다/전 육지, surface→atmosphere 연동, 땅 비율↑→냉각) |

---

## 3. “어디서 어떻게” 연결되는지 (데이터 흐름)

```
[설정 기본값]
  solar/surface/surface_schema.py
    F_LAND_EARTH=0.29, A_LAND_DEFAULT=0.30, A_OCEAN_DEFAULT=0.08
         │
         ▼
  SurfaceSchema(land_fraction=0.29)  ──►  effective_albedo()  ──►  A_eff
         │
         │  (BrainCore 연동 시)
         ▼
  solar/brain_core_bridge.py
    sfc = SurfaceSchema(land_fraction=0.29)
    albedo = sfc.effective_albedo()   # 지구만
         │
         ▼
  AtmosphereColumn(..., albedo=albedo, ...)
         │
         ▼
  solar/atmosphere/column.py
    T_surface (복사 평형), surface_heat_flux(), habitable 등
```

- **단독 사용**: `SurfaceSchema`만 쓰고 `effective_albedo()`를 직접 `AtmosphereColumn(albedo=...)`에 넘김.  
- **BrainCore 경로**: `brain_core_bridge`가 surface 스키마로 albedo 정한 뒤 column 생성.

---

## 4. 요약 표 — “셋째날 환경 구성 파일이 뭐가 있지?” 할 때

| 구분 | 파일 (경로는 CookiieBrain/ 기준) |
|------|----------------------------------|
| **구성 정의(코드)** | `solar/surface/surface_schema.py`, `solar/surface/__init__.py` |
| **구성 사용(코드)** | `solar/atmosphere/column.py`, `solar/brain_core_bridge.py` |
| **설계·개념(문서)** | `docs/CREATION_DAYS_AND_PHASES.md`, `solar/surface/README.md` |
| **참고 문서** | `solar/README.md`, `docs/EMERGENCE_TRAJECTORY.md`, `docs/VERSION_LOG.md`, 루트 `README.md` |
| **검증** | `examples/surface_day3_demo.py` |

**설정 파일(JSON/YAML 등)** 은 없고, **코드 기본값 + API 인자**로만 셋째날 환경이 구성됨.  
**상세 설명**(환경설정 범위 A~E, 수식, 검증, 다음 기어): `solar/surface/README.md`.

---

## 5. 구조 점검 결과 (피드백 반영)

업로드본 기준으로 셋째날(Phase 7) 환경설정을 구조적으로 확인한 요약.

### 5.1 개념·문서

- **solar/surface/README.md**: 땅·바다 분리, A_eff = f_land×A_land + (1-f_land)×A_ocean — 일관.
- **docs/DAY3_ENVIRONMENT_WHERE_AND_WHAT.md**: 코드 위치·연결 경로 — 일관.

### 5.2 코드 구조

| 파일 | 역할 | 점검 |
|------|------|------|
| **surface_schema.py** | SurfaceSchema, effective_albedo(); atmosphere/core/em 미참조 | ✔ 순수 계산, 레이어 규칙 준수 |
| **surface/__init__.py** | SurfaceSchema, effective_albedo export | ✔ 문서 예시와 일치 |
| **brain_core_bridge.py** | SurfaceSchema → albedo → AtmosphereColumn(albedo=...) | ✔ 데이터 흐름 명확 |
| **surface_day3_demo.py** | f_land=0/0.29/1, T_surface 연동 검증 | ✔ 정상이면 셋째날 물리 연결 완료 |

### 5.3 현재 셋째날 상태

| 항목 | 상태 |
|------|------|
| 물리 개념 (땅·바다 분리, 가중 평균 알베도, atmosphere 연동) | ✔ 완료 |
| 아키텍처 (surface 독립, atmosphere가 읽기, bridge가 조립) | ✔ 의존 방향 정상 |
| **아직 없음** | 전역 평균 land_fraction만 존재. 공간 격자 없음. |

**미구현**: 셋째날 2·3단계 — 식생 피드백, 탄소순환, 증산, 토양 열용량 차이, 해양 열수송, 대륙 분포 공간성.  
→ 현재는 **"정적 분리 모델"** 단계.

### 5.4 다음 물리 법칙 후보 (셋째날 이후)

1. Ice–albedo feedback  
2. Land vs ocean **heat capacity** 차이  
3. Evapotranspiration  
4. CO₂ weathering cycle  
5. Ocean heat transport  

**현 단계에서 가장 안전한 다음 기어**: **heat capacity 차이** 추가.

### 5.5 Phase 8 방향

환경 설정(Phase 1~7) 완료 후:

- **Phase 8**: 원시 대사 — 물질 반응 동역학, 뉴런 창발.
- "땅과 바다 경계에서 자가순환하는 첫 객체" → 반응-확산(Reaction-Diffusion) 로직 후보.

**다음 작업 선택지**  
- **(A)** surface에 land vs ocean **열용량 차이** 추가 (가장 안전한 다음 기어)  
- **(B)** Phase 8: 최소 반응계(Brusselator/L-V) + 반응-확산으로 "호흡하는 세포/원시 뉴런" 시뮬레이션 설계
