# EdenOS 설계 감사(Audit) 피드백 확인

**성격**: 설계자 본인의 설계 감사 — 자기 코드를 엔지니어링 눈으로 돌아본 결과.  
**기준**: 신학 해석 제외, 순수 보안·아키텍처 관점만.

---

## 1. 감사 결과 요약 (원본)

| 영역 | 상태 | 의미 |
|------|------|------|
| FSM 설계 (선악과 상태 전이) | ✅ GOOD | 방향 맞음 |
| Observer Reference Frame | ✅ GOOD | 유지 |
| Kernel 격리 | ✅ 완료 | Adam/Eve는 KernelProxy만, Runner가 kernel+proxy 조립 |
| Physics 불변 보장 | ✅ 규약 | LORE→Physical 역침투 금지 규약 명시 |
| Scheduler | ✅ 도입 | EdenScheduler, tick 기반 실행 |
| Intent Validator | ✅ 도입 | intent_validator.py, Validator→Executor 흐름 |
| mutation_rate 위치 | ✅ 분리 | evolution_config, Eve는 주입만 |

---

## 2. 현재 코드 상태 대조

### 2.1 Kernel 격리 ✅ 완료 (v1.1.0 반영)

**한 일**  
- `kernel/` 폴더: `life_kernel.py`(EdenKernel), `kernel_proxy.py`(KernelProxy).  
- `adam.py`: `from .tree_of_life import ...` 제거, `KernelProxy` 만 사용.  
- **런타임 경로**: Runner는 `EdenKernel` + `KernelProxy` 를 생성하고, `adam.observe(kernel_proxy=...)`, `adam.act(kernel_proxy=...)` 만 호출. Adam 은 `proxy.request_tree_access()`, `proxy.trigger_kernel_trap()` 경유만 사용.  
- **eve.py**: `TreeOfLife`, `KnowledgeTree` import 제거, `KernelProxy` 타입만 사용. `observe`/`act` 모두 `kernel_proxy` 인자로 아담에 전달.  
- **eden_os_runner.py**: `life_tree`/`know_tree` 제거, `kernel` + `kernel_proxy` 조립. Step 3 은 `kernel.step(1)`, Step 5 는 `kernel_proxy` 만 Adam/Eve 에 전달. 계승 시 새 관리자용 `make_kernel_proxy(kernel, new_adam.id)` + `activate()` 로 `_kernel_proxy` 갱신.  
- **observer_mode.py**: `InternalObserver.snapshot()` 에서 `adam.observe(..., kernel_proxy=runner._kernel_proxy)` 사용.

**결론**: Agent 가 커널 객체를 직접 import 하거나 런타임에 raw tree 를 받지 않음. Kernel 격리 완료.

---

### 2.2 Physics 불변 보장 ✅ 규약 명시

**현재**  
- `EdenWorldEnv`: `@dataclass(frozen=True)` 적용됨 ✅  
- `Observation`, `Intent`, `ActionResult`, `BandInfo`, `ForkingState`, `ExpulsionRecord` 등도 `frozen=True` 사용.

**우려**  
- “LORE 이벤트 → 환경 파라미터 변경”이 **구조적으로** 열려 있는지 여부.  
- **원칙**: Narrative → Physics 흐름은 **절대 불허**. Physics → Scenario → Narrative 단방향만 허용.  
- **권장**: 모든 환경/물리 관련 스냅샷 타입에 `frozen=True` 또는 `__frozen__` 규약을 명시하고, LORE 레이어가 이 타입을 **수정하는 코드 경로가 없음**을 검토.

**결론**: 규약 문서화 완료. LORE가 물리 필드를 수정하는 코드 경로는 없음.

---

### 2.3 Scheduler ✅ 도입됨

**현재**  
- `EdenOSRunner.step()` 이 7단계를 **순차적으로** 한 번에 실행 (env → rivers → tree → guard → agents → lineage → log).  
- 단순 스크립트 순서이며, “phase/tick 기반 스케줄러”는 없음.

**권장**  
- `EdenScheduler` (또는 동일 역할) 도입:  
  - phases = [ENV_UPDATE, INFRA_UPDATE, SECURITY_CHECK, AGENT_EXECUTION, LINEAGE_UPDATE, LOG_COMMIT]  
  - `scheduler.tick()` → 각 서브시스템을 phase 순서로 한 틱씩 실행.  
- Runner는 “스케줄러를 한 번 돌린다”는 식으로만 호출.

