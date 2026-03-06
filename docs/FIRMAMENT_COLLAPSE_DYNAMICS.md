# 궁창 붕괴 동역학 — 본편 서사로 가는 로직 정리

**목적**: 지금까지 논의한 개념(동시성 epoch, 이중 서사, instability)이 **궁창 붕괴 이벤트로 수렴**하도록 로직을 고정하고, 본편 서사에 동역학으로 구현할 때 쓰는 기준 문서.

---

## 1. 포인트

- **다양한 개념의 동역학이 궁창 붕괴 이벤트로 가야 한다.**
- 붕괴는 “버튼 한 번”이 아니라, **행성 스트레스·인구·에너지 누적**이 임계를 넘을 때 **시스템이 스스로 전이**하는 구조로 둔다.
- 서사(LORE)는 **관찰자(인류 vs 아담 계열)**에 따라 “대홍수” vs “라그나로크”로 다르게 기록될 뿐, **물리 이벤트는 하나**.

---

## 2. 아담→노아 구간: 동시성(Concurrency) 모델

- **세대 연대기가 아니라 동시 존재 공간**으로 둔다.
  - Pool A: 일반 인류 (창 1장, 120년 한계, 땅 위 대량 스폰).
  - Pool B: 아담 계열 (에덴 관리자 → 추방 후 땅에서 동시 활동).
- 아담, 셋, 에노스, … 노아의 아버지 라멕까지가 **한 시대에 동시에 맵에 존재**하며, 각자 수백 년을 살며 자원(GPP)·에너지를 소비한다.
- “하나님의 아들들 + 사람의 딸들” = Pool B와 Pool A의 **교배(크로스)** → 네피림(하이브리드) 스폰.
- 이 **동시 활동 전체**가 행성 스트레스·수증기 부담·에너지 누적을 올려, **instability**가 임계에 도달하게 만든다.

---

## 3. 궁창 붕괴 = 동역학적 전이 (외부 트리거 아님)

- **입력**: 매 틱/매 연도, 지상·생태계에서 나오는 상태량.
  - `planet_stress` (행성 스트레스 지수, 0~1).
  - (선택) 인구/생물량 비율, GPP 초과 사용률, 상층 수증기 W(t) 등.
- **불안정도**:  
  `instability(t) = f(planet_stress, ...)`  
  예: `instability = planet_stress` 또는 `min(1, planet_stress + α * population_pressure)`.
- **붕괴 조건**:  
  `instability(t) >= threshold` 이면  
  `FirmamentLayer`가 **자동으로** `collapse_triggered = True` 로 세팅하고, 같은/다음 `step()`에서 `_do_collapse()` 실행.
- 그러면 “궁창 붕괴”는 **서사가 트리거하는 게 아니라**, 위 동역학이 임계를 넘은 **결과**가 된다.
- **주의**: 위 `instability(t)`를 **누가 어떻게 계산하는지**는 본편(Runner/통합) 몫이다. 현재는 **계산 모듈이 없어** instability는 외부 주입 상태다. → §6·§7 참고.

---

## 4. 이중 서사 (Dual Logging) — LORE 레이어

- **같은 물리 이벤트**(캐노피 응축, 40일 폭우, S→0, 수명/환경 급변)를:
  - **일반 인류(NPC) 시점**: “대홍수” — 맵이 물로 초기화된 재난.
  - **아담 계열(관리자) 시점**: “라그나로크” — 신들의 시대가 끝나고 불멸성(900년)을 잃는 종말.
- 구현: 이벤트 발생 시 **로그 메시지/서사 문자열**만 관찰자 타입(admin_line vs general)에 따라 다르게 출력. **이벤트 자체는 하나** (FloodEvent 한 번).

---

## 5. 본편에서의 연결

- **FirmamentLayer.step(dt_yr, instability=None, instability_threshold=0.85)**  
  - 호출하는 쪽(Runner 또는 통합 레이어)이 `planet_stress`(및 필요 시 인구/GPP 압력)를 모아 `instability`를 계산해 넘긴다.  
  - `instability`가 주어지고 `>= threshold`이면 `collapse_triggered = True` 로 세팅 → 같은 step 또는 다음 step에서 붕괴 실행.
