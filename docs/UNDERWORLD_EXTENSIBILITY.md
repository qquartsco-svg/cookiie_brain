# 언더월드(하데스 목소리) 확장성 분석 + 피드백 확인

**목적**: 현재 언더월드가 "따로 엔진 모듈화"할 확장성이 있는지, 피드백에서 지적한 병목과 개선 방향을 코드 기준으로 정리.

---

## 0. 현재 워크스페이스 상태 (피드백 확인 결과)

**rules.py 분리 리팩터링**  
- **이 워크스페이스(CookiieBrain) 기준**: 이미 반영되어 있음.  
- `solar/underworld/rules.py`: RuleSpec, DEFAULT_RULES, evaluate_rules(), **evaluate_rules_all()** (복합 위반 리스트).
- `solar/underworld/hades.py`: **evaluate_rules_all(deep)** 사용, **listen() -> List[ConsciousnessSignal]**.
- (다른 경로(/mnt/data 등) 업로드본에서는 반영 전 상태일 수 있음.)

**HomeostasisEngine · IntegrityFSM · 지상 연동**  
- 이미 구현되어 있음: `eden_os_runner.py`에서 `hades.listen()` → `hades_signal` → `adam.observe(..., hades_signal)`, `homeostasis.update(..., hades_signal, stress_injection)`, `integrity_fsm.step(tick, integrity)`.  
- 하데스 경고(severity)가 stress/integrity에 반영되고, integrity가 N tick θ 이하로 유지되면 자연 전이(MORTAL_NPC) 또는 선악과 시 `force_mortal()`로 즉시 전이.

**남은 확장 포인트**  
- ~~(B) world_snapshot~~: **반영됨** — `evaluate_rules_all(deep, world_snapshot=world_snapshot)` 로 전달, `_sensitivity_factor(world_snapshot)` 에서 `getattr(world_snapshot, "eden_index", 1.0)` 으로 severity 민감도 보정. eden_index 낮을수록 severity 증폭.  
- ~~(C) 단일 신호~~: **반영됨** — `listen() -> List[ConsciousnessSignal]`, `evaluate_rules_all()` 로 복합 위반 시 여러 신호 반환. Homeostasis는 리스트 시 최대 severity로 스트레스 가산.

**설계 보강 (보안/무결성)**  
- **ConsciousnessSignal 불변**: `@dataclass(frozen=True)` — 지상 에이전트가 severity 등 위변조 불가.  
- **강제 파이프라인**: Runner가 hades 신호를 HomeostasisEngine·IntegrityFSM에 직접 주입하므로, 에이전트가 observe에서 무시해도 임계치 초과 시 자연 강등 동역학 작동.

---

## 1. 현재 구조가 확장에 유리한 점 (피드백 확인 ✅)

| 항목 | 코드 상태 | 의미 |
|------|-----------|------|
| **의존성 방향** | `underworld` 가 `solar.eden` 을 import 하지 않음. `consciousness`, `deep_monitor` 만 참조. | 패키지 분리·재사용 시 부작용 적음. |
| **단일 진입점** | `HadesObserver.listen(tick, world_snapshot=None, deep_engine=None) -> List[ConsciousnessSignal]` | 지상 러너가 observe/homeostasis에 리스트 주입. 복합 위반 시 다중 신호. |
| **스텁 경로** | `read_deep_snapshot(engine=None)` → `core_available=False` 이면 QUIET 반환. | 물리 코어 없어도 동작. |

→ **따로 엔진 모듈화 가능해 보인다** 는 피드백과 일치.

---

## 2. 확장 시 막혔던 지점 (병목) — 현재 상태

### (A) 룰셋이 `listen()` 안에 하드코딩 — **해소됨**

**이전**: severity/signal_type/message 가 hades.py 내부에 고정되어 있던 상태.  
**현재**: `rules.py`에 RuleSpec·DEFAULT_RULES·evaluate_rules()로 분리됨. hades.py는 `evaluate_rules(deep)` 호출만 함. 룰 추가·정책 변경은 rules.py만 수정하면 됨. (섹션 0 참고.)