**결론**: phase 기반 tick 구조 도입 완료.

---

### 2.4 Intent Validator ✅ 도입됨

**현재**  
- Agent → Intent → (Guard 검사) → act() 내부에서 분기 실행.  
- **Intent 자체를 검증하는 레이어**(illegal intent 차단, rate limiting, world consistency check)는 없음.

**권장**  
- `intent_validator.py` (또는 동일 역할):  
  - 입력: Agent, Intent, WorldState(또는 스냅샷).  
  - 출력: allow / deny + reason.  
- 흐름: Agent → Intent → **Validator** → Executor(Runner/act).

**결론**: Agent → Intent → Validator → Executor 흐름 반영 완료.

---

### 2.5 mutation_rate 위치 ✅ 분리됨

**현재**  
- **Eve** (`eve.py`): `SuccessionEvent.mutation_rate`, `make_eve(..., mutation_rate=0.05)` — 계승 시 **정책 변형** 비율.  
- **Lineage** (`lineage.py`): `mutation_rate` 필드는 없음. 대신 “정책 변형(mutation)” 개념이 주석/설명에 등장.  
- 감사 지적: “mutation_rate가 Lineage 안에 있으면 안 됨, **evolution/ 분리 필요**”, “Agent는 mutation을 몰라야 한다”.

**해석**  
- 생물학적 mutation_factor(world.ic)와 계승 정책 변형(mutation_rate)은 **다른 레이어**.  
- 정책 변형률은 “진화/시나리오” 레이어에 두고, Eve/Lineage는 그 레이어에서 **주입받는 값**만 쓰는 구조가 맞음.

**권장**  
- `evolution/` (또는 `scenario/`) 같은 모듈에서 `policy_mutation_rate`(또는 동일 개념)를 CONFIG로 정의.  
- Eve / Lineage는 이 값을 인자로 받기만 하고, 기본값을 “evolution에서 온 설정”으로 채움.

**결론**: 정책 변형률이 evolution 레이어에서 정의·주입되도록 반영 완료.

---

### 2.6 FSM 설계 ✅ / Observer ✅

- 선악과 상태 전이(IMMORTAL_ADMIN → MORTAL_NPC, 비가역)는 `lineage.py` 에서 명확히 구현됨.  
- Observer Mode (Internal/External/Relative)는 유지하는 것이 맞음.

---

## 3. 우선순위 정리 (감사 권장 순서)

| 순위 | 항목 | 작업 |
|------|------|------|
| 1 | Kernel 격리 완료 | Runner에서 Adam.act()에 kernel_proxy만 넘기고, act() 내부는 proxy 전용으로 변경. Eve에서 TreeOfLife/KnowledgeTree import 제거, proxy 또는 추상 타입만 사용. |
| 2 | Scheduler 도입 | EdenScheduler(phases + tick) 도입, Runner는 scheduler 기반으로 실행. |
| 3 | Intent Validator | intent_validator.py 추가, Agent → Intent → Validator → Executor 흐름으로 검증 레이어 삽입. |
| 4 | Physics 격리 재확인 | LORE가 물리/환경 스냅샷을 수정하는 경로가 없는지 점검. 필요 시 모든 물리 관련 타입 frozen 규약 문서화. |
| 5 | mutation_rate 분리 | policy_mutation_rate(또는 동일 개념)를 evolution/ 또는 scenario config로 이동, Eve/Lineage는 주입만 받기. |

---

## 4. 한 줄 결론

- 감사 결과는 **설계자 본인의 설계 감사**로 보는 것이 맞고, **엔지니어링적으로 타당**하다.  
- **Kernel 격리**, **Physics 규약**, **Scheduler**, **Intent Validator**, **mutation_rate evolution 분리** 가 모두 반영된 상태다.  
- 이 문서는 **구현 반영 후** 갱신된 코드 상태 기준이다.

---

## 5. 추가 보안/구조 패치 제안 대조

(외부 피드백: "권한 역설 해결, CoordinateMapper, Eve Pub/Sub, 로그 위변조 방지" 4가지)

### 5.1 권한 역설 — Kernel Trap 선행 ✅ 반영됨

**제안**: 선악과 API를 "커널 트랩"으로 설계하고, **아담이 트리거하는 순간 커널이 토큰을 먼저 만료** → 그 다음 lineage 강등 → 체루빔이 낮아진 권한으로 403.

