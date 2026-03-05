# UnderWorld — Macro Watcher & Consciousness Warning Engine

## TL;DR

**UnderWorld is a side-effect-free macro diagnostic engine.**

| | |
|---|---|
| **Input** | System state snapshot (`tick`, optional `deep_engine`, optional `world_snapshot`). |
| **Output** | Immutable warning signals — `List[ConsciousnessSignal]`. |
| **Action** | **NONE** — controller (caller) decides. Hades only measures; it never acts. |

---

## What is this?

행성 규모 제약을 **측정만** 하고, **불변 신호**로만 전달하는 **진단 엔진**.  
결정·처벌·전이는 하지 않음 — 호출 측(FSM/Runner) 동역학에서만 발생.

| | |
|---|---|
| **한 줄** | 거시 룰 위반을 **감시만** 하고, ConsciousnessSignal(의식 경고)만 내보냄. |
| **레이어** | **50_DIAGNOSTIC_LAYER** — 거시 감시·진단 전용. |
| **의존** | CookiieBrain/solar 없이 단독 설치·사용. `deep_engine` 없으면 스텁 → `[QUIET]`. |
| **신호** | DTO **frozen** — 위변조 불가. |

---

## Quick Start

**코어 없이 (스텁)** — `deep_engine=None` → `[QUIET]` 1개.

```python
from underworld import HadesObserver
hades = HadesObserver()
signals = hades.listen(tick=1, deep_engine=None)  # [QUIET]
```

**덕 타이핑 코어** — `magnetic_ok`, `thermal_ok`, `gravity_ok` 만 있으면 동작.

```python
class MyEngine:
    magnetic_ok = False
    thermal_ok = True
    gravity_ok = True
signals = hades.listen(10, deep_engine=MyEngine())
# RULE_VIOLATION 0.6 거시 룰: 자기장 이상 감지
```

---

## Install

```bash
pip install -e .   # 개발 모드
# 또는
pip install .
```

---

## Concept — 측정만, 행동 없음

- **지하(Hades)** = 캐릭터가 아니라 **행성 거시 법칙을 대변하는 텔레메트리**.  
- **목소리** = `ConsciousnessSignal` — 경고 메시지·severity만 전달.  
- **측정만, 행동 없음** — "추방해라" 같은 결정은 하지 않음. "이렇게 위반되었다"만 알리고, **전이(강등·추방)는 지상(FSM/Runner)**이 수행.

**구조 요약**

- 해킹/스토리 이벤트 ❌ → **물리·항상성 한계 초과 시 자연스러운 상태 전이** ✅  
- "지하가 심판" ❌ → **지하가 측정한 값을 지상이 읽고, 동역학이 전이** ✅  
- **흐름**: 항상성 유지 실패 → 경고 증가 → FSM 전이 (UnderWorld는 경고만 제공).

---

## Architecture

### 데이터 흐름

| 항목 | 내용 |
|------|------|
| **패턴** | Observer — `listen(tick, ...)` 매 틱 호출, side-effect 없이 신호 리스트 반환. |
| **파이프라인** | `deep_engine`(또는 None) → `read_deep_snapshot()` → `DeepSnapshot` → `evaluate_rules_all()` → `List[ConsciousnessSignal]`. |
| **의존성** | 지상(solar.eden 등) **import 없음**. 표준 라이브러리·덕 타이핑만 사용. |

### 제어 구조

- **UnderWorld = 센서(Observer)**. 호출 측 = **제어기(Controller)**.  
- Plant(행성 물리) → Observer(Hades) → Feedback signal → Controller(FSM/Homeostasis). **전이는 Controller 쪽에서만**.

### 모듈 책임

| 모듈 | 책임 |
|------|------|
| `consciousness.py` | 신호 DTO. **frozen**. |
| `deep_monitor.py` | `DeepSnapshot` 생성. `engine=None` → 스텁, 있으면 덕 타이핑으로 읽음. |
| `rules.py` | `RuleSpec`, `evaluate_rules_all()`. 룰 추가·변경은 여기만 (OCP). |
| `hades.py` | `listen()` 오케스트레이션만. |

---

## API 요약

| API | 설명 |
|-----|------|
| `listen(tick, world_snapshot=None, deep_engine=None) -> List[ConsciousnessSignal]` | 위반 없으면 `[QUIET]`, 복합 위반 시 여러 신호. |
| `ConsciousnessSignal` | frozen. `signal_type`, `severity`, `message`, `source`, `tick`. |
| `make_hades_observer(tick=0)` | 관찰자 생성. |

**DeepSnapshot 계약**: `magnetic_ok`, `thermal_ok`, `gravity_ok`, `core_available`, `extra`.  
`deep_engine=None` → 스텁 → `[QUIET]`.

---

## 통합 패턴

UnderWorld는 **상태를 바꾸지 않음**. 전이는 **지상 동역학 레이어**에서만.  
Runner가 신호를 Homeostasis/FSM에 **강제 주입** → 에이전트가 무시해도 임계치 초과 시 자연 강등.