### (B) `world_snapshot` 이 실제로 사용되지 않음 — **해소됨**

**코드**: `listen(..., world_snapshot: Any = None)` → `evaluate_rules_all(deep, world_snapshot=world_snapshot)`. rules.py 에 `_sensitivity_factor(world_snapshot)` 추가, `getattr(world_snapshot, "eden_index", 1.0)` 로 민감도 계수 계산. eden_index 가 낮을수록 severity 증폭 (최대 1.0 cap).

### (C) 신호가 1개만 나감 (단일 메시지) — **해소됨**

**코드**: `listen() -> List[ConsciousnessSignal]`, `evaluate_rules_all(deep)` 로 **복합 위반 시 여러 신호** 반환. Homeostasis는 리스트 시 최대 severity 등으로 스트레스 가산.

**이전**: "가장 심각한 것 1개"만 반환하던 상태.  
**현재**: 동시 다발 위반(thermal + magnetic 등)이면 각 위반당 `ConsciousnessSignal` 한 개씩 리스트로 반환. (섹션 0 참고.)

---

## 3. 확장 방향 요약 (피드백 4가지 + 모듈 경계)

| 방향 | 현재 | 확장 시 |
|------|------|---------|
| **1. 동적 신탁(LLM/Oracle)** | 하드코딩 문자열 | 물리 파라미터 배열 → LLM 프롬프트 → 자연어 메시지 생성. ConsciousnessSignal.message 만 교체 가능하게. |
| **2. 멀티 에이전트 브로드캐스트** | 아담 단일 수신 | listen() 반환을 Pub/Sub로 분배. 수신자별 필터(예: 노아만 방주 신호). |
| **3. 시계열 이상 탐지** | 임계값 즉시 severity | ML 기반 이상 탐지, 수천 틱 드리프트 분석, "N틱 전" 점진적 경고 강화. |
| **4. 카르마/신용 계수** | 경고만 전달 | 에이전트별 경고 무시 누적 DB → 체루빔/다운스트림에서 신용 파라미터로 사용. (Hades는 측정만, 행동은 타 모듈.) |

### (D) 공명/파동 전파 모델 (WaveBus + Siren Nodes) — **새 확장 포인트**

**의도**: UnderWorld의 불가침 규칙(측정만, 행동 없음)을 유지한 채, 신호를 “중앙 경고 → 파동 형태 전파 → 지역/에이전트가 수신 후 동역학으로 반응”하는 **분산 항상성** 구조로 확장한다.

#### 역할 분리 (불가침 경계 추가)

- **Hades = Measure / Publish (Origin)**: raw 진단 신호를 발행만 한다.  
  - 불변식: **Hades ONLY measures. Hades NEVER acts.**
- **WaveBus = Propagate (Medium)**: 라우팅/지연/감쇠/필터링 등 “전파 물리”만 담당한다.  
  - 불변식: *WaveBus NEVER decides/acts.*
- **Siren = Transduce / Broadcast (Resonator)**: raw telemetry를 지역 컨텍스트로 **변환/재방송**한다. 판단자는 아니다.  
  - 불변식: **Sirens ONLY propagate/transform. Sirens NEVER decide/act.**
- **World Receivers = React (Controller side)**: Homeostasis/IntegrityFSM/Runner에서 누적·전이·행동이 발생한다.

#### 파동(감쇠) 함수 스케치

신호 전파는 결정론적 함수로 두면 테스트/재현성이 좋아진다.

\[
severity' = f(severity, distance, medium, time)
\]

예시(개념):

- 글로벌 `SYSTEM_PANIC` → 지역 `ENTROPY_WARNING` → 개인 `intuition` (동일 원신호의 스케일 변환)

#### 코드 합성 위치 (권장)

Hades는 그대로 두고, **Runner(또는 별도 레이어)** 에서 합성한다. (Hades API/책임 불변 유지)

