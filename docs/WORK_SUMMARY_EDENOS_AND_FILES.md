# EdenOS 관련 전체 작업 점검 — 파일·폴더·수정 내역

**목적**: 지금까지 만진 파일·폴더 위치·수정 내용을 한눈에 보고, 다음 작업을 판단할 수 있도록 정리.

---

## 1. 작업이 진행된 맥락 (흐름)

1. **EdenOS 설계 감사(Audit) 반영**  
   - Kernel 격리, Physics 규약, Scheduler, Intent Validator, mutation_rate 분리 → 코드·문서 반영.
2. **README·GitHub·블록체인**  
   - 루트 README 갱신, blockchain/ 서명·검증 안내, PHAM 체인 검증 스크립트·워크플로 추가.
3. **추가 보안/동역학 피드백 반영**  
   - Kernel Trap vs 동역학 레이어 분리, Hades(지하) 개념 정리, 항상성·Integrity FSM·Underworld 구현 및 Runner 연동.

---

## 2. 폴더 구조 (변경·추가된 부분 중심)

```
CookiieBrain/
├── .github/
│   └── workflows/
│       └── pham-verify.yml          ← [신규] PHAM 체인 무결성 CI
│
├── blockchain/
│   ├── README.md                    ← [수정] 서명 방법·체인 검증 안내
│   └── pham_verify_chain.py         ← [신규] pham_chain_*.json 검증 스크립트
│
├── docs/
│   ├── EDEN_OS_AUDIT_FEEDBACK_CHECK.md   ← [신규] 감사 피드백 대조 + 추가 4가지 패치·동역학 정리
│   └── EDENOS_DYNAMICS_AND_UNDERWORLD.md ← [신규] Kernel Trap vs Dynamics, Hades 개념·폴더 구조
│
├── README.md                        ← [수정] 버전 v1.1.0, eden_os 목록, PHAM·검증 링크
│
└── solar/
    ├── eden/
    │   └── eden_os/
    │       ├── adam.py              ← [수정] observe(hades_signal), KernelProxy만 사용
    │       ├── eden_os_runner.py    ← [수정] Scheduler, IntentValidator, Homeostasis, IntegrityFSM, Hades 연동
    │       ├── eden_world.py        ← [수정] 물리 격리 규약 docstring
    │       ├── eve.py               ← [수정] mutation_rate = evolution_config 주입
    │       ├── genesis_log.py       ← [수정] GenesisLog @dataclass(frozen=True)
    │       ├── evolution_config.py  ← [신규] policy_mutation_rate, get_policy_mutation_rate()
    │       ├── homeostasis_engine.py← [신규] stress/integrity 매 틱, stress_injection
    │       ├── integrity_fsm.py    ← [신규] N-tick 연속 → IMMORTAL→DEGRADED→MORTAL 전이
    │       ├── intent_validator.py  ← [신규] Intent 검증 레이어 (Validator→Executor)
    │       ├── scheduler.py         ← [신규] EdenScheduler, EdenPhase, tick(runner)
    │       ├── README.md            ← [수정] kernel/, scheduler, intent_validator, evolution_config 반영
    │       └── kernel/               ← [신규 폴더]
    │           ├── __init__.py
    │           ├── life_kernel.py   ← EdenKernel, trap_knowledge_consumed
    │           └── kernel_proxy.py  ← KernelProxy (Agent는 이것만 접근)
    │
    └── underworld/                  ← [신규 폴더] 지하(Hades) 레이어
        ├── __init__.py
        ├── consciousness.py         ← ConsciousnessSignal, SignalType
        ├── deep_monitor.py          ← DeepSnapshot, read_deep_snapshot (day4/core 선택)
        └── hades.py                  ← HadesObserver, listen() → 지상에 목소리 전달
```

---

## 3. 신규 생성된 파일 (경로 + 역할)

| 경로 | 역할 |
|------|------|
| `.github/workflows/pham-verify.yml` | push/PR 시 지정된 PHAM 체인 8개 무결성 검증 |
| `blockchain/pham_verify_chain.py` | pham_chain_*.json 의 prev_hash·hash 연결 검증 |
| `docs/EDEN_OS_AUDIT_FEEDBACK_CHECK.md` | 감사 피드백 대조표, 추가 4가지 패치·동역학 정리 |
| `docs/EDENOS_DYNAMICS_AND_UNDERWORLD.md` | Kernel Trap vs Dynamics, Hades 개념, 폴더 구조 문서 |
| `solar/eden/eden_os/evolution_config.py` | EVOLUTION_CONFIG, get_policy_mutation_rate() — Eve mutation_rate 주입용 |
| `solar/eden/eden_os/homeostasis_engine.py` | HomeostasisEngine: stress_index·integrity 매 틱, stress_injection(선악과) |
| `solar/eden/eden_os/integrity_fsm.py` | IntegrityFSM: θ1/θ2·N-tick → IMMORTAL→DEGRADED→MORTAL, force_mortal() |
| `solar/eden/eden_os/intent_validator.py` | IntentValidator, ValidationResult — Agent→Validator→Executor |
| `solar/eden/eden_os/scheduler.py` | EdenScheduler, EdenPhase, make_scheduler(), tick(runner) |
| `solar/eden/eden_os/kernel/__init__.py` | kernel 패키지 공개 |
| `solar/eden/eden_os/kernel/life_kernel.py` | EdenKernel, trap_knowledge_consumed (토큰 만료·생명나무 lock) |
| `solar/eden/eden_os/kernel/kernel_proxy.py` | KernelProxy — Agent는 이 경로로만 커널 접근 |
| `solar/underworld/__init__.py` | underworld 패키지, ConsciousnessSignal·HadesObserver 공개 |
| `solar/underworld/consciousness.py` | ConsciousnessSignal(frozen), SignalType (ENTROPY_WARNING 등) |
| `solar/underworld/deep_monitor.py` | DeepSnapshot, read_deep_snapshot (day4/core 선택 의존) |
| `solar/underworld/hades.py` | HadesObserver, listen(tick, world, deep_engine) → ConsciousnessSignal |