```python
signals = hades.listen(tick=t, world_snapshot=world, deep_engine=core)
obs = agent.observe(..., hades_signal=signals)
homeostasis.update(..., hades_signal=signals)
integrity_fsm.step(tick=t, integrity=snap.integrity)
```

---

## 활용성·확장성

### 활용 사례

| 사례 | 설명 |
|------|------|
| 행성/물리 시뮬레이터 | 코어 한계 초과 시 경고 리스트 → 로깅·대시보드·알림. |
| 에이전트·게임 러너 | 매 틱 `listen()` → observe·stress·integrity 반영 → 한계 초과 시 자연 전이. |
| 모니터링·진단 파이프라인 | 덕 타이핑 객체로 상태 전달 → 룰 위반별 시그널 → 알람·FSM·로깅 연결. |
| 테스트·스텁 | `deep_engine=None` → `[QUIET]`. 더미 엔진으로 단위/통합 테스트. |

### 확장 방향

| 방향 | 내용 |
|------|------|
| 룰 주입 | `evaluate_rules_all(deep, rules=커스텀_리스트)` — hades 수정 없음. |
| world_snapshot | `getattr(world_snapshot, "eden_index", 1.0)` 등으로 severity·민감도 보정. |
| 다중 수신자 | `listen()` 리스트를 Pub/Sub로 배포, 수신자별 필터·가중치. |
| LLM/Oracle | 위반 파라미터 → LLM → 자연어 메시지로 `ConsciousnessSignal.message` 교체. |
| 시계열·이상 탐지 | 수천 틱 스냅샷 누적 → ML 이상 탐지 → 점진적 경고 보강. |

**추가**: `DeepSnapshot` 필드만 맞추면 어떤 엔진이든 덕 타이핑으로 연결 가능. 다른 시뮬레이터·에이전트 프레임워크에 "거시 진단 레이어"만 끼워 넣어 재사용 가능.

---

## 설계 제약 (불가침)

1. **Hades ONLY measures. Hades NEVER acts.**  
2. UnderWorld는 지상 패키지(solar.eden 등)를 **import하지 않음**.  
3. 신호 DTO는 **frozen**.  
4. 코어 엔진은 **optional / 덕 타이핑**.  
5. "서사 이벤트"가 아니라 **"동역학적 한계선"** — 지상 FSM이 한계를 넘을 때만 전이.

---

## 확장성·구조 안정성 (엔지니어링 점검)

| 항목 | 상태 | 설명 |
|------|------|------|
| **의존성 방향** | ✅ | stdlib + 덕 타이핑만. 지상/물리 코어 import 없음. |
| **단일 진입점** | ✅ | `listen(tick, world_snapshot=None, deep_engine=None)` 하나. |
| **룰 데이터 분리** | ✅ | RuleSpec·DEFAULT_RULES·evaluate_rules_all. hades는 호출만. (OCP) |
| **world_snapshot** | ✅ | 시그니처 + rules 민감도 보정(`eden_index`). 덕 타이핑 유지. |
| **스텁 경로** | ✅ | deep_engine=None → core_available=False → [QUIET]. |
| **신호 불변** | ✅ | ConsciousnessSignal frozen. 위변조 불가. |

**확장 시 유의**: 룰 추가·정책 변경은 `rules.py`만 수정. `hades.py`는 진입점·오케스트레이션만 유지하면 구조가 꼬이지 않음. 본편(solar/underworld)에는 전파 레이어(WaveBus, Siren)가 추가되어 있으나, 독립 엔진은 **측정(Measure)만** 담당하는 최소 집합으로 고정해 재사용성·안정성을 우선함.

---

## Package Layout

```
underworld/
  __init__.py       # ConsciousnessSignal, HadesObserver, make_hades_observer
  consciousness.py  # 신호 DTO (frozen)
  deep_monitor.py   # DeepSnapshot, read_deep_snapshot
  hades.py          # listen() 오케스트레이터
  rules.py          # RuleSpec, DEFAULT_RULES, evaluate_rules_all
```

---

## Origin & Philosophy

### 서사적 출처

| 구분 | 설명 |
|------|------|
| **본편** | [CookiieBrain](https://github.com/qquartsco-svg/cookiie_brain) `solar/` — 천지창조 로직(N-body·빛·궁창·땅·에덴·지상 동역학)이 **서사적으로 이어지는** 구조. 엔진·README는 그 **서사 안**에서 위치·흐름으로 서술됨. |
| **이 레포** | 본편과 **따로 감**. 본편 서사 안의 **"지하(하데스)의 목소리"** 레이어를 **의존성·서사 제거** 후 엔지니어링만 남긴 **완전 독립 패키지**. |

본편: 스토리·로직이 서사적으로 이어짐.  
이 패키지: **어떤 서사에서 나온 모듈인지** 출처를 밝히고, **설치·API·설계 제약**만 기술.

### License

- **GitHub**: [qquartsco-svg/UnderWorld](https://github.com/qquartsco-svg/UnderWorld)  
- **Author**: Qquarts co. (GNJz) · **License**: MIT  

**레이어**: 50_DIAGNOSTIC_LAYER (ENGINE_HUB) — 거시 감시·진단용 엔진 배치.