```python
raw = hades.listen(tick=t, deep_engine=core, world_snapshot=world)  # measures only

wave = wave_bus.propagate(raw, context=world)  # pure propagation/attenuation

for siren in sirens:  # pure transducer/broadcaster
    local_signals = siren.broadcast(wave, region=region_state)
    receivers.deliver(local_signals)  # decide/act happens here (homeostasis/fsm)
```

#### DTO 전략 (추천 2안)

- **안 A (단일 DTO 유지)**: `ConsciousnessSignal`에 `scope`/`region`/`attenuated_from` 같은 메타를 추가해도 되지만,
  UnderWorld의 “순수 진단 DTO”가 비대해질 수 있다.
- **안 B (계층 DTO 분리)**:  
  - Raw: `ConsciousnessSignal` (Hades가 만드는 원신호, 현재 유지)  
  - Propagated: `WavePacket` (WaveBus가 만드는 전파 패킷)  
  - Perceived: `PerceptionSignal` (Siren이 만드는 의미론적 이벤트)

UnderWorld(핵심)의 안정성을 최우선으로 하면 **안 B**가 경계가 깨끗하다.

#### 구현 상태 (코드 반영)

- **propagation.py**: `WavePacket`, `PerceptionSignal` (frozen). `PerceptionSignal.is_quiet`, `to_consumable_severity()`.
- **wave_bus.py**: `WaveBus.propagate(signals, context=..., distance=..., medium=..., tick=...)` → `List[WavePacket]`. 감쇠 `severity' = severity / (1 + distance) * medium_factor`. `propagate()` 편의 함수.
- **siren.py**: `Siren(region_id, message_template=...)`, `broadcast(wave_packets, region_state=..., tick=...)` → `List[PerceptionSignal]`. `make_siren(region_id, ...)`.
- **Runner에서 선택 사용**: 기존처럼 `hades_signal = hades.listen(...)` 만 써도 되고, 전파 레이어를 쓰면  
  `raw = hades.listen(...)` → `wave = wave_bus.propagate(raw, ...)` → `for siren in sirens: perceived.extend(siren.broadcast(wave, ...))` → `hades_signal = perceived` 로 넘기면 된다. `PerceptionSignal`은 `severity`, `message`, `is_quiet` 를 갖추어 기존 `observe`/`homeostasis.update` 와 호환된다.

**모듈 경계 제안 (피드백 반영)**  
- `consciousness.py`: 신호 DTO — 현 상태 유지.  
- `deep_monitor.py`: DeepSnapshot + 어댑터 — 프로토콜(엔진에서 읽을 필드 명세)만 정리하면 확장에 유리.  
- `hades.py`: **오케스트레이터** — 룰 평가는 `rules.evaluate_rules_all(deep)` 호출만.  
- **rules.py (추가됨)**: RuleSpec, DEFAULT_RULES, evaluate_rules(), **evaluate_rules_all()**. 룰 목록·스코어링·메시지를 데이터로 보관 → hades.py 수정 없이 룰만 교체 가능.

---

## 4. 피드백 확인 결론

- **확장성**: underworld 는 "독립 패키지로 떼어낼 수 있는 형태"에 가깝다. (의존성 단순, 단일 진입점, 코어 없을 때 QUIET 스텁.)
- **룰 하드코딩 (A)**: **해소됨** — 이 워크스페이스 기준 `rules.py` 분리 및 hades 연동 완료. 다른 경로(/mnt/data 등) 업로드본은 별도 확인 필요.
- **지상 연동**: HomeostasisEngine·IntegrityFSM·runner에서 hades_signal 수신·stress/integrity 반영·N-tick 연속 시 자연 전이 이미 구현됨.
- **다음 확장 시 점검**: deep_monitor 프로토콜 명세, (B) world_snapshot 민감도 보정 **반영 완료**.
- **레이어 고정**: 수정·보완 시 레이어 꼬임 방지를 위해 [solar/underworld/LAYERS.md](../solar/underworld/LAYERS.md) 의 허용/금지 의존성 준수.