---

## 4. 수정된 파일 (경로 + 변경 요약)

| 경로 | 변경 요약 |
|------|-----------|
| `README.md` | 버전 v1.1.0, eden_os 폴더 목록(kernel/, scheduler, intent_validator, evolution_config), PHAM 블록·검증 링크 |
| `blockchain/README.md` | 서명 명령(방법 A/B), 체인 검증(pham_verify_chain.py), v4 형식 참고 문구 |
| `solar/eden/eden_os/README.md` | 아키텍처에 kernel/, scheduler, intent_validator, evolution_config, 물리 격리·mutation 주입·Scheduler.tick 반영 |
| `solar/eden/eden_os/adam.py` | `observe(..., hades_signal=None)` 추가 — 목소리 있으면 notes·anomaly 반영 |
| `solar/eden/eden_os/eden_os_runner.py` | (1) Scheduler.tick() 사용 (2) IntentValidator (3) HomeostasisEngine·IntegrityFSM·Hades 생성 및 Step 5 전 hades.listen(), observe(hades_signal), 선악과 시 stress_injection·force_mortal, 동역학/선악과 둘 다에 대해 record_expulsion |
| `solar/eden/eden_os/eden_world.py` | docstring에 물리 격리 규약(LORE→PHYSICAL 금지, Physics→Scenario→Narrative 단방향) 명시 |
| `solar/eden/eden_os/eve.py` | mutation_rate=None 시 get_policy_mutation_rate() 사용, make_eve()에서 evolution_config 주입 |
| `solar/eden/eden_os/genesis_log.py` | GenesisLog 를 `@dataclass(frozen=True)` 로 변경 (위변조 방지) |

---

## 5. 현재 상태 요약

- **EdenOS 감사 항목**: Kernel 격리, Physics 규약, Scheduler, Intent Validator, mutation_rate 분리 — 코드·문서 반영 완료.
- **동역학 레이어**: 선악과 = 이벤트만이 아니라 “대량 stress_injection + integrity 붕괴”로 통합; N-tick 연속 조건으로 자연 전이(IntegrityFSM) 가능.
- **지하(Hades)**: underworld 패키지 추가, 지상 observe에 목소리(hades_signal) 전달, Homeostasis의 stress에도 반영.
- **블록체인**: PHAM 체인 검증 스크립트·CI 추가, README에 서명/검증 방법 정리.

---

## 6. 다음에 판단·결정할 수 있는 포인트

1. **DEGRADED_ADMIN**  
   - IntegrityFSM에는 있으나, lineage.AdamProcessMode는 아직 IMMORTAL / MORTAL 두 개만 있음.  
   - DEGRADED를 lineage에 넣을지, “행동 공간만 축소”로만 둘지 결정.

2. **CoordinateMapper**  
   - 감사 피드백 5.2: 좌표 역전(lat×-1) 캡슐화 제안.  
   - 현재는 genesis_narrative·lineage 등에만 사용. 카인/아벨 이동·물리 연동 시 단일 매퍼 도입 여부.

3. **observe() 에서 hades_signal**  
   - 이미 `adam.observe(..., hades_signal=hades_signal)` 로 전달되고, notes·anomaly에 반영됨.  
   - decide() 정책에서 “지하 경고 시 우선 반응” 같은 룰을 넣을지.

4. **day4/core 연동**  
   - deep_monitor는 day4/core 가 있으면 읽도록 되어 있고, 없으면 스텁.  
   - 실제 지자기·지열 등으로 Hades severity를 채울지, 어떤 지표를 쓸지.

5. **커밋 단위**  
   - 감사 반영 / README·블록체인 / 동역학·Underworld 를 한 커밋으로 묶을지, 주제별로 나눌지.

---

이 문서는 **지금 만진 파일·폴더 위치와 수정 내용**을 기준으로 정리한 점검용 문서다.  
다음 작업 방향을 정할 때 이걸 보고 판단하면 된다.
