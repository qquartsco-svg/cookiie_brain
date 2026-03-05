# _02_creation_days — 천지창조 day1~7 (MOE Phase 서사 레이어)

**역할**: `_01_beginnings/joe` 가 거시 물리 조건(질량·회전·물·판)을 1차 필터링한 뒤, **그 위에 실제 환경을 쌓는 레이어**다. day1~7, `fields/`, `physics/`, `engines/`, `day7/runner` 가 함께 **MOE(미시 환경 엔진)에 해당하는 입력·맥락**을 만든다.

- **Layer 1 — Pre-Genesis (JOE)**: `_01_beginnings/joe` 에서 planet_stress·instability로 "붕괴하지 않을 행성"만 통과시킨다.
- **Layer 2 — Creation Days (MOE)**: 이 폴더가 담당. 빛/궁창/땅/별/생물/완결을 수치로 쌓아, `PlanetRunner` 스냅샷과 6도메인(대기·수권·지질·자기권·궤도·생물권)을 채운다.
- **Layer 3 — Eden Search & Cherubim**: `_03_eden_os_underworld/eden/search.py` 가 이 스냅샷을 받아 **EdenCandidate / SearchResult** 를 만들고, `eden_os/cherubim_guard` 가 접근 정책을 붙인다.
- **Layer 4 — EdenOS**: `eden_os/eden_os_runner.py` 가 선택된 IC를 OS 커널 위에서 돌리며, 관리·추방·계승 서사를 실행한다.

즉 **조(JOE) → (_02_creation_days 전체) → eden.search(EdenSearchEngine) → cherubim_guard → EdenOSRunner** 가 하나의 테라포밍 탐색기 파이프라인으로 이어진다.

## Day7 PlanetRunner와 MOE 대응

- `day7/runner.py` 의 `make_planet_runner()` 는 `engines/`의 12 Well System(대기·수권·지질·생물 등)을 묶어, **행성 한 스텝 스냅샷**을 만든다.
- 이 스냅샷 구조는 `solar/eden/initial_conditions.InitialConditions` 및 `eden/search.EdenCriteria` 와 맞물려 있다.
- 그래서 Day7에서 출력된 안정 행성 스냅샷은 곧 **MOE가 보는 6도메인 환경 상태**로 해석될 수 있고, 에덴 탐색/체루빔/ EdenOS 단계로 자연스럽게 넘길 수 있다.

이 README는 서사 배치만 정리한다. 구체 수식·물리는 `engines/README.md`, `solar/eden/README.md`, `_meta/20_CONCEPT/maps/TERRAFORMING_EXPLORER_FLOW.md` 를 참고하면 된다.
