# 00 — 우주필드 · 태양 · 태양계 · 달 · 지구

**개념**: 중력장 위에 점 질량이 놓이고, 태양계·달·지구가 형성되는 단계.  
지구 "환경 설정"의 **무대**가 되는 스케일.

---

## 성경 창조 의미

> *"태초에 하나님이 천지를 창조하시니라"* (창 1:1)  
> 빛도, 궁창도, 땅과 바다도 없이 — **공간과 질량**만이 존재하는 단계.  
> “하늘과 땅”의 **장(場)** 이 세워지는 기반.

---

## 실제 파일 구성

| 경로 (solar/ 기준) | 역할 |
|--------------------|------|
| **data/solar_system_data.py** | NASA/JPL 행성 질량·반지름·궤도 요소, `build_solar_system()` |
| **data/__init__.py** | data 패키지 export |
| **core/evolution_engine.py** | N-body 심플렉틱 적분, Body3D, SurfaceOcean, 조석·세차·해류 |
| **core/central_body.py** | 중심천체(태양) 정의 |
| **core/orbital_moon.py** | 위성 궤도 |
| **core/tidal_field.py** | 조석장 |
| **core/__init__.py** | core 패키지 export |

---

## 엔지니어링 — 환경설정 관점

- **상태변수**: `pos`, `vel`, `spin_axis`, `obliquity`, `depths[]`, `vorticity[]` (전역, 공간 격자 없음)
- **입력**: `build_solar_system()` 반환 dict → `engine.add_body(Body3D(**d))`, `engine.giant_impact(...)`
- **출력**: `engine.step(dt)` 후 각 body의 위치·속도·자전축·해양 우물 상태.  
  이후 레이어(em, atmosphere, surface)가 이 **궤도·중력·표면** 정보를 읽어 환경을 쌓음.
- **의존**: data → core. core는 em/atmosphere/surface를 **참조하지 않음** (하위만 읽음).

---

## 다음 레이어

→ **01_light**: 이 계에 빛(광도)이 켜짐.
