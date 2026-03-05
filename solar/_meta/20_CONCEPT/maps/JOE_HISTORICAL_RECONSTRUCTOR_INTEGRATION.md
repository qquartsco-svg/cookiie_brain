# 역사 추적 엔진(HistoricalDataReconstructor) ↔ JOE 연동 가능성 분석

**작성**: JOE 역추적·정보 추적 엔진 결합 설계에 따른 분석  
**대상 모듈**: `HistoricalDataReconstructor`  
**위치**: `00_BRAIN/Brain_Disorder_Simulation_Engine/Unsolved_Problems_Engines/HistoricalDataReconstructor`  
**ENGINE_HUB 링크**: `50_DIAGNOSTIC_LAYER/HistoricalDataReconstructor` → 동일 소스 심볼릭 링크

---

## 0. 피드백 요약 — 역할 고정 (꼭 지킬 것)

- **HDR은 “물리 역적분(현재 지구 → 초기상태)”을 직접 하지 않는다.**  
  HDR은 **“관찰/로그가 흩어져 있어도 시간·문맥·인과로 재조립해서 기원(Origin)을 찾는”** 엔진이다.  
  → JOE의 물리 엔진과는 **기록/추적 레이어**로 결합하는 것이 정답.

- **연결되는 지점 (딱 2개)**  
  - **A. “추적” 파트**: JOE가 매 스텝/스테이지마다 만든 스냅샷을 “흩어진 단편”으로 취급 → HDR이 P(x,t) 정렬·유사도/인과로 체인 재구성 → TraceBack으로 Origin(가장 초기 스냅샷) 반환.  
    즉 **“초기상태를 계산해서 만들어내는”** 게 아니라 **“이미 관측/생성해둔 상태들 중 초기 버전/원인 스냅샷을 찾아주는”** 연결.  
  - **B. “물리 파라미터가 언제/왜 바뀌었는지” 추적**: JOE 스냅샷·stress/instability가 이벤트 트리거(궁창 붕괴 등)와 연결되므로, HDR로 **“어떤 파라미터 변화/외부 입력이 instability 임계로 이어졌는지”**를 인과 체인으로 재구성(테라포밍/룰 튜닝 감사).

- **반대로, “바로 안 되는 것”**  
  HDR의 TraceBack은 **해시/문맥 체인의 역추적**이지, **동역학 방정식의 역적분(역시간 시뮬레이션)**이 아니다.  
  “현재 지구(상태 벡터) → 중력/회전/판/물 보존법칙으로 Day0를 역으로 계산”하는 것은 **JOE 쪽에 역시간 적분기/adjoint/추정(필터링) 로직**이 있어야 하며, HDR는 **그 결과를 증거 체인으로 고정·재조립**하는 역할이다.

- **한 줄 결론**  
  **“현재 지구 입력 → 초기 상태까지 추적”의 본체는 JOE 역추정 로직**이고,  
  **HDR는 그 과정을 ‘역사(History)로 봉인’**해서 **검증/재현/감사 가능한 체인**으로 만드는 역할로 결합한다.

---

## 1. HistoricalDataReconstructor 요약

### 1.1 한 문장 정의 (CONCEPT.md)

> "온라인에 퍼져있는 가역적인 역사 데이터들을 **관찰자 시점**에서 **비가역적 해시 흐름**으로 정리하고, **역전파처럼 역추적**하여 **기원(Origin)**을 찾아가는 시스템"

### 1.2 입력/출력

| 항목 | 내용 |
|------|------|
| **입력** | `scattered_data`: `List[Dict]` — `{"content": str, "source": str, "timestamp": float}` |
| **핵심 API** | `reconstruct_from_scattered_data(scattered_data)` → `ReconstructedChain` |
| **역추적 API** | `trace_back_to_origin(chain)` → `DataFragment` (기원 단편) |
| **출력 구조** | `ReconstructedChain`: `fragments`, `hash_chain`, `origin`, `target`, `causal_links`, `verify_chain()` |

