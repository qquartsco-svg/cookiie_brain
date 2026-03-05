# 20_CONCEPT — 개념·문서 축

**역할**: 창조일·파이프라인 순서와 **레이어↔코드 경로** 매핑. 코드 없음, 문서만 있음.

---

## 이 축 안에 뭐가 있는지 (확인용)

| 하위 | 파일 | 확인 방법 |
|------|------|-----------|
| **creation_days/** | README.md | 1~7일차 개념 + `solar/code/dayN` 경로 표. 열어서 일차별 코드 위치 확인. |
| **pipeline_phases/** | README.md | precreation→…→monitoring 단계 + `solar/code/` 경로 표. |
| **maps/** | README.md, **LAYERS.md** | 레이어↔폴더 전체 일람. **LAYERS.md** 에서 "이 레이어 → 어느 경로" 확인. |

---

## 어떻게 확인·수정하나

- **레이어 순서·경로가 궁금할 때** → `maps/LAYERS.md` 열기.
- **N일차가 어디 코드인지** → `creation_days/README.md` 표 참고.
- **파이프라인 단계가 어디 코드인지** → `pipeline_phases/README.md` 표 참고.
- **상세 개념**(성경 의미, 엔지니어링) → `../concept/` (00_system, 01_light, …) 각 README.

이 축은 "폴더만 있는 게 아니라" 위 파일들로 **확인 가능하도록** 구성되어 있음.
