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
- (B) `world_snapshot`: 시그니처만 있고 listen 내부에서 아직 사용하지 않음. 민감도 보정용. **덕 타이핑**: underworld는 지상 클래스를 import하지 않고 `getattr(world_snapshot, "eden_index", 1.0)` 로만 사용.  
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

### (B) `world_snapshot` 이 실제로 사용되지 않음 — **미해결(확장 포인트)**

**코드**: `listen(..., world_snapshot: Any = None)` 시그니처만 있고, 본문에서 미사용.

**영향**: "지상 상태 + 지하 감시" 결합형 경고(예: EdenIndex 하락 시 민감도 상승)를 만들려면 규칙 레이어가 따로 필요.

**개선**: 룰 평가 시 `world_snapshot` (eden_index 등) 을 넘기고, 룰 정책에서 severity 보정에 사용. (섹션 0 “남은 확장 포인트” 참고.)

### (C) 신호가 1개만 나감 (단일 메시지) — **현재 유지, 확장 가능**

**코드**: 현재는 "가장 심각한 것 1개"에 가깝게 하나의 `ConsciousnessSignal` 만 반환.

**영향**: 동시 다발 위반(thermal + magnetic 등)을 배열로 보내거나, reason 코드 누적이 어려움.

**개선**: 필요 시 `list[ConsciousnessSignal]` 또는 `signals: tuple[ConsciousnessSignal, ...]` 반환으로 확장. (섹션 0 참고.)

---

## 3. 확장 방향 요약 (피드백 4가지 + 모듈 경계)

| 방향 | 현재 | 확장 시 |
|------|------|---------|
| **1. 동적 신탁(LLM/Oracle)** | 하드코딩 문자열 | 물리 파라미터 배열 → LLM 프롬프트 → 자연어 메시지 생성. ConsciousnessSignal.message 만 교체 가능하게. |
| **2. 멀티 에이전트 브로드캐스트** | 아담 단일 수신 | listen() 반환을 Pub/Sub로 분배. 수신자별 필터(예: 노아만 방주 신호). |
| **3. 시계열 이상 탐지** | 임계값 즉시 severity | ML 기반 이상 탐지, 수천 틱 드리프트 분석, "N틱 전" 점진적 경고 강화. |
| **4. 카르마/신용 계수** | 경고만 전달 | 에이전트별 경고 무시 누적 DB → 체루빔/다운스트림에서 신용 파라미터로 사용. (Hades는 측정만, 행동은 타 모듈.) |

**모듈 경계 제안 (피드백 반영)**  
- `consciousness.py`: 신호 DTO — 현 상태 유지.  
- `deep_monitor.py`: DeepSnapshot + 어댑터 — 프로토콜(엔진에서 읽을 필드 명세)만 정리하면 확장에 유리.  
- `hades.py`: **오케스트레이터** — 룰 평가는 `rules.evaluate_rules(deep)` 호출만.  
- **rules.py (추가됨)**: RuleSpec, DEFAULT_RULES, evaluate_rules(). 룰 목록·스코어링·메시지를 데이터로 보관 → hades.py 수정 없이 룰만 교체 가능.

---

## 4. 피드백 확인 결론

- **확장성**: underworld 는 "독립 패키지로 떼어낼 수 있는 형태"에 가깝다. (의존성 단순, 단일 진입점, 코어 없을 때 QUIET 스텁.)
- **룰 하드코딩 (A)**: **해소됨** — 이 워크스페이스 기준 `rules.py` 분리 및 hades 연동 완료. 다른 경로(/mnt/data 등) 업로드본은 별도 확인 필요.
- **지상 연동**: HomeostasisEngine·IntegrityFSM·runner에서 hades_signal 수신·stress/integrity 반영·N-tick 연속 시 자연 전이 이미 구현됨.
- **다음 확장 시 점검**: (B) world_snapshot 민감도 보정, (C) 다중 신호 반환, deep_monitor 프로토콜 명세.