### 1.3 로직 요약

1. **수집**: `content` + `source` + `timestamp` → `DataFragment` (시공간 좌표화 P(x,t))
2. **문맥 분석**: 유사도(Content, Time, Source) + 인과 관계 추론 → `CausalLink[]`
3. **재구성**: 인과 순서로 스토리 흐름 정렬 → 해시 체인 `Hash₀ = H(F₀)`, `Hashₙ = H(Fₙ \|\| Hashₙ₋₁)`
4. **역추적**: `TraceBack(Hashₙ) → … → Hash₀` → 기원 = `fragments[0]` (검증 후)

**중요**: HDR의 “기원(Origin)”은 **물리적 초기조건을 ‘추정’해서 찾는 것이 아니라**, 체인에 들어간 단편들 중 **첫 단편을 ‘검증 가능한 기원’으로 고정**하는 방식이다. (해시 체인 검증 후 `origin = fragments[0]` 반환)

### 1.4 의존성

- **TransparencyEngine.crypto**: `hash_chain`, `verify_hash_chain` (해시 체인 구축/검증)
- 연동 가이드: 재구성된 체인을 TransparencyEngine에 고정(비가역 기록)하는 패턴 제시

---

## 2. JOE와의 역할 비교

| 구분 | JOE (조) | HistoricalDataReconstructor |
|------|----------|-----------------------------|
| **도메인** | 행성 거시 물리 (M, R, ω, W_total, sigma_plate, …) | 온라인/흩어진 역사 데이터 (텍스트·출처·시간) |
| **입력** | 거시 스냅샷(dict) 또는 물리량 → Feature Layer → 스냅샷 | `content`, `source`, `timestamp` 단편 리스트 |
| **역추적 의미** | **추정/동화**: 현재 관측 → 초기 후보 집합 + MAP (물리 모델 기반) | **해시 체인 역순**: 최종 해시 → 검증하며 기원(첫 단편) 반환 |
| **역할** | 평가기(Observer) + Forward/Inference (물리 역추정) | 재구성기(문맥·인과 정렬) + 비가역 체인 + 기원 조회 |
| **시간 축** | 물리 시간 (예: t_span [0, 1e9, 4.5e9] yr) | Unix timestamp / 관찰자 수집 시점 |

**정리**:  
- JOE = **물리 법칙 기반** 역추정 (초기 후보 분포, ill-posed 대응).  
- HDR = **데이터 무결성 + 인과 정렬** 기반 역추적 (해시 체인 → 기원 단편).  
→ **도메인은 다르지만, “시점별 시퀀스 → 기원(첫 시점)”이라는 구조는 맞물릴 수 있음.**

---

## 3. 연동 가능성 — 시나리오

### 3.1 시나리오 A: JOE 스냅샷 시퀀스 → HDR “데이터 단편”으로 재구성

**아이디어**: JOE가 생성한 시점별 거시 스냅샷을 HDR의 `scattered_data` 형식으로 변환한 뒤, HDR로 인과 정렬·해시 체인·기원 조회를 맡긴다.

- **변환 규칙**  
  - `content`: 스냅샷 직렬화 (예: JSON 문자열 또는 `repr(snapshot)`).  
  - `source`: `"joe_observer"` 또는 `"joe://planet_id/t={t}"`.  
  - `timestamp`: **물리 시간(yr)을 그대로 넣지 말 것** — HDR 시간 유사도가 1일(86400초) 기준 정규화라서, yr→초로 넣으면 TimeSim이 거의 0이 됨. **스텝 인덱스(0, 1, 2, …)**를 쓰는 것이 안전하고, 시간 정렬이 목적이면 이게 가장 깔끔함.

- **흐름**  
  1. `forward_dynamics(x0, t_span)` → `snapshots = [snap(t₁), snap(t₂), …]`  
  2. `snapshots` → `scattered_data = [{"content": serialize(s), "source": "joe", "timestamp": t_i}]`  
  3. `reconstructor.reconstruct_from_scattered_data(scattered_data)` → `ReconstructedChain`  
  4. `trace_back_to_origin(chain)` → 기원 = 시간순 첫 스냅샷에 해당하는 단편.

