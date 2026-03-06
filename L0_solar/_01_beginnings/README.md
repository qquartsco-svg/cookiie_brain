# `_01_beginnings` — 서사의 시작점 · JOE 관찰자

**L0_solar 서사 레이어 1번째 챕터**

---

## 왜 이 모듈이 서사의 첫 번째인가 — 서사 체인과 엔지니어링 구현

---

### 이 레이어의 위치

```
[태초]
_01_beginnings  ←  여기. 서사의 출발점.
      ↓  planet_stress, instability, habitability_label
_02_creation_days   Day1~7 환경 구축
      ↓  6도메인 스냅샷
_03_eden_os_underworld  에덴 운영
      ↓  ...이후 서사 전개
```

이 레이어가 없으면 서사가 시작되지 않는다.
행성이 거주 가능한지, 창조 서사를 이어갈 수 있는지 — 이 레이어가 그 판단을 내린다.

---

### 서사적 역할 — 관찰자 JOE (조)

**JOE(조)**는 빛이 있기 이전, Day 1 이전의 관찰자다.
파인만의 정지 관측자 개념. 행성의 거시 물리 조건만으로 다음 질문에 답한다:

- 이 행성은 창조 서사를 받아들일 수 있는 조건인가?
- `planet_stress`(판 응력·자전·수분 등)는 임계 이하인가?
- `instability`(불안정 지수)는 서사 진행이 가능한 수준인가?

JOE의 판단이 통과해야 `_02_creation_days`가 시작된다.
통과하지 못하면 — 이 행성에서는 서사가 없다.

**엔지니어링 구현**:
```python
from L0_solar._01_beginnings.joe.run import run_joe
from L0_solar._01_beginnings.joe.aggregator import compute_planet_stress_and_instability

snapshot = run_joe(initial_conditions)
stress, instability, label = compute_planet_stress_and_instability(snapshot)
# label: "habitable" → _02_creation_days 진행
# label: "unstable"  → 서사 중단
```

---

## 폴더 구조

```
_01_beginnings/
├── joe/                     JOE 관찰자 엔진
│   ├── _core.py             PANGEA §4 코어 수식 (독립 엔진과 동일)
│   ├── aggregator.py        스냅샷 → planet_stress / instability / label
│   ├── observer.py          관측 파이프라인
│   ├── run.py               진입점: run_joe(ic) → snapshot
│   ├── feature_layers/      물리값 → 스냅샷 키 변환
│   │   ├── cosmic.py        궤도·태양 거리 특성
│   │   ├── mass_rotation.py 질량·자전 특성
│   │   ├── retention.py     대기 보존력
│   │   └── water_plate_proxy.py  수분·판 응력 대리 변수
│   └── README.md
└── __init__.py
```

---

## 엔지니어링 구조

### 입력 / 출력

| 항목 | 타입 | 설명 |
|---|---|---|
| 입력 | `InitialConditions` | 행성 궤도·질량·자전·수분·판 파라미터 |
| 출력 | `planet_stress` | 0.0~1.0 (판 응력·자전·수분 종합) |
| 출력 | `instability` | 0.0~1.0 (창공 붕괴 임계 판단 기준) |
| 출력 | `habitability_label` | `"habitable"` / `"marginal"` / `"unstable"` |

### 핵심 계산 파이프라인

```
InitialConditions
      ↓
feature_layers/ (cosmic + mass_rotation + retention + water_plate_proxy)
      ↓
JOE 스냅샷 (표준 키셋 완성)
      ↓
aggregator.py / PANGEA §4 (planet_stress, instability 산출)
      ↓
habitability_label → _02_creation_days 진입 여부 결정
```

### 기어 분리 원칙

- `_core.py`는 `_02_creation_days` 이하를 **절대 import하지 않는다**
- 독립 엔진 `Joe_Engine`과 수식·계수 완전 동일 (ENGINE_HUB 기준)
- `rotation_stable` 보정만 solar 전용으로 추가

---

## 다음 단계로 전달되는 값

`_01_beginnings`의 출력이 `_02_creation_days` 및 이후 레이어의 입력이 된다:

```python
# _04_firmament_era 붕괴 트리거에도 사용
FirmamentLayer.step(instability=instability)  # 0.85 이상이면 붕괴

# _05_noah_flood 외부 충격 가중
FloodEngine(base_instability=instability)
```

---

## 블록체인 서명

```bash
cd blockchain
python3 pham_sign_v4.py ../L0_solar/_01_beginnings/joe/aggregator.py \
    --author "GNJz" --desc "JOE 관찰자 aggregator"
python3 pham_sign_v4.py ../L0_solar/_01_beginnings/joe/_core.py \
    --author "GNJz" --desc "PANGEA §4 코어"
```

체인 파일: `blockchain/pham_chain_exploration.json` (JOE 탐색 결과 서명)

---

## 확장성 / 활용성

| 확장 방향 | 연결 지점 | 설명 |
|---|---|---|
| 다중 행성 탐색 | `run_joe()` 반복 호출 | 파라미터 공간에서 거주 가능 행성 탐색 |
| 독립 엔진 연결 | `ENGINE_HUB/Joe_Engine` | 설치 시 `_core.py` 자동 업그레이드 |
| Milankovitch 연동 | `feature_layers/cosmic.py` | 궤도 이심률·경사각 → 거주가능성 변화 추적 |
| L4_analysis 연결 | `planet_stress` 출력값 | Layer_1 통계역학으로 stress 분포 분석 |
