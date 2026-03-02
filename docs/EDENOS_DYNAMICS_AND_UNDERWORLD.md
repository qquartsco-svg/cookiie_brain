# EdenOS — 동역학 레이어 + 지하(Underworld) 개념 정리

**목적**: Kernel Trap(보안 경계) vs 상태 전이(동역학)를 레이어로 분리하고, 지하(Hades) 감시자를 설계 문서로 고정.

---

## 1. 두 개의 다른 레이어 (충돌 아님)

| 레이어 | 역할 | 질문 |
|--------|------|------|
| **Kernel Trap** | 보안 경계 | "이 행동 이후로는 커널 접근 불가" — 누가 무엇을 할 수 있는가 (권한 경계) |
| **Dynamics** | 상태 전이 | "integrity가 N tick 연속 θ 이하 → 자연 강등" — 시스템 상태가 어떻게 흘러가는가 (동역학) |

- **현재 구현**: 선악과 이벤트 → 즉시 권한 박탈 → 추방 (이벤트 기반, 단일 트리거).
- **보완 방향**: 선택 → 스트레스 누적 → integrity 하락 → 자연 전이 (연속 동역학).

선악과는 **폐지가 아니라** "integrity를 즉각 붕괴시키는 충격파"로 동역학 안에 통합된다.

---

## 2. 통합 상태 전이 구조 (목표)

```
IMMORTAL_ADMIN
  │  integrity ≥ θ1  →  유지 (에덴 운영 정상)
  │  integrity < θ1  for N ticks  →
  ▼
DEGRADED_ADMIN
  │  integrity ≥ θ2  →  회복 가능
  │  integrity < θ2  for N ticks  →
  ▼
MORTAL_NPC  (비가역)
```

- **Kernel Trap** 역할: 선악과 = 한 번에 대량 `stress_injection` → integrity가 급격히 θ2 이하로 꺾임 → N tick 대기 없이 즉시 전이 조건 충족.

---

## 3. 관리자 역할 재정의

- **기존**: 권한을 가진 superuser → "누가 내 권한을 빼앗느냐" 문제.
- **올바른 것**: **항상성 유지 컨트롤러 (homeostasis controller)** → "시스템이 자연스럽게 흘러가도록 유지하는 것"이 임무 → 유지에 실패하면 역할 공간이 자연히 축소.

해킹 불가. 동역학적 흐름으로만 전이.

---

## 4. 추가 구현 요소 (EdenOS)

| 추가할 것 | 역할 |
|-----------|------|
| **HomeostasisEngine** | 매 tick stress / integrity 계산 |
| **IntegrityFSM** | N tick 연속 조건 감시 → 자연 전이 (IMMORTAL → DEGRADED → MORTAL) |
| Admin 행동 공간 축소 | DEGRADED 시 observe 범위 축소, act 선택지 감소 |
| **stress_injection API** | 선악과 이벤트 = 대량 stress 주입으로 치환 |

---

## 5. 지하(Underworld) — Hades 레이어

**관계**:

- **지상 (Surface)** ← EdenOS 항상성 관리 시스템 (아담/이브).
- **지하 (Underworld)** ← Hades — 룰의 거시적 감시자 (의식의 목소리).
- **지구 물리 코어** ← solar/day4/core/ (중력장, 자기장, 맨틀).

Hades는 인격화된 악역이 아니다. 물리 시스템 관점:

- 지구 내부 (core/mantle) → 지자기장, 지각 운동/지진/열류 → 전 행성 규모 물리 법칙 집행자.
- 지상 에이전트(아담)는 로컬 최적화 (강 유량, GPP, 생태계).
- Hades는 **행성 전체 스케일의 룰이 지켜지는지** 감시. 무너지려 할 때 "목소리"가 올라옴.

---

## 6. Hades 시스템 설계

**HadesObserver (underworld layer)**

- **입력**: solar/day4/core/ (자기장, 지열, 중력) — deep_monitor 경유.
- **감시**: 행성 거시 룰 위반 여부  
  - 자기장 붕괴 임박?  
  - 대기권 strip 조건?  
  - 열역학 2법칙 위반 패턴?
- **출력**: **ConsciousnessSignal** → 지상 Observer 레이어로 전달 (경고, 압력, 임박 신호).

**불가침 규칙 (설계 붕괴 방지)**

- **Hades ONLY measures. Hades NEVER acts.**
- Hades는 관측·신호 생성만 함. 결정(decide)·처벌(punish)·의도(want)를 가지면 안 됨.
- 행동/전이는 항상 Dynamics(IntegrityFSM, lineage 등) 쪽에서만 발생.
- 이 규칙이 깨지면 physics layer → narrative agent 로 붕괴. (hades.py docstring 동일 문구 유지)

**목소리 구조**

- `ConsciousnessSignal`: source, severity, signal_type, message, tick (frozen).
- signal_type 예: `ENTROPY_WARNING`, `RULE_VIOLATION`, `SYSTEM_PANIC`.

**에이전트 observe() 연동**

- `hades_signal = hades.listen(tick, world)` → Runner가 Step 5 전에 호출.
- `obs = adam.observe(world, ..., hades_signal=hades_signal)` → 목소리가 있으면 `obs.notes`에 `[지하] 메시지` 포함, severity > 0.5 이면 anomaly.
- 동일 `hades_signal`을 HomeostasisEngine.update()에 전달 → stress/integrity에 반영.

---

## 7. 폴더 구조

```
solar/
├── eden/           ← 지상 (EdenOS)
│   └── eden_os/
│       ├── homeostasis_engine.py   — stress / integrity 매 틱
│       ├── integrity_fsm.py        — N-tick 연속 → 자연 전이
│       └── ...
│
└── underworld/     ← 지하 (Hades 레이어)
    ├── __init__.py
    ├── hades.py           — 거시 감시자 + listen() API
    ├── consciousness.py  — ConsciousnessSignal (목소리)
    └── deep_monitor.py    — day4/core 물리값 읽기
```

---

## 8. 엔지니어링 관점 피드백 요약 (확인 반영)

- **레이어 분리**: Surface(로컬 최적화) vs Underworld(거시 제약) — 계층 분리 유지.
- **보안 모델**: 해커/악역 제거 → 물리 기반 피드백(규칙이 감시). 해킹 개념 없음.
- **상태 전이**: 공격자/추방자 없이 동역학적 전이만 존재 (identity loss = dynamical phase transition).
- **관리자**: superuser가 아니라 homeostasis controller. 실패 시 처벌이 아니라 역할 공간 축소.
- **유일한 위험**: Hades가 “의도”를 갖는 순간 설계 붕괴 → **Hades ONLY measures, NEVER acts** 로 고정.

이 문서는 피드백 개념 정리 + 구현 방향 고정용이다. 구현은 단계별로 진행한다.