- **효과**  
  - JOE는 “물리 역추정”만 담당.  
  - HDR는 “같은 물리 시퀀스”를 **기록·인과·무결성** 관점에서 재구성하고, **기원 = 첫 시점**을 해시 검증과 함께 반환.  
  - TransparencyEngine과 연동 시, JOE 결과 체인을 비가역적으로 고정하는 데 HDR 통합 패턴을 그대로 사용 가능.

**연동 가능**: ✅ **가능**. 어댑터만 정의하면 됨.

---

### 3.2 시나리오 B: HDR “기록 체인”으로 JOE 역추정 결과 고정

**아이디어**: JOE의 `infer_initial_candidates(y_now)` 결과(초기 후보 리스트 + MAP)를 “결정 이력”으로 보고, HDR로 그 순서를 체인화·고정한다.

- **변환**  
  - 각 후보 `x0_i`를 스냅샷으로 직렬화 → `content`.  
  - `source`: `"joe_inference"`, **`timestamp`**: **순서 인덱스(0, 1, 2, …)** 권장 (HDR 시간 유사도 정규화 이슈 회피).

- **흐름**  
  1. JOE: `infer_initial_candidates(y_now)` → `x0_hat`, `candidates`.  
  2. `candidates` (또는 `[x0_hat] + candidates`) → `scattered_data`.  
  3. HDR: `reconstruct_from_scattered_data` → 체인 생성.  
  4. TransparencyEngine 연동으로 “이 역추정 결과”를 비가역 기록.

- **효과**  
  - “어떤 초기 조건에서 현재 관측이 나왔는지”에 대한 **감사/추적 가능한 기록** 확보.  
  - JOE는 물리 엔진으로만 두고, “기록·검증”은 HDR(+ TransparencyEngine)이 담당.

**연동 가능**: ✅ **가능**. 시나리오 A와 동일한 어댑터 패턴으로 처리 가능.

---

### 3.3 시나리오 C: 정보 추적 엔진(타임라인) = HDR 체인

**아이디어**: JOE_REVERSE_MODE에서 말한 “정보 추적 엔진이 시점별 스냅샷을 주면 JOE가 각 시점을 평가하고 t=0을 초기로 사용”할 때, 그 “시점별 스냅샷” 저장소를 HDR 체인으로 구현한다.

- **역할 분담**  
  - **저장**: 시점별 스냅샷을 `DataFragment` 시퀀스로 저장 → HDR 해시 체인.  
  - **조회**: `trace_back_to_origin(chain)` → t=0에 해당하는 스냅샷(기원 단편의 `content` 역직렬화).  
  - **JOE**: 이미 만들어진 체인에서 기원을 읽어와서, 필요 시 `assess(origin_snapshot)` 등으로 재평가.

- **효과**  
  - “물리적 기억”을 **해시로 검증 가능한 시계열**로 유지.  
  - Hippo(인지 기억)와는 별개로, **행성 거시 시퀀스 전용** “역사 추적” 레이어로 HDR 사용 가능.

**연동 가능**: ✅ **가능**. 스냅샷 직렬화/역직렬화와 `source`/`timestamp` 규약만 정하면 됨.

---

## 4. 제약·조건 (안 하면 망가짐 — 꼭 처리)

