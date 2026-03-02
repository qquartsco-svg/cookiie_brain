# solar/underworld — 지하·하데스 목소리 (거시 감시·의식 경고)

물리 코어(day4) 위에서 **행성 규모 룰 위반**을 감시하고, **의식 경고(ConsciousnessSignal)** 만 내보내는 레이어.  
지상(EdenOS)은 이 신호를 observe/homeostasis/integrity_fsm에 반영해, “동역학적 한계선”을 넘을 때만 자연스럽게 상태 전이(MORTAL_NPC 등)를 수행한다.

> **설계 규칙 (불가침)**  
> **Hades ONLY measures. Hades NEVER acts.**  
> 언더월드는 관측·신호 생성만 담당. 결정·처벌·전이는 지상 동역학(IntegrityFSM 등) 전용.

---

## 1. 개념·서사

| 구분 | 설명 |
|------|------|
| **역할** | “지하의 목소리” — 인격화된 악역이 아니라, **거시 룰 위반을 측정해 신호로만 전달**하는 관측자. |
| **입력** | (선택) 물리 코어(EvolutionEngine 등)의 스냅샷. 없으면 조용(QUIET) 반환. |
| **출력** | `ConsciousnessSignal` 1개: QUIET / RULE_VIOLATION / ENTROPY_WARNING / SYSTEM_PANIC. |
| **지상 연동** | EdenOS Runner가 매 틱 `hades.listen()` 호출 → 반환값을 `observe`, `homeostasis.update`, `integrity_fsm.step`에 넘김. |

이 경계가 유지될 때 “해킹/스토리 진행”이 아니라 **물리·동역학이 한계선을 넘으면 자연스럽게 NPC로 흐르는** 구조가 유지된다.

---

## 2. 로직·데이터 흐름

```
물리 코어(선택) ──► deep_monitor.read_deep_snapshot(tick, engine)
                            │
                            ▼
                    DeepSnapshot (magnetic_ok, thermal_ok, gravity_ok, …)
                            │
                            ▼
                    rules.evaluate_rules(deep)  ──► (severity, signal_type, message)
                            │
                            ▼
                    ConsciousnessSignal(source="underworld.hades", …)
                            │
                            ▼
                    지상: observe(hades_signal), homeostasis.update(…), integrity_fsm.step(…)
```

### 2.1 진입점 API

| API | 설명 |
|-----|------|
| `HadesObserver.listen(tick, world_snapshot=None, deep_engine=None) -> ConsciousnessSignal` | 현재 틱 기준 “목소리” 1개 반환. `world_snapshot`은 추후 민감도 보정용(현재 미사용). `deep_engine` 없으면 스텁으로 QUIET. |

### 2.2 룰 정책 (데이터 주도)

- **rules.py**: `RuleSpec`(check_key, violation_severity, signal_type, message), `DEFAULT_RULES` 리스트, `evaluate_rules(deep_snapshot, rules=None)`.
- **hades.py**: 룰/문구/심각도 없음. `evaluate_rules(deep)` 호출만 수행.
- 룰 추가·정책 변경 시 **rules.py만 수정**하면 됨 (OCP).

### 2.3 신호 타입

| signal_type | 의미 |
|-------------|------|
| QUIET | 위반 없음 (또는 core_available=False). |
| RULE_VIOLATION | 거시 룰 위반 (예: 자기장 이상). |
| ENTROPY_WARNING | 열역학적 불안정 등. |
| SYSTEM_PANIC | 중력장 이상 등 심각. |

---

## 3. 엔지니어링 (독립 모듈화 관점)

추후 `underworld`를 별도 패키지로 분리할 때를 전제로 한 요약.

| 항목 | 내용 |
|------|------|
| **의존성** | `solar.eden` 을 import 하지 않음. 내부는 `consciousness`, `deep_monitor`, `rules` 만 참조. |
| **진입점** | `listen(tick, world_snapshot=None, deep_engine=None)` 하나. 호출 측(EdenOS Runner)이 신호를 observe/homeostasis/integrity_fsm에 주입. |
| **물리 코어** | `deep_monitor.read_deep_snapshot(engine=...)` 로 엔진을 선택 인자로 받음. 없으면 `core_available=False` → QUIET. |
| **룰 확장** | `RuleSpec` 리스트 주입 또는 `evaluate_rules(deep, rules=...)` 로 정책 교체. hades.py 수정 불필요. |
| **확장 포인트** | (B) `world_snapshot`을 evaluate_rules에 넘겨 severity/민감도 보정. (C) 다중 위반 시 `list[ConsciousnessSignal]` 반환. |

상세: [docs/UNDERWORLD_EXTENSIBILITY.md](../../docs/UNDERWORLD_EXTENSIBILITY.md)

### 3.1 파일 역할

| 파일 | 역할 |
|------|------|
| `consciousness.py` | `ConsciousnessSignal`, `SignalType` — 신호 DTO. |
| `deep_monitor.py` | `DeepSnapshot`, `read_deep_snapshot()` — 물리 코어 어댑터. |
| `hades.py` | `HadesObserver`, `listen()` — 오케스트레이터. |
| `rules.py` | `RuleSpec`, `DEFAULT_RULES`, `evaluate_rules()` — 룰 데이터·평가. |

---

## 4. 관련 문서

| 문서 | 설명 |
|------|------|
| [solar/README.md](../README.md) | 전체 흐름·레이어·언더월드 섹션 요약. |
| [docs/UNDERWORLD_EXTENSIBILITY.md](../../docs/UNDERWORLD_EXTENSIBILITY.md) | 확장성·피드백 확인·확장 포인트. |
| [docs/EDENOS_DYNAMICS_AND_UNDERWORLD.md](../../docs/EDENOS_DYNAMICS_AND_UNDERWORLD.md) | EdenOS 동역학과 언더월드 연동 맥락. |
