# 아담·이브 시스템 — 12 시스템의 관리자·운영자 계승

> *"여호와 하나님이 땅의 흙으로 사람을 지으시고..."*
> *"...아담에게서 취하신 그 갈빗대로 여자를 만드시고..."*
> — 창세기 2:7, 22

---

## 1. 개념 흐름

```
천지창조 (Day1~7)
  └─ 물리·생물·진화 OS가 완성된 행성
         ↓
    에덴 시스템 (창세기 2장~)
  ┌─────────────────────────┐
  │  아담 (Adam)            │  ← 12 시스템 관리자
  │  이브 (Eve)             │  ← 아담에서 파생된 운영자
  │  아담 × 이브 → 자녀     │  ← 관리 계승 (세대 전달)
  └─────────────────────────┘
         ↓
    12 시스템 위임·분산 관리
```

**핵심**: 천지창조가 끝난 뒤, 그 시스템을 "누가 운영하는가"의 문제.
아담·이브는 행성 운영 프로토콜의 **최초 관리자 인스턴스**다.

---

## 2. 시스템 대응

### 2.1 아담 — 12 시스템 관리자

| 성경 | 시스템 |
|------|--------|
| 땅의 흙으로 만들어짐 | Day3 Surface + Day6 Genome — 물리 기반 위에 초기화된 에이전트 |
| 에덴을 경작·관리 | PlanetRunner의 **관리자 에이전트** — 12밴드·12엔진을 감독 |
| 동물에게 이름을 붙임 | 12 밴드/엔진에 **역할(label)을 부여**하는 명명 계층 |
| 모든 나무의 열매 허락 | 12 시스템의 **자원 접근 권한** 보유 |
| 선악을 알게 하는 나무 금지 | **임계(Threshold) 관리** — 넘으면 안 되는 시스템 경계 |

```python
# 시스템 대응 (개념 코드)
class Adam:
    """12 시스템 관리자.

    - 12개 밴드(지파)를 감독
    - 각 밴드에 역할(이름) 부여
    - SabbathJudge를 통해 안정성 모니터링
    - 임계(threshold) 위반 감지 → 경보
    """
    def __init__(self, runner: PlanetRunner, judge: SabbathJudge):
        self.runner = runner
        self.judge  = judge
        self.band_names = self._assign_names()   # "이름 붙이기"

    def watch(self, dt_yr=1.0):
        snap = self.runner.step(dt_yr)
        self.judge.push(snap)
        return snap, self.judge.judge()
```

---

### 2.2 이브 — 운영자 (아담에서 파생)

| 성경 | 시스템 |
|------|--------|
| 아담의 갈빗대에서 만들어짐 | Adam의 **상태(GenomeState)에서 파생**된 에이전트 |
| "돕는 배필" | 관리(모니터링)와 **운영(실행)의 분리** |
| 아담과 한 몸 | 동일한 행성 위에서 **상호 참조** |
| 이브가 선악과를 먼저 봄 | **탐색(Exploration)** 역할 — Day6 SelectionEngine의 ♀ |
| 아담에게 전달 | 탐색 결과를 관리자에게 **피드백** |

```python
# 시스템 대응 (개념 코드)
class Eve:
    """운영자 — 아담에서 파생, 탐색·실행 담당.

    - Adam.genome에서 초기화
    - 각 스텝에서 12 밴드를 순회하며 이상 탐지
    - 이상 발견 시 Adam에게 신호
    """
    def __init__(self, adam: Adam):
        self.adam   = adam
        self.genome = adam.runner._genomes[0].__class__(
            traits=[t + 0.01 for t in adam.runner._genomes[0].traits]
        )  # 갈빗대 = genome에서 미세 변이로 파생

    def explore(self, snap: PlanetSnapshot) -> dict:
        """12개 밴드 순회 — 이상 탐지."""
        alerts = {}
        for i, T in enumerate(snap.band_T):
            if T > 320.0:
                alerts[f"band_{i}"] = f"과열 {T:.1f}K"
        return alerts
```

---

### 2.3 아담 × 이브 → 계승 (세대 전달)

| 성경 | 시스템 |
|------|--------|
| 자녀를 낳음 | Day6 ReproductionEngine — 재조합으로 새 Genome 생성 |
| 카인·아벨 (다른 역할) | 자녀 에이전트의 **역할 분화** (관리자 계승 vs 탐색자 계승) |
| 세대 계승 | **PlanetRunner를 물려받는 관리자 체인** |

```
Adam (gen=0)  ×  Eve (gen=0)
       ↓  ReproductionEngine.recombine()
    Child (gen=1) — 새 관리자 후보
       ↓  SelectionEngine.select()
    적합도 높은 자녀가 다음 관리자로
```

이것이 **12 시스템의 운영자 계승** 메커니즘이다.

---

## 3. 전체 흐름도

```
천지창조 (Day1~7)
│
│  Day1: 빛 (EM)
│  Day2: 대기 (Atmosphere)
│  Day3: 땅·불·스트레스 (Surface, Fire, Stress)
│  Day4: 리듬·질소·해양·계절 (Milankovitch, N, Ocean, Season)
│  Day5: 이동·먹이사슬·수송 (Mobility, FoodWeb, Transport)
│  Day6: 진화 OS 수렴 (Genome, Mutation, Reproduction, Selection)
│  Day7: 완성·안식 (PlanetRunner, SabbathJudge)
│
└─► 행성이 안정적으로 돌아감 (12엔진 × 12밴드)
         ↓
    에덴 시스템 (창세기 2장)

    Adam ──────────────────────────────────────────
    │  역할: 12 시스템 감독자                      │
    │  입력: PlanetSnapshot (12밴드 상태)           │
    │  출력: 이름 부여, 임계 관리, 안정 판정 요청   │
    │                                               │
    Eve ←── Adam.genome + 미세 변이                 │
    │  역할: 탐색자·실행자                          │
    │  입력: 12밴드 상태                            │
    │  출력: 이상 탐지 신호 → Adam에게 피드백       │
    │                                               │
    Adam × Eve ─────────────────────────────────────
         ↓  ReproductionEngine
    Children (gen+1) — 다음 관리자 후보
         ↓  SelectionEngine
    적합도 기반 계승자 선택
         ↓
    다음 세대의 12 시스템 관리 시작
```

---

## 4. 코드 레이어 배치 (예정)

```
solar/
├── day1~7/           ← 천지창조 완성 ✅
├── engines/          ← 12개 독립 엔진 ✅
└── eden/             ← 에덴 시스템 (예정)
    ├── __init__.py
    ├── adam.py       ← Adam 에이전트 (12 시스템 관리자)
    ├── eve.py        ← Eve 에이전트 (탐색자·운영자)
    ├── lineage.py    ← 세대 계승 로직 (ReproductionEngine 활용)
    └── eden_demo.py  ← 데모
```

---

## 5. 핵심 통찰

**아담은 새로운 물리 기어가 아니다.**
아담은 Day1~7이 만들어낸 행성 위에서
12개 밴드(지파)와 12개 엔진(제자)을 **감독하고 이름 붙이고 임계를 관리**하는
**최초의 에이전트 계층**이다.

**이브는 아담의 복제가 아니다.**
미세한 변이(갈빗대)에서 파생된, **탐색과 피드백을 담당**하는
**보완 에이전트**다.

**계승은 진화 OS(Day6)를 통해 일어난다.**
새로운 세대는 ReproductionEngine이 만들고,
SelectionEngine이 적합도로 다음 관리자를 고른다.

이것이 **천지창조 → 에덴 → 12 시스템 운영**의 전체 흐름이다.