| 항목 | 내용 |
|------|------|
| **(1) timestamp 스케일** | HDR의 시간 유사도는 **1일(86400초) 기준** 정규화가 들어가 있다. 물리 시간(년/억년)을 초로 넣으면 TimeSim이 거의 항상 0으로 떨어진다. **JOE 스냅샷 체인 용도라면 `timestamp`는 “스텝 인덱스”(0, 1, 2, …)로 쓰는 것이 안전**하다. 시간 정렬이 목적이면 이게 제일 깔끔하다. |
| **(2) 인과 정렬 vs 이미 정렬된 시퀀스** | JOE 스냅샷은 **애초에 시간순으로 생성** 가능하므로, HDR의 `build_story_flow`가 내용 유사도로 순서를 섞지 않게 하거나(가중치/임계값 조정), **JOE 쪽에서 이미 정렬된 리스트를 넘기고 HDR는 “체인만” 쓰는 모드**로 제한하는 것이 맞다. |
| **의존성** | HDR는 `transparency_engine.crypto`에 의존. CookiieBrain에 TransparencyEngine이 없으면 해시 체인 부분을 자체 구현하거나 선택 의존으로 두어야 함. |
| **입력 형식** | HDR는 `content: str`. 스냅샷은 JSON 등 문자열로 직렬화 필요. |
| **위치** | HDR는 CookiieBrain 워크스페이스 밖(00_BRAIN 하위). 연동 시 경로/패키지 의존성 또는 어댑터를 CookiieBrain 쪽에 두는 구성이 필요. |

---

## 5. 권장 구현 단계

1. **계약 정의 (CookiieBrain 쪽)**  
   - `joe/snapshot_chain_adapter.py` (또는 `solar/_meta/...` 문서):  
     - JOE 스냅샷 시퀀스 `List[Snapshot]` ↔ HDR `scattered_data` 변환 규칙.  
     - `source`/`timestamp`/`content` 필드 규약.

2. **어댑터 구현 (선택)**  
   - `snapshots_to_scattered_data(snapshots, source_prefix="joe")`  
   - `reconstructed_chain_origin_to_snapshot(chain)` (기원 단편의 `content` → dict 스냅샷).

3. **의존성 처리**  
   - HistoricalDataReconstructor(및 TransparencyEngine)를 optional로 두고,  
     있으면 HDR 호출, 없으면 “스냅샷 리스트의 첫 원소 = 기원”만 반환하는 폴백.

4. **문서 반영**  
   - JOE_REVERSE_MODE.md 또는 JOE_FEEDBACK_REFERENCE.md에  
     “정보 추적 엔진 = HistoricalDataReconstructor 연동(선택)” 및 위 시나리오 요약 추가.

---

## 6. 결론

| 질문 | 답 |
|------|----|
| **연동 가능한가?** | **된다.** 다만 연결의 의미는 아래와 같이 고정한다. |
| **역할 구분** | **JOE(물리 엔진)**: 현재 → 과거 “역추정/동역학 계산” 자체를 수행. **HDR(역사 추적 엔진)**: JOE가 만든 스냅샷/후보/결정 흐름을 `content`/`source`/`timestamp`로 받아, 해시 체인 + `verify_chain`으로 **“조작/누락 불가한 시간 흐름”**으로 고정하고, `origin`=첫 단편을 **검증 가능한 형태**로 제공. |
| **한 줄** | “현재 지구 입력 → 초기 상태까지 추적”의 **본체는 JOE 역추정 로직**이고, HDR는 그 과정을 **‘역사(History)로 봉인’**해서 **다시 검증/재현/감사 가능한 체인**으로 만드는 역할로 결합된다. |
| **구현 시 필수** | (1) `timestamp` = 스텝 인덱스(0,1,2,…) 사용. (2) JOE는 이미 정렬된 스냅샷 리스트를 넘기고, HDR는 체인만 쓰는 모드 또는 인과 가중치 조정. |
| **다음 단계** | (1) 스냅샷 ↔ `content`/`source`/`timestamp` 규약 문서화, (2) `snapshot_chain_adapter.py` 등 optional 어댑터 구현, (3) TransparencyEngine 의존성 여부에 따른 폴백. |

---

**관련 문서**  
- JOE: `JOE_REVERSE_MODE.md`, `JOE_FEEDBACK_REFERENCE.md`, `forward_inference.py`  
- HDR: `00_BRAIN/.../HistoricalDataReconstructor/CONCEPT.md`, `DESIGN.md`, `INTEGRATION_GUIDE.md`
