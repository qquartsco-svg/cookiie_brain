# CookiieBrain

천지창조부터 노아 대홍수까지. 서사가 물리 위에서 돌아가는 시뮬레이션 엔진.

---

## 레이어 구조

CookiieBrain은 4개의 레이어가 순서대로 쌓인다.  
아래 레이어가 위 레이어의 기반이 된다.

```
L0_solar/        ← [Layer 0] 서사 — 천지창조·에덴·노아가 실행되는 곳
L1_dynamics/     ← [Layer 1~2] 동역학 — 행성이 굴러다니는 물리 엔진
L3_memory/       ← [Layer 3] 기억 — 우물을 만들고 키우고 지우는 엔진
L4_analysis/     ← [Layer 4] 분석 — 궤적·물리량을 측정. 시스템 변경 안 함
```

각 레이어의 상세 개념은 **[LAYERS.md](./LAYERS.md)** 참조.

---

## 폴더 한눈에 보기

| 폴더 | 레이어 | 종류 | 한 줄 설명 |
|------|--------|------|-----------|
| `L0_solar/` | Layer 0 | 서사 엔진 | 천지창조 day1~7, 에덴OS, 언더월드, 노아 홍수 시나리오 실행 |
| `L1_dynamics/` | Layer 1~2 | 물리 엔진 | 자전·조석·에너지 지형·요동. 행성이 움직이는 물리 기반 |
| `L3_memory/` | Layer 3 | 기억 엔진 | 우물(MemoryStore) 생성·강화·소멸. 동적 지형 제어 |
| `L4_analysis/` | Layer 4 | 분석 모듈 | Layer 1~6 궤적 측정. 읽기 전용. 시스템 건드리지 않음 |
| `examples/` | — | 검증·데모 | 각 레이어 실행해보는 스크립트 모음 |
| `docs/` | — | 문서 | 설계 문서·개념 문서 |
| `blockchain/` | — | 기록 | PHAM 서명·체인 |
| `ENGINE_HUB` | — | 링크 | 00_BRAIN/ENGINE_HUB 독립 엔진 심볼릭 링크 |

---

## 레이어 흐름

```
[Layer 0 — 서사]
  L0_solar/
  천지창조 day1~7 → 에덴OS·언더월드 → 노아 대홍수
       │
       │  cookiie_brain_engine.py (오케스트레이터)
       ↓
[Layer 1~2 — 동역학]
  L1_dynamics/
  Phase_A: 자전·조석·코리올리
  Phase_B: 우물→가우시안 에너지 지형
  Phase_C: 열적 요동·FDT
       │
       ↓
[Layer 3 — 기억]
  L3_memory/
  MemoryStore: 우물 생성·강화·감쇠·소멸
  EnergyBudgeter: 탐색·정착·리콜 제어
       │
       ↓
[Layer 4 — 분석]
  L4_analysis/
  Layer_1~6 측정. 시스템 변경 없음
```

---

## 진입점

```python
from cookiie_brain_engine import CookiieBrainEngine

engine = CookiieBrainEngine()
engine.run()
```
