# 03 — 땅과 바다

**개념**: 물을 한 곳으로 모으고 땅이 드러나는 단계.  
대륙 비율·유효 알베도로 지표면 분화.

---

## 성경 창조 의미

> *"물을 한 곳으로 모으고 땅이 드러나게 하시니라"* (창 1:9)  
> **셋째날**. 바다와 **땅**이 구분됨.  
> 엔진에서는 `land_fraction`, 육지/바다 알베도로 **유효 알베도**를 주고, 대기 열평형이 그 값을 읽어 지표 온도를 결정함.

---

## 실제 파일 구성

| 경로 (solar/ 기준) | 역할 |
|--------------------|------|
| **surface/surface_schema.py** | `SurfaceSchema(land_fraction, albedo_land, albedo_ocean)`, `effective_albedo()`, 상수 F_LAND_EARTH, A_LAND_DEFAULT, A_OCEAN_DEFAULT |
| **surface/__init__.py** | SurfaceSchema, effective_albedo export |

---

## 엔지니어링 — 환경설정 관점

- **상태/출력**: `A_eff = f_land × A_land + (1 − f_land) × A_ocean` [0, 1].  
  **사용처**: `atmosphere/column.py` — `AtmosphereColumn(albedo=sfc.effective_albedo(), ...)` 또는 `brain_core_bridge`가 이 값을 column에 전달.
- **입력**: 상수만 사용. (옵션: data에서 행성별 기본값)
- **의존**: **없음**. atmosphere가 surface를 **읽기만** 함.

---

## 다음 레이어

→ **04_onward**: 넷째날 이후(해·달·별, 생명·인지).
