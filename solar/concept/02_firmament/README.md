# 02 — 궁창 (바다-하늘 분리)

**개념**: 궁창 위의 물과 궁창 아래의 물이 나뉘는 단계.  
대기(기체)·바다(액체) 분리, 온실 효과, 수순환.

---

## 구현 위치

| 폴더 | 내용 |
|------|------|
| **`../atmosphere/`** | AtmosphereColumn, greenhouse, water_cycle, T_surface, P_surface, water_phase |

---

## 상태·출력

- `T_surface`, `P_surface`, composition, `water_phase`, `habitable`
- **입력**: `../em/` 의 F_solar, `../surface/` 의 유효 알베도(옵션)

---

## 다음 레이어

→ **03_surface**: 땅과 바다 분리(지표면 분화).
