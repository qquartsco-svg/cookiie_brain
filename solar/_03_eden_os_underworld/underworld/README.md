# solar/underworld — 지하·하데스 목소리 (거시 감시·의식 경고)

**본편 위치**: 이 폴더는 [CookiieBrain/solar](https://github.com/qquartsco-svg/cookiie_brain) 의 **천지창조 로직·서사 흐름 안**에 있는 엔진이다. [solar/README.md](../README.md)의 개념 레이어 테이블에서 **"지하"** 한 줄로 이어져 나온다.  
**독립 엔진**: CookiieBrain/solar 의존 없이 단독 사용 시 **[qquartsco-svg/UnderWorld](https://github.com/qquartsco-svg/UnderWorld)** 레포 참고. 그쪽 README에 서사적 출처·엔지니어링이 분리되어 있다.

---

## 서사 — 이 레이어가 만들어지는 맥락

solar의 **개념 레이어(Creation Days)** 는 대략 다음 순서로 쌓인다.

- **day4/core, data**: 태양계 중력장·우주필드·달·지구. 물리 코어.
- **day1~day3**: 빛·궁창·땅/바다/식생·Gaia. 환경이 형성됨.
- **day4** 순환: 질소·Milankovitch·조석. 장주기 순환.
- **day5~day6**: 생물 이동·진화 상호작용.
- **cognitive/, bridge/**: 인지·BrainCore 브리지.

이 흐름 **안**에서, **물리 코어(day4)와 지상(EdenOS·에덴·아담)** 사이에는 “행성이 거시 룰을 지키는지”를 **감시만** 하고, 그 결과를 **의식 경고(ConsciousnessSignal)** 로만 올려보내는 레이어가 필요해진다. 그게 **underworld(지하·하데스 목소리)** 다.  
즉, **서사적으로** “천지창조·에덴·지상 동역학”이 이어지는 본편 구조 위에, **거시 제약 감시**라는 한 역할만 떼어 둔 레이어가 이 폴더다.  
**지상(EdenOS)** 은 이 신호를 observe / homeostasis / integrity_fsm에 반영해, **동역학적 한계선**을 넘을 때만 자연스럽게 상태 전이(MORTAL_NPC 등)를 수행한다.  
→ “해킹/스토리 이벤트”가 아니라 **물리·항상성 한계 → 경고 → FSM 전이**로만 흐르게 하는 것이 설계 목표다.  
서사상 다음 장은 **지상** — [solar/eden/](../eden/) 의 에덴·아담·Runner가 이 목소리를 받아 항상성과 무결성으로 이어가는 부분이다.

---

## 한 줄 요약

물리 코어(day4) 위에서 **행성 규모 룰 위반**을 감시하고, **의식 경고(ConsciousnessSignal)** 만 내보내는 레이어.  
지상(EdenOS)은 이 신호를 observe/homeostasis/integrity_fsm에 반영해, “동역학적 한계선”을 넘을 때만 자연스럽게 상태 전이(MORTAL_NPC 등)를 수행한다.

> **설계 규칙 (불가침)**  
> **Hades ONLY measures. Hades NEVER acts.**  
> 언더월드는 관측·신호 생성만 담당. 결정·처벌·전이는 지상 동역학(IntegrityFSM 등) 전용.

**레이어 불가침 (수정·보완 시)**  
모듈 간 의존성은 **한 방향**만 허용된다. 아래 → 위 순서를 지키면 꼬이지 않는다.  
- **L0**: `consciousness`, `rules` (기반. 서로 참조 금지, stdlib만)  
- **L0'**: `deep_monitor` (물리 어댑터. 선택적 day4)  
- **L1**: `hades` (측정만. consciousness, deep_monitor, rules만 참조)  
- **L1.5**: `propagation` (전파 DTO. hades/wave_bus/siren 참조 금지)  
- **L2**: `wave_bus`, `siren` (전파·변환만. hades 참조 금지)  
- **외부**: `solar.eden` 은 **어떤 underworld 모듈에서도 import 금지**.  
→ 상세: [LAYERS.md](LAYERS.md)

**신호 불변성 (보안/무결성)**  
모든 `ConsciousnessSignal` 객체는 `@dataclass(frozen=True)`로 생성되며, 지상의 그 어떤 에이전트(Root Admin 포함)도 수신된 경고(severity 등)를 위변조하거나 지울 수 없다. 신호는 생성 후 읽기 전용이다.

**강제 파이프라인 (동역학 보완)**  
에이전트(아담)가 observe() 단계에서 하데스의 목소리를 "듣고도" 의도적으로 무시하더라도, **EdenOS Runner는 하데스 신호를 HomeostasisEngine과 IntegrityFSM에 하드웨어 인터럽트처럼 강제로 직접 주입한다.** 따라서 에이전트 의지와 무관하게, 임계치를 넘으면 반드시 자연 강등(Downgrade) 동역학이 작동한다.

---

## 1. 개념·서사

| 구분 | 설명 |
|------|------|
| **역할** | “지하의 목소리” — 인격화된 악역이 아니라, **거시 룰 위반을 측정해 신호로만 전달**하는 관측자. |
| **입력** | (선택) 물리 코어(EvolutionEngine 등)의 스냅샷. 없으면 조용(QUIET) 반환. |
| **출력** | `List[ConsciousnessSignal]`. 평상시 `[QUIET]`, 복합 위반 시 `[RULE_VIOLATION, ENTROPY_WARNING, ...]` 등 여러 신호. FSM이 스트레스를 다중으로 누적 가능. |
| **지상 연동** | EdenOS Runner가 매 틱 `hades.listen()` 호출 → 반환 **리스트**를 observe(첫 항목 또는 전체), homeostasis.update(리스트), integrity_fsm.step에 넘김. **Runner가 신호를 강제 주입**하므로 에이전트가 무시해도 동역학은 작동. |

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
                    rules.evaluate_rules_all(deep)  ──► list[(severity, signal_type, message)]
                            │
                            ▼
                    ConsciousnessSignal(source="underworld.hades", …)  × N (위반 개수)
                            │
                            ▼
                    지상: observe(hades_signals), homeostasis.update(…, hades_signals), integrity_fsm.step(…)
                    ※ Runner가 리스트를 강제 주입 — 에이전트 무시 불가.

(선택) 전파 레이어: raw = hades.listen(...) → wave = wave_bus.propagate(raw, ...) → siren.broadcast(wave, ...) → PerceptionSignal 리스트를 hades_signal 로 넘겨도 됨. WaveBus/Siren 은 전파·변환만, 판단/전이 없음.
```

### 2.1 진입점 API

| API | 설명 |
|-----|------|
| `HadesObserver.listen(tick, world_snapshot=None, deep_engine=None) -> List[ConsciousnessSignal]` | 현재 틱 기준 목소리 **리스트** 반환. 위반 없으면 `[QUIET]`, 복합 위반 시 여러 신호. `world_snapshot`은 덕 타이핑(아래)만 사용. `deep_engine` 없으면 `[QUIET]`. |

**world_snapshot 덕 타이핑 (의존성 격리)**  
underworld는 지상 클래스(EdenWorldEnv 등)를 import하지 않는다. `Any`/`Protocol`만 사용하고, `getattr(world_snapshot, "eden_index", 1.0)` 로 지표만 추출해 순환 참조를 막는다.

### 2.2 룰 정책 (데이터 주도)

- **rules.py**: `RuleSpec`(check_key, violation_severity, signal_type, message), `DEFAULT_RULES` 리스트, `evaluate_rules(deep_snapshot, rules=None)`(단일), `evaluate_rules_all(deep_snapshot, rules=None)`(다중 위반 → 리스트).
- **hades.py**: 룰/문구/심각도 없음. `evaluate_rules_all(deep)` 호출만 수행.
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
| **룰 확장** | `RuleSpec` 리스트 주입 또는 `evaluate_rules` / `evaluate_rules_all(deep, rules=...)` 로 정책 교체. hades.py 수정 불필요. |
| **확장 포인트** | (B) `world_snapshot`을 evaluate_rules에 넘겨 severity/민감도 보정(덕 타이핑 유지). (C) 다중 위반은 **현재 구현됨**: `listen() -> List[ConsciousnessSignal]`. |

상세: [docs/UNDERWORLD_EXTENSIBILITY.md](../../docs/UNDERWORLD_EXTENSIBILITY.md)

### 3.1 파일 역할

| 파일 | 역할 |
|------|------|
| `consciousness.py` | `ConsciousnessSignal`, `SignalType` — 신호 DTO. |
| `deep_monitor.py` | `DeepSnapshot`, `read_deep_snapshot()` — 물리 코어 어댑터. |
| `hades.py` | `HadesObserver`, `listen()` — 오케스트레이터. |
| `rules.py` | `RuleSpec`, `DEFAULT_RULES`, `evaluate_rules()`, `evaluate_rules_all()` — 룰 데이터·평가. |
| `propagation.py` | `WavePacket`, `PerceptionSignal` — 전파 계층 DTO (공명/파동 확장). |
| `wave_bus.py` | `WaveBus`, `propagate()` — 감쇠/전파만 (판단·행동 없음). |
| `siren.py` | `Siren`, `make_siren()` — 지역 변환/재방송만 (판단·행동 없음). |

**레이어 순서·의존성**: [LAYERS.md](LAYERS.md) — 수정 시 참고.

---

## 4. 관련 문서

| 문서 | 설명 |
|------|------|
| [solar/README.md](../README.md) | 전체 흐름·개념 레이어 테이블(지하 포함)·본편 서사. |
| [solar/day4/README.md](../day4/README.md) | 물리 코어(EvolutionEngine 등) — underworld가 스냅샷을 읽는 상위 레이어. |
| [docs/UNDERWORLD_EXTENSIBILITY.md](../../docs/UNDERWORLD_EXTENSIBILITY.md) | 확장성·피드백 확인·확장 포인트. |
| [docs/EDENOS_DYNAMICS_AND_UNDERWORLD.md](../../docs/EDENOS_DYNAMICS_AND_UNDERWORLD.md) | EdenOS 동역학과 언더월드 연동 맥락(지상에서 신호 수신·전이). |
| **독립 엔진** | [qquartsco-svg/UnderWorld](https://github.com/qquartsco-svg/UnderWorld) — 본편 서사 출처 + 엔지니어링만 정리된 독립 패키지. |
