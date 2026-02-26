# 03 — 땅과 바다

**개념**: 물을 한 곳으로 모으고 땅이 드러나는 단계.  
대륙 비율·유효 알베도로 지표면 분화.

---

## 구현 위치

| 폴더 | 내용 |
|------|------|
| **`../surface/`** | SurfaceSchema, land_fraction, effective_albedo |

---

## 상태·출력

- `A_eff = f_land × A_land + (1−f_land) × A_ocean`
- **사용처**: `../atmosphere/` column이 이 알베도로 T_surface 계산

---

## 다음 레이어

→ **04_onward**: 넷째날 이후(해·달·별, 생명·인지).
