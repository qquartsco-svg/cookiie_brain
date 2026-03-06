# solar/ 폴더 — 파일이 어디 있는지

**파일은 다 있습니다.** 폴더별 개수만 세어도 아래와 같음.

| 폴더 | .py 파일 수 | 내용 |
|------|-------------|------|
| **_01_beginnings** | 4 | joe/observer.py, run.py, __init__.py |
| **_02_creation_days** | 127 | day1~day7, bridge, engines, fields, physics, surface 전부 |
| **_03_eden_os_underworld** | 49 | eden/, biosphere/, day6 없음(→_02), cognitive/, governance/, monitoring/, underworld/ |
| **_04_firmament_era** | 2 | engine.py + __init__.py (구현: _03/eden/firmament.py) |
| **_05_noah_flood** | 2 | engine.py + __init__.py (구현: _03/eden/flood.py) |

**Finder에서 비어 보일 때**

- 상단에 **「iCloud 동기화 일시 정지됨」** 이면, 파일이 iCloud에만 있고 로컬에 안 내려와 있을 수 있음.
- **해결**: iCloud Drive 동기화 다시 켜거나, 터미널에서 `ls solar/_02_creation_days/day4/` 로 확인.

**코드 열기**

- 천지창조 day1~7: `solar/_02_creation_days/day1/` ~ `day7/`, `bridge/`, `engines/` 등.
- 에덴·언더월드: `solar/_03_eden_os_underworld/eden/`, `underworld/` 등.
- 궁창/대홍수 본문: `_03_eden_os_underworld/eden/firmament.py`, `flood.py`.
