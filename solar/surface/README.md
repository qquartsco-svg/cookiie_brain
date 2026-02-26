# solar/surface/ — 땅과 바다의 분리 (셋째날 / Phase 7)

> *"하나님이 물을 한 곳으로 모으고 땅이 드러나게 하시니라"*

---

## 개념

**궁창(둘째날)**이 바다와 하늘을 나눴다면,  
**셋째날**은 바다와 **땅**을 나눈다.

- **땅 (land)**: 물이 모여 드러난 육지
- **바다 (ocean)**: 물이 모인 곳
- **대륙 비율** `f_land`: 전 표면 중 육지 비율 (지구 ≈ 0.29)

---

## 물리

유효 알베도 (land/ocean 가중 평균):
```
A_eff = f_land × A_land + (1 - f_land) × A_ocean
```

| 파라미터 | 지구 근사 | 설명 |
|----------|-----------|------|
| f_land | 0.29 | 대륙 비율 |
| A_land | 0.30 | 육지 평균 (숲·사막·빙하 혼합) |
| A_ocean | 0.08 | 해양 평균 |

---

## 모듈

| 파일 | 역할 |
|------|------|
| `surface_schema.py` | SurfaceSchema, effective_albedo |
| `__init__.py` | 패키지 API |

---

## 사용

```python
from solar.surface import SurfaceSchema, effective_albedo

# 지구 기본
sfc = SurfaceSchema(land_fraction=0.29)
A = sfc.effective_albedo()   # ~0.12 (ocean-dominated)

# 화성 (거의 육지)
sfc_mars = SurfaceSchema(land_fraction=1.0, albedo_land=0.25)
A_mars = sfc_mars.effective_albedo()
```

atmosphere/와 연동:
```python
from solar.surface import SurfaceSchema
from solar.atmosphere import AtmosphereColumn

sfc = SurfaceSchema(land_fraction=0.29)
atm = AtmosphereColumn(
    body_name="Earth",
    albedo=sfc.effective_albedo(),   # surface에서 A 사용
    ...
)
```

---

## 의존

- `surface/`는 core/, em/, atmosphere/를 참조하지 않음.
- `atmosphere/`가 surface의 effective_albedo를 **읽음**.