- **Runner/통합**  
  - 매 틱 `planet_stress`(또는 EdenOS 측에서 대리 지표)를 읽고, `instability = f(planet_stress, ...)` 로 계산한 뒤 `FirmamentLayer.step(dt_yr, instability=instability)` 호출.
- **LORE**  
  - FloodEvent 발생 시, 현재 “관찰자”가 admin_line이면 “라그나로크”, general이면 “대홍수” 등으로 메시지/서사만 분기.

---

## 6. 구현 상태 — 불안정도(instability)는 "외부 주입"

- **개념**: 붕괴는 instability ≥ threshold일 때 **시스템이 스스로 전이**. 설계 방향은 위와 같다.
- **현재 코드**: `FirmamentLayer.step(dt_yr, instability=...)`에 **넣을 값은 호출 측이 계산**해야 함.  
  **instability를 계산하는 본편 모듈은 아직 없음.**  
  즉, instability는 문서상 설계만 있고, **실제로는 외부에서 주입**해야 붕괴가 터진다.  
  Runner가 FirmamentLayer를 직접 제어하지 않으며, `planet_stress → instability` 연결은 **미구현**.
- **다음 단계**: 아래 7절처럼 **instability 계산 함수**를 하나 확정하지 않으면, 붕괴는 여전히 "외부 입력"이다.

---

## 7. instability 계산 함수 (설계·결정 필요)

붕괴가 "동역학적 전이"가 되려면, **매 틱/매 연도 instability를 계산하는 실제 함수**가 필요하다.

**후보 식 (플레이스홀더)**:

```text
instability(t) = a * planet_stress
                 + b * population_pressure   # 선택: 동시성 epoch 시 구현
                 + c * water_vapor_mass      # 선택: 상층 수증기 W(t) 등
```

- **최소 버전**: `instability = planet_stress` (단일 변수).  
  day7 Runner의 `planet_stress` 또는 gaia_engine의 `planet_stress_ema`를 그대로 넘기면 됨.
- **확장 버전**: population_pressure, water_vapor_mass 등 추가 시, **동시성 epoch**(여러 admin_line·일반 인류·네피림 동시 상주) 및 생태/대기 모듈이 선행되어야 함.

**결정 필요**:
- **A)** 먼저 **planet_stress 기반 단일 instability**만 Runner에 연결해 "붕괴 = 동역학"을 완성할지,
- **B)** **population 동역학**(동시성 에이전트 수, pressure 지표)을 먼저 넣고 그다음 instability 공식에 반영할지.

문서·개념은 (동시성, 네피림, 라그나로크 등) 코드보다 앞서 나가 있으므로, 구현 단계에서는 **A → B** 순서로 단계를 나누는 편이 위험을 줄인다.

---

## 8. 요약

| 항목 | 내용 |
|------|------|
| **아담→노아** | 동시성 epoch. 여러 관리자·일반 인류·네피림이 동시에 활동. **(개념·문서만; 코드 미구현)** |
| **붕괴 원인** | 동역학: instability(planet_stress, …) ≥ threshold → 궁창 자동 붕괴. **(FirmamentLayer는 구현됨; instability 계산 모듈 없음)** |
| **이중 서사** | 같은 FloodEvent를 인류는 "대홍수", 아담 계열은 "라그나로크"로 기록 (LORE). **(문서만)** |
| **구현** | FirmamentLayer에 `instability` 인자 있음; **Runner가 instability를 계산해 넣어 호출하는 부분은 미구현.** |

이렇게 하면 "이런저런 개념의 동역학이 궁창 붕괴 이벤트로 가는" 로직이 본편 서사에 명확히 반영된다.  
현재는 **설계 약 70%, 본편 통합 약 40%** 수준이며, **instability 계산 함수 확정**이 다음 스텝이다.