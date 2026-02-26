# 01 — 빛이 있으라

**개념**: 중력장 위에 **빛**이 켜지고, 형태와 온도가 존재하기 시작하는 단계.  
지구 환경 설정의 **첫 번째** 레이어.

---

## 성경 창조 의미

> *"하나님이 이르시되 빛이 있으라 하시니 빛이 있었고"* (창 1:3)  
> **첫째날**. 공간과 질량만 있던 세계에 **복사(빛)** 가 들어옴.  
> 엔진에서는 “태양 광도 F(r)”가 켜져서, 이후 대기·표면 열평형의 **입력**이 됨.

---

## 실제 파일 구성

| 경로 (solar/ 기준) | 역할 |
|--------------------|------|
| **em/solar_luminosity.py** | 태양 광도 L, 조도 F(r) [W/m²], `SolarLuminosity`, `irradiance_si(r_au)` |
| **em/_constants.py** | 전자기·복사 관련 상수 |
| **em/__init__.py** | em 패키지 export (SolarLuminosity, magnetic_dipole, solar_wind, magnetosphere 등) |
| **em/light/** | (선택) 빛 전용 서브 문서 |

---

## 엔지니어링 — 환경설정 관점

- **상태/출력**: `F_solar` [W/m²] — 궤도 반지름 r에서의 복사 플럭스.  
  대기 column의 `equilibrium_temp(F)`, `step(F, dt)` **입력**으로 사용됨.
- **입력**: `core/` 의 궤도(행성–태양 거리 r). em은 core를 **직접 import 하지 않고**, 호출자가 r을 넘김.
- **의존**: 독립 모듈. atmosphere가 em의 F를 **읽기만** 함.

---

## 다음 레이어

→ **02_firmament**: 바다와 하늘(궁창) 분리, 온실·수순환.
