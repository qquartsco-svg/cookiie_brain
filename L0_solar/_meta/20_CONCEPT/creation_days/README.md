# creation_days — 1~7일차 개념·코드 매핑

창조 1~7일 각각이 **무슨 개념**인지, **실제 코드는 solar/ 어디**에 있는지 요약.

---

## 일차별 요약

| 일차 | 개념 | 실제 코드 경로 (solar/ 기준) |
|------|------|-----------------------------|
| **1일** | 빛이 있으라 — 복사·광도가 켜짐 | `day1/em/` — SolarLuminosity, magnetic_dipole, solar_wind, magnetosphere |
| **2일** | 궁창 — 바다와 하늘 분리, 대기·수순환 | `day2/atmosphere/` — column, greenhouse, water_cycle |
| **3일** | 땅과 바다 — 지표·알베도·생물권·불 | `day3/surface/`, `day3/biosphere/`, `day3/fire/` |
| **4일** | 해·달·별 — 궤도·데이터·질소·조석·밀란코비치 | `day4/core/`, `day4/data/`, `day4/nitrogen/`, `day4/gravity_tides/`, `day4/cycles/` |
| **5일** | 생명·이동·먹이사슬 | `day5/` — mobility_engine, seed_transport, food_web |
| **6일** | 접촉·종·진화·가이아 피드백 | `day6/` — contact_engine, species_engine, gaia_feedback 등 |
| **7일** | 완결·안식·행성 러너 | `day7/` — completion_engine, runner, sabbath |

---

## 상세 개념·성경 의미

각 날짜에 대한 **성경 창조 의미**와 **엔지니어링 설명**(입출력, 의존)은  
**`solar/concept/`** 아래에 있음:

- 00_system → 우주·태양계·지구 기반 (day4/data, day4/core에 대응)
- 01_light → 1일, day1/em
- 02_firmament → 2일, day2/atmosphere
- 03_surface → 3일, day3/surface, day3/biosphere
- 04_onward → 4일 이후, day4~day7 + eden, cognitive 등

각 폴더의 **README.md**를 열면 해당 레이어의 파일 구성·역할 표가 나옴.
