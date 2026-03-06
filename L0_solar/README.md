# L0_solar — Layer 0 : 서사 엔진

CookiieBrain의 **서사(이야기)가 실행되는 곳.**  
천지창조부터 노아 대홍수까지 시간 순서대로 펼쳐지는 시나리오 레이어.  
아래 레이어(`L1_dynamics`, `L3_memory`)의 물리 엔진 위에서 돌아간다.

---

## 이 레이어가 하는 일

- 천지창조 day1~7 시나리오 실행
- 에덴OS, 언더월드, 하데스 운영
- 노아 대홍수 시뮬레이션
- 루시퍼 충돌 이벤트 추정
- **충돌 후 극지방 첫 결빙 동역학 시뮬레이션** (`_07_polar_ice/`)
- **대륙 빙상 성장 · 빙하시대 진입 시뮬레이션** (`_08_ice_age/`)

물리 계산은 직접 안 한다. `L1_dynamics`가 만든 장(field) 위에서 서사를 얹는다.  
단, `_07_polar_ice/`와 `_08_ice_age/`는 자체 물리 방정식을 포함한다.

---

## 폴더 구조

```
L0_solar/
├── _01_beginnings/          ← 태초. 빛·시간 개념 시작. Joe 관찰자
├── _02_creation_days/       ← 천지창조 day1~7. 대기·바다·생명·행성
│   ├── day1/                  대기 형성
│   ├── day2/                  물 분리
│   ├── day3/                  육지·식물
│   ├── day4/                  태양·달·별 (밀란코비치 사이클)
│   ├── day5/                  씨앗·생명 이동
│   ├── bridge/                Gaia Loop ↔ CookiieBrain 연결
│   ├── engines/               10_net_well 등 서브 엔진
│   ├── fields/                장(field) 초기화
│   └── physics/               루시퍼 코어 물리
├── _03_eden_os_underworld/  ← 에덴OS + 언더월드 + 하데스 운영
│   ├── eden/                  에덴 탐색·거버넌스
│   ├── underworld/            심층 모니터링
│   ├── biosphere/             생태계
│   ├── cognitive/             스핀-링 커플링
│   ├── governance/            하데스 거버넌스
│   └── monitoring/            시스템 모니터
├── _04_firmament_era/       ← 창공 시대. 궁창 안정화
├── _05_noah_flood/          ← 노아 대홍수 시나리오·엔진
├── _06_lucifer_impact/      ← 루시퍼 충돌 추정치 (에너지·크레이터·쓰나미)
├── _07_polar_ice/           ← 충돌 후 극지방 결빙 시뮬레이션 (단기 0~50년)
├── _08_ice_age/             ← 대륙 빙상 성장 · 빙하시대 진입 (장기 ~100,000년)
├── _meta/                   ← 개념 맵·설계 문서
├── pipeline.py              ← 서사 전체 파이프라인 실행
└── verify_imports.py        ← import 검증
```

---

## 서사 흐름

```
_01_beginnings  →  _02_creation_days (day1→day7)
      ↓
_03_eden_os_underworld  →  _04_firmament_era
      ↓
_05_noah_flood  →  _06_lucifer_impact  →  _07_polar_ice  →  _08_ice_age
```

**각 단계 핵심:**

| 단계 | 이벤트 | 수치 결과 |
|------|--------|-----------|
| `_04_firmament_era` | 창공(수증기 캐노피) 안정화 | 극지방 0°C 유지 |
| `_05_noah_flood` | 창공 붕괴 → impulse_shock | T_instability > 0.85 임계값 초과 |
| `_06_lucifer_impact` | 루시퍼 충돌 | E=2.2×10⁶ MT, AOD=1.26 (태양광 72% 차단) |
| `_07_polar_ice` | 첫 극지방 결빙 | 충돌 후 1개월 → 결빙, 2.9년 → h=5m, 항구적 빙하 |
| `_08_ice_age` | 대륙 빙상 · 빙하시대 | 20,000yr → 빙하선 70°N, 50,000yr → −86m 해수면, 100,000yr → −125m (LGM) |

---

## 다른 레이어와의 관계

| 방향 | 대상 | 내용 |
|------|------|------|
| 사용 | `L1_dynamics` | 자전·조석·에너지 지형 위에서 서사 실행 |
| 사용 | `L3_memory` | 서사 이벤트를 우물(기억)로 기록 |
| 측정됨 | `L4_analysis` | 서사 실행 결과를 분석 레이어가 측정 |
