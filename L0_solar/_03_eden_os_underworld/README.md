# `_03_eden_os_underworld` — 에덴OS · 언더월드 · 하데스

**L0_solar 서사 레이어 3번째 챕터**

---

## 왜 이 모듈이 여기 있는가 — 서사 체인과 엔지니어링 구현

---

### 1단계 — _01_beginnings : 행성이 거주 가능하다는 판정이 났다

**서사**: JOE가 `habitability_label="habitable"` 판정.
이 행성에서 서사가 시작될 수 있다.

**엔지니어링**: `instability < 0.85`, `planet_stress < threshold` → `_02_creation_days` 진입 허가

---

### 2단계 — _02_creation_days : 행성 물리 환경이 구축됐다

**서사**: Day 1~7. 대기·수권·지질·자기권·궤도·생물권 6개 도메인이 완성됐다.
물리 행성이 준비됐다. 이제 그 위에서 무언가를 운영해야 한다.

**엔지니어링**: 6도메인 스냅샷 → `make_antediluvian()` → 에덴 초기 조건 생성

---

### 3단계 — _03_eden_os_underworld ← 여기

**서사**: 완성된 물리 행성 위에 에덴이 올라온다.
체루빔이 에덴 Basin을 지키고, 에덴OS가 환경을 운영하며,
언더월드가 심층에서 감시하고, 하데스가 거버넌스를 담당한다.
창공(Firmament)이 이 모든 것을 덮어 안정적인 온실 환경을 유지한다.

**이 레이어가 하는 일**:
- 에덴 탐색 후 최적 Basin 선정
- 체루빔 가드 + 에덴OS로 에덴 환경 운영
- 창공 상태 감시 (`instability` 누적 추적)
- 이상 감지 시 `_04_firmament_era` → `_05_noah_flood` 트리거 준비

**엔지니어링 구현**:
```python
from L0_solar._03_eden_os_underworld.eden.search import EdenSearch
from L0_solar._03_eden_os_underworld.eden.eden_os import EdenOSRunner
from L0_solar._03_eden_os_underworld.eden.firmament import FirmamentLayer

# 에덴 탐색
search = EdenSearch()
candidate = search.find_best_basin(planet_snapshot)

# 에덴 운영
os_runner = EdenOSRunner(candidate)
firmament = FirmamentLayer(initial_conditions=make_antediluvian())

# 매 스텝 실행
state = firmament.step(dt_yr=1.0, instability=current_instability)
# state["collapse_triggered"] == True → _05_noah_flood 진입
```

---

## 폴더 구조

```
_03_eden_os_underworld/
│
├── eden/                    에덴 시스템 (창세기 2장)
│   ├── firmament.py         창공(궁창) 레이어 — 온실·붕괴 감지
│   ├── flood.py             대홍수 이벤트 엔진
│   ├── initial_conditions.py  make_antediluvian() / make_postdiluvian()
│   ├── search.py            에덴 탐색 엔진 (EdenCandidate 랭킹)
│   ├── biology.py           생물학 레이어 (수명·생태계 안정성)
│   ├── geography.py         에덴 시대 지리·자기장
│   └── eden_os/             에덴OS 운영 시스템
│       ├── runner.py        EdenOSRunner
│       └── cherubim.py      체루빔 가드
│
├── underworld/              심층 모니터링
│   └── deep_monitor.py      상태공간 이상 감지
│
├── biosphere/               생태계 연동
│
├── cognitive/               스핀-링 커플링 (인지 레이어)
│
├── governance/              거버넌스
│   └── hades/               하데스 — 위반 감지·제재
│
├── monitoring/              시스템 모니터
│
└── __init__.py
```

---

## 서브모듈 역할

### eden/ — 에덴 시스템

| 파일 | 서사 역할 | 핵심 출력 |
|---|---|---|
| `firmament.py` | 창공 유지·붕괴 감지 | `collapse_triggered`, `H2O_canopy_kg` |
| `flood.py` | 대홍수 진행 | `FloodSnapshot`, `sea_level_anomaly_m` |
| `initial_conditions.py` | 에덴/현재지구 초기값 | `make_antediluvian()`, `make_postdiluvian()` |
| `search.py` | 최적 에덴 탐색 | `EdenCandidate`, 위도·알베도·생물다양성 |
| `biology.py` | 생물학적 거주가능성 | `lifespan_yr`, `ecosystem_stability` |

### underworld/ — 심층 감시

창공 시대의 에덴 Basin 내부에서 이상 신호를 감지한다.
`instability` 누적 추적 → `_04_firmament_era`에 피드백.

### governance/hades/ — 하데스

에덴OS 규칙 위반·임계 초과 시 제재 실행.
에덴 서사의 "죄와 벌" 로직을 거버넌스 코드로 구현.

### cognitive/ — 스핀-링 커플링

에덴OS의 의사결정 레이어. 상태공간의 스핀-링 결합을 인지 모델로 연결.
`L1_dynamics/Phase_C` 요동 레이어와 결합.

---

## 창공 붕괴 임계 — _04, _05 트리거 조건

```python
# firmament.py 내부 로직
if self.instability >= 0.85:
    self._do_collapse()   # H2O_canopy → 0, collapse_triggered = True
    # → _04_firmament_era에서 감지
    # → _05_noah_flood으로 상태 전달
```

`instability`는 두 가지 경로로 누적된다:
1. `_01_beginnings/joe`의 `planet_stress` 기본값
2. `_06_lucifer_impact`의 외부 에너지 주입 (impulse_shock)

---

## 블록체인 서명

```bash
cd blockchain
python3 pham_sign_v4.py ../L0_solar/_03_eden_os_underworld/eden/firmament.py \
    --author "GNJz" --desc "창공 레이어"
python3 pham_sign_v4.py ../L0_solar/_03_eden_os_underworld/eden/flood.py \
    --author "GNJz" --desc "대홍수 엔진"
```

서명 체인:
- `blockchain/pham_chain_firmament.json`
- `blockchain/pham_chain_flood.json`
- `blockchain/pham_chain_hades.json`
- `blockchain/pham_chain_consciousness.json`
- `blockchain/pham_chain_search.json`

---

## 확장성 / 활용성

| 확장 방향 | 연결 지점 | 설명 |
|---|---|---|
| 에덴 다중 후보 비교 | `EdenSearch.find_all()` | 조건별 에덴 Basin 랭킹 비교 |
| 창공 붕괴 시나리오 | `FirmamentLayer(instability=x)` | 임계값 조정으로 붕괴 시점 실험 |
| 언더월드 확장 | `underworld/deep_monitor.py` | L1_dynamics Phase_C 요동 입력 연결 |
| 하데스 정책 변경 | `governance/hades/` | 거버넌스 규칙 파라미터화 |
| 독립 에덴 탐색기 | `eden/search.py` 분리 | 다른 행성계 에덴 탐색에 재사용 |
