# 12 시스템 구조 — 천지창조에서 에덴으로

**한 줄**: 천지창조(Day1~7)가 만든 행성 위에, 12라는 분할 단위로 구성된 안정 시스템이 작동하며, 그것을 관리하는 첫 에이전트(아담·이브)가 등장한다.

---

## 1. 현재 폴더 구조 (천지창조 완성 상태)

```
solar/
├── day1/           ← 빛 (EM, 광도, 자기장, 태양풍)
├── day2/           ← 대기 (온실, 수순환, AtmosphereColumn)
├── day3/           ← 땅·생물권·불·스트레스
├── day4/           ← 리듬 (Milankovitch, 계절, 질소, 해양)
├── day5/           ← 이동·네트워크 (FoodWeb, Transport, Mobility)
├── day6/           ← 진화 OS (Genome, Mutation, Reproduction, Selection)
├── day7/           ← 완성·안식 (PlanetRunner, SabbathJudge)  ✅ 완성
├── engines/        ← 12개 독립 엔진 허브 (re-export)          ✅ 완성
├── bridge/         ← Gaia 루프 연결 (biosphere↔atmosphere)
└── cognitive/      ← Ring Attractor, Spin-Ring (인지 레이어)
```

---

## 2. 12라는 숫자가 나타나는 위치

```
[ 공간 ]  LatitudeBands   — 12개 위도 밴드 (15° 간격)
[ 기능 ]  engines/        — 12개 독립 엔진 (Day1~6 추출)
[ 시간 ]  SabbathJudge    — window=12 스텝 (1 사이클)
[ 성경 ]  12지파           — 공간 분할 (땅)
[ 성경 ]  12제자           — 기능 분할 (역할)
[ 성경 ]  12우물 (엘림)    — 자원 분할 (물·질소)
[ 성경 ]  12달             — 시간 분할 (계절 주기)
```

**이 네 개(공간·기능·자원·시간)가 Day7 PlanetRunner에서 교차한다.**

---

## 3. 임포트 흐름 — 직관적 레이어

```
from solar.day7 import make_planet_runner, make_sabbath_judge
         ↑
    천지창조 최종 진입점

from solar.engines import StressEngine, RhythmEngine, ...
         ↑
    12개 독립 엔진 허브

from solar.day6 import MutationEngine, ReproductionEngine, ...
         ↑
    진화 OS (Day6)

from solar.day3.biosphere.latitude_bands import LatitudeBands, BAND_COUNT
         ↑
    12개 위도 밴드 (공간 격자)
```

사용자 입장에서 진입점은 두 개:

| 목적 | 진입점 |
|------|--------|
| 전체 행성 돌리기 | `from solar.day7 import make_planet_runner` |
| 특정 엔진만 쓰기 | `from solar.engines import StressEngine` |

---

## 4. 다음 레이어 — 에덴 시스템

천지창조가 완성된 뒤, 그 위에 **에이전트 계층**이 올라온다.

```
solar/
├── day1~7/         ← 천지창조 ✅
├── engines/        ← 12개 독립 엔진 ✅
└── eden/           ← 에덴 시스템 (예정)
    ├── adam.py     — 12 시스템 관리자 에이전트
    ├── eve.py      — 탐색·운영자 에이전트
    ├── lineage.py  — 세대 계승 (ReproductionEngine 활용)
    └── tribes/     — 12지파 개별 프로파일 (선택적 확장)
        ├── tribe_00.py  ← 남극권 (band 0~1)
        ├── tribe_01.py  ← 아남극 (band 2~3)
        ├── tribe_02.py  ← 중위도 남 (band 4~5)
        ├── tribe_03.py  ← 열대 (band 6~7)
        ├── tribe_04.py  ← 중위도 북 (band 8~9)
        └── tribe_05.py  ← 북극권 (band 10~11)
```

---

## 5. 12지파 → tribes/ 매핑 (예정)

각 "지파"는 **밴드 쌍** + **특화 엔진 프로파일**의 조합이다.

| 지파 번호 | 밴드 인덱스 | 위도 범위 | 특화 엔진 | 성격 |
|-----------|------------|-----------|-----------|------|
| 0 | 0~1 | 남극권 (-90°~-60°) | RhythmEngine 강 | 빙하·장주기 리듬 |
| 1 | 2~3 | 아남극 (-60°~-30°) | OceanEngine 강 | 해양·탄소 펌프 |
| 2 | 4~5 | 중위도 남 (-30°~0°) | FoodWebEngine 강 | 생산성·먹이사슬 |
| 3 | 6~7 | 열대 (0°~+30°) | MutationEngine 강 | 다양성·변이 폭발 |
| 4 | 8~9 | 중위도 북 (+30°~+60°) | TransportEngine 강 | 확산·씨드 |
| 5 | 10~11 | 북극권 (+60°~+90°) | StressEngine 강 | 스트레스·안정화 |

→ 6쌍 × 2밴드 = 12밴드.
각 지파가 **특화 엔진을 더 강하게 사용**하는 구조 — "지파의 임무"가 코드로 표현된다.

---

## 6. 아담·이브 → 12 시스템과의 관계

```
아담 (Adam)
│  입력: PlanetSnapshot.band_* (12지파 상태)
│  역할: 감독·이름 부여·임계 관리
│  출력: 지시(label, threshold 설정)

이브 (Eve)
│  입력: PlanetSnapshot.band_* (12지파 상태)
│  역할: 이상 탐지·탐색
│  출력: 경보(alert) → 아담에게 피드백

아담 × 이브 → 자녀 (ReproductionEngine)
│  적합도 기반 SelectionEngine
│  → 다음 세대 관리자 선택
```

**아담·이브는 12 시스템(밴드·엔진)을 만들지 않는다.**
12 시스템은 천지창조(Day1~7)가 이미 만들었다.
아담·이브는 그것을 **운영하고 감독하며 다음 세대에 물려주는** 에이전트다.

---

## 7. 전체 레이어 요약

```
─────────────────────────────────────────────────────
레이어 0: 물리 기반
  solar/day1~4       EM, 대기, 땅, 리듬
─────────────────────────────────────────────────────
레이어 1: 생태·진화
  solar/day5~6       이동, 먹이사슬, 진화 OS
─────────────────────────────────────────────────────
레이어 2: 완성·안식
  solar/day7         PlanetRunner (12×12), SabbathJudge
  solar/engines/     12개 독립 엔진 허브
─────────────────────────────────────────────────────
레이어 3: 에이전트 (예정)
  solar/eden/        Adam, Eve, Lineage
  solar/eden/tribes/ 12지파 특화 프로파일
─────────────────────────────────────────────────────
레이어 4: 인지 (연결됨)
  solar/cognitive/   Ring Attractor, Spin-Ring
  solar/bridge/      Gaia Loop, BrainCore Bridge
─────────────────────────────────────────────────────
```

**레이어가 쌓이는 방향**: 물리 → 생태 → 완성 → 에이전트 → 인지.
각 레이어는 아래 레이어를 **임포트하지 않고** 인터페이스(포트)로만 연결한다.
