# `_03_eden_os_underworld/governance/` — 에덴 거버넌스

**L0_solar > _03_eden_os_underworld 서브폴더**

---

## 서사 위치 및 역할

```
_03_eden_os_underworld/
      │
      ├── eden/           에덴 운영 시스템
      ├── underworld/     심층 감시
      ├── cognitive/      인지 레이어
      ├── governance/ ←  여기. 규칙 집행 · 위반 감지
      │   └── hades/      하데스 — 거버넌스 집행자
      ├── biosphere/
      └── monitoring/
```

**서사**: 에덴이 운영되는 동안 규칙(질서)을 유지하는 레이어.
에덴OS의 상태가 임계를 벗어나거나, 외부 충격(`instability` 급등)이 발생하면
하데스(`hades/`)가 감지하고 제재를 집행한다.
창공 붕괴(`collapse_triggered`)의 조건 중 하나가 이 거버넌스 레이어에서 결정된다.

---

## 폴더 구조

```
governance/
├── hades/               하데스 — 거버넌스 집행자
│   ├── __init__.py      listen() 래퍼
│   └── README.md
└── __init__.py
```

---

## 엔지니어링 역할

`hades/`는 `listen()` 래퍼다. 실제 구현은 `underworld/`에 있다.

```python
# governance/hades/listen() 래퍼
# 실제 구현:
from L0_solar._03_eden_os_underworld.underworld.hades import (
    HadesObserver, make_hades_observer, ConsciousnessSignal
)

observer = make_hades_observer(eden_state)
signal = observer.listen(current_state)
# signal.violation → instability 가중치 증가 → FirmamentLayer.step() 입력
```

**거버넌스 → 창공 붕괴 연결**:
```
HadesObserver.listen() → ConsciousnessSignal.violation
  → instability += violation_weight
  → FirmamentLayer.step(instability=누적값)
  → instability ≥ 0.85 → collapse_triggered = True
  → _05_noah_flood 진입
```

---

## 블록체인 서명

```bash
cd blockchain
python3 pham_sign_v4.py ../L0_solar/_03_eden_os_underworld/governance/hades/__init__.py \
    --author "GNJz" --desc "하데스 거버넌스"
```

서명 체인: `blockchain/pham_chain_hades.json`

---

## 확장성

| 방향 | 설명 |
|---|---|
| 거버넌스 정책 변경 | `HadesObserver` 파라미터 조정으로 붕괴 임계 실험 |
| 다중 위반 유형 | `ConsciousnessSignal` 확장 → 다양한 불안정 원인 추적 |
| L4_analysis 연결 | 위반 신호 시계열 → 통계역학 분석 |
