# L3_memory — Layer 3 : 기억 엔진

CookiieBrain의 **동적 지형 제어 레이어.**  
`L1_dynamics`가 만든 에너지 지형 위의 우물(well)을 생성·강화·감쇠·소멸시키는 엔진.  
서사(`L0_solar`)의 이벤트가 기억으로 남는 방식을 정의한다.

> **태양이 떠야 행성이 돈다.**  
> `L1_dynamics`가 "행성이 굴러다닐 지형"이라면,  
> `L3_memory`는 그 지형을 **스스로 만들고, 깎고, 키우는 태양**이다.

---

## 이 레이어가 하는 일

- 우물(MemoryWell) 생성 · 강화 · 감쇠 · 소멸 (MemoryStore)
- I(x,v,t) 주입 자동 제어 — 탐색·정착·리콜 상태 전환 (EnergyBudgeter)
- MemoryStore + EnergyBudgeter 통합 운영 (HippoMemoryEngine)

---

## 폴더 구조

```
L3_memory/
├── README.md                ← 지금 읽고 있는 문서
├── __init__.py              ← MemoryStore, EnergyBudgeter, HippoMemoryEngine 공개
├── memory_store.py          ← (A) 우물 생애주기: 생성 · 강화 · 감쇠 · 소멸
├── energy_budgeter.py       ← (B) I(x,v,t) 자동 제어: 탐색 · 정착 · 리콜
└── hippo_memory_engine.py   ← 통합 엔진 + HippoConfig
```

---

## 핵심 개념

### 우물(MemoryWell) 생애주기

```
생성 (birth)
  → 강화 (reinforce)   ← 같은 장소를 반복 방문할수록 깊어짐
  → 감쇠 (decay)       ← 오래 방문 안 하면 얕아짐
  → 소멸 (fade)        ← 깊이 임계값 아래로 떨어지면 사라짐
```

### 상태 전환 (EnergyBudgeter)

| 상태 | 설명 |
|------|------|
| 탐색 (explore) | 넓게 돌아다님. 약한 주입 |
| 정착 (settle) | 우물 안으로 빠져들기 시작 |
| 리콜 (recall) | 기존 우물 재방문. 강한 주입 |

---

## 주의: 00_BRAIN/Hippo_Memory_Engine과 다르다

이 폴더(`L3_memory`)는 **CookiieBrain 전용** 기억 레이어.  
`00_BRAIN/ENGINE_HUB`의 `Hippo_Memory_Engine`과 코드·데이터가 연결되지 않는다.  
이름이 비슷하지만 완전히 별개 구현체.

---

## 다른 레이어와의 관계

| 방향 | 대상 | 내용 |
|------|------|------|
| 읽고 제어 | `L1_dynamics` | Phase_B 우물 포텐셜을 읽어서 동적으로 변형 |
| 기록 | `L0_solar` | 서사 이벤트 → 우물로 변환해 기억에 저장 |
| 측정됨 | `L4_analysis` | 우물 상태·변화를 분석 레이어가 측정 |
