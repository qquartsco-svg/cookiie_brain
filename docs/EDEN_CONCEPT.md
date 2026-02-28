# 에덴 시스템 — 창세기 2장: Observer / Controller 레이어

> *"여호와 하나님이 땅의 흙으로 사람을 지으시고 생기를 그 코에 불어넣으시니 사람이 생령이 되니라"*
> — 창세기 2:7

**목적**: 천지창조(Day1~7)가 완결된 이후, 그 위에 올라오는 새로운 챕터의 구조를 정의한다.

---

## 1. 챕터 구조 — Day가 아니라 새로운 시작

```
창세기 1장: 천지창조  Day1~7   ← 완결된 한 단위 ✅
                ↓
창세기 2장: 에덴      Eden     ← 새로운 챕터 (Day 번호 없음)
                ↓
창세기 3장: 타락      Fall
창세기 4장: 가인·아벨 Lineage
...
```

**Day8은 없다.** 창조가 끝난 뒤에 시작되는 건 새로운 번호 체계다.

```
코드 구조:

solar/
├── day1~7/     ← 1챕터: 천지창조 ✅ 완결
├── engines/    ← 12 Well System ✅ 독립 엔진
└── eden/       ← 2챕터: 에덴 시스템 (다음)
```

---

## 2. 시스템 이론 전환

```
1챕터 (Day1~7)                 2챕터 (Eden~)
─────────────────────────────────────────────
physics + biology  (plant)     →  그대로 유지
cybernetics layer  (Day7)      →  그대로 유지
                               +  observer (아담)
                               +  controller (이브)
                               +  lineage (계승)
```

제어이론으로 보면:

```
Supervisor (Day7)
    "시스템이 안정인가?" → is_stable, PlanetSnapshot

Observer (Eden — 아담)        ← 새로 추가
    "12개 밴드 각각 무슨 상태인가?" → 진단·레이블링

Controller (Eden — 이브)      ← 새로 추가
    "어느 밴드에 교정이 필요한가?" → 교정 신호

Lineage (Eden — 계승)         ← 새로 추가
    "다음 관리자를 어떻게 선택하는가?" → ReproductionEngine
```

---

## 3. 아담 = Observer

| 성경 | 시스템 역할 |
|------|------------|
| 에덴을 경작·관리 | State observer — 전 지구 상태 관측 |
| 동물에게 이름을 붙임 | State labeling — 12 밴드에 의미 부여 |
| 선악을 알게 하는 나무 금지 | Hard constraint — 임계 설정 |
| 모든 나무 열매 허락 | Feasible region 정의 |

```python
class Adam:
    """Observer — 12밴드 상태를 읽고 진단한다.

    천지창조(Day1~7)가 만든 행성을
    12개 밴드(지파) 단위로 감독하는 첫 에이전트.
    """
    def observe(self, snap: PlanetSnapshot) -> Diagnosis:
        labels     = self._label_bands(snap.band_T, snap.band_N_soil)
        violations = self._check_constraints(snap)
        return Diagnosis(labels=labels, violations=violations,
                         time_yr=snap.time_yr)
```

---

## 4. 이브 = Controller (아담에서 파생)

| 성경 | 시스템 역할 |
|------|------------|
| 아담의 갈빗대에서 만들어짐 | Adam.genome에서 초기화된 보완 에이전트 |
| 돕는 배필 | Observer 보완 — 탐색·교정 신호 생성 |
| 선악과를 먼저 봄 | Exploratory policy — 탐색 우선 |
| 아담에게 전달 | 피드백 루프 완성 |

```python
class Eve:
    """Controller — 아담의 진단을 받아 교정 신호를 생성.

    아담(Adam.genome)에서 미세 변이로 파생.
    갈빗대 = genome에서 분기한 보완 에이전트.
    """
    def control(self, diagnosis: Diagnosis) -> ControlSignal:
        corrections = {}
        for band_id, violation in diagnosis.violations.items():
            corrections[band_id] = self._correct(violation)
        return ControlSignal(corrections=corrections)
```

---

## 5. 아담 × 이브 → 계승

```
Adam (gen=0)  ×  Eve (gen=0)
       ↓  Day6 ReproductionEngine.recombine()
    Child (gen=1) — 다음 Observer/Controller 후보
       ↓  Day6 SelectionEngine.select()
    fitness = time_to_stable (SabbathJudge 기반)
       ↓
    적합도 높은 자녀 → 다음 에덴 관리자
```

**적합도 기준**: 더 빠르게 SabbathJudge.is_stable을 달성시키는 쌍이 이긴다.

---

## 6. Day7 한계와 에덴의 해결

Day7의 알려진 한계 (explicit Euler ordering):

```
⚠️ Atmosphere ↔ Biosphere 는 실제로 동시 방정식
   현재는 순차 실행으로 근사
```

에덴(Adam/Eve)이 올라오면 이 문제를 **제어 루프**로 해결할 수 있다:

```python
# Eden 방식: Observer/Controller가 sub-iteration 수렴 판정
for k in range(inner_iters):
    snap = runner.step()
    diag = adam.observe(snap)
    ctrl = eve.control(diag)
    runner.apply_correction(ctrl)
    if adam.converged(diag): break
```

---

## 7. 예정 구조

```
solar/
├── day1~7/         ← 1챕터: 천지창조 ✅
├── engines/        ← 12 Well System ✅
└── eden/           ← 2챕터: 에덴 시스템
    ├── __init__.py
    ├── adam.py         ← Observer
    ├── eve.py          ← Controller
    ├── lineage.py      ← 세대 계승
    ├── eden_demo.py    ← 통합 테스트
    └── tribes/         ← 12지파 특화 프로파일 (선택)
```

---

## 8. 핵심

```
Day1~7: "세계를 만들었다"        → 천지창조 완결
Day7:   "세계가 안정인가?"       → SabbathJudge
Eden:   "누가 관리하는가?"       → Adam (observer)
                                   Eve (controller)
                                   자녀 (계승)
```

**Day7(supervisor)이 없으면 Eden은 의미없다.**
안정성이 확인된 시스템 위에서만 observer/controller가 의미를 가진다.

이것이 창세기에서 천지창조(1장) 이후
에덴(2장)이 시작되는 **시스템 이론적 이유**다.