**현재 코드**  
- `adam.py`: `access_knowledge_tree` 의도 시 `kernel_proxy.trigger_kernel_trap()` 호출 후 `_knowledge_consumed = True`, `AdminStatus.EXPELLED` 설정.  
- `life_kernel.py` `trap_knowledge_consumed()`: (1) KnowledgeTree.consume (2) **expire_token(agent_id)** (3) 생명나무 lock (4) trap_fired 기록.  
- Runner는 `act()` 반환 후 `adam.knowledge_consumed`를 보고 `lineage.record_expulsion()` 호출.

**결론**: **트랩이 act() 내부에서 먼저 실행**되므로, 권한 강등은 커널(토큰 만료) → lineage(MORTAL_NPC) 순서가 보장됨. Root가 스스로 체루빔을 해제할 수 없음.

---

### 5.2 좌표 역전 캡슐화 — CoordinateMapper 🟡 미도입

**제안**: `lat * -1` 등을 여러 곳에서 쓰지 말고, **CoordinateMapper**(to_eden_view / to_modern_view)로 캡슐화.

**현재**  
- `genesis_narrative.py`: 에덴/현재 좌표를 딕셔너리(`eden_lat`, `current_lat`)로 보관. 주석에 "좌표 역전 (lat×−1)" 명시.  
- `lineage.py`: 카인/아벨 스폰지 `current_lat`/`eden_lat` 하드코딩.  
- 물리/시나리오 레이어는 `_BAND_LATS` 등 절대 위도 사용.

**결론**: 좌표 역전이 서사/로그 레이어에만 국한되어 있으나, **공통 CoordinateMapper는 없음**. 추후 카인/아벨 에이전트 이동·물리 엔진 연동 시 단일 매퍼 도입 권장.

---

### 5.3 이브 비동기 이벤트 (Pub/Sub) 🟡 현재는 틱 검사

**제안**: 선악과 후 "지금 포크해야 하나?" 매 틱 검사 대신, **Event('FALL_OF_MAN') 브로드캐스트 → Eve 데몬이 구독 후 lineage.fork() 활성화**.

**현재**  
- Runner `_execute_tick()`: 선악과 감지 시 `lineage.record_expulsion()` 호출 → 같은 틱/다음 틱에 `lineage.is_expelled and not _offspring_spawned`이면 `spawn_cain_and_abel()` 호출.  
- Eve는 `check_succession(adam, obs)`로 **계승 조건**(수명/에덴 지수)만 검사. 선악과→카인/아벨 스폰은 Runner가 직접 처리.

**결론**: 선악과→스폰은 **Runner 단일 경로**에서 순차 처리. Pub/Sub로 바꾸면 이벤트 추적·디버깅이 명확해지나, 현재 규모에서는 틱 기반으로도 동작상 문제 없음. 확장 시 이벤트 버스 도입 검토 가능.

---

### 5.4 로그 위변조 방지 (WORM) ✅ 불변 구조

**제안**: genesis_log를 "생성 순간 해시가 찍히는 WORM", 에이전트가 수정 불가하도록.

**현재**  
- `GenesisEvent`: `@dataclass(frozen=True)` — 필드 변경 불가.  
- `GenesisLog`: `adam_event`/`eve_event`는 불변 객체. 로그는 `_finalize_genesis()`에서 **한 번만** 생성되고 Runner가 덮어쓰지 않음.  
- 에이전트(아담/이브/카인 등)는 `GenesisLog` 인스턴스를 받지 않으며, 수정 경로 없음.

**결론**: 탄생 이벤트는 frozen, 생성 시점 단일. **런타임에서 에이전트가 genesis 로그를 수정할 수 있는 경로는 없음.** (선택: `GenesisLog` 자체를 `frozen=True`로 강화 가능.)

---

## 6. 동역학/항상성 피드백 (참고)

**요지**: "관리자 = 해킹으로 쫓겨나는 게 아니라, **항상성(integrity) 붕괴에 의한 자연 전이**로 설계할 수 있다."

**현재 설계**  
- 선악과 = **이벤트 기반** 전이 (knowledge_consumed = True 트리거).  
- 동역학적 전이(integrity < θ 연속 N틱 → DEGRADED → MORTAL_NPC)는 **미구현**.

**정리**  
- 현재는 "선악과 섭취" 단일 이벤트로 비가역 전이.  
- 추후 **stress_index / stability / integrity**를 틱별로 계산하고, "integrity < θ for N ticks" 시 자동 강등하는 모드는 **별도 확장**으로 도입 가능. 신학 해석은 제외하고, 옵션으로만 문서화해 두면 됨.

