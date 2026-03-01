# 🌍 CookiieBrain — Solar Eden

> *"에덴은 좌표가 아니라 상태(state)다."*

**CookiieBrain / solar.eden**은 Cherubim Engine의 에덴 OS 로직을
태양계 스케일 시뮬레이션 엔진(Solar)에 통합한 구현체다.

행성 운영 체제(Planetary OS)의 전체 스토리라인이
`solar.eden.eden_os` 서브패키지 안에서 실행된다.

---

## 구조

```
solar/
└─ eden/
   ├─ initial_conditions.py   — 6개 파라미터 → 전 지구 동역학 상태
   ├─ firmament.py            — 궁창(수증기 캐노피) 물리 모델
   ├─ flood.py                — 대홍수 4단계 전이 곡선
   ├─ geography.py            — 자기장 좌표계 + 시대별 지형
   ├─ search.py               — EdenSearchEngine (파라미터 공간 탐색)
   ├─ biology.py              — 물리 환경 → 수명 / 체형 / 생태계
   └─ eden_os/
      ├─ eden_world.py        LAYER 0 — 궁창시대 환경 스냅샷
      ├─ rivers.py            LAYER 1 — 4대강 방향 그래프
      ├─ tree_of_life.py      LAYER 2 — 생명나무 + 선악과
      ├─ cherubim_guard.py    LAYER 3 — 체루빔 접근 제어
      ├─ adam.py              LAYER 4 — Root Admin 에이전트
      ├─ eve.py               LAYER 4 — 보조 프로세서 + 계승 트리거
      ├─ lineage.py           LAYER 5 — 계승 그래프 + 상태 머신
      ├─ eden_os_runner.py    LAYER 6 — 7단계 통합 실행기
      ├─ genesis_log.py       LAYER 4.5a — 탄생 순간 불변 로그
      ├─ observer_mode.py     LAYER 4.5b — 독립 관찰자 (상대성)
      └─ genesis_narrative.py LAYER 4.5c — 창세기 지리 서사 체인
```

---

## 빠른 시작

```python
from solar.eden.eden_os import make_eden_os_runner

runner = make_eden_os_runner()
runner.run(steps=24)
runner.print_report()

# 탄생 순간 로그
runner.genesis_log.print_moment()

# 선악과 이벤트 + 카인·아벨 스폰
runner.print_expulsion_report()

# 에덴→아르헨티나→아마존 GPP 체인
runner.print_narrative_report()
```

---

## 본편 스토리라인

전체 서사 및 설계 철학은 Cherubim Engine 참조.

→ **[Cherubim Engine](https://github.com/qquartsco-svg/Cherubim_Engine)**

---

## 블록체인 서명

```
PHAM — Planetary Hash + Author Mark

설계자   : GNJz
엔진명   : CookiieBrain / Solar Eden
버전     : v0.5.0
원본     : Cherubim Engine v2.3.0

Co-Authored-By: Claude (Anthropic)
Repository    : https://github.com/qquartsco-svg/cookiie_brain
```

---

> *"그 길을 우리는 코드로 찾는다."*
